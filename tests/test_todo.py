"""Unit tests for Task Manager Todo platform."""
from __future__ import annotations

from datetime import date, datetime, timezone
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock

# Mock homeassistant module hierarchy
ha_mock = MagicMock()
dt_mock = MagicMock()
dt_mock.now.return_value = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)

# Mock TodoListEntityFeature as an IntFlag-like object matching HA core
class MockTodoListEntityFeature:
    CREATE_TODO_ITEM = 1
    DELETE_TODO_ITEM = 2
    UPDATE_TODO_ITEM = 4
    MOVE_TODO_ITEM = 8
    SET_DUE_DATE_ON_ITEM = 16
    SET_DUE_DATETIME_ON_ITEM = 32
    SET_DESCRIPTION_ON_ITEM = 64

class MockTodoItem:
    def __init__(self, uid="", summary="", status=None, due=None, description=""):
        self.uid = uid
        self.summary = summary
        self.status = status
        self.due = due
        self.description = description

class MockTodoItemStatus:
    NEEDS_ACTION = "needs_action"
    COMPLETED = "completed"

class MockTodoListEntity:
    pass

todo_comp_mock = MagicMock()
todo_comp_mock.TodoListEntity = MockTodoListEntity
todo_comp_mock.TodoListEntityFeature = MockTodoListEntityFeature
todo_comp_mock.TodoItem = MockTodoItem
todo_comp_mock.TodoItemStatus = MockTodoItemStatus

sys.modules["homeassistant"] = ha_mock
sys.modules["homeassistant.components"] = MagicMock(todo=todo_comp_mock)
sys.modules["homeassistant.components.todo"] = todo_comp_mock
sys.modules["homeassistant.config_entries"] = ha_mock
sys.modules["homeassistant.core"] = ha_mock
sys.modules["homeassistant.helpers"] = ha_mock
sys.modules["homeassistant.helpers.dispatcher"] = ha_mock
sys.modules["homeassistant.helpers.entity_platform"] = ha_mock
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

todo_spec = importlib.util.spec_from_file_location(
    "custom_components.task_manager.todo",
    project_root / "custom_components" / "task_manager" / "todo.py",
)
todo_mod = importlib.util.module_from_spec(todo_spec)
sys.modules["custom_components.task_manager.todo"] = todo_mod
todo_spec.loader.exec_module(todo_mod)

TaskManagerTodoListEntity = todo_mod.TaskManagerTodoListEntity
TaskManagerData = storage_mod.TaskManagerData


class TestTaskManagerTodo(unittest.TestCase):
    """Test suite for Task Manager Todo platform."""

    def test_supported_features_no_attribute_error(self):
        """Test supported features are resolved without error."""
        storage_mock = MagicMock()
        storage_mock.data = TaskManagerData()

        entity = TaskManagerTodoListEntity(storage_mock)
        self.assertIsNotNone(entity._attr_supported_features)
        self.assertTrue(entity._attr_supported_features & MockTodoListEntityFeature.CREATE_TODO_ITEM)
        self.assertTrue(entity._attr_supported_features & MockTodoListEntityFeature.UPDATE_TODO_ITEM)
        self.assertTrue(entity._attr_supported_features & MockTodoListEntityFeature.DELETE_TODO_ITEM)
        self.assertTrue(entity._attr_supported_features & MockTodoListEntityFeature.SET_DUE_DATE_ON_ITEM)
        self.assertTrue(entity._attr_supported_features & MockTodoListEntityFeature.SET_DESCRIPTION_ON_ITEM)

    def test_todo_items_generation(self):
        """Test todo_items returns properly mapped tasks."""
        storage_mock = MagicMock()
        data = TaskManagerData()
        data.create_task({"title": "Clean sink", "due_date": "2026-09-26", "due_time": "14:00"})
        storage_mock.data = data

        entity = TaskManagerTodoListEntity(storage_mock)
        items = entity.todo_items
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].summary, "Clean sink")
        self.assertEqual(items[0].due, datetime(2026, 9, 26, 14, 0))


if __name__ == "__main__":
    unittest.main()
