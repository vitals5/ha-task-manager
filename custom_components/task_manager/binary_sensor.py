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
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SIGNAL_TASK_MANAGER_UPDATED
from .storage import TaskManagerStorage

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Task Manager binary sensors."""
    storage: TaskManagerStorage = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([TaskManagerOverdueBinarySensor(storage)])


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
