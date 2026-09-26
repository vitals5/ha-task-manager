"""The Task Manager integration."""
from __future__ import annotations

import logging
import os
from typing import Any

from homeassistant.components import panel_custom
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN, FRONTEND_DIR, PLATFORMS, URL_BASE
from .services import async_register_services, async_unregister_services
from .storage import TaskManagerStorage
from .websocket import async_register_websocket_api

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Task Manager from a config entry."""
    storage = TaskManagerStorage(hass)
    await storage.async_load()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = storage

    # Register WebSocket API and action services
    async_register_websocket_api(hass, storage)
    async_register_services(hass, storage)

    # Set up platforms (calendar, sensor, todo)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Sync external provider tasks
    try:
        await storage.async_sync_providers()
    except Exception as err:
        _LOGGER.warning("Could not initially sync providers: %s", err)

    # Listen for state changes on external provider todo entities
    @callback
    def _async_on_state_change(event: Any) -> None:
        """Handle state change of external provider todo entities."""
        entity_id = event.data.get("entity_id", "")
        if not entity_id.startswith("todo.") or entity_id.startswith(f"todo.{DOMAIN}"):
            return
        provider_ids = {p.get("entity_id") for p in storage.data.providers}
        if entity_id in provider_ids:
            hass.async_create_task(storage.async_sync_providers())

    entry.async_on_unload(
        hass.bus.async_listen(EVENT_STATE_CHANGED, _async_on_state_change)
    )

    # Set up custom sidebar panel & static HTTP assets
    await _async_setup_frontend(hass)

    _LOGGER.info("Task Manager integration setup completed successfully")
    return True


async def _async_setup_frontend(hass: HomeAssistant) -> None:
    """Register HTTP static path and custom sidebar panel."""
    # Register static path for frontend assets
    if hasattr(hass.http, "async_register_static_paths"):
        from homeassistant.components.http import StaticPathConfig
        await hass.http.async_register_static_paths([
            StaticPathConfig(URL_BASE, FRONTEND_DIR, cache_headers=False)
        ])
    else:
        hass.http.register_static_path(URL_BASE, FRONTEND_DIR, cache_headers=False)

    version_str = "1.0.8"
    try:
        js_file = os.path.join(FRONTEND_DIR, "task-manager-panel.js")
        if os.path.exists(js_file):
            version_str = f"{version_str}.{int(os.path.getmtime(js_file))}"
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
                module_url=f"{URL_BASE}/task-manager-panel.js?v={version_str}",
                embed_iframe=False,
                require_admin=False,
            )
            _LOGGER.info("Registered Task Manager sidebar panel at /task-manager (v=%s)", version_str)
        except Exception as err:
            _LOGGER.error("Failed to register Task Manager sidebar panel: %s", err)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Task Manager config entry."""
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
    return unload_ok
