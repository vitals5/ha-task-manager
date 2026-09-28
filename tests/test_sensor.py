"""Unit tests for Task Manager Sensor platform."""
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

class MockSensorEntity:
    """Mock Home Assistant SensorEntity."""
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

    @property
    def native_unit_of_measurement(self):
        return getattr(self, "_attr_native_unit_of_measurement", None)

    async def async_remove(self):
        pass

    def async_write_ha_state(self):
        pass

class MockSensorStateClass:
    TOTAL = "total"
    MEASUREMENT = "measurement"

sensor_comp_mock = MagicMock()
sensor_comp_mock.SensorEntity = MockSensorEntity
sensor_comp_mock.SensorStateClass = MockSensorStateClass

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
components_mock.sensor = sensor_comp_mock
sys.modules["homeassistant.components"] = components_mock
sys.modules["homeassistant.components.websocket_api"] = ws_api_mock
sys.modules["homeassistant.components.sensor"] = sensor_comp_mock
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

util_mock = sys.modules.get("homeassistant.util") or MagicMock()
def mock_slugify(val):
    import re
    return re.sub(r"[^a-zA-Z0-9_]+", "_", str(val).lower()).strip("_")
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

from task_manager.sensor import (
    TaskManagerSummarySensor,
    TaskManagerUserSensor,
    TaskManagerThingSensor,
    TaskManagerTaskSensor,
    async_setup_entry,
)
from task_manager.const import (
    DOMAIN,
    TASK_STATE_DONE,
    TASK_STATE_DUE,
    TASK_STATE_DUE_SOON,
    TASK_STATE_INACTIVE,
)
from task_manager.storage import TaskManagerStorage, TaskManagerData


