"""Unit tests for Task Manager data storage and business logic."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

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

TaskManagerData = storage_mod.TaskManagerData
TaskManagerStorage = storage_mod.TaskManagerStorage
calculate_next_due_date = storage_mod.calculate_next_due_date
is_thing_threshold_reached = storage_mod.is_thing_threshold_reached
FAR_FUTURE_DUE_DATE = const_mod.FAR_FUTURE_DUE_DATE


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

    def test_thing_update_value_with_none_arguments(self):
        """Test updating thing value when value or delta is explicitly None."""
        thing = self.data.create_thing({
            "name": "Coffee Machine",
            "current_value": 10,
        })
        # Delta update with value=None
        res = self.data.update_thing_value(thing["id"], delta=1, value=None)
        self.assertEqual(res["current_value"], 11)

        # Value update with delta=None
        res2 = self.data.update_thing_value(thing["id"], delta=None, value=25)
        self.assertEqual(res2["current_value"], 25)

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

    def test_provider_management(self):
        """Test adding, listing, and removing external providers."""
        prov = self.data.add_provider("todo.google_groceries", "Groceries", "google_tasks", "mdi:google")
        self.assertEqual(prov["entity_id"], "todo.google_groceries")
        self.assertEqual(prov["name"], "Groceries")
        self.assertEqual(len(self.data.get_providers()), 1)

        # Update existing
        prov2 = self.data.add_provider("todo.google_groceries", "Updated Groceries")
        self.assertEqual(prov2["name"], "Updated Groceries")
        self.assertEqual(len(self.data.get_providers()), 1)

        # Remove provider
        ok = self.data.remove_provider("todo.google_groceries")
        self.assertTrue(ok)
        self.assertEqual(len(self.data.get_providers()), 0)

    def test_external_tasks_merge_and_overlay(self):
        """Test merging external tasks with local overlays."""
        self.data.add_provider("todo.test_list", "Test Provider", "todoist")
        self.data.external_tasks_cache["todo.test_list"] = [
            {
                "uid": "ext_item_123",
                "title": "Buy Milk",
                "description": "2% organic milk",
                "status": "pending",
                "due_date": "2026-09-30",
                "due_time": "14:00",
            }
        ]

        # Add overlay
        self.data.set_overlay("ext_item_123", {
            "points": 25,
            "priority": "p1",
            "assignees": ["user_household"],
        })

        all_tasks = self.data.get_all_tasks(include_external=True)
        # Should include default tasks + the external task
        ext_task = next((t for t in all_tasks if t.get("is_external")), None)
        self.assertIsNotNone(ext_task)
        self.assertEqual(ext_task["id"], "ext:todo.test_list:ext_item_123")
        self.assertEqual(ext_task["title"], "Buy Milk")
        self.assertEqual(ext_task["points"], 25)
        self.assertEqual(ext_task["priority"], "p1")
        self.assertEqual(ext_task["provider_name"], "Test Provider")
        self.assertEqual(ext_task["provider_type"], "todoist")

    def test_thing_threshold_operator_and_linkage(self):
        """Test threshold calculation for both >= and <= operators."""
        # GTE operator (count up)
        thing_gte = {
            "current_value": 50,
            "target_value": 100,
            "threshold_operator": ">=",
        }
        self.assertFalse(is_thing_threshold_reached(thing_gte))
        thing_gte["current_value"] = 100
        self.assertTrue(is_thing_threshold_reached(thing_gte))
        thing_gte["current_value"] = 105
        self.assertTrue(is_thing_threshold_reached(thing_gte))

        # LTE operator (countdown, e.g. vacuum brush life 100% -> 0%)
        thing_lte = {
            "current_value": 15,
            "target_value": 0,
            "threshold_operator": "<=",
        }
        self.assertFalse(is_thing_threshold_reached(thing_lte))
        thing_lte["current_value"] = 0
        self.assertTrue(is_thing_threshold_reached(thing_lte))
        thing_lte["current_value"] = -2
        self.assertTrue(is_thing_threshold_reached(thing_lte))

    def test_task_linked_to_thing_threshold_due_date_lifecycle(self):
        """Test full lifecycle of a task linked to a countdown Thing without time fallback."""
        # 1. Create a Thing with external_entity_id and countdown operator
        thing = self.data.create_thing({
            "name": "Roborock Main Brush",
            "external_entity_id": "sensor.p50_pro_ultra_main_brush_left",
            "threshold_operator": "<=",
            "target_value": 0,
            "initial_value": 100,
            "current_value": 45,
            "unit": "%",
        })
        self.assertEqual(thing["threshold_operator"], "<=")
        self.assertEqual(thing["initial_value"], 100)
        self.assertEqual(thing["external_entity_id"], "sensor.p50_pro_ultra_main_brush_left")

        # 2. Create a recurring task linked to this Thing, with no time schedule fallback
        task = self.data.create_task({
            "title": "Clean or replace main brush",
            "linked_thing_id": thing["id"],
            "recurrence": {
                "enabled": True,
                "type": "none",
                "interval": 1,
            },
        })
        # Since threshold is not reached yet (45 > 0) and no schedule fallback, due date is FAR_FUTURE_DUE_DATE
        self.assertEqual(task["due_date"], FAR_FUTURE_DUE_DATE)

        # 3. Simulate external sensor counting down and reaching threshold (0%)
        self.data.update_thing_value(thing["id"], value=0)

        # Pending linked task should automatically have its due_date pulled to today (2026-09-26)
        updated_task = self.data.get_task(task["id"])
        self.assertEqual(updated_task["due_date"], "2026-09-26")

        # 4. Complete the task
        self.data.complete_task(task["id"])

        # Thing's current value should reset to initial_value (100) because it's a countdown (<=)
        rechecked_thing = self.data.get_thing(thing["id"])
        self.assertEqual(rechecked_thing["current_value"], 100)

        # Recurring task remains pending, but its next due_date is set back to FAR_FUTURE_DUE_DATE
        rechecked_task = self.data.get_task(task["id"])
        self.assertEqual(rechecked_task["status"], "pending")
        self.assertEqual(rechecked_task["due_date"], FAR_FUTURE_DUE_DATE)

    def test_task_linked_to_thing_with_fallback_schedule(self):
        """Test task linked to Thing with a fallback time schedule."""
        thing = self.data.create_thing({
            "name": "Coffee Machine Descaling",
            "threshold_operator": ">=",
            "target_value": 100,
            "current_value": 20,
            "unit": "cups",
        })

        # Task linked to Thing with a weekly fallback schedule
        task = self.data.create_task({
            "title": "Descale Coffee Machine",
            "linked_thing_id": thing["id"],
            "due_date": "2026-09-26",
            "recurrence": {
                "enabled": True,
                "type": "weekly",
                "interval": 1,
                "based_on": "due_date",
            },
        })
        # Due date should remain the configured fallback date, not far future
        self.assertEqual(task["due_date"], "2026-09-26")

        # Complete task
        self.data.complete_task(task["id"])

        # Next due date should be calculated using the recurrence fallback (next week: 2026-10-03)
        updated_task = self.data.get_task(task["id"])
        self.assertEqual(updated_task["due_date"], "2026-10-03")
        self.assertEqual(updated_task["status"], "pending")

    def test_thing_script_entity_crud(self):
        """Test creating and updating Thing with script_entity_id."""
        thing = self.data.create_thing({
            "name": "Roborock Main Brush",
            "script_entity_id": "script.reset_main_brush",
        })
        self.assertEqual(thing["script_entity_id"], "script.reset_main_brush")

        # Update script entity
        updated = self.data.update_thing(thing["id"], {"script_entity_id": "script.custom_reset"})
        self.assertEqual(updated["script_entity_id"], "script.custom_reset")

        # Remove script entity
        updated2 = self.data.update_thing(thing["id"], {"script_entity_id": None})
        self.assertIsNone(updated2["script_entity_id"])

    def test_duplicate_task(self):
        """Test duplicating a task creates an independent copy."""
        task = self.data.create_task({
            "title": "Clean oven",
            "description": "Use special spray",
            "priority": "p2",
            "points": 20,
            "reminders": [15, 60],
            "subtasks": [{"id": "s1", "title": "Spray walls", "completed": True}],
        })
        clone = self.data.duplicate_task(task["id"])
        self.assertIsNotNone(clone)
        self.assertNotEqual(clone["id"], task["id"])
        self.assertEqual(clone["title"], "Clean oven (Copy)")
        self.assertEqual(clone["priority"], "p2")
        self.assertEqual(clone["points"], 20)
        self.assertEqual(clone["reminders"], [15, 60])
        self.assertEqual(len(clone["subtasks"]), 1)
        self.assertFalse(clone["subtasks"][0]["completed"])

    def test_calculate_next_due_date_weekdays(self):
        """Test calculating next due date with selected weekdays."""
        rec = {
            "type": "weekly",
            "interval": 1,
            "weekdays": [2, 4],  # Wednesday (2) and Friday (4)
        }
        # From Monday 2026-09-28 -> next is Wednesday 2026-09-30
        next_due = calculate_next_due_date("2026-09-28", rec)
        self.assertEqual(next_due, "2026-09-30")


class TestTaskManagerStorageAsync(unittest.IsolatedAsyncioTestCase):
    """Async test suite for Task Manager storage actions and script triggers."""

    async def test_task_completion_triggers_thing_script(self):
        """Test completing a task linked to a Thing automatically runs its script entity."""
        hass = MagicMock()
        hass.services = MagicMock()
        hass.services.async_call = AsyncMock()

        storage = TaskManagerStorage(hass)
        storage.async_save = AsyncMock()

        thing = storage.data.create_thing({
            "name": "Roborock Brush",
            "script_entity_id": "script.reset_robot_brush",
            "threshold_operator": "<=",
            "target_value": 0,
            "current_value": 0,
        })

        task = storage.data.create_task({
            "title": "Clean Robot Brush",
            "linked_thing_id": thing["id"],
        })

        # Complete task via async_complete_task
        completed_task = await storage.async_complete_task(task["id"])
        self.assertIsNotNone(completed_task)

        # Verify script service was called
        hass.services.async_call.assert_called_once_with(
            "script", "turn_on", {"entity_id": "script.reset_robot_brush"}, blocking=False
        )

        # Verify activity log
        log_actions = [entry["action"] for entry in storage.data.activity_log]
        self.assertIn("thing_script_triggered", log_actions)

    async def test_task_completion_triggers_thing_script_custom_name(self):
        """Test script call when script_entity_id does not have script. prefix."""
        hass = MagicMock()
        hass.services = MagicMock()
        hass.services.async_call = AsyncMock()

        storage = TaskManagerStorage(hass)
        storage.async_save = AsyncMock()

        thing = storage.data.create_thing({
            "name": "Filter",
            "script_entity_id": "custom_filter_reset",
        })

        task = storage.data.create_task({
            "title": "Replace Filter",
            "linked_thing_id": thing["id"],
        })

        await storage.async_complete_task(task["id"])
        hass.services.async_call.assert_called_once_with(
            "script", "custom_filter_reset", {}, blocking=False
        )

    async def test_automation_events_fired(self):
        """Test automation events are emitted via hass.bus.async_fire."""
        hass = MagicMock()
        hass.bus = MagicMock()
        hass.bus.async_fire = MagicMock()

        storage = TaskManagerStorage(hass)
        storage.async_save = AsyncMock()

        # 1. Create task
        task = await storage.async_save_task({
            "title": "Water Plants",
            "current_assignee": "user_household",
        })
        created_events = [c for c in hass.bus.async_fire.call_args_list if c[0][0] == const_mod.EVENT_TASK_CREATED]
        self.assertTrue(len(created_events) > 0)
        self.assertEqual(created_events[0][0][1]["task_title"], "Water Plants")

        assigned_events = [c for c in hass.bus.async_fire.call_args_list if c[0][0] == const_mod.EVENT_TASK_ASSIGNED]
        self.assertTrue(len(assigned_events) > 0)

        # 2. Complete task
        await storage.async_complete_task(task["id"])
        completed_events = [c for c in hass.bus.async_fire.call_args_list if c[0][0] == const_mod.EVENT_TASK_COMPLETED]
        self.assertTrue(len(completed_events) > 0)

        # 3. Reset task
        await storage.async_reset_task(task["id"])
        reopened_events = [c for c in hass.bus.async_fire.call_args_list if c[0][0] == const_mod.EVENT_TASK_REOPENED]
        self.assertTrue(len(reopened_events) > 0)

    async def test_duplicate_and_move_task_async(self):
        """Test async_duplicate_task and async_move_task."""
        hass = MagicMock()
        hass.bus = MagicMock()
        hass.bus.async_fire = MagicMock()

        storage = TaskManagerStorage(hass)
        storage.async_save = AsyncMock()

        task = storage.data.create_task({"title": "Clean Balcony"})
        clone = await storage.async_duplicate_task(task["id"])
        self.assertIsNotNone(clone)
        self.assertEqual(clone["title"], "Clean Balcony (Copy)")

        moved = await storage.async_move_task(task["id"], "task_manager")
        self.assertIsNotNone(moved)
        self.assertEqual(moved["title"], "Clean Balcony")


if __name__ == "__main__":
    unittest.main()

