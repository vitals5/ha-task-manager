"""Unit tests for Task Manager Binary Sensor platform."""
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

class MockBinarySensorEntity:
    """Mock Home Assistant BinarySensorEntity."""
    _attr_has_entity_name = True
    _attr_device_class = None
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

    def async_write_ha_state(self):
        pass

    def async_on_remove(self, cb):
        pass

class MockBinarySensorDeviceClass:
    PROBLEM = "problem"

binary_sensor_comp_mock = MagicMock()
binary_sensor_comp_mock.BinarySensorEntity = MockBinarySensorEntity
binary_sensor_comp_mock.BinarySensorDeviceClass = MockBinarySensorDeviceClass

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
components_mock.binary_sensor = binary_sensor_comp_mock
sys.modules["homeassistant.components"] = components_mock
sys.modules["homeassistant.components.websocket_api"] = ws_api_mock
sys.modules["homeassistant.components.binary_sensor"] = binary_sensor_comp_mock

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

dt_mock = MagicMock()
dt_mock.now.return_value = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)
dt_mock.DEFAULT_TIME_ZONE = timezone.utc

def mock_slugify(val):
    import re
    return re.sub(r"[^a-zA-Z0-9_]+", "_", str(val).lower()).strip("_")

util_mock = sys.modules.get("homeassistant.util") or MagicMock()
util_mock.dt = dt_mock
util_mock.slugify = mock_slugify
sys.modules["homeassistant.util"] = util_mock
sys.modules["homeassistant.util.dt"] = dt_mock

project_root = Path(__file__).resolve().parent.parent
pkg_path = project_root / "custom_components"
if str(pkg_path) not in sys.path:
    sys.path.insert(0, str(pkg_path))

from task_manager.binary_sensor import (
    TaskManagerOverdueBinarySensor,
    TaskManagerPartsLowStockBinarySensor,
    TaskManagerTaskProblemBinarySensor,
    async_setup_entry,
)
from task_manager.const import DOMAIN, TASK_STATE_DONE, TASK_STATE_DUE
from task_manager.storage import TaskManagerData, TaskManagerStorage


class TestTaskManagerBinarySensor(unittest.TestCase):
    """Test Task Manager binary sensor entities."""

    def setUp(self):
        """Set up test environment."""
        self.hass = MagicMock()
        self.hass.data = {}
        self.hass.services = MagicMock()
        self.hass.states = MagicMock()
        self.hass.states.get.return_value = None

        self.storage = TaskManagerStorage(self.hass)
        self.storage.data = TaskManagerData()
        # Initialize default minimal state
        self.storage.data.tasks = []
        self.storage.data.things = []
        self.storage.data.parts = []
        self.storage.data.users = [{"id": "u1", "name": "Alice"}]

    def test_overdue_binary_sensor(self):
        """Test overdue binary sensor on/off states and attributes."""
        sensor = TaskManagerOverdueBinarySensor(self.storage)
        sensor.hass = self.hass

        # Initially no tasks -> off
        self.assertFalse(sensor.is_on)
        self.assertEqual(sensor.extra_state_attributes["overdue_count"], 0)

        # Add a task due in the past (overdue relative to 2026-09-26)
        task = self.storage.data.create_task({
            "title": "Clean Filter",
            "due_date": "2026-09-20",
            "status": "pending",
        })
        self.assertTrue(sensor.is_on)
        self.assertEqual(sensor.extra_state_attributes["overdue_count"], 1)
        self.assertEqual(len(sensor.extra_state_attributes["overdue_tasks"]), 1)
        self.assertEqual(sensor.extra_state_attributes["overdue_tasks"][0]["title"], "Clean Filter")

        # Mark task completed -> off
        self.storage.data.complete_task(task["id"])
        self.assertFalse(sensor.is_on)
        self.assertEqual(sensor.extra_state_attributes["overdue_count"], 0)

    def test_parts_low_stock_binary_sensor(self):
        """Test parts low stock binary sensor on/off states and attributes."""
        sensor = TaskManagerPartsLowStockBinarySensor(self.storage)
        sensor.hass = self.hass

        # Initially no parts -> off
        self.assertFalse(sensor.is_on)
        self.assertEqual(sensor.extra_state_attributes["low_stock_count"], 0)

        # Add part with normal stock
        part = self.storage.data.create_part({
            "name": "Water Filter Cartridge",
            "stock": 5,
            "min_stock": 2,
        })
        self.assertFalse(sensor.is_on)

        # Adjust stock below min_stock -> on
        self.storage.data.adjust_part_stock(part["id"], -4)  # stock = 1 <= min_stock 2
        self.assertTrue(sensor.is_on)
        self.assertEqual(sensor.extra_state_attributes["low_stock_count"], 1)
        self.assertEqual(sensor.extra_state_attributes["low_stock_parts"][0]["name"], "Water Filter Cartridge")

        # Restock -> off
        self.storage.data.adjust_part_stock(part["id"], 5)  # stock = 6 > min_stock 2
        self.assertFalse(sensor.is_on)
        self.assertEqual(sensor.extra_state_attributes["low_stock_count"], 0)

    def test_task_problem_binary_sensor(self):
        """Test individual task problem binary sensor."""
        # Due task -> problem ON
        task = self.storage.data.create_task({
            "title": "Mow the Lawn",
            "due_date": "2026-09-26",
            "status": "pending",
        })
        sensor = TaskManagerTaskProblemBinarySensor(self.storage, task["id"])
        sensor.hass = self.hass

        self.assertEqual(sensor.entity_id, "binary_sensor.task_manager_mow_the_lawn_problem")
        self.assertTrue(sensor.is_on)

        # Complete task -> problem OFF
        self.storage.data.complete_task(task["id"])
        self.assertFalse(sensor.is_on)

    def test_async_setup_entry_creates_sensors(self):
        """Test async_setup_entry creates static and task problem binary sensors."""
        self.storage.data.create_task({"title": "Task 1", "due_date": "2026-09-26"})
        self.storage.data.create_task({"title": "Task 2", "due_date": "2026-09-28"})

        entry = MagicMock()
        entry.entry_id = "test_entry"
        self.hass.data[DOMAIN] = {entry.entry_id: self.storage}

        added_entities = []
        def mock_add_entities(entities):
            added_entities.extend(entities)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(async_setup_entry(self.hass, entry, mock_add_entities))
        finally:
            loop.close()

        # 2 static (overdue + parts low stock) + 2 tasks = 4 binary sensors
        self.assertEqual(len(added_entities), 4)
        types = [type(e).__name__ for e in added_entities]
        self.assertIn("TaskManagerOverdueBinarySensor", types)
        self.assertIn("TaskManagerPartsLowStockBinarySensor", types)
        self.assertEqual(types.count("TaskManagerTaskProblemBinarySensor"), 2)


if __name__ == "__main__":
    unittest.main()