class TestTaskManagerSensors(unittest.IsolatedAsyncioTestCase):
    """Test suite for Task Manager Sensor platform."""

    async def asyncSetUp(self):
        """Set up test environment."""
        self.hass = MagicMock()
        self.entry = MagicMock()
        self.entry.entry_id = "test_entry_sensor"

        self.storage = MagicMock(spec=TaskManagerStorage)
        self.storage.data = TaskManagerData()
        self.storage.data.tasks.clear()
        self.storage.data.users.clear()
        self.storage.data.things.clear()
        self.hass.data = {DOMAIN: {self.entry.entry_id: self.storage}}

    async def test_summary_sensors(self):
        """Test summary sensors counts."""
        self.storage.data.create_task({"title": "T1", "status": "pending", "due_date": "2026-09-20"})
        self.storage.data.create_task({"title": "T2", "status": "pending", "due_date": "2026-09-30"})
        t3 = self.storage.data.create_task({"title": "T3", "due_date": "2026-09-26"})
        self.storage.data.update_task(t3["id"], {"status": "completed", "completed_at": "2026-09-26T10:00:00Z"})

        total_sensor = TaskManagerSummarySensor(self.storage, "total", "Total Tasks", "mdi:clipboard")
        pending_sensor = TaskManagerSummarySensor(self.storage, "pending", "Pending Tasks", "mdi:clipboard")
        overdue_sensor = TaskManagerSummarySensor(self.storage, "overdue", "Overdue Tasks", "mdi:clipboard")
        done_sensor = TaskManagerSummarySensor(self.storage, "completed_today", "Completed Today", "mdi:clipboard")

        total_sensor.hass = self.hass
        pending_sensor.hass = self.hass
        overdue_sensor.hass = self.hass
        done_sensor.hass = self.hass

        self.assertEqual(total_sensor.native_value, 3)
        self.assertEqual(pending_sensor.native_value, 2)
        self.assertEqual(overdue_sensor.native_value, 1)  # T1 is overdue (2026-09-20 < 2026-09-26)
        self.assertEqual(done_sensor.native_value, 1)     # T3 completed today

    async def test_user_sensor(self):
        """Test user points sensor."""
        user = self.storage.data.create_user({"name": "Alice", "points": 150})
        user_sensor = TaskManagerUserSensor(self.storage, user["id"])
        user_sensor.hass = self.hass

        self.assertEqual(user_sensor.native_value, 150)
        self.assertEqual(user_sensor.native_unit_of_measurement, "pts")
        self.assertEqual(user_sensor.unique_id, f"{DOMAIN}_user_{user['id']}_points")

    async def test_thing_sensor(self):
        """Test thing sensor value and extra attributes."""
        thing = self.storage.data.create_thing({
            "name": "Water Filter",
            "current_value": 85,
            "target_value": 100,
            "unit": "L",
            "threshold_operator": ">=",
        })
        thing_sensor = TaskManagerThingSensor(self.storage, thing["id"])
        thing_sensor.hass = self.hass

        self.assertEqual(thing_sensor.native_value, 85)
        self.assertEqual(thing_sensor.native_unit_of_measurement, "L")
        attrs = thing_sensor.extra_state_attributes
        self.assertEqual(attrs["progress_percent"], 85.0)
        self.assertFalse(attrs["threshold_reached"])

    async def test_task_sensor_states_and_attributes(self):
        """Test task sensor states: due, due_soon, done, inactive, and attributes."""
        from datetime import date, timedelta
        now = dt_mock.now()
        today = now.date() if hasattr(now, "date") else date.today()
        today_str = today.strftime("%Y-%m-%d")
        tomorrow_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")

        # 1. Active task due today -> due
        task = self.storage.data.create_task({
            "title": "Clean Oven",
            "due_date": today_str,
            "tags": ["kitchen", "deep_clean"],
            "due_soon_days": 2,
            "notification_interval": 3,
        })
        sensor = TaskManagerTaskSensor(self.storage, task["id"])
        sensor.hass = self.hass

        self.assertEqual(sensor.entity_id, "sensor.task_manager_clean_oven")
        self.assertEqual(sensor.native_value, TASK_STATE_DUE)
        self.assertEqual(sensor.icon, "mdi:alert-circle-outline")

        attrs = sensor.extra_state_attributes
        self.assertEqual(attrs["task_id"], task["id"])
        self.assertEqual(attrs["due_in"], 0)
        self.assertEqual(attrs["due_soon_days"], 2)
        self.assertEqual(attrs["notification_interval"], 3)
        self.assertEqual(attrs["tags"], ["kitchen", "deep_clean"])
        self.assertTrue(attrs["is_active"])

        # 2. Inactive task -> inactive
        self.storage.data.pause_task(task["id"])
        self.assertEqual(sensor.native_value, TASK_STATE_INACTIVE)
        self.assertEqual(sensor.icon, "mdi:pause-circle-outline")

        # 3. Resume task, set due_date in future within due_soon_days -> due_soon
        self.storage.data.resume_task(task["id"])
        self.storage.data.update_task(task["id"], {"due_date": tomorrow_str})
        self.assertEqual(sensor.native_value, TASK_STATE_DUE_SOON)
        self.assertEqual(sensor.icon, "mdi:clock-alert-outline")

        # 4. Completed task -> done
        self.storage.data.update_task(task["id"], {"status": "completed"})
        self.assertEqual(sensor.native_value, TASK_STATE_DONE)
        self.assertEqual(sensor.icon, "mdi:checkbox-marked-circle")

    async def test_async_setup_entry_registers_dynamic_sensors(self):
        """Test setup entry registers summary, user, thing, and task sensors."""
        u1 = self.storage.data.create_user({"name": "Bob"})
        th1 = self.storage.data.create_thing({"name": "Furnace Filter"})
        t1 = self.storage.data.create_task({"title": "Change Filter"})

        added_entities = []
        def mock_add_entities(entities):
            added_entities.extend(entities)

        await async_setup_entry(self.hass, self.entry, mock_add_entities)

        # 5 summary sensors (including parts low stock) + 1 user + 1 thing + 1 task = 8
        self.assertEqual(len(added_entities), 8)
