"""WebSocket API handlers for Task Manager."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .providers import async_get_available_todo_entities
from .storage import TaskManagerStorage

_LOGGER = logging.getLogger(__name__)


def async_register_websocket_api(hass: HomeAssistant, storage: TaskManagerStorage) -> None:
    """Register all Task Manager WebSocket commands."""

    @websocket_api.websocket_command({vol.Required("type"): "task_manager/get_data"})
    @websocket_api.async_response
    async def ws_get_data(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle get_data command."""
        connection.send_result(msg["id"], storage.get_view_data())

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/save_task",
        vol.Required("task"): dict,
    })
    @websocket_api.async_response
    async def ws_save_task(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle save or update task command."""
        task_data = msg["task"]
        result = await storage.async_save_task(task_data)
        connection.send_result(msg["id"], {"success": True, "task": result, "data": storage.get_view_data()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/complete_task",
        vol.Required("task_id"): str,
        vol.Optional("user_id"): vol.Any(str, None),
    })
    @websocket_api.async_response
    async def ws_complete_task(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle complete task command."""
        result = await storage.async_complete_task(msg["task_id"], user_id=msg.get("user_id"))
        if not result:
            connection.send_error(msg["id"], "task_not_found", "Task not found")
            return
        connection.send_result(msg["id"], {"success": True, "task": result, "data": storage.get_view_data()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/reset_task",
        vol.Required("task_id"): str,
    })
    @websocket_api.async_response
    async def ws_reset_task(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle reset task command."""
        result = await storage.async_reset_task(msg["task_id"])
        if not result:
            connection.send_error(msg["id"], "task_not_found", "Task not found")
            return
        connection.send_result(msg["id"], {"success": True, "task": result, "data": storage.get_view_data()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/delete_task",
        vol.Required("task_id"): str,
    })
    @websocket_api.async_response
    async def ws_delete_task(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle delete task command."""
        success = await storage.async_delete_task(msg["task_id"])
        connection.send_result(msg["id"], {"success": success, "data": storage.get_view_data()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/update_subtask",
        vol.Required("task_id"): str,
        vol.Required("subtask_id"): str,
        vol.Required("completed"): bool,
    })
    @websocket_api.async_response
    async def ws_update_subtask(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle update subtask command."""
        task_id = msg["task_id"]
        if task_id.startswith("ext:"):
            parts = task_id.split(":", 2)
            uid = parts[2]
            overlay = storage.data.get_overlay(uid)
            subtasks = overlay.get("subtasks", [])
            for st in subtasks:
                if st.get("id") == msg["subtask_id"]:
                    st["completed"] = msg["completed"]
                    break
            storage.data.set_overlay(uid, overlay)
            await storage.async_save()
            connection.send_result(msg["id"], {"success": True, "data": storage.get_view_data()})
        else:
            success = storage.data.update_subtask(task_id, msg["subtask_id"], msg["completed"])
            if success:
                await storage.async_save()
            connection.send_result(msg["id"], {"success": success, "data": storage.get_view_data()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/save_thing",
        vol.Required("thing"): dict,
    })
    @websocket_api.async_response
    async def ws_save_thing(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle save or update thing command."""
        thing_data = msg["thing"]
        thing_id = thing_data.get("id")

        if thing_id and storage.data.get_thing(thing_id):
            result = storage.data.update_thing(thing_id, thing_data)
        else:
            result = storage.data.create_thing(thing_data)

        await storage.async_save()
        connection.send_result(msg["id"], {"success": True, "thing": result, "data": storage.get_view_data()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/update_thing_value",
        vol.Required("thing_id"): str,
        vol.Optional("value"): vol.Any(int, float, None),
        vol.Optional("delta"): vol.Any(int, float, None),
        vol.Optional("reset", default=False): bool,
    })
    @websocket_api.async_response
    async def ws_update_thing_value(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle update or reset thing value command."""
        result = storage.data.update_thing_value(
            thing_id=msg["thing_id"],
            value=msg.get("value"),
            delta=msg.get("delta"),
            reset=msg.get("reset", False),
        )
        if not result:
            connection.send_error(msg["id"], "thing_not_found", "Thing not found")
            return
        await storage.async_save()
        connection.send_result(msg["id"], {"success": True, "thing": result, "data": storage.get_view_data()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/delete_thing",
        vol.Required("thing_id"): str,
    })
    @websocket_api.async_response
    async def ws_delete_thing(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle delete thing command."""
        thing_id = msg["thing_id"]
        success = storage.data.delete_thing(thing_id)
        if success:
            try:
                from homeassistant.helpers import entity_registry as er
                ent_reg = er.async_get(hass)
                reg_id = ent_reg.async_get_entity_id("sensor", DOMAIN, f"{DOMAIN}_thing_{thing_id}")
                if reg_id:
                    ent_reg.async_remove(reg_id)
            except Exception as err:
                _LOGGER.debug("Could not remove thing from entity registry: %s", err)
            await storage.async_save()
        connection.send_result(msg["id"], {"success": success, "data": storage.get_view_data()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/save_user",
        vol.Required("user"): dict,
    })
    @websocket_api.async_response
    async def ws_save_user(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle save or update user command."""
        user_data = msg["user"]
        user_id = user_data.get("id")

        if user_id and storage.data.get_user(user_id):
            result = storage.data.update_user(user_id, user_data)
        else:
            result = storage.data.create_user(user_data)

        await storage.async_save()
        connection.send_result(msg["id"], {"success": True, "user": result, "data": storage.get_view_data()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/delete_user",
        vol.Required("user_id"): str,
    })
    @websocket_api.async_response
    async def ws_delete_user(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle delete user command."""
        user_id = msg["user_id"]
        success = storage.data.delete_user(user_id)
        if success:
            try:
                from homeassistant.helpers import entity_registry as er
                ent_reg = er.async_get(hass)
                for domain, uid in [
                    ("sensor", f"{DOMAIN}_user_{user_id}_points"),
                    ("todo", f"{DOMAIN}_todo_{user_id}"),
                    ("calendar", f"{DOMAIN}_calendar_{user_id}"),
                ]:
                    reg_id = ent_reg.async_get_entity_id(domain, DOMAIN, uid)
                    if reg_id:
                        ent_reg.async_remove(reg_id)
            except Exception as err:
                _LOGGER.debug("Could not remove user entities from registry: %s", err)
            await storage.async_save()
        connection.send_result(msg["id"], {"success": success, "data": storage.get_view_data()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/save_label",
        vol.Required("label"): dict,
    })
    @websocket_api.async_response
    async def ws_save_label(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle save or update label command."""
        label_data = msg["label"]
        label_id = label_data.get("id")

        if label_id and storage.data.get_label(label_id):
            result = storage.data.update_label(label_id, label_data)
        else:
            result = storage.data.create_label(label_data)

        await storage.async_save()
        connection.send_result(msg["id"], {"success": True, "label": result, "data": storage.get_view_data()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/delete_label",
        vol.Required("label_id"): str,
    })
    @websocket_api.async_response
    async def ws_delete_label(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle delete label command."""
        success = storage.data.delete_label(msg["label_id"])
        if success:
            await storage.async_save()
        connection.send_result(msg["id"], {"success": success, "data": storage.get_view_data()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/update_settings",
        vol.Required("settings"): dict,
    })
    @websocket_api.async_response
    async def ws_update_settings(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle update settings command."""
        result = storage.data.update_settings(msg["settings"])
        await storage.async_save()
        connection.send_result(msg["id"], {"success": True, "settings": result, "data": storage.get_view_data()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/import_data",
        vol.Required("data"): dict,
        vol.Optional("merge", default=False): bool,
    })
    @websocket_api.async_response
    async def ws_import_data(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle import backup data command."""
        storage.data.import_data(msg["data"], merge=msg.get("merge", False))
        await storage.async_save()
        connection.send_result(msg["id"], {"success": True, "data": storage.get_view_data()})

    # Provider management commands
    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/get_ha_todo_entities",
    })
    @websocket_api.async_response
    async def ws_get_ha_todo_entities(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Return available external todo entities in Home Assistant."""
        entities = async_get_available_todo_entities(hass)
        connection.send_result(msg["id"], {"entities": entities})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/link_provider",
        vol.Required("entity_id"): str,
        vol.Optional("name", default=""): str,
        vol.Optional("provider_type", default="generic"): str,
        vol.Optional("icon", default="mdi:format-list-checks"): str,
    })
    @websocket_api.async_response
    async def ws_link_provider(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Link an external todo provider."""
        provider = storage.data.add_provider(
            entity_id=msg["entity_id"],
            name=msg.get("name", ""),
            provider_type=msg.get("provider_type", "generic"),
            icon=msg.get("icon", "mdi:format-list-checks"),
        )
        await storage.async_save()
        await storage.async_sync_providers()
        connection.send_result(msg["id"], {
            "success": True,
            "provider": provider,
            "providers": storage.data.providers,
            "data": storage.get_view_data(),
        })

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/unlink_provider",
        vol.Required("entity_id"): str,
    })
    @websocket_api.async_response
    async def ws_unlink_provider(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Unlink an external todo provider."""
        success = storage.data.remove_provider(msg["entity_id"])
        if success:
            await storage.async_save()
        connection.send_result(msg["id"], {
            "success": success,
            "providers": storage.data.providers,
            "data": storage.get_view_data(),
        })

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/sync_providers",
    })
    @websocket_api.async_response
    async def ws_sync_providers(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Trigger a sync of external todo providers."""
        await storage.async_sync_providers()
        connection.send_result(msg["id"], {
            "success": True,
            "data": storage.get_view_data(),
        })

    websocket_api.async_register_command(hass, ws_get_data)
    websocket_api.async_register_command(hass, ws_save_task)
    websocket_api.async_register_command(hass, ws_complete_task)
    websocket_api.async_register_command(hass, ws_reset_task)
    websocket_api.async_register_command(hass, ws_delete_task)
    websocket_api.async_register_command(hass, ws_update_subtask)
    websocket_api.async_register_command(hass, ws_save_thing)
    websocket_api.async_register_command(hass, ws_update_thing_value)
    websocket_api.async_register_command(hass, ws_delete_thing)
    websocket_api.async_register_command(hass, ws_save_user)
    websocket_api.async_register_command(hass, ws_delete_user)
    websocket_api.async_register_command(hass, ws_save_label)
    websocket_api.async_register_command(hass, ws_delete_label)
    websocket_api.async_register_command(hass, ws_update_settings)
    websocket_api.async_register_command(hass, ws_import_data)
    websocket_api.async_register_command(hass, ws_get_ha_todo_entities)
    websocket_api.async_register_command(hass, ws_link_provider)
    websocket_api.async_register_command(hass, ws_unlink_provider)
    websocket_api.async_register_command(hass, ws_sync_providers)
    _LOGGER.debug("Registered Task Manager WebSocket API commands")
