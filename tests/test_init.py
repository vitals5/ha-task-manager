"""Unit tests for Task Manager __init__.py and lifecycle."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Mock homeassistant module hierarchy
ha_mock = MagicMock()
core_mock = MagicMock()

def dummy_callback(func):
    return func

ha_mock.callback = dummy_callback
core_mock.callback = dummy_callback
core_mock.HomeAssistant = MagicMock
ha_mock.core = core_mock

if "homeassistant.core" in sys.modules:
    sys.modules["homeassistant.core"].callback = dummy_callback

ha_const_mock = MagicMock()
ha_const_mock.EVENT_STATE_CHANGED = "state_changed"
ha_mock.const = ha_const_mock

sys.modules.setdefault("homeassistant", ha_mock)
sys.modules.setdefault("homeassistant.core", core_mock)
sys.modules.setdefault("homeassistant.const", ha_const_mock)
sys.modules["homeassistant.const"] = ha_const_mock
sys.modules.setdefault("homeassistant.config_entries", MagicMock())
sys.modules.setdefault("homeassistant.components", MagicMock())
sys.modules.setdefault("homeassistant.helpers.dispatcher", MagicMock())
panel_custom_mock = MagicMock()
panel_custom_mock.async_register_panel = AsyncMock()
sys.modules.setdefault("homeassistant.components.panel_custom", panel_custom_mock)
sys.modules.setdefault("homeassistant.components.http", MagicMock())
ws_api_mock = MagicMock()
ws_registered_handlers = {}
def mock_ws_register_cmd(hass, handler):
    name = getattr(handler, "__name__", "")
    ws_registered_handlers[name] = handler
ws_api_mock.async_register_command = mock_ws_register_cmd
ws_api_mock.websocket_command = lambda schema: (lambda f: f)
ws_api_mock.async_response = lambda f: f
sys.modules["homeassistant.components.websocket_api"] = ws_api_mock
sys.modules["homeassistant.components"].websocket_api = ws_api_mock
helpers_mock = MagicMock()
helpers_mock.__path__ = []
sys.modules.setdefault("homeassistant.helpers", helpers_mock)
sys.modules["homeassistant.helpers"].__path__ = []
sys.modules.setdefault("homeassistant.helpers.dispatcher", MagicMock())
sys.modules.setdefault("homeassistant.helpers.event", MagicMock())
sys.modules.setdefault("homeassistant.helpers.storage", MagicMock())

def mock_slugify(val):
    import re
    return re.sub(r"[^a-zA-Z0-9_]+", "_", str(val).lower()).strip("_")

util_mock = MagicMock()
util_mock.slugify = mock_slugify
dt_mock = MagicMock()
dt_mock.now.return_value = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)
dt_mock.DEFAULT_TIME_ZONE = timezone.utc
util_mock.dt = dt_mock

sys.modules["homeassistant.util"] = util_mock
sys.modules["homeassistant.util.dt"] = dt_mock
sys.modules.setdefault("voluptuous", MagicMock())

# Import task_manager package
PKG_DIR = Path(__file__).resolve().parent.parent / "custom_components" / "task_manager"
if str(PKG_DIR.parent) not in sys.path:
    sys.path.insert(0, str(PKG_DIR.parent))

import task_manager


class TestTaskManagerInit(unittest.IsolatedAsyncioTestCase):
    """Test setup and unload of task_manager component."""

    async def test_async_setup_and_unload_entry(self):
        """Test async_setup_entry runs without NameError and registers everything."""
        hass = MagicMock()
        hass.data = {}
        hass.config_entries = MagicMock()
        hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
        hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
        hass.bus = MagicMock()
        hass.bus.async_listen = MagicMock(return_value=MagicMock())
        hass.http = MagicMock()
        hass.http.async_register_static_paths = AsyncMock(return_value=None)

        entry = MagicMock()
        entry.entry_id = "test_entry_123"
        entry.async_on_unload = MagicMock()

        hass.async_create_task = asyncio.create_task
        lovelace_mock = MagicMock()
        resources_mock = MagicMock()
        resources_mock.loaded = True
        resources_mock.async_items = MagicMock(return_value=[])
        resources_mock.async_create_item = AsyncMock()
        lovelace_mock.resources = resources_mock
        hass.data["lovelace"] = lovelace_mock

        with patch.object(task_manager.TaskManagerStorage, "async_load", AsyncMock()):
            with patch.object(task_manager.TaskManagerStorage, "async_sync_providers", AsyncMock()):
                with patch("task_manager.panel_custom.async_register_panel", AsyncMock()):
                    result = await task_manager.async_setup_entry(hass, entry)
                    self.assertTrue(result)
                    self.assertIn("task_manager", hass.data)
                    self.assertIn("test_entry_123", hass.data["task_manager"])
                    self.assertTrue(hass.data.get("task_manager_card_registered"))
                    # Allow async_create_task to complete
                    await asyncio.sleep(0.01)
                    resources_mock.async_create_item.assert_called_once()

                # Test unload
                unload_result = await task_manager.async_unload_entry(hass, entry)
                self.assertTrue(unload_result)
                self.assertNotIn("test_entry_123", hass.data["task_manager"])
                self.assertNotIn("task_manager_card_registered", hass.data)

    async def test_external_entity_state_change_updates_thing(self):
        """Test state changes on external numeric entities automatically update linked things."""
        hass = MagicMock()
        hass.data = {}
        hass.config_entries = MagicMock()
        hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
        hass.states = MagicMock()
        hass.states.get.return_value = None
        listeners = {}
        def mock_listen(event_type, callback):
            listeners[event_type] = callback
            return MagicMock()
        hass.bus = MagicMock()
        hass.bus.async_listen = mock_listen
        hass.http = MagicMock()
        hass.http.async_register_static_paths = AsyncMock(return_value=None)
        hass.async_create_task = MagicMock()

        entry = MagicMock()
        entry.entry_id = "test_entry_456"
        entry.async_on_unload = MagicMock()

        with patch.object(task_manager.TaskManagerStorage, "async_load", AsyncMock()):
            with patch.object(task_manager.TaskManagerStorage, "async_sync_providers", AsyncMock()):
                with patch("task_manager.panel_custom.async_register_panel", AsyncMock()):
                    await task_manager.async_setup_entry(hass, entry)

        storage = hass.data["task_manager"]["test_entry_456"]
        thing = storage.data.create_thing({
            "name": "Brush",
            "external_entity_id": "sensor.vacuum_brush_life",
            "threshold_operator": "<=",
            "target_value": 0,
            "current_value": 80,
        })

        # Simulate state change event
        event = MagicMock()
        event.data = {
            "entity_id": "sensor.vacuum_brush_life",
            "new_state": MagicMock(state="0.0"),
        }
        from homeassistant.const import EVENT_STATE_CHANGED
        cb = listeners.get(EVENT_STATE_CHANGED)
        self.assertIsNotNone(cb)
        cb(event)

        updated_thing = storage.data.get_thing(thing["id"])
        self.assertEqual(updated_thing["current_value"], 0.0)
        hass.async_create_task.assert_called()
        for call in hass.async_create_task.call_args_list:
            call[0][0].close()

    async def test_ws_get_ha_numeric_entities_and_scripts(self):
        """Test ws_get_ha_numeric_entities and ws_get_ha_scripts return valid entities."""
        hass = MagicMock()
        mock_states = [
            MagicMock(entity_id="sensor.vacuum_brush", state="42.5", attributes={"unit_of_measurement": "%", "friendly_name": "Main Brush"}),
            MagicMock(entity_id="number.fan_speed", state="unavailable", attributes={"friendly_name": "Fan Speed"}),
            MagicMock(entity_id="counter.water_filter_cycles", state="12", attributes={"friendly_name": "Cycles"}),
            MagicMock(entity_id="script.clean_now", state="off", attributes={"friendly_name": "Clean Now"}),
            MagicMock(entity_id="switch.kitchen_light", state="on", attributes={"friendly_name": "Kitchen Light"}),
            MagicMock(entity_id="sensor.task_manager_user_1_points", state="100", attributes={}),
        ]
        hass.states.async_all.return_value = mock_states

        connection = MagicMock()
        connection.send_result = MagicMock()

        from task_manager import websocket as tm_ws
        tm_ws.websocket_api.async_register_command = mock_ws_register_cmd
        tm_ws.async_register_websocket_api(hass, MagicMock())

        handler_num = ws_registered_handlers.get("ws_get_ha_numeric_entities")
        self.assertIsNotNone(handler_num)
        await handler_num(hass, connection, {"id": 1, "type": "task_manager/get_ha_numeric_entities"})

        connection.send_result.assert_called_once()
        res_num = connection.send_result.call_args[0][1]
        num_eids = [e["entity_id"] for e in res_num["entities"]]
        self.assertIn("sensor.vacuum_brush", num_eids)
        self.assertIn("number.fan_speed", num_eids)
        self.assertIn("counter.water_filter_cycles", num_eids)
        self.assertNotIn("switch.kitchen_light", num_eids)
        self.assertNotIn("sensor.task_manager_user_1_points", num_eids)

        connection.send_result.reset_mock()
        handler_script = ws_registered_handlers.get("ws_get_ha_scripts")
        self.assertIsNotNone(handler_script)
        await handler_script(hass, connection, {"id": 2, "type": "task_manager/get_ha_scripts"})

        connection.send_result.assert_called_once()
        res_scripts = connection.send_result.call_args[0][1]
        script_eids = [s["entity_id"] for s in res_scripts["scripts"]]
        self.assertIn("script.clean_now", script_eids)

    async def test_ws_pause_and_resume_task_registration(self):
        """Test ws_pause_task, ws_resume_task, and ws_set_last_done_date are registered and callable."""
        hass = MagicMock()
        storage = MagicMock()
        storage.async_pause_task = AsyncMock(return_value={"id": "t1", "is_active": False})
        storage.async_resume_task = AsyncMock(return_value={"id": "t1", "is_active": True})
        storage.get_view_data = MagicMock(return_value={"tasks": []})

        connection = MagicMock()
        connection.send_result = MagicMock()

        from task_manager import websocket as tm_ws
        tm_ws.websocket_api.async_register_command = mock_ws_register_cmd
        tm_ws.async_register_websocket_api(hass, storage)

        # Check pause
        pause_handler = ws_registered_handlers.get("ws_pause_task")
        self.assertIsNotNone(pause_handler)
        await pause_handler(hass, connection, {"id": 10, "type": "task_manager/pause_task", "task_id": "t1"})
        storage.async_pause_task.assert_awaited_once_with("t1")
        connection.send_result.assert_called_once()

        # Check resume
        connection.send_result.reset_mock()
        resume_handler = ws_registered_handlers.get("ws_resume_task")
        self.assertIsNotNone(resume_handler)
        await resume_handler(hass, connection, {"id": 11, "type": "task_manager/resume_task", "task_id": "t1"})
        storage.async_resume_task.assert_awaited_once_with("t1")
        connection.send_result.assert_called_once()

        # Check all 31 functions registered
        self.assertIn("ws_pause_task", ws_registered_handlers)
        self.assertIn("ws_resume_task", ws_registered_handlers)
        self.assertIn("ws_set_last_done_date", ws_registered_handlers)
        self.assertIn("ws_delete_history_entry", ws_registered_handlers)
        self.assertEqual(len(ws_registered_handlers), 32)

    async def test_ws_delete_history_entry_registration_and_execution(self):
        """Test ws_delete_history_entry is registered and calls storage.async_delete_task_history_entry."""
        hass = MagicMock()
        storage = MagicMock()
        storage.async_delete_task_history_entry = AsyncMock(return_value=True)
        storage.get_view_data = MagicMock(return_value={"tasks": []})

        connection = MagicMock()
        connection.send_result = MagicMock()

        from task_manager import websocket as tm_ws
        tm_ws.websocket_api.async_register_command = mock_ws_register_cmd
        tm_ws.async_register_websocket_api(hass, storage)

        delete_handler = ws_registered_handlers.get("ws_delete_history_entry")
        self.assertIsNotNone(delete_handler)
        await delete_handler(
            hass,
            connection,
            {
                "id": 99,
                "type": "task_manager/delete_history_entry",
                "task_id": "reading_task_1",
                "entry_index": 2,
                "completed_at": "2026-09-29T10:00:00",
            },
        )
        storage.async_delete_task_history_entry.assert_awaited_once_with(
            "reading_task_1", entry_index=2, completed_at="2026-09-29T10:00:00"
        )
        connection.send_result.assert_called_once_with(
            99, {"success": True, "data": {"tasks": []}}
        )

    async def test_ws_save_part_compatibility(self):
        """Test ws_save_part accepts both 'part' and 'part_data' payloads."""
        hass = MagicMock()
        storage = MagicMock()
        storage.data.get_part.return_value = None
        storage.async_create_part = AsyncMock(return_value={"id": "p1", "name": "Filter"})
        storage.async_update_part = AsyncMock(return_value={"id": "p1", "name": "Filter Updated"})
        storage.get_view_data = MagicMock(return_value={"parts": []})

        connection = MagicMock()
        connection.send_result = MagicMock()

        from task_manager import websocket as tm_ws
        tm_ws.websocket_api.async_register_command = mock_ws_register_cmd
        tm_ws.async_register_websocket_api(hass, storage)

        handler = ws_registered_handlers.get("ws_save_part")
        self.assertIsNotNone(handler)

        # 1. Test with 'part_data' (legacy / previous frontend call)
        await handler(hass, connection, {"id": 1, "type": "task_manager/save_part", "part_data": {"name": "Filter"}})
        storage.async_create_part.assert_awaited_once_with({"name": "Filter"})
        connection.send_result.assert_called_once_with(1, {"success": True, "part": {"id": "p1", "name": "Filter"}, "data": {"parts": []}})

        # 2. Test with 'part' (standard schema)
        storage.async_create_part.reset_mock()
        connection.send_result.reset_mock()
        await handler(hass, connection, {"id": 2, "type": "task_manager/save_part", "part": {"name": "Filter"}})
        storage.async_create_part.assert_awaited_once_with({"name": "Filter"})
        connection.send_result.assert_called_once_with(2, {"success": True, "part": {"id": "p1", "name": "Filter"}, "data": {"parts": []}})

        # 3. Test with both 'part' and 'part_data'
        storage.async_create_part.reset_mock()
        connection.send_result.reset_mock()
        await handler(hass, connection, {"id": 3, "type": "task_manager/save_part", "part": {"name": "Filter"}, "part_data": {"name": "Filter"}})
        storage.async_create_part.assert_awaited_once_with({"name": "Filter"})
        connection.send_result.assert_called_once_with(3, {"success": True, "part": {"id": "p1", "name": "Filter"}, "data": {"parts": []}})

        # 4. Test update existing part
        storage.data.get_part.return_value = {"id": "p1", "name": "Filter"}
        connection.send_result.reset_mock()
        await handler(hass, connection, {"id": 4, "type": "task_manager/save_part", "part": {"id": "p1", "name": "Filter Updated"}})
        storage.async_update_part.assert_awaited_once_with("p1", {"id": "p1", "name": "Filter Updated"})
        connection.send_result.assert_called_once_with(4, {"success": True, "part": {"id": "p1", "name": "Filter Updated"}, "data": {"parts": []}})

    async def test_lovelace_resource_registration_and_update(self):
        """Test Lovelace resource registration updates existing resource if url changed."""
        hass = MagicMock()
        hass.data = {}
        hass.config_entries = MagicMock()
        hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
        hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
        hass.bus = MagicMock()
        hass.http = MagicMock()
        hass.http.async_register_static_paths = AsyncMock(return_value=None)
        hass.async_create_task = asyncio.create_task

        lovelace_mock = MagicMock()
        resources_mock = MagicMock()
        resources_mock.loaded = True
        resources_mock.async_items = MagicMock(return_value=[
            {"id": "res_1", "res_type": "module", "url": "/task_manager_ui/task-manager-card.js?v=old"}
        ])
        resources_mock.async_update_item = AsyncMock()
        resources_mock.async_create_item = AsyncMock()
        lovelace_mock.resources = resources_mock
        hass.data["lovelace"] = lovelace_mock

        entry = MagicMock()
        entry.entry_id = "test_entry_789"
        entry.async_on_unload = MagicMock()

        with patch.object(task_manager.TaskManagerStorage, "async_load", AsyncMock()):
            with patch.object(task_manager.TaskManagerStorage, "async_sync_providers", AsyncMock()):
                with patch("task_manager.panel_custom.async_register_panel", AsyncMock()):
                    await task_manager.async_setup_entry(hass, entry)
                    await asyncio.sleep(0.01)
                    resources_mock.async_update_item.assert_called_once()
                    self.assertIn("/task_manager_ui/task-manager-card.js", resources_mock.async_update_item.call_args[0][1]["url"])

    def test_manifest_hassfest_compliance(self):
        """Test manifest.json conforms to Hassfest ordering rules (domain, name, then alphabetical)."""
        manifest_path = os.path.join(os.path.dirname(__file__), "..", "custom_components", "task_manager", "manifest.json")
        with open(manifest_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        keys = list(raw.keys())
        expected = ["domain", "name"] + sorted(k for k in raw if k not in ("domain", "name"))
        self.assertEqual(keys, expected, "Manifest keys must be: domain, name, then alphabetical order (Hassfest requirement)")


if __name__ == "__main__":
    unittest.main()

