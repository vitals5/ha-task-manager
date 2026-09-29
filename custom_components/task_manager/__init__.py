"""The Task Manager integration."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
import os
from typing import Any

from homeassistant.components import panel_custom
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED, EVENT_STATE_CHANGED
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.event import async_call_later, async_track_time_change
from homeassistant.util import dt as dt_util

from .const import (
    DATA_REMINDER_TIMERS,
    DOMAIN,
    EVENT_TASK_DUE,
    EVENT_TASK_OVERDUE,
    EVENT_TASK_REMINDER,
    FRONTEND_DIR,
    PLATFORMS,
    SIGNAL_TASK_MANAGER_UPDATED,
    URL_BASE,
)
from .services import async_register_services, async_unregister_services
from .storage import TaskManagerStorage
from .websocket import async_register_websocket_api

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Task Manager from a config entry."""
    storage = TaskManagerStorage(hass)
    await storage.async_load()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = storage
    reminder_timers: dict[tuple[str, int], Any] = {}
    hass.data.setdefault(DATA_REMINDER_TIMERS, {})[entry.entry_id] = reminder_timers

    # Register WebSocket API and action services
    async_register_websocket_api(hass, storage)
    async_register_services(hass, storage)

    # Set up platforms (binary_sensor, calendar, sensor, todo)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Sync external provider tasks
    try:
        await storage.async_sync_providers()
    except Exception as err:
        _LOGGER.warning("Could not initially sync providers: %s", err)

    # Initial sync of external entities linked to Things
    things_updated = False
    for th in storage.data.things:
        ext_id = th.get("external_entity_id")
        if ext_id and hass.states.get(ext_id):
            st = hass.states.get(ext_id)
            if st and st.state not in ("unavailable", "unknown"):
                try:
                    val = float(st.state)
                    if storage.data.update_thing_value(th["id"], value=val):
                        things_updated = True
                except (ValueError, TypeError):
                    pass
    if things_updated:
        try:
            await storage.async_save()
        except Exception as err:
            _LOGGER.debug("Could not save storage after initial things sync: %s", err)

    # Reminder & Daily Event Management
    @callback
    def _fire_reminder(task: dict[str, Any], offset: int) -> None:
        """Fire event when task reminder arrives."""
        storage.fire_task_event(EVENT_TASK_REMINDER, task, {"reminder_offset_minutes": offset})

    @callback
    def _reschedule_reminders() -> None:
        """Schedule in-memory timers for configured task reminders."""
        # Cancel active timers
        for unsub in reminder_timers.values():
            try:
                unsub()
            except Exception:
                pass
        reminder_timers.clear()

        now = dt_util.now()
        all_tasks = storage.data.get_all_tasks(include_external=True)
        for task in all_tasks:
            if task.get("status") != "pending":
                continue
            due_date = task.get("due_date")
            reminders = task.get("reminders")
            if not due_date or not reminders:
                continue

            due_time = task.get("due_time") or "09:00"
            try:
                time_parts = due_time.split(":")
                hour = int(time_parts[0])
                minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                date_parts = [int(p) for p in due_date.split("-")]
                due_dt = dt_util.now().replace(
                    year=date_parts[0],
                    month=date_parts[1],
                    day=date_parts[2],
                    hour=hour,
                    minute=minute,
                    second=0,
                    microsecond=0,
                )
            except Exception:
                continue

            for offset in reminders:
                try:
                    offset_min = int(offset)
                    target_dt = due_dt - timedelta(minutes=offset_min)
                    if target_dt > now:
                        delay = (target_dt - now).total_seconds()
                        key = (task["id"], offset_min)
                        task_snapshot = dict(task)

                        def _make_handler(t: dict[str, Any], o: int):
                            return lambda _: _fire_reminder(t, o)

                        reminder_timers[key] = async_call_later(hass, delay, _make_handler(task_snapshot, offset_min))
                except (ValueError, TypeError):
                    continue

    _reschedule_reminders()
    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_TASK_MANAGER_UPDATED, _reschedule_reminders)
    )

    # Midnight daily check for due and overdue events
    @callback
    def _check_daily_due_tasks(now: Any = None) -> None:
        """Check for due and overdue tasks and fire automation events."""
        today_str = dt_util.now().date().strftime("%Y-%m-%d")
        all_tasks = storage.data.get_all_tasks(include_external=True)
        for t in all_tasks:
            if t.get("status") == "pending":
                due = t.get("due_date", "")
                if due:
                    if due == today_str:
                        storage.fire_task_event(EVENT_TASK_DUE, t)
                    elif due < today_str:
                        storage.fire_task_event(EVENT_TASK_OVERDUE, t)

    _check_daily_due_tasks()
    entry.async_on_unload(
        async_track_time_change(hass, _check_daily_due_tasks, hour=0, minute=0, second=0)
    )

    # Listen for state changes on external provider todo entities and linked thing entities
    @callback
    def _async_on_state_change(event: Any) -> None:
        """Handle state change of external provider todo entities and linked thing entities."""
        entity_id = event.data.get("entity_id", "")
        if not entity_id:
            return

        # 1. External Todo Provider sync
        if entity_id.startswith("todo.") and not entity_id.startswith(f"todo.{DOMAIN}"):
            provider_ids = {p.get("entity_id") for p in storage.data.providers}
            if entity_id in provider_ids:
                hass.async_create_task(storage.async_sync_providers())
                return

        # 2. Linked numeric entities for Things
        things_to_update = [
            th for th in storage.data.things
            if th.get("external_entity_id") == entity_id
        ]
        if things_to_update:
            new_state = event.data.get("new_state")
            if new_state and new_state.state not in ("unavailable", "unknown"):
                try:
                    val = float(new_state.state)
                    updated = False
                    for th in things_to_update:
                        if storage.data.update_thing_value(th["id"], value=val):
                            updated = True
                    if updated:
                        hass.async_create_task(storage.async_save())
                except (ValueError, TypeError):
                    pass

    entry.async_on_unload(
        hass.bus.async_listen(EVENT_STATE_CHANGED, _async_on_state_change)
    )

    # Set up custom sidebar panel & static HTTP assets
    await _async_setup_frontend(hass)

    _LOGGER.info("Task Manager integration setup completed successfully")
    return True


