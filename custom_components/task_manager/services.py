"""Service call handlers for Task Manager."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    PRIORITIES,
    PRIORITY_NONE,
    SERVICE_AWARD_POINTS,
    SERVICE_COMPLETE_TASK,
    SERVICE_CREATE_TASK,
    SERVICE_DELETE_TASK,
    SERVICE_RESET_TASK,
    SERVICE_UPDATE_SUBTASK,
    SERVICE_UPDATE_TASK,
    SERVICE_UPDATE_THING,
)
from .storage import TaskManagerStorage

_LOGGER = logging.getLogger(__name__)

SCHEMA_CREATE_TASK = vol.Schema({
    vol.Required("title"): cv.string,
    vol.Optional("description", default=""): cv.string,
    vol.Optional("due_date"): cv.string,
    vol.Optional("priority", default=PRIORITY_NONE): vol.In(PRIORITIES),
    vol.Optional("assignee"): cv.string,
    vol.Optional("points"): cv.positive_int,
    vol.Optional("linked_thing_id"): cv.string,
})

SCHEMA_COMPLETE_TASK = vol.Schema({
    vol.Optional("task_id"): cv.string,
    vol.Optional("task_title"): cv.string,
    vol.Optional("user_id"): cv.string,
})

SCHEMA_RESET_TASK = vol.Schema({
    vol.Optional("task_id"): cv.string,
    vol.Optional("task_title"): cv.string,
})

SCHEMA_DELETE_TASK = vol.Schema({
    vol.Required("task_id"): cv.string,
})

SCHEMA_UPDATE_THING = vol.Schema({
    vol.Required("thing_id"): cv.string,
    vol.Optional("value"): vol.Any(vol.Coerce(float), None),
    vol.Optional("delta"): vol.Any(vol.Coerce(float), None),
    vol.Optional("reset", default=False): cv.boolean,
    vol.Optional("target_value"): vol.Coerce(float),
    vol.Optional("threshold_value"): vol.Coerce(float),
    vol.Optional("threshold_operator"): vol.In([">=", "<=", "gte", "lte"]),
    vol.Optional("external_entity_id"): vol.Any(cv.entity_id, None),
})

SCHEMA_AWARD_POINTS = vol.Schema({
    vol.Required("user_id"): cv.string,
    vol.Required("points"): cv.positive_int,
    vol.Optional("reason", default=""): cv.string,
})


def async_register_services(hass: HomeAssistant, storage: TaskManagerStorage) -> None:
    """Register all integration action services."""

    async def handle_create_task(call: ServiceCall) -> None:
        """Handle creating a task via service."""
        data = dict(call.data)
        assignee = data.pop("assignee", None)
        if assignee:
            data["assignees"] = [assignee]
            data["current_assignee"] = assignee
        storage.data.create_task(data)
        await storage.async_save()

    async def handle_complete_task(call: ServiceCall) -> None:
        """Handle completing a task via service."""
        task_id = call.data.get("task_id")
        task_title = call.data.get("task_title")
        user_id = call.data.get("user_id")

        target_id = task_id
        if not target_id and task_title:
            for t in storage.data.tasks:
                if t.get("title", "").strip().lower() == task_title.strip().lower() and t.get("status") == "pending":
                    target_id = t["id"]
                    break

        if target_id:
            storage.data.complete_task(target_id, user_id=user_id)
            await storage.async_save()
        else:
            _LOGGER.warning("Task Manager: Task '%s' not found to complete", task_id or task_title)

    async def handle_reset_task(call: ServiceCall) -> None:
        """Handle resetting a task via service."""
        task_id = call.data.get("task_id")
        task_title = call.data.get("task_title")

        target_id = task_id
        if not target_id and task_title:
            for t in storage.data.tasks:
                if t.get("title", "").strip().lower() == task_title.strip().lower():
                    target_id = t["id"]
                    break

        if target_id:
            storage.data.reset_task(target_id)
            await storage.async_save()

    async def handle_delete_task(call: ServiceCall) -> None:
        """Handle deleting a task via service."""
        task_id = call.data["task_id"]
        if storage.data.delete_task(task_id):
            await storage.async_save()

    async def handle_update_thing(call: ServiceCall) -> None:
        """Handle updating or resetting a Thing via service."""
        thing_id = call.data["thing_id"]
        prop_updates = {}
        for k in ("target_value", "threshold_value", "threshold_operator", "external_entity_id"):
            if k in call.data:
                prop_updates[k] = call.data[k]
        if prop_updates:
            storage.data.update_thing(thing_id, prop_updates)

        if any(k in call.data for k in ("value", "delta", "reset")):
            storage.data.update_thing_value(
                thing_id=thing_id,
                value=call.data.get("value"),
                delta=call.data.get("delta"),
                reset=call.data.get("reset", False),
            )
        await storage.async_save()

    async def handle_award_points(call: ServiceCall) -> None:
        """Handle awarding points to a user via service."""
        user_id = call.data["user_id"]
        points = call.data["points"]
        reason = call.data.get("reason", "")
        storage.data.award_points(user_id, points, reason)
        await storage.async_save()

    hass.services.async_register(DOMAIN, SERVICE_CREATE_TASK, handle_create_task, schema=SCHEMA_CREATE_TASK)
    hass.services.async_register(DOMAIN, SERVICE_COMPLETE_TASK, handle_complete_task, schema=SCHEMA_COMPLETE_TASK)
    hass.services.async_register(DOMAIN, SERVICE_RESET_TASK, handle_reset_task, schema=SCHEMA_RESET_TASK)
    hass.services.async_register(DOMAIN, SERVICE_DELETE_TASK, handle_delete_task, schema=SCHEMA_DELETE_TASK)
    hass.services.async_register(DOMAIN, SERVICE_UPDATE_THING, handle_update_thing, schema=SCHEMA_UPDATE_THING)
    hass.services.async_register(DOMAIN, SERVICE_AWARD_POINTS, handle_award_points, schema=SCHEMA_AWARD_POINTS)


def async_unregister_services(hass: HomeAssistant) -> None:
    """Unregister all integration services."""
    services = [
        SERVICE_CREATE_TASK,
        SERVICE_COMPLETE_TASK,
        SERVICE_RESET_TASK,
        SERVICE_DELETE_TASK,
        SERVICE_UPDATE_THING,
        SERVICE_AWARD_POINTS,
    ]
    for s in services:
        hass.services.async_remove(DOMAIN, s)
