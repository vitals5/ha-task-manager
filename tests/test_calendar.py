"""Unit tests for Task Manager Calendar platform."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock

# Mock homeassistant module hierarchy
ha_mock = MagicMock()
dt_mock = MagicMock()
dt_mock.DEFAULT_TIME_ZONE = timezone.utc
dt_mock.now.return_value = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)

class MockCalendarEvent:
    def __init__(self, start=None, end=None, summary="", description="", uid=""):
        self.start = start
        self.end = end
        self.summary = summary
        self.description = description
        self.uid = uid

class MockCalendarEntity:
    pass

cal_comp_mock = MagicMock()
cal_comp_mock.CalendarEntity = MockCalendarEntity
cal_comp_mock.CalendarEvent = MockCalendarEvent

sys.modules["homeassistant"] = ha_mock
sys.modules["homeassistant.components"] = MagicMock(calendar=cal_comp_mock)
sys.modules["homeassistant.components.calendar"] = cal_comp_mock
sys.modules["homeassistant.config_entries"] = ha_mock
sys.modules["homeassistant.core"] = ha_mock
sys.modules["homeassistant.helpers"] = ha_mock
sys.modules["homeassistant.helpers.dispatcher"] = ha_mock
sys.modules["homeassistant.helpers.entity_platform"] = ha_mock
sys.modules["homeassistant.helpers.storage"] = ha_mock
sys.modules["homeassistant.util"] = MagicMock(dt=dt_mock)
sys.modules["homeassistant.util.dt"] = dt_mock

project_root = Path(__file__).parent.parent

pkg_mock = MagicMock()
pkg_mock.__path__ = [str(project_root / "custom_components" / "task_manager")]
sys.modules["custom_components"] = MagicMock()
sys.modules["custom_components.task_manager"] = pkg_mock

const_spec = importlib.util.spec_from_file_location(
    "custom_components.task_manager.const",
    project_root / "custom_components" / "task_manager" / "const.py",
)
const_mod = importlib.util.module_from_spec(const_spec)
sys.modules["custom_components.task_manager.const"] = const_mod
const_spec.loader.exec_module(const_mod)

providers_spec = importlib.util.spec_from_file_location(
    "custom_components.task_manager.providers",
    project_root / "custom_components" / "task_manager" / "providers.py",
)
providers_mod = importlib.util.module_from_spec(providers_spec)
sys.modules["custom_components.task_manager.providers"] = providers_mod
providers_spec.loader.exec_module(providers_mod)

storage_spec = importlib.util.spec_from_file_location(
    "custom_components.task_manager.storage",
    project_root / "custom_components" / "task_manager" / "storage.py",
)
storage_mod = importlib.util.module_from_spec(storage_spec)
sys.modules["custom_components.task_manager.storage"] = storage_mod
storage_spec.loader.exec_module(storage_mod)

cal_spec = importlib.util.spec_from_file_location(
    "custom_components.task_manager.calendar",
    project_root / "custom_components" / "task_manager" / "calendar.py",
)
cal_mod = importlib.util.module_from_spec(cal_spec)
sys.modules["custom_components.task_manager.calendar"] = cal_mod
cal_spec.loader.exec_module(cal_mod)

_task_to_event = cal_mod._task_to_event
_expand_task_occurrences = cal_mod._expand_task_occurrences
TaskManagerCalendarEntity = cal_mod.TaskManagerCalendarEntity


class TestTaskManagerCalendar(unittest.TestCase):
    """Test suite for calendar platform."""

    def test_task_to_all_day_event(self):
        """Test converting all-day task to CalendarEvent."""
        task = {
            "id": "task_1",
            "title": "Clean kitchen",
            "due_date": "2026-09-28",
            "description": "Thorough counter wipe",
        }
        event = _task_to_event(task)
        self.assertIsNotNone(event)
        self.assertEqual(event.summary, "Clean kitchen")
        self.assertEqual(event.start, date(2026, 9, 28))
        self.assertEqual(event.end, date(2026, 9, 29))
        self.assertEqual(event.description, "Thorough counter wipe")

    def test_task_to_timed_event(self):
        """Test converting timed task to CalendarEvent."""
        task = {
            "id": "task_2",
            "title": "Water Plants",
            "due_date": "2026-09-28",
            "due_time": "15:30",
        }
        event = _task_to_event(task)
        self.assertIsNotNone(event)
        self.assertEqual(event.summary, "Water Plants")
        self.assertIsInstance(event.start, datetime)
        self.assertEqual(event.start.hour, 15)
        self.assertEqual(event.start.minute, 30)
        self.assertEqual(event.end, event.start + timedelta(minutes=30))

    def test_expand_recurring_events(self):
        """Test projecting recurring daily tasks within a date range."""
        task = {
            "id": "task_daily",
            "title": "Daily Walk",
            "due_date": "2026-09-26",
            "recurrence": {
                "enabled": True,
                "type": "daily",
                "interval": 1,
            },
        }
        start = datetime(2026, 9, 26, 0, 0, tzinfo=timezone.utc)
        end = datetime(2026, 9, 30, 0, 0, tzinfo=timezone.utc)

        events = _expand_task_occurrences(task, start, end)
        self.assertGreaterEqual(len(events), 4)

    def test_calendar_entity_filtering(self):
        """Test user filtering on calendar entity."""
        storage = MagicMock()
        storage.get_all_tasks.return_value = [
            {
                "id": "t1",
                "title": "Alice Task",
                "due_date": "2026-09-27",
                "current_assignee": "user_alice",
                "assignees": ["user_alice"],
                "status": "pending",
                "recurrence": {"enabled": False},
            },
            {
                "id": "t2",
                "title": "Bob Task",
                "due_date": "2026-09-27",
                "current_assignee": "user_bob",
                "assignees": ["user_bob"],
                "status": "pending",
                "recurrence": {"enabled": False},
            },
        ]

        # Entity for Alice only
        cal_alice = TaskManagerCalendarEntity(storage, "user_alice", "Task Manager (Alice)")
        tasks = cal_alice._get_applicable_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Alice Task")

        # Entity for All
        cal_all = TaskManagerCalendarEntity(storage, "all", "Task Manager Chores")
        all_tasks = cal_all._get_applicable_tasks()
        self.assertEqual(len(all_tasks), 2)


if __name__ == "__main__":
    unittest.main()