async def _async_setup_frontend(hass: HomeAssistant) -> None:
    """Register HTTP static path, Lovelace dashboard card, and custom sidebar panel."""
    # Register static path for frontend assets
    if hasattr(hass.http, "async_register_static_paths"):
        from homeassistant.components.http import StaticPathConfig
        await hass.http.async_register_static_paths([
            StaticPathConfig(URL_BASE, FRONTEND_DIR, cache_headers=False)
        ])
    else:
        hass.http.register_static_path(URL_BASE, FRONTEND_DIR, cache_headers=False)

    version_str = "1.0.25"
    try:
        card_file = os.path.join(FRONTEND_DIR, "task-manager-card.js")
        if os.path.exists(card_file):
            version_str = f"{version_str}.{int(os.path.getmtime(card_file))}"
    except Exception:
        pass

    card_url = f"{URL_BASE}/task-manager-card.js?v={version_str}"

    # 1. Register Lovelace card via add_extra_js_url so it is loaded on all HA dashboards
    if not hass.data.get(f"{DOMAIN}_card_registered"):
        hass.data[f"{DOMAIN}_card_registered"] = True
        try:
            from homeassistant.components.frontend import add_extra_js_url
            add_extra_js_url(hass, card_url)
            _LOGGER.info("Registered Task Manager Lovelace card via add_extra_js_url: %s", card_url)
        except Exception as err:
            _LOGGER.debug("Could not register Lovelace card via add_extra_js_url: %s", err)

        # 2. Also auto-register in Lovelace resources storage collection if available
        async def _async_register_lovelace_resource() -> None:
            try:
                lovelace = hass.data.get("lovelace")
                if not lovelace:
                    return
                resources = getattr(lovelace, "resources", None)
                if not resources:
                    return
                if not getattr(resources, "loaded", True):
                    try:
                        await resources.async_load()
                    except Exception:
                        pass
                existing = None
                for item in resources.async_items():
                    url = item.get("url", "")
                    if url.startswith(f"{URL_BASE}/task-manager-card.js"):
                        existing = item
                        break
                if existing:
                    if existing.get("url") != card_url and hasattr(resources, "async_update_item"):
                        await resources.async_update_item(existing["id"], {"res_type": "module", "url": card_url})
                elif hasattr(resources, "async_create_item"):
                    await resources.async_create_item({"res_type": "module", "url": card_url})
                    _LOGGER.info("Auto-registered Task Manager Lovelace resource: %s", card_url)
            except Exception as err:
                _LOGGER.debug("Could not auto-register Lovelace resource: %s", err)

        if getattr(hass, "is_running", True):
            hass.async_create_task(_async_register_lovelace_resource())
        else:
            async def _on_ha_started(_event: Any) -> None:
                await _async_register_lovelace_resource()
            hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _on_ha_started)

    # 3. Register custom sidebar panel
    panel_version = "1.0.25"
    try:
        js_file = os.path.join(FRONTEND_DIR, "task-manager-panel.js")
        if os.path.exists(js_file):
            panel_version = f"{panel_version}.{int(os.path.getmtime(js_file))}"
    except Exception:
        pass

    if not hass.data.get(f"{DOMAIN}_panel_registered"):
        hass.data[f"{DOMAIN}_panel_registered"] = True
        try:
            await panel_custom.async_register_panel(
                hass=hass,
                frontend_url_path="task-manager",
                webcomponent_name="task-manager-panel",
                sidebar_title="Task Manager",
                sidebar_icon="mdi:checkbox-marked-circle-outline",
                module_url=f"{URL_BASE}/task-manager-panel.js?v={panel_version}",
                embed_iframe=False,
                require_admin=False,
            )
            _LOGGER.info("Registered Task Manager sidebar panel at /task-manager (v=%s)", panel_version)
        except Exception as err:
            _LOGGER.error("Failed to register Task Manager sidebar panel: %s", err)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Task Manager config entry."""
    # Cancel reminder timers
    timers_by_entry = hass.data.get(DATA_REMINDER_TIMERS, {}).pop(entry.entry_id, {})
    for unsub in timers_by_entry.values():
        try:
            unsub()
        except Exception:
            pass

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        if not hass.data[DOMAIN]:
            async_unregister_services(hass)
            if hass.data.get(f"{DOMAIN}_panel_registered"):
                try:
                    frontend = hass.components.frontend
                    frontend.async_remove_panel("task-manager")
                    hass.data[f"{DOMAIN}_panel_registered"] = False
                except Exception as err:
                    _LOGGER.debug("Could not remove panel: %s", err)
            hass.data.pop(f"{DOMAIN}_card_registered", None)
    return unload_ok
