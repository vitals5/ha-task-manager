"""Sensor platform for Task Manager integration."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SIGNAL_TASK_MANAGER_UPDATED
from .storage import TaskManagerStorage

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Task Manager sensors."""
    storage: TaskManagerStorage = hass.data[DOMAIN][entry.entry_id]

    created_ids: set[str] = set()

    # Initial static summary sensors
    summary_sensors = [
        TaskManagerSummarySensor(storage, "total", "Task Manager Total Tasks", "mdi:clipboard-text-outline"),
        TaskManagerSummarySensor(storage, "pending", "Task Manager Pending Tasks", "mdi:clipboard-clock-outline"),
        TaskManagerSummarySensor(storage, "overdue", "Task Manager Overdue Tasks", "mdi:alert-circle-outline"),
        TaskManagerSummarySensor(storage, "completed_today", "Task Manager Completed Today", "mdi:check-circle-outline"),
    ]
    for s in summary_sensors:
        created_ids.add(s.unique_id)
    async_add_entities(summary_sensors)

    @callback
    def update_dynamic_sensors() -> None:
        """Add new sensors for newly added users or things."""
        new_entities = []

        # User Sensors
        for user in storage.data.users:
            u_id = f"user_{user['id']}"
            if u_id not in created_ids:
                created_ids.add(u_id)
                new_entities.append(TaskManagerUserSensor(storage, user["id"]))

        # Thing Sensors
        for thing in storage.data.things:
            th_id = f"thing_{thing['id']}"
            if th_id not in created_ids:
                created_ids.add(th_id)
                new_entities.append(TaskManagerThingSensor(storage, thing["id"]))

        if new_entities:
            async_add_entities(new_entities)

    update_dynamic_sensors()
    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_TASK_MANAGER_UPDATED, update_dynamic_sensors)
    )


class TaskManagerSummarySensor(SensorEntity):
    """Summary sensor for task counts."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, storage: TaskManagerStorage, count_type: str, name: str, icon: str) -> None:
        """Initialize summary sensor."""
        self._storage = storage
        self._count_type = count_type
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{count_type}_tasks"
        self._attr_icon = icon

    async def async_added_to_hass(self) -> None:
        """Register listener."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_TASK_MANAGER_UPDATED, self._handle_update
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle state update."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        """Return the count."""
        tasks = self._storage.data.tasks
        today_str = dt_util.now().date().strftime("%Y-%m-%d")

        if self._count_type == "total":
            return len(tasks)

        if self._count_type == "pending":
            return sum(1 for t in tasks if t.get("status") == "pending")

        if self._count_type == "overdue":
            count = 0
            for t in tasks:
                if t.get("status") == "pending":
                    due = t.get("due_date", "")
                    if due and due < today_str:
                        count += 1
            return count

        if self._count_type == "completed_today":
            count = 0
            for t in tasks:
                if t.get("status") == "completed":
                    comp = t.get("completed_at", "")
                    if comp and comp[:10] == today_str:
                        count += 1
                for h in t.get("history", []):
                    comp = h.get("completed_at", "")
                    if comp and comp[:10] == today_str:
                        count += 1
            return count

        return 0


class TaskManagerUserSensor(SensorEntity):
    """Sensor for individual user points and stats."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, storage: TaskManagerStorage, user_id: str) -> None:
        """Initialize user sensor."""
        self._storage = storage
        self._user_id = user_id
        user = storage.data.get_user(user_id)
        user_name = user["name"] if user else user_id
        self._attr_name = f"Task Manager {user_name} Points"
        self._attr_unique_id = f"{DOMAIN}_user_{user_id}_points"
        self._attr_icon = "mdi:star-circle-outline"
        self._attr_native_unit_of_measurement = "pts"

    async def async_added_to_hass(self) -> None:
        """Register listener."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_TASK_MANAGER_UPDATED, self._handle_update
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle state update."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        """Return user points."""
        user = self._storage.data.get_user(self._user_id)
        return user.get("points", 0) if user else 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return user stats attributes."""
        user = self._storage.data.get_user(self._user_id)
        if not user:
            return {}

        today_str = dt_util.now().date().strftime("%Y-%m-%d")
        due_count = sum(
            1 for t in self._storage.data.tasks
            if t.get("status") == "pending"
            and (t.get("current_assignee") == self._user_id or self._user_id in t.get("assignees", []))
            and t.get("due_date", "") <= today_str
        )

        return {
            "user_id": self._user_id,
            "user_name": user.get("name"),
            "streak": user.get("streak", 0),
            "completed_count": user.get("completed_count", 0),
            "tasks_due": due_count,
            "last_completed_date": user.get("last_completed_date", ""),
        }


class TaskManagerThingSensor(SensorEntity):
    """Sensor for household things/meters."""

    _attr_has_entity_name = True

    def __init__(self, storage: TaskManagerStorage, thing_id: str) -> None:
        """Initialize thing sensor."""
        self._storage = storage
        self._thing_id = thing_id
        thing = storage.data.get_thing(thing_id)
        thing_name = thing["name"] if thing else thing_id
        self._attr_name = f"Task Manager Thing {thing_name}"
        self._attr_unique_id = f"{DOMAIN}_thing_{thing_id}"
        self._attr_icon = thing.get("icon", "mdi:chart-arc") if thing else "mdi:chart-arc"

    async def async_added_to_hass(self) -> None:
        """Register listener."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_TASK_MANAGER_UPDATED, self._handle_update
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle state update."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> float | int:
        """Return current value."""
        thing = self._storage.data.get_thing(self._thing_id)
        return thing.get("current_value", 0) if thing else 0

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of measurement."""
        thing = self._storage.data.get_thing(self._thing_id)
        return thing.get("unit") if thing else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return thing metadata."""
        thing = self._storage.data.get_thing(self._thing_id)
        if not thing:
            return {}

        target = float(thing.get("target_value", 100))
        cur = float(thing.get("current_value", 0))
        pct = round((cur / target) * 100, 1) if target > 0 else 0.0

        return {
            "thing_id": self._thing_id,
            "category": thing.get("category", ""),
            "target_value": target,
            "progress_percent": pct,
            "auto_task_creation": thing.get("auto_task_creation", False),
            "last_reset": thing.get("last_reset", ""),
        }
