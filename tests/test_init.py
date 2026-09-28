"""Unit tests for Task Manager __init__.py and lifecycle."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import importlib.util
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
sys.modules.setdefault("homeassistant.util", MagicMock())
sys.modules.setdefault("homeassistant.util.dt", MagicMock())
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

        with patch.object(task_manager.TaskManagerStorage, "async_load", AsyncMock()):
            with patch.object(task_manager.TaskManagerStorage, "async_sync_providers", AsyncMock()):
                with patch("task_manager.panel_custom.async_register_panel", AsyncMock()):
                    result = await task_manager.async_setup_entry(hass, entry)
                    self.assertTrue(result)
                    self.assertIn("task_manager", hass.data)
                    self.assertIn("test_entry_123", hass.data["task_manager"])

                # Test unload
                unload_result = await task_manager.async_unload_entry(hass, entry)
                self.assertTrue(unload_result)
                self.assertNotIn("test_entry_123", hass.data["task_manager"])

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

        from task_manager.websocket import async_register_websocket_api
        async_register_websocket_api(hass, MagicMock())

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
        self.assertNotIn("switch.kitchen_light", script_eids)


if __name__ == "__main__":
    unittest.main()

