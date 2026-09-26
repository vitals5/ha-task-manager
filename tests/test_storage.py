"""Unit tests for Task Manager data storage and business logic."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock

# Mock homeassistant module hierarchy for local testing
ha_mock = MagicMock()
dt_mock = MagicMock()
dt_mock.now.return_value = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)

sys.modules["homeassistant"] = ha_mock
sys.modules["homeassistant.core"] = ha_mock
sys.modules["homeassistant.helpers"] = ha_mock
sys.modules["homeassistant.helpers.dispatcher"] = ha_mock
sys.modules["homeassistant.helpers.storage"] = ha_mock
sys.modules["homeassistant.util"] = MagicMock(dt=dt_mock)
sys.modules["homeassistant.util.dt"] = dt_mock

project_root = Path(__file__).parent.parent

const_spec = importlib.util.spec_from_file_location(
    "custom_components.task_manager.const",
    project_root / "custom_components" / "task_manager" / "const.py",
)
const_mod = importlib.util.module_from_spec(const_spec)
sys.modules["custom_components.task_manager.const"] = const_mod
const_spec.loader.exec_module(const_mod)

storage_spec = importlib.util.spec_from_file_location(
    "custom_components.task_manager.storage",
    project_root / "custom_components" / "task_manager" / "storage.py",
)
storage_mod = importlib.util.module_from_spec(storage_spec)
sys.modules["custom_components.task_manager.storage"] = storage_mod
storage_spec.loader.exec_module(storage_mod)

TaskManagerData = storage_mod.TaskManagerData
calculate_next_due_date = storage_mod.calculate_next_due_date


class TestTaskManagerStorage(unittest.TestCase):
    """Test suite for Task Manager storage and logic."""

    def setUp(self):
        """Set up fresh data container for each test."""
        self.data = TaskManagerData()

    def test_default_data_initialization(self):
        """Test default dataset initialization."""
        self.assertGreaterEqual(len(self.data.users), 1)
        self.assertGreaterEqual(len(self.data.things), 3)
        self.assertGreaterEqual(len(self.data.labels), 6)
        self.assertEqual(len(self.data.tasks), 0)
        self.assertTrue(self.data.settings.get("gamification_enabled"))

    def test_create_and_get_task(self):
        """Test task creation and retrieval."""
        task = self.data.create_task({
            "title": "Clean kitchen counters",
            "description": "Wipe with disinfectant",
            "priority": "p2",
            "points": 15,
            "subtasks": ["Spray cleaner", "Wipe dry"],
        })
        self.assertIsNotNone(task.get("id"))
        self.assertEqual(task["title"], "Clean kitchen counters")
        self.assertEqual(task["status"], "pending")
        self.assertEqual(len(task["subtasks"]), 2)
        self.assertEqual(task["points"], 15)

        retrieved = self.data.get_task(task["id"])
        self.assertEqual(retrieved["id"], task["id"])

    def test_update_task(self):
        """Test task updating."""
        task = self.data.create_task({"title": "Vacuum living room"})
        t_id = task["id"]

        updated = self.data.update_task(t_id, {
            "title": "Vacuum entire ground floor",
            "priority": "p1",
            "subtasks": ["Living room", "Hallway"],
        })
        self.assertEqual(updated["title"], "Vacuum entire ground floor")
        self.assertEqual(updated["priority"], "p1")
        self.assertEqual(len(updated["subtasks"]), 2)

    def test_complete_non_recurring_task(self):
        """Test completing a non-recurring task awards points and marks status completed."""
        user = self.data.users[0]
        initial_points = user.get("points", 0)

        task = self.data.create_task({
            "title": "Dust shelves",
            "points": 20,
            "current_assignee": user["id"],
        })

        completed = self.data.complete_task(task["id"], user_id=user["id"])
        self.assertEqual(completed["status"], "completed")
        self.assertIsNotNone(completed["completed_at"])
        self.assertEqual(completed["completed_by"], user["id"])

        # Check points awarded
        updated_user = self.data.get_user(user["id"])
        self.assertEqual(updated_user["points"], initial_points + 20)
        self.assertEqual(updated_user["completed_count"], 1)
        self.assertEqual(updated_user["streak"], 1)

    def test_complete_recurring_task_smart_subtask_reset(self):
        """Test recurring tasks advance due date and automatically reset subtasks."""
        task = self.data.create_task({
            "title": "Take out trash",
            "due_date": "2026-09-26",
            "recurrence": {
                "enabled": True,
                "type": "daily",
                "interval": 2,
                "based_on": "due_date",
            },
            "subtasks": ["Recycling", "Compost"],
        })
        t_id = task["id"]

        # Check off a subtask first
        subtask_id = task["subtasks"][0]["id"]
        self.data.update_subtask(t_id, subtask_id, completed=True)
        self.assertTrue(self.data.get_task(t_id)["subtasks"][0]["completed"])

        # Complete recurring task
        completed = self.data.complete_task(t_id)
        # Status should remain pending for next occurrence
        self.assertEqual(completed["status"], "pending")
        self.assertEqual(completed["due_date"], "2026-09-28")

        # Subtasks must be reset to False!
        for st in completed["subtasks"]:
            self.assertFalse(st["completed"])

    def test_assignee_rotation_round_robin(self):
        """Test assignee rotation cycles through members upon recurring completion."""
        user_a = self.data.create_user({"name": "Alice"})
        user_b = self.data.create_user({"name": "Bob"})

        task = self.data.create_task({
            "title": "Mow the lawn",
            "assignees": [user_a["id"], user_b["id"]],
            "current_assignee": user_a["id"],
            "rotation_mode": "round_robin",
            "recurrence": {
                "enabled": True,
                "type": "weekly",
                "interval": 1,
            },
        })

        # Complete first cycle
        self.data.complete_task(task["id"])
        updated = self.data.get_task(task["id"])
        self.assertEqual(updated["current_assignee"], user_b["id"])

        # Complete second cycle
        self.data.complete_task(task["id"])
        updated2 = self.data.get_task(task["id"])
        self.assertEqual(updated2["current_assignee"], user_a["id"])

    def test_linked_thing_reset_on_task_completion(self):
        """Test linked Thing counter resets to 0 when chore is completed."""
        thing = self.data.create_thing({
            "name": "Coffee Maker",
            "current_value": 85,
            "target_value": 100,
            "unit": "cups",
        })

        task = self.data.create_task({
            "title": "Descale Coffee Maker",
            "linked_thing_id": thing["id"],
            "thing_action": "reset",
        })

        self.data.complete_task(task["id"])

        updated_thing = self.data.get_thing(thing["id"])
        self.assertEqual(updated_thing["current_value"], 0)
        self.assertIsNotNone(updated_thing["last_reset"])

    def test_thing_auto_task_creation(self):
        """Test reaching Thing threshold automatically creates a maintenance task."""
        thing = self.data.create_thing({
            "name": "HVAC Filter",
            "current_value": 85,
            "target_value": 90,
            "unit": "days",
            "auto_task_creation": True,
            "auto_task_title": "Replace HVAC Filter Now",
        })

        # Increment past target
        self.data.update_thing_value(thing["id"], delta=10)

        # Verify auto task was generated
        auto_tasks = [t for t in self.data.tasks if t["title"] == "Replace HVAC Filter Now"]
        self.assertEqual(len(auto_tasks), 1)
        self.assertEqual(auto_tasks[0]["priority"], "p1")
        self.assertEqual(auto_tasks[0]["linked_thing_id"], thing["id"])

    def test_labels_management(self):
        """Test label creation and deletion."""
        label = self.data.create_label({"name": "Garage", "color": "#f59e0b"})
        self.assertIsNotNone(self.data.get_label(label["id"]))

        # Assign label to task
        task = self.data.create_task({"title": "Clean workbench", "labels": [label["id"]]})
        self.assertIn(label["id"], task["labels"])

        # Delete label
        self.data.delete_label(label["id"])
        self.assertIsNone(self.data.get_label(label["id"]))
        self.assertNotIn(label["id"], self.data.get_task(task["id"])["labels"])

    def test_export_and_import(self):
        """Test data export and import backup functionality."""
        self.data.create_task({"title": "Task A"})
        exported = self.data.to_dict()

        new_data = TaskManagerData()
        new_data.import_data(exported)
        self.assertEqual(len(new_data.tasks), len(self.data.tasks))
        self.assertEqual(new_data.tasks[0]["title"], "Task A")


if __name__ == "__main__":
    unittest.main()
