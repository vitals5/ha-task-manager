"""Todo platform for Task Manager integration."""
from __future__ import annotations

from datetime import date, datetime
import logging
from typing import Any

from homeassistant.components.todo import (
    TodoListEntity,
    TodoListEntityFeature,
    TodoItem,
    TodoItemStatus,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    PRIORITIES,
    PRIORITY_NONE,
    SIGNAL_TASK_MANAGER_UPDATED,
)
from .storage import TaskManagerStorage

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Task Manager todo entities."""
    storage: TaskManagerStorage = hass.data[DOMAIN][entry.entry_id]

    # Clean up orphaned todo entities from registry on startup
    try:
        ent_reg = er.async_get(hass)
        valid_uids = {f"{DOMAIN}_todo_shared"} | {f"{DOMAIN}_todo_{u['id']}" for u in storage.data.users}
        for reg_entry in er.async_entries_for_config_entry(ent_reg, entry.entry_id):
            if reg_entry.domain == "todo" and reg_entry.unique_id not in valid_uids:
                _LOGGER.info("Removing orphaned todo entity from registry: %s", reg_entry.entity_id)
                ent_reg.async_remove(reg_entry.entity_id)
    except Exception as err:
        _LOGGER.debug("Could not cleanup orphaned todo entities: %s", err)

    shared_todo_added = False
    active_user_todos: dict[str, TaskManagerTodoListEntity] = {}

    @callback
    def update_entities() -> None:
        """Dynamically add or remove todo lists for users."""
        nonlocal shared_todo_added
        new_entities = []

        # 1. Main Shared / All Chores List
        if not shared_todo_added:
            shared_todo_added = True
            new_entities.append(TaskManagerTodoListEntity(storage, user_id=None))

        current_user_ids = {u["id"] for u in storage.data.users}

        # 2. Add new user lists
        for user in storage.data.users:
            u_id = user["id"]
            if u_id not in active_user_todos:
                entity = TaskManagerTodoListEntity(storage, user_id=u_id)
                active_user_todos[u_id] = entity
                new_entities.append(entity)

        # 3. Remove deleted user lists
        for u_id in list(active_user_todos.keys()):
            if u_id not in current_user_ids:
                entity = active_user_todos.pop(u_id)
                hass.async_create_task(entity.async_remove())
                try:
                    ent_reg = er.async_get(hass)
                    reg_id = ent_reg.async_get_entity_id("todo", DOMAIN, f"{DOMAIN}_todo_{u_id}")
                    if reg_id:
                        ent_reg.async_remove(reg_id)
                except Exception as err:
                    _LOGGER.debug("Error removing user todo from registry: %s", err)

        if new_entities:
            async_add_entities(new_entities)

    update_entities()
    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_TASK_MANAGER_UPDATED, update_entities)
    )


class TaskManagerTodoListEntity(TodoListEntity):
    """Representation of a Task Manager Todo List."""

    _attr_has_entity_name = True
    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
    )
    if hasattr(TodoListEntityFeature, "SET_DUE_DATE_ON_ITEM"):
        _attr_supported_features |= TodoListEntityFeature.SET_DUE_DATE_ON_ITEM
    if hasattr(TodoListEntityFeature, "SET_DUE_DATETIME_ON_ITEM"):
        _attr_supported_features |= TodoListEntityFeature.SET_DUE_DATETIME_ON_ITEM
    if hasattr(TodoListEntityFeature, "SET_DESCRIPTION_ON_ITEM"):
        _attr_supported_features |= TodoListEntityFeature.SET_DESCRIPTION_ON_ITEM

    def __init__(self, storage: TaskManagerStorage, user_id: str | None = None) -> None:
        """Initialize the todo list."""
        self._storage = storage
        self._user_id = user_id

        if user_id is None:
            self._attr_unique_id = f"{DOMAIN}_todo_shared"
            self._attr_name = "Task Manager All Chores"
            self._attr_icon = "mdi:clipboard-check-multiple-outline"
        else:
            user = storage.data.get_user(user_id)
            user_name = user["name"] if user else user_id
            self._attr_unique_id = f"{DOMAIN}_todo_{user_id}"
            self._attr_name = f"Task Manager ({user_name})"
            self._attr_icon = "mdi:checkbox-marked-circle-outline"

    async def async_added_to_hass(self) -> None:
        """Register dispatcher listener."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_TASK_MANAGER_UPDATED, self._handle_data_update
            )
        )

    @callback
    def _handle_data_update(self) -> None:
        """Handle updated data from storage."""
        self.async_write_ha_state()

    @property
    def todo_items(self) -> list[TodoItem]:
        """Return items from Task Manager storage."""
        items: list[TodoItem] = []
        for task in self._storage.data.tasks:
            # If user-specific list, filter tasks assigned to this user
            if self._user_id is not None:
                if task.get("current_assignee") != self._user_id and self._user_id not in task.get("assignees", []):
                    continue

            due: date | datetime | None = None
            due_date_str = task.get("due_date")
            due_time_str = task.get("due_time")
            if due_date_str:
                try:
                    if due_time_str:
                        due = datetime.strptime(f"{due_date_str[:10]} {due_time_str[:5]}", "%Y-%m-%d %H:%M")
                    else:
                        due = datetime.strptime(due_date_str[:10], "%Y-%m-%d").date()
                except ValueError:
                    due = None

            status = (
                TodoItemStatus.COMPLETED
                if task.get("status") == "completed"
                else TodoItemStatus.NEEDS_ACTION
            )

            items.append(
                TodoItem(
                    uid=task["id"],
                    summary=task.get("title", ""),
                    status=status,
                    due=due,
                    description=task.get("description", ""),
                )
            )
        return items

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Create a new task in Task Manager."""
        due_str = dt_util.now().date().strftime("%Y-%m-%d")
        due_time = ""
        if item.due:
            if isinstance(item.due, datetime):
                due_str = item.due.strftime("%Y-%m-%d")
                due_time = item.due.strftime("%H:%M")
            else:
                due_str = item.due.strftime("%Y-%m-%d")

        assignees = [self._user_id] if self._user_id else []

        task_data = {
            "title": item.summary,
            "description": item.description or "",
            "due_date": due_str,
            "due_time": due_time,
            "priority": PRIORITY_NONE,
            "assignees": assignees,
            "current_assignee": self._user_id,
        }
        self._storage.data.create_task(task_data)
        await self._storage.async_save()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Update an existing task in Task Manager."""
        task = self._storage.data.get_task(item.uid)
        if not task:
            return

        updates: dict[str, Any] = {}
        if item.summary:
            updates["title"] = item.summary
        if item.description is not None:
            updates["description"] = item.description
        if item.due:
            if isinstance(item.due, datetime):
                updates["due_date"] = item.due.strftime("%Y-%m-%d")
                updates["due_time"] = item.due.strftime("%H:%M")
            else:
                updates["due_date"] = item.due.strftime("%Y-%m-%d")

        # Check status transition
        if item.status == TodoItemStatus.COMPLETED and task.get("status") != "completed":
            await self._storage.async_complete_task(item.uid, user_id=self._user_id)
        elif item.status == TodoItemStatus.NEEDS_ACTION and task.get("status") == "completed":
            await self._storage.async_reset_task(item.uid)
        elif updates:
            self._storage.data.update_task(item.uid, updates)
            await self._storage.async_save()

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        """Delete tasks from Task Manager."""
        for uid in uids:
            self._storage.data.delete_task(uid)
        await self._storage.async_save()
