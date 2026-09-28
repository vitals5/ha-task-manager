"""Button platform for Task Manager integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .const import DOMAIN, SIGNAL_TASK_MANAGER_UPDATED
from .storage import TaskManagerStorage

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Task Manager button platform."""
    storage: TaskManagerStorage = hass.data[DOMAIN][entry.entry_id]

    active_buttons: dict[str, TaskManagerTaskButton] = {}
    active_skip_buttons: dict[str, TaskManagerTaskSkipButton] = {}

    @callback
    def update_dynamic_buttons() -> None:
        """Add new buttons or remove deleted buttons for tasks."""
        new_buttons: list[ButtonEntity] = []
        current_task_ids = {t["id"] for t in storage.data.tasks}

        # 1. Add new task buttons (Complete & Skip)
        for task in storage.data.tasks:
            t_id = task["id"]
            if t_id not in active_buttons:
                btn = TaskManagerTaskButton(storage, t_id)
                active_buttons[t_id] = btn
                new_buttons.append(btn)

            if t_id not in active_skip_buttons:
                skip_btn = TaskManagerTaskSkipButton(storage, t_id)
                active_skip_buttons[t_id] = skip_btn
                new_buttons.append(skip_btn)

        # 2. Remove deleted task buttons
        for t_id in list(active_buttons.keys()):
            if t_id not in current_task_ids:
                btn = active_buttons.pop(t_id)
                hass.async_create_task(btn.async_remove())
                try:
                    ent_reg = er.async_get(hass)
                    reg_id = ent_reg.async_get_entity_id(
                        "button", DOMAIN, f"{DOMAIN}_task_{t_id}_complete"
                    )
                    if reg_id:
                        ent_reg.async_remove(reg_id)
                except Exception as err:
                    _LOGGER.debug("Error removing button from registry: %s", err)

        for t_id in list(active_skip_buttons.keys()):
            if t_id not in current_task_ids:
                skip_btn = active_skip_buttons.pop(t_id)
                hass.async_create_task(skip_btn.async_remove())
                try:
                    ent_reg = er.async_get(hass)
                    reg_id = ent_reg.async_get_entity_id(
                        "button", DOMAIN, f"{DOMAIN}_task_{t_id}_skip"
                    )
                    if reg_id:
                        ent_reg.async_remove(reg_id)
                except Exception as err:
                    _LOGGER.debug("Error removing skip button from registry: %s", err)

        if new_buttons:
            async_add_entities(new_buttons)

    # Initial registration
    update_dynamic_buttons()

    # Listen for updates
    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_TASK_MANAGER_UPDATED, update_dynamic_buttons)
    )


class TaskManagerTaskButton(ButtonEntity):
    """Button entity to quickly complete/mark a task as done."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:checkbox-marked-circle-outline"

    def __init__(self, storage: TaskManagerStorage, task_id: str) -> None:
        """Initialize task complete button."""
        self._storage = storage
        self._task_id = task_id
        task = self._storage.data.get_task(task_id) or {}
        title = task.get("title", "Task")
        self._attr_name = f"{title} Complete"
        self._attr_unique_id = f"{DOMAIN}_task_{task_id}_complete"
        safe_title = slugify(title) or task_id[:8]
        self.entity_id = f"button.task_manager_{safe_title}_mark_as_done"

    @property
    def available(self) -> bool:
        """Return True if task exists and is active."""
        task = self._storage.data.get_task(self._task_id)
        return bool(task)

    async def async_press(self) -> None:
        """Handle button press to complete the task."""
        await self._storage.async_complete_task(self._task_id)


class TaskManagerTaskSkipButton(ButtonEntity):
    """Button entity to quickly skip the current recurrence of a task."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:skip-next-circle-outline"

    def __init__(self, storage: TaskManagerStorage, task_id: str) -> None:
        """Initialize task skip button."""
        self._storage = storage
        self._task_id = task_id
        task = self._storage.data.get_task(task_id) or {}
        title = task.get("title", "Task")
        self._attr_name = f"{title} Skip"
        self._attr_unique_id = f"{DOMAIN}_task_{task_id}_skip"
        safe_title = slugify(title) or task_id[:8]
        self.entity_id = f"button.task_manager_{safe_title}_skip"

    @property
    def available(self) -> bool:
        """Return True if task exists and is active."""
        task = self._storage.data.get_task(self._task_id)
        return bool(task)

    async def async_press(self) -> None:
        """Handle button press to skip the task."""
        await self._storage.async_skip_task(self._task_id)
