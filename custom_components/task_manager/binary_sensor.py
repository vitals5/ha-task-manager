"""Binary sensor platform for Task Manager integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util, slugify

from .const import DOMAIN, SIGNAL_TASK_MANAGER_UPDATED, TASK_STATE_DUE
from .storage import TaskManagerStorage, is_part_low_stock

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Task Manager binary sensors."""
    storage: TaskManagerStorage = hass.data[DOMAIN][entry.entry_id]

    static_entities = [
        TaskManagerOverdueBinarySensor(storage),
        TaskManagerPartsLowStockBinarySensor(storage),
    ]
    async_add_entities(static_entities)

    active_task_binary_sensors: dict[str, TaskManagerTaskProblemBinarySensor] = {}

    @callback
    def update_dynamic_binary_sensors() -> None:
        """Add new binary sensors or remove deleted ones for tasks."""
        new_entities = []
        current_task_ids = {t["id"] for t in storage.data.tasks}

        # 1. Add new task binary sensors
        for task in storage.data.tasks:
            t_id = task["id"]
            if t_id not in active_task_binary_sensors:
                sensor = TaskManagerTaskProblemBinarySensor(storage, t_id)
                active_task_binary_sensors[t_id] = sensor
                new_entities.append(sensor)

        # 2. Remove deleted task binary sensors
        for t_id in list(active_task_binary_sensors.keys()):
            if t_id not in current_task_ids:
                sensor = active_task_binary_sensors.pop(t_id)
                hass.async_create_task(sensor.async_remove())
                try:
                    ent_reg = er.async_get(hass)
                    reg_id = ent_reg.async_get_entity_id(
                        "binary_sensor", DOMAIN, f"{DOMAIN}_task_{t_id}_problem"
                    )
                    if reg_id:
                        ent_reg.async_remove(reg_id)
                except Exception as err:
                    _LOGGER.debug("Error removing task problem binary sensor from registry: %s", err)

        if new_entities:
            async_add_entities(new_entities)

    # Initial registration
    update_dynamic_binary_sensors()

    # Listen for updates
    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_TASK_MANAGER_UPDATED, update_dynamic_binary_sensors)
    )


class TaskManagerOverdueBinarySensor(BinarySensorEntity):
    """Binary sensor indicating if there are overdue tasks."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, storage: TaskManagerStorage) -> None:
        """Initialize overdue binary sensor."""
        self._storage = storage
        self._attr_name = "Task Manager Overdue"
        self._attr_unique_id = f"{DOMAIN}_overdue"
        self._attr_icon = "mdi:alert-circle-outline"

    async def async_added_to_hass(self) -> None:
        """Register listeners."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_TASK_MANAGER_UPDATED, self._handle_update
            )
        )
        # Re-evaluate automatically at midnight
        self.async_on_remove(
            async_track_time_change(
                self.hass, self._handle_time_update, hour=0, minute=0, second=0
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle state update from storage."""
        self.async_write_ha_state()

    @callback
    def _handle_time_update(self, now: Any) -> None:
        """Handle midnight time change."""
        self.async_write_ha_state()

    def _get_overdue_tasks(self) -> list[dict[str, Any]]:
        """Get list of overdue tasks."""
        today_str = dt_util.now().date().strftime("%Y-%m-%d")
        all_tasks = self._storage.data.get_all_tasks(include_external=True)
        overdue = []
        for t in all_tasks:
            if t.get("status") == "pending":
                due = t.get("due_date", "")
                if due and due < today_str:
                    overdue.append({
                        "id": t.get("id"),
                        "title": t.get("title", ""),
                        "due_date": due,
                        "due_time": t.get("due_time"),
                        "assignee": t.get("current_assignee"),
                        "priority": t.get("priority"),
                        "is_external": t.get("is_external", False),
                    })
        return overdue

    @property
    def is_on(self) -> bool:
        """Return True if any task is overdue."""
        return len(self._get_overdue_tasks()) > 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        overdue = self._get_overdue_tasks()
        all_tasks = self._storage.data.get_all_tasks(include_external=True)
        pending = [t for t in all_tasks if t.get("status") == "pending"]
        return {
            "overdue_tasks": overdue,
            "overdue_count": len(overdue),
            "pending_count": len(pending),
            "total_count": len(all_tasks),
        }


class TaskManagerPartsLowStockBinarySensor(BinarySensorEntity):
    """Binary sensor indicating if any spare parts require reordering."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, storage: TaskManagerStorage) -> None:
        """Initialize parts low stock binary sensor."""
        self._storage = storage
        self._attr_name = "Task Manager Parts Need Reorder"
        self._attr_unique_id = f"{DOMAIN}_parts_need_reorder"
        self._attr_icon = "mdi:package-variant-closed-alert"

    async def async_added_to_hass(self) -> None:
        """Register listeners."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_TASK_MANAGER_UPDATED, self._handle_update
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle state update from storage."""
        self.async_write_ha_state()

    def _get_low_stock_parts(self) -> list[dict[str, Any]]:
        """Get parts that are at or below reorder threshold."""
        return [p for p in self._storage.data.parts if is_part_low_stock(p)]

    @property
    def is_on(self) -> bool:
        """Return True if any part is low on stock."""
        return len(self._get_low_stock_parts()) > 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return low stock parts details."""
        low_parts = self._get_low_stock_parts()
        return {
            "low_stock_parts": [
                {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "stock": p.get("stock"),
                    "min_stock": p.get("min_stock"),
                    "storage_location": p.get("storage_location"),
                    "reorder_url": p.get("reorder_url"),
                }
                for p in low_parts
            ],
            "low_stock_count": len(low_parts),
            "total_parts": len(self._storage.data.parts),
        }


class TaskManagerTaskProblemBinarySensor(BinarySensorEntity):
    """Binary sensor representing whether an individual task is in a problem state (due/overdue)."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, storage: TaskManagerStorage, task_id: str) -> None:
        """Initialize task problem binary sensor."""
        self._storage = storage
        self._task_id = task_id
        task = storage.data.get_task(task_id) or {}
        title = task.get("title", "Task")
        self._attr_name = f"Task {title} Problem"
        self._attr_unique_id = f"{DOMAIN}_task_{task_id}_problem"
        safe_title = slugify(title) or task_id[:8]
        self.entity_id = f"binary_sensor.task_manager_{safe_title}_problem"

    async def async_added_to_hass(self) -> None:
        """Register update listener."""
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
    def is_on(self) -> bool:
        """Return True if task effective state is due (due or overdue)."""
        state, _ = self._storage.data.get_task_effective_state(self._task_id, self.hass)
        return state == TASK_STATE_DUE

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return task attributes."""
        _, attrs = self._storage.data.get_task_effective_state(self._task_id, self.hass)
        return attrs
