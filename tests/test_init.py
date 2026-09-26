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

core_mock.callback = dummy_callback
core_mock.HomeAssistant = MagicMock

sys.modules.setdefault("homeassistant", ha_mock)
sys.modules.setdefault("homeassistant.core", core_mock)
sys.modules.setdefault("homeassistant.config_entries", MagicMock())
sys.modules.setdefault("homeassistant.const", MagicMock())
sys.modules.setdefault("homeassistant.components", MagicMock())
panel_custom_mock = MagicMock()
panel_custom_mock.async_register_panel = AsyncMock()
sys.modules.setdefault("homeassistant.components.panel_custom", panel_custom_mock)
sys.modules.setdefault("homeassistant.components.http", MagicMock())
sys.modules.setdefault("homeassistant.helpers", MagicMock())
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


if __name__ == "__main__":
    unittest.main()
