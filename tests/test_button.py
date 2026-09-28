"""Unit tests for Task Manager Button platform."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Mock homeassistant module hierarchy
ha_mock = MagicMock()
ha_mock.__path__ = []
core_mock = MagicMock()

def dummy_callback(func):
    return func

ha_mock.callback = dummy_callback
core_mock.callback = dummy_callback

ha_const_mock = MagicMock()
ha_const_mock.EVENT_HOMEASSISTANT_STARTED = "homeassistant_started"
ha_const_mock.EVENT_STATE_CHANGED = "state_changed"

class MockButtonEntity:
    """Mock Home Assistant ButtonEntity."""
    _attr_has_entity_name = True
    _attr_icon = ""

    def __init__(self):
        self.hass = MagicMock()

    @property
    def name(self):
        return getattr(self, "_attr_name", None)

    @property
    def unique_id(self):
        return getattr(self, "_attr_unique_id", None)

    async def async_remove(self):
        pass

button_comp_mock = MagicMock()
button_comp_mock.ButtonEntity = MockButtonEntity

sys.modules.setdefault("homeassistant", ha_mock)
sys.modules["homeassistant"].__path__ = []
sys.modules.setdefault("homeassistant.core", core_mock)
sys.modules.setdefault("homeassistant.const", ha_const_mock)
sys.modules["homeassistant.const"] = ha_const_mock
components_mock = sys.modules.get("homeassistant.components") or MagicMock()
ws_api_mock = sys.modules.get("homeassistant.components.websocket_api") or MagicMock()
ws_api_mock.websocket_command = lambda schema: (lambda f: f)
ws_api_mock.async_response = lambda f: f
components_mock.websocket_api = ws_api_mock
components_mock.button = button_comp_mock
sys.modules["homeassistant.components"] = components_mock
sys.modules["homeassistant.components.websocket_api"] = ws_api_mock
sys.modules["homeassistant.components.button"] = button_comp_mock
sys.modules.setdefault("homeassistant.config_entries", MagicMock())
helpers_mock = MagicMock()
helpers_mock.__path__ = []
sys.modules.setdefault("homeassistant.helpers", helpers_mock)
sys.modules["homeassistant.helpers"].__path__ = []
sys.modules.setdefault("homeassistant.helpers.entity_registry", MagicMock())
sys.modules.setdefault("homeassistant.helpers.dispatcher", MagicMock())
sys.modules.setdefault("homeassistant.helpers.entity_platform", MagicMock())
sys.modules.setdefault("homeassistant.helpers.storage", MagicMock())
sys.modules.setdefault("homeassistant.helpers.event", MagicMock())
sys.modules.setdefault("voluptuous", MagicMock())

def mock_slugify(val):
    import re
    return re.sub(r"[^a-zA-Z0-9_]+", "_", str(val).lower()).strip("_")

util_mock = sys.modules.get("homeassistant.util") or MagicMock()
util_mock.slugify = mock_slugify
dt_mock = MagicMock()
dt_mock.now.return_value = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)
dt_mock.DEFAULT_TIME_ZONE = timezone.utc
util_mock.dt = dt_mock

sys.modules["homeassistant.util"] = util_mock
sys.modules["homeassistant.util.dt"] = dt_mock

project_root = Path(__file__).resolve().parent.parent
pkg_path = project_root / "custom_components"
if str(pkg_path) not in sys.path:
    sys.path.insert(0, str(pkg_path))

from task_manager.button import TaskManagerTaskButton, async_setup_entry
from task_manager.const import DOMAIN
from task_manager.storage import TaskManagerStorage, TaskManagerData


class TestTaskManagerButton(unittest.IsolatedAsyncioTestCase):
    """Test suite for Task Manager Button platform."""

    async def asyncSetUp(self):
        """Set up test environment."""
        self.hass = MagicMock()
        self.entry = MagicMock()
        self.entry.entry_id = "test_entry_btn"

        self.storage = MagicMock(spec=TaskManagerStorage)
        self.storage.data = TaskManagerData()
        self.storage.async_complete_task = AsyncMock()

        self.hass.data = {DOMAIN: {self.entry.entry_id: self.storage}}

    async def test_button_properties(self):
        """Test button initialization and properties."""
        task = self.storage.data.create_task({
            "title": "Clean Dishwasher Filter",
            "due_date": "2026-10-01",
        })

        button = TaskManagerTaskButton(self.storage, task["id"])
        self.assertEqual(button.name, "Clean Dishwasher Filter Complete")
        self.assertEqual(button.unique_id, f"{DOMAIN}_task_{task['id']}_complete")
        self.assertEqual(button.entity_id, "button.task_manager_clean_dishwasher_filter_mark_as_done")
        self.assertTrue(button.available)

        # Press action
        await button.async_press()
        self.storage.async_complete_task.assert_awaited_once_with(task["id"])

    async def test_button_available_when_deleted(self):
        """Test button available returns False if task is deleted."""
        button = TaskManagerTaskButton(self.storage, "nonexistent_task_id")
        self.assertFalse(button.available)

    async def test_async_setup_entry_registers_buttons(self):
        """Test setup entry registers buttons for existing tasks."""
        t1 = self.storage.data.create_task({"title": "Task 1"})
        t2 = self.storage.data.create_task({"title": "Task 2"})

        added_entities = []
        def mock_add_entities(entities):
            added_entities.extend(entities)

        await async_setup_entry(self.hass, self.entry, mock_add_entities)

        self.assertEqual(len(added_entities), 2)
        button_task_ids = {b._task_id for b in added_entities}
        self.assertEqual(button_task_ids, {t1["id"], t2["id"]})
