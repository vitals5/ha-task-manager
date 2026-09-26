"""Provider adapters and external todo integration for Task Manager."""
from __future__ import annotations

from datetime import date, datetime
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

# Known provider metadata
PROVIDER_METADATA: dict[str, dict[str, str]] = {
    "google_tasks": {
        "name": "Google Tasks",
        "icon": "mdi:google",
    },
    "todoist": {
        "name": "Todoist",
        "icon": "mdi:checkbox-marked",
    },
    "caldav": {
        "name": "CalDAV / Nextcloud",
        "icon": "mdi:calendar-sync",
    },
    "local_todo": {
        "name": "Local To-do",
        "icon": "mdi:clipboard-list",
    },
    "bring": {
        "name": "Bring Shopping",
        "icon": "mdi:cart",
    },
    "shopping_list": {
        "name": "Shopping List",
        "icon": "mdi:cart-outline",
    },
    "generic": {
        "name": "External To-do",
        "icon": "mdi:format-list-checks",
    },
}


def detect_provider_type(hass: HomeAssistant, entity_id: str) -> dict[str, str]:
    """Detect the integration domain, icon, and friendly name for a todo entity."""
    domain = "generic"
    name = entity_id

    try:
        entity_reg = er.async_get(hass)
        entry = entity_reg.async_get(entity_id)
        if entry:
            name = getattr(entry, "name", None) or getattr(entry, "original_name", None) or entity_id
            if getattr(entry, "config_entry_id", None) and hasattr(hass, "config_entries"):
                cfg = hass.config_entries.async_get_entry(entry.config_entry_id)
                if cfg:
                    domain = getattr(cfg, "domain", "generic")
            elif getattr(entry, "platform", None):
                domain = entry.platform
    except Exception:
        pass

    try:
        state = hass.states.get(entity_id) if hass and hasattr(hass, "states") else None
        if state and hasattr(state, "attributes") and isinstance(state.attributes, dict):
            fn = state.attributes.get("friendly_name")
            if fn:
                name = fn
    except Exception:
        pass

    # Heuristic fallback if domain is generic
    if domain == "generic":
        lower_id = entity_id.lower()
        if "google" in lower_id:
            domain = "google_tasks"
        elif "todoist" in lower_id:
            domain = "todoist"
        elif "bring" in lower_id:
            domain = "bring"
        elif "caldav" in lower_id or "nextcloud" in lower_id:
            domain = "caldav"
        elif "local" in lower_id:
            domain = "local_todo"
        elif "shopping" in lower_id or "einkauf" in lower_id:
            domain = "shopping_list"

    meta = PROVIDER_METADATA.get(domain, {
        "name": domain.replace("_", " ").title() if isinstance(domain, str) else "External To-do",
        "icon": "mdi:format-list-checks",
    })

    return {
        "provider_type": domain or "generic",
        "name": name or entity_id,
        "provider_name": meta.get("name", "External To-do"),
        "icon": meta.get("icon", "mdi:format-list-checks"),
    }


def async_get_available_todo_entities(hass: HomeAssistant, our_domain: str = "task_manager") -> list[dict[str, Any]]:
    """Return all available external todo entities in Home Assistant."""
    result: list[dict[str, Any]] = []
    seen: set[str] = set()

    # 1. From states
    if hasattr(hass, "states"):
        states = []
        try:
            states = hass.states.async_all("todo")
        except TypeError:
            try:
                states = [s for s in hass.states.async_all() if getattr(s, "domain", "") == "todo" or getattr(s, "entity_id", "").startswith("todo.")]
            except Exception:
                states = []
        except Exception:
            states = []

        for state in states:
            try:
                e_id = getattr(state, "entity_id", None)
                if not e_id or not e_id.startswith("todo."):
                    continue
                if e_id.startswith(f"todo.{our_domain}"):
                    continue
                if e_id in seen:
                    continue
                seen.add(e_id)
                meta = detect_provider_type(hass, e_id)
                result.append({
                    "entity_id": e_id,
                    "name": meta["name"],
                    "provider_type": meta["provider_type"],
                    "provider_name": meta["provider_name"],
                    "icon": meta["icon"],
                })
            except Exception as err:
                _LOGGER.debug("Error processing todo state: %s", err)

    # 2. From entity registry
    try:
        entity_reg = er.async_get(hass)
        entries = list(entity_reg.entities.values()) if hasattr(entity_reg.entities, "values") else []
        for entry in entries:
            try:
                if getattr(entry, "domain", None) != "todo":
                    continue
                e_id = getattr(entry, "entity_id", None)
                if not e_id or not e_id.startswith("todo."):
                    continue
                if e_id.startswith(f"todo.{our_domain}"):
                    continue
                if e_id in seen:
                    continue
                seen.add(e_id)
                meta = detect_provider_type(hass, e_id)
                result.append({
                    "entity_id": e_id,
                    "name": meta["name"],
                    "provider_type": meta["provider_type"],
                    "provider_name": meta["provider_name"],
                    "icon": meta["icon"],
                })
            except Exception as err:
                _LOGGER.debug("Error processing entity registry entry: %s", err)
    except Exception as err:
        _LOGGER.debug("Error querying entity registry: %s", err)

    return result


