"""WebSocket API handlers for Task Manager."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
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
        connection.send_result(msg["id"], storage.data.to_dict())

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
        task_id = task_data.get("id")

        if task_id and storage.data.get_task(task_id):
            result = storage.data.update_task(task_id, task_data)
        else:
            result = storage.data.create_task(task_data)

        await storage.async_save()
        connection.send_result(msg["id"], {"success": True, "task": result, "data": storage.data.to_dict()})

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
        result = storage.data.complete_task(msg["task_id"], user_id=msg.get("user_id"))
        if not result:
            connection.send_error(msg["id"], "task_not_found", "Task not found")
            return
        await storage.async_save()
        connection.send_result(msg["id"], {"success": True, "task": result, "data": storage.data.to_dict()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/reset_task",
        vol.Required("task_id"): str,
    })
    @websocket_api.async_response
    async def ws_reset_task(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle reset task command."""
        result = storage.data.reset_task(msg["task_id"])
        if not result:
            connection.send_error(msg["id"], "task_not_found", "Task not found")
            return
        await storage.async_save()
        connection.send_result(msg["id"], {"success": True, "task": result, "data": storage.data.to_dict()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/delete_task",
        vol.Required("task_id"): str,
    })
    @websocket_api.async_response
    async def ws_delete_task(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle delete task command."""
        success = storage.data.delete_task(msg["task_id"])
        if success:
            await storage.async_save()
        connection.send_result(msg["id"], {"success": success, "data": storage.data.to_dict()})

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
        success = storage.data.update_subtask(msg["task_id"], msg["subtask_id"], msg["completed"])
        if success:
            await storage.async_save()
        connection.send_result(msg["id"], {"success": success, "data": storage.data.to_dict()})

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
        connection.send_result(msg["id"], {"success": True, "thing": result, "data": storage.data.to_dict()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/update_thing_value",
        vol.Required("thing_id"): str,
        vol.Optional("value"): vol.Any(int, float),
        vol.Optional("delta"): vol.Any(int, float),
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
        connection.send_result(msg["id"], {"success": True, "thing": result, "data": storage.data.to_dict()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/delete_thing",
        vol.Required("thing_id"): str,
    })
    @websocket_api.async_response
    async def ws_delete_thing(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle delete thing command."""
        success = storage.data.delete_thing(msg["thing_id"])
        if success:
            await storage.async_save()
        connection.send_result(msg["id"], {"success": success, "data": storage.data.to_dict()})

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
        connection.send_result(msg["id"], {"success": True, "user": result, "data": storage.data.to_dict()})

    @websocket_api.websocket_command({
        vol.Required("type"): "task_manager/delete_user",
        vol.Required("user_id"): str,
    })
    @websocket_api.async_response
    async def ws_delete_user(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Handle delete user command."""
        success = storage.data.delete_user(msg["user_id"])
        if success:
            await storage.async_save()
        connection.send_result(msg["id"], {"success": success, "data": storage.data.to_dict()})

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
        connection.send_result(msg["id"], {"success": True, "label": result, "data": storage.data.to_dict()})

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
        connection.send_result(msg["id"], {"success": success, "data": storage.data.to_dict()})

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
        connection.send_result(msg["id"], {"success": True, "settings": result, "data": storage.data.to_dict()})

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
        connection.send_result(msg["id"], {"success": True, "data": storage.data.to_dict()})

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
    _LOGGER.debug("Registered Task Manager WebSocket API commands")