async def async_read_external_tasks(hass: HomeAssistant, entity_id: str) -> list[dict[str, Any]]:
    """Read tasks from an external Home Assistant todo entity."""
    tasks: list[dict[str, Any]] = []

    # Method 1: Try reading directly from todo entity in hass.data
    try:
        todo_comp = hass.data.get("todo")
        if todo_comp and hasattr(todo_comp, "get_entity"):
            entity = todo_comp.get_entity(entity_id)
            if entity and hasattr(entity, "todo_items") and entity.todo_items is not None:
                for item in entity.todo_items:
                    uid = getattr(item, "uid", None) or getattr(item, "id", None)
                    if not uid:
                        continue
                    due_date = None
                    due_time = None
                    due = getattr(item, "due", None)
                    if due is not None:
                        if isinstance(due, datetime):
                            local_due = due.astimezone(dt_util.DEFAULT_TIME_ZONE)
                            due_date = local_due.date().isoformat()
                            due_time = local_due.strftime("%H:%M")
                        elif isinstance(due, date):
                            due_date = due.isoformat()
                        elif isinstance(due, str):
                            due_date = due[:10]

                    status_val = getattr(item, "status", "needs_action")
                    is_done = status_val == "completed"

                    tasks.append({
                        "uid": str(uid),
                        "title": getattr(item, "summary", "") or getattr(item, "title", ""),
                        "description": getattr(item, "description", "") or "",
                        "status": "completed" if is_done else "pending",
                        "due_date": due_date,
                        "due_time": due_time,
                    })
                return tasks
    except Exception as err:
        _LOGGER.debug("Could not read directly from entity %s: %s", entity_id, err)

    # Method 2: Call Home Assistant todo.get_items service
    try:
        response = await hass.services.async_call(
            "todo",
            "get_items",
            {"status": ["needs_action", "completed"]},
            target={"entity_id": entity_id},
            blocking=True,
            return_response=True,
        )
        if response and isinstance(response, dict):
            entity_data = response.get(entity_id, {})
            items = entity_data.get("items", [])
            for item in items:
                uid = item.get("uid") or item.get("id")
                if not uid:
                    continue
                due_val = item.get("due") or item.get("due_date")
                due_date = None
                due_time = None
                if due_val:
                    if "T" in due_val:
                        parts = due_val.split("T")
                        due_date = parts[0]
                        due_time = parts[1][:5]
                    else:
                        due_date = due_val[:10]

                is_done = item.get("status") == "completed"
                tasks.append({
                    "uid": str(uid),
                    "title": item.get("summary", "") or item.get("title", ""),
                    "description": item.get("description", "") or "",
                    "status": "completed" if is_done else "pending",
                    "due_date": due_date,
                    "due_time": due_time,
                })
    except Exception as err:
        _LOGGER.error("Failed to fetch items from external todo %s: %s", entity_id, err)

    return tasks


async def async_create_external_task(
    hass: HomeAssistant,
    entity_id: str,
    title: str,
    due_date: str | None = None,
    due_time: str | None = None,
    description: str | None = None,
) -> bool:
    """Create a new task in an external todo list."""
    service_data: dict[str, Any] = {"item": title}
    if due_date:
        if due_time:
            service_data["due_datetime"] = f"{due_date}T{due_time}:00"
        else:
            service_data["due_date"] = due_date
    if description:
        service_data["description"] = description

    try:
        await hass.services.async_call(
            "todo",
            "add_item",
            service_data,
            target={"entity_id": entity_id},
            blocking=True,
        )
        return True
    except Exception as err:
        _LOGGER.error("Failed to add item to external todo %s: %s", entity_id, err)
        return False


async def async_update_external_task(
    hass: HomeAssistant,
    entity_id: str,
    uid: str,
    title: str | None = None,
    status: str | None = None,
    due_date: str | None = None,
    due_time: str | None = None,
    description: str | None = None,
) -> bool:
    """Update or complete/reset a task in an external todo list."""
    service_data: dict[str, Any] = {"item": uid}
    if title:
        service_data["rename"] = title
    if status is not None:
        service_data["status"] = "completed" if status == "completed" else "needs_action"
    if due_date:
        if due_time:
            service_data["due_datetime"] = f"{due_date}T{due_time}:00"
        else:
            service_data["due_date"] = due_date
    if description is not None:
        service_data["description"] = description

    try:
        await hass.services.async_call(
            "todo",
            "update_item",
            service_data,
            target={"entity_id": entity_id},
            blocking=True,
        )
        return True
    except Exception as err:
        _LOGGER.error("Failed to update item in external todo %s: %s", entity_id, err)
        return False


async def async_delete_external_task(
    hass: HomeAssistant,
    entity_id: str,
    uid: str,
) -> bool:
    """Delete a task from an external todo list."""
    try:
        await hass.services.async_call(
            "todo",
            "remove_item",
            {"item": [uid]},
            target={"entity_id": entity_id},
            blocking=True,
        )
        return True
    except Exception as err:
        _LOGGER.error("Failed to remove item from external todo %s: %s", entity_id, err)
        return False
