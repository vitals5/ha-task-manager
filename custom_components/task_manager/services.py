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
    SERVICE_ADD_TASK,
    SERVICE_ADJUST_PART_STOCK,
    SERVICE_ASSIGN_TASK,
    SERVICE_AWARD_POINTS,
    SERVICE_COMPLETE_TASK,
    SERVICE_CREATE_TASK,
    SERVICE_DELETE_PART,
    SERVICE_DELETE_TASK,
    SERVICE_DELETE_TASK_HISTORY_ENTRY,
    SERVICE_DUPLICATE_TASK,
    SERVICE_MARK_AS_DONE,
    SERVICE_MOVE_TASK,
    SERVICE_PAUSE_TASK,
    SERVICE_RECORD_READING,
    SERVICE_REOPEN_TASK,
    SERVICE_RESET_TASK,
    SERVICE_RESUME_TASK,
    SERVICE_SAVE_PART,
    SERVICE_SET_LAST_DONE_DATE,
    SERVICE_SKIP_TASK,
    SERVICE_UPDATE_SUBTASK,
    SERVICE_UPDATE_TASK,
    SERVICE_UPDATE_THING,
    SERVICE_INCREMENT_THING,
)
from .storage import TaskManagerStorage

_LOGGER = logging.getLogger(__name__)

SCHEMA_CREATE_TASK = vol.Schema({
    vol.Required("title"): cv.string,
    vol.Optional("description"): cv.string,
    vol.Optional("notes"): cv.string,
    vol.Optional("due_date"): cv.string,
    vol.Optional("due_time"): cv.string,
    vol.Optional("priority", default=PRIORITY_NONE): vol.Any(vol.In(PRIORITIES), vol.Coerce(str)),
    vol.Optional("assignee"): cv.string,
    vol.Optional("assigned_person"): cv.string,
    vol.Optional("points"): cv.positive_int,
    vol.Optional("linked_thing_id"): cv.string,
    vol.Optional("tags"): vol.Any(cv.string, [cv.string]),
    vol.Optional("labels"): vol.Any(cv.string, [cv.string]),
    vol.Optional("reminders"): vol.Any(cv.string, [vol.Coerce(int)]),
    vol.Optional("subtasks"): list,
    vol.Optional("task_type"): cv.string,
    vol.Optional("reading_unit"): cv.string,
    vol.Optional("last_reading_value"): vol.Coerce(float),
    vol.Optional("registers"): list,
    vol.Optional("consumed_parts"): list,
    vol.Optional("on_complete_entity_id"): cv.string,
    vol.Optional("default_duration_minutes"): vol.Coerce(int),
    vol.Optional("default_cost"): vol.Coerce(float),
})

SCHEMA_COMPLETE_TASK = vol.Schema({
    vol.Optional("task_id"): cv.string,
    vol.Optional("entity_id"): cv.string,
    vol.Optional("task_title"): cv.string,
    vol.Optional("user_id"): cv.string,
    vol.Optional("tag"): cv.string,
    vol.Optional("cost"): vol.Coerce(float),
    vol.Optional("duration_minutes"): vol.Coerce(int),
    vol.Optional("notes"): cv.string,
    vol.Optional("completed_at"): cv.string,
    vol.Optional("reading_value"): vol.Coerce(float),
    vol.Optional("readings"): list,
    vol.Optional("consumed_parts"): list,
})

SCHEMA_SKIP_TASK = vol.Schema({
    vol.Optional("task_id"): cv.string,
    vol.Optional("entity_id"): cv.string,
    vol.Optional("task_title"): cv.string,
})

SCHEMA_RECORD_READING = vol.Schema({
    vol.Optional("task_id"): cv.string,
    vol.Optional("entity_id"): cv.string,
    vol.Optional("task_title"): cv.string,
    vol.Optional("reading_value"): vol.Coerce(float),
    vol.Optional("readings"): list,
    vol.Optional("notes"): cv.string,
    vol.Optional("completed_at"): cv.string,
    vol.Optional("user_id"): cv.string,
})

SCHEMA_DELETE_TASK_HISTORY_ENTRY = vol.Schema({
    vol.Optional("task_id"): cv.string,
    vol.Optional("entity_id"): cv.string,
    vol.Optional("task_title"): cv.string,
    vol.Optional("entry_index", default=-1): vol.Coerce(int),
    vol.Optional("completed_at"): cv.string,
})

SCHEMA_ADJUST_PART_STOCK = vol.Schema({
    vol.Required("part_id"): cv.string,
    vol.Optional("stock"): vol.Coerce(float),
    vol.Optional("delta"): vol.Coerce(float),
})

SCHEMA_SAVE_PART = vol.Schema({
    vol.Optional("id"): cv.string,
    vol.Required("name"): cv.string,
    vol.Optional("thing_id"): vol.Any(cv.string, None),
    vol.Optional("part_number", default=""): cv.string,
    vol.Optional("stock", default=0.0): vol.Coerce(float),
    vol.Optional("min_stock", default=1.0): vol.Coerce(float),
    vol.Optional("unit", default="pcs"): cv.string,
    vol.Optional("unit_price", default=0.0): vol.Coerce(float),
    vol.Optional("storage_location", default=""): cv.string,
    vol.Optional("reorder_url", default=""): cv.string,
    vol.Optional("notes", default=""): cv.string,
})

SCHEMA_DELETE_PART = vol.Schema({
    vol.Required("part_id"): cv.string,
})

SCHEMA_SET_LAST_DONE_DATE = vol.Schema({
    vol.Optional("task_id"): cv.string,
    vol.Optional("entity_id"): cv.string,
    vol.Optional("task_title"): cv.string,
    vol.Required("date"): cv.string,
})

SCHEMA_PAUSE_RESUME_TASK = vol.Schema({
    vol.Optional("task_id"): cv.string,
    vol.Optional("entity_id"): cv.string,
    vol.Optional("task_title"): cv.string,
})

SCHEMA_RESET_TASK = vol.Schema({
    vol.Optional("task_id"): cv.string,
    vol.Optional("entity_id"): cv.string,
    vol.Optional("task_title"): cv.string,
    vol.Optional("assigned_person"): cv.string,
    vol.Optional("user_id"): cv.string,
    vol.Optional("tag"): cv.string,
})

SCHEMA_DELETE_TASK = vol.Schema({
    vol.Required("task_id"): cv.string,
})

SCHEMA_ASSIGN_TASK = vol.Schema({
    vol.Optional("task_id"): cv.string,
    vol.Optional("task_title"): cv.string,
    vol.Optional("person"): cv.string,
    vol.Optional("assignee"): cv.string,
    vol.Optional("assigned_person"): cv.string,
})

SCHEMA_MOVE_TASK = vol.Schema({
    vol.Optional("task_id"): cv.string,
    vol.Optional("task_title"): cv.string,
    vol.Optional("target_provider", default="task_manager"): cv.string,
    vol.Optional("target_entity_id"): cv.string,
})

SCHEMA_DUPLICATE_TASK = vol.Schema({
    vol.Optional("task_id"): cv.string,
    vol.Optional("task_title"): cv.string,
})

SCHEMA_UPDATE_THING = vol.Schema({
    vol.Optional("thing_id"): cv.string,
    vol.Optional("entity_id"): vol.Any(cv.entity_id, [cv.entity_id], cv.string, [cv.string]),
    vol.Optional("thing_name"): cv.string,
    vol.Optional("name"): cv.string,
    vol.Optional("value"): vol.Any(vol.Coerce(float), None),
    vol.Optional("delta"): vol.Any(vol.Coerce(float), None),
    vol.Optional("amount"): vol.Any(vol.Coerce(float), None),
    vol.Optional("reset", default=False): cv.boolean,
    vol.Optional("target_value"): vol.Coerce(float),
    vol.Optional("threshold_value"): vol.Coerce(float),
    vol.Optional("threshold_operator"): vol.In([">=", "<=", "gte", "lte"]),
    vol.Optional("external_entity_id"): vol.Any(cv.entity_id, cv.string, None),
    vol.Optional("script_entity_id"): vol.Any(cv.entity_id, cv.string, None),
})

SCHEMA_INCREMENT_THING = vol.Schema({
    vol.Optional("thing_id"): cv.string,
    vol.Optional("entity_id"): vol.Any(cv.entity_id, [cv.entity_id], cv.string, [cv.string]),
    vol.Optional("thing_name"): cv.string,
    vol.Optional("name"): cv.string,
    vol.Optional("amount", default=1.0): vol.Coerce(float),
    vol.Optional("delta"): vol.Coerce(float),
    vol.Optional("step"): vol.Coerce(float),
})

SCHEMA_AWARD_POINTS = vol.Schema({
    vol.Required("user_id"): cv.string,
    vol.Required("points"): cv.positive_int,
    vol.Optional("reason", default=""): cv.string,
})


def resolve_task_id(call_data: dict[str, Any], storage: TaskManagerStorage, hass: HomeAssistant) -> str | None:
    """Resolve a target task ID from task_id, entity_id, or task_title."""
    task_id = call_data.get("task_id")
    if task_id:
        return str(task_id)

    entity_id = call_data.get("entity_id")
    if entity_id:
        try:
            from homeassistant.helpers import entity_registry as er
            ent_reg = er.async_get(hass)
            entry = ent_reg.async_get(entity_id)
            if entry and isinstance(getattr(entry, "unique_id", None), str):
                for t in storage.data.tasks:
                    if entry.unique_id in (
                        f"{DOMAIN}_task_{t['id']}_status",
                        f"{DOMAIN}_task_{t['id']}_complete",
                    ):
                        return t["id"]
        except Exception:
            pass

        from homeassistant.util import slugify
        for t in storage.data.get_all_tasks(include_external=True):
            safe = str(slugify(t.get("title", "")) or "")
            if safe and safe in entity_id:
                return t["id"]
            if t.get("id") == entity_id:
                return t["id"]

    task_title = call_data.get("task_title")
    if task_title:
        for t in storage.data.get_all_tasks(include_external=True):
            if t.get("title", "").strip().lower() == task_title.strip().lower():
                return t["id"]

    return None


def resolve_thing_ids(call_data: dict[str, Any], storage: TaskManagerStorage, hass: HomeAssistant) -> list[str]:
    """Resolve target Thing IDs from thing_id, entity_id, or name/thing_name."""
    thing_ids: list[str] = []

    # 1. Direct thing_id (single or list)
    raw_thing_id = call_data.get("thing_id")
    if raw_thing_id:
        if isinstance(raw_thing_id, list):
            thing_ids.extend([str(x) for x in raw_thing_id if x])
        else:
            thing_ids.append(str(raw_thing_id))

    # 2. Entity IDs (single or list)
    raw_entity_id = call_data.get("entity_id")
    entity_ids: list[str] = []
    if raw_entity_id:
        if isinstance(raw_entity_id, list):
            entity_ids.extend([str(x) for x in raw_entity_id if x])
        else:
            entity_ids.append(str(raw_entity_id))

    for entity_id in entity_ids:
        found_id: str | None = None
        # Try entity registry unique_id
        try:
            from homeassistant.helpers import entity_registry as er
            ent_reg = er.async_get(hass)
            entry = ent_reg.async_get(entity_id)
            if entry and isinstance(getattr(entry, "unique_id", None), str):
                uid = entry.unique_id
                prefix = f"{DOMAIN}_thing_"
                if uid.startswith(prefix):
                    candidate = uid[len(prefix):]
                    if storage.data.get_thing(candidate):
                        found_id = candidate
                if not found_id:
                    for th in storage.data.things:
                        if uid in (f"{DOMAIN}_thing_{th['id']}", th["id"]):
                            found_id = th["id"]
                            break
        except Exception:
            pass

        # Try state attributes (e.g. sensor.task_manager_thing_xxx has attribute thing_id)
        if not found_id:
            try:
                st = hass.states.get(entity_id)
                if st and st.attributes.get("thing_id"):
                    attr_th_id = str(st.attributes["thing_id"])
                    if storage.data.get_thing(attr_th_id):
                        found_id = attr_th_id
            except Exception:
                pass

        # Fallback to direct ID or slug match
        if not found_id:
            from homeassistant.util import slugify
            for th in storage.data.things:
                if th["id"] == entity_id:
                    found_id = th["id"]
                    break
                safe = str(slugify(th.get("name", "")) or "")
                if safe and (safe in entity_id or entity_id.endswith(safe)):
                    found_id = th["id"]
                    break

        if found_id and found_id not in thing_ids:
            thing_ids.append(found_id)

    # 3. Fallback to thing_name / name
    name = call_data.get("thing_name") or call_data.get("name")
    if name and not thing_ids:
        name_lower = str(name).strip().lower()
        for th in storage.data.things:
            if th.get("name", "").strip().lower() == name_lower:
                thing_ids.append(th["id"])
                break

    return thing_ids


def async_register_services(hass: HomeAssistant, storage: TaskManagerStorage) -> None:
    """Register all integration action services."""

    async def handle_create_task(call: ServiceCall) -> None:
        """Handle creating a task via service."""
        data = dict(call.data)
        if "notes" in data and "description" not in data:
            data["description"] = data.pop("notes")
        assignee = data.pop("assigned_person", None) or data.pop("assignee", None)
        if assignee:
            data["assignees"] = [assignee]
            data["current_assignee"] = assignee
        tags = data.pop("tags", None) or data.pop("labels", None)
        if tags is not None:
            if isinstance(tags, str):
                data["labels"] = [t.strip() for t in tags.split(",") if t.strip()]
            else:
                data["labels"] = list(tags)
        reminders = data.pop("reminders", None)
        if reminders is not None:
            if isinstance(reminders, str):
                rems = []
                for r in reminders.split(","):
                    try:
                        rems.append(int(r.strip()))
                    except ValueError:
                        pass
                data["reminders"] = rems
            elif isinstance(reminders, list):
                data["reminders"] = [int(r) for r in reminders]

        prio = str(data.get("priority", PRIORITY_NONE)).lower()
        if prio in ("1", "low"):
            prio = "p4"
        elif prio in ("2", "medium"):
            prio = "p3"
        elif prio in ("3", "high"):
            prio = "p2"
        elif prio in ("urgent", "p1"):
            prio = "p1"
        data["priority"] = prio

        await storage.async_save_task(data)

    async def handle_complete_task(call: ServiceCall) -> None:
        """Handle completing a task via service."""
        user_id = call.data.get("user_id")
        tag = call.data.get("tag")
        cost = call.data.get("cost")
        duration_minutes = call.data.get("duration_minutes")
        notes = call.data.get("notes")
        completed_at = call.data.get("completed_at")
        reading_value = call.data.get("reading_value")
        readings = call.data.get("readings")
        consumed_parts = call.data.get("consumed_parts")

        kwargs: dict[str, Any] = {"user_id": user_id}
        if cost is not None:
            kwargs["cost"] = cost
        if duration_minutes is not None:
            kwargs["duration_minutes"] = duration_minutes
        if notes is not None:
            kwargs["notes"] = notes
        if completed_at is not None:
            kwargs["completed_at"] = completed_at
        if reading_value is not None:
            kwargs["reading_value"] = reading_value
        if readings is not None:
            kwargs["readings"] = readings
        if consumed_parts is not None:
            kwargs["consumed_parts"] = consumed_parts

        if tag:
            all_tasks = storage.data.get_all_tasks(include_external=True)
            for t in all_tasks:
                if t.get("status") == "pending" and (tag in t.get("labels", []) or tag in t.get("tags", [])):
                    await storage.async_complete_task(t["id"], **kwargs)
            return

        target_id = resolve_task_id(call.data, storage, hass)
        if target_id:
            await storage.async_complete_task(target_id, **kwargs)
        else:
            _LOGGER.warning("Task Manager: Task '%s' not found to complete", call.data.get("task_id") or call.data.get("task_title") or call.data.get("entity_id"))

    async def handle_skip_task(call: ServiceCall) -> None:
        """Handle skipping the current recurrence of a task via service."""
        target_id = resolve_task_id(call.data, storage, hass)
        if target_id:
            await storage.async_skip_task(target_id)
        else:
            _LOGGER.warning("Task Manager: Task '%s' not found to skip", call.data.get("task_id") or call.data.get("task_title") or call.data.get("entity_id"))

    async def handle_record_reading(call: ServiceCall) -> None:
        """Handle recording a meter/utility reading for a task via service."""
        target_id = resolve_task_id(call.data, storage, hass)
        reading_value = call.data.get("reading_value")
        readings = call.data.get("readings")
        notes = call.data.get("notes")
        completed_at = call.data.get("completed_at")
        user_id = call.data.get("user_id")

        if target_id:
            await storage.async_record_reading(
                task_id=target_id,
                reading_value=reading_value,
                readings=readings,
                notes=notes,
                completed_at=completed_at,
                user_id=user_id,
            )
        else:
            _LOGGER.warning("Task Manager: Task '%s' not found to record reading", call.data.get("task_id") or call.data.get("task_title") or call.data.get("entity_id"))

    async def handle_delete_task_history_entry(call: ServiceCall) -> None:
        """Handle deleting a task history entry via service."""
        target_id = resolve_task_id(call.data, storage, hass)
        entry_index = call.data.get("entry_index")
        completed_at = call.data.get("completed_at")
        if target_id:
            await storage.async_delete_task_history_entry(
                task_id=target_id,
                entry_index=entry_index,
                completed_at=completed_at,
            )
        else:
            _LOGGER.warning("Task Manager: Task '%s' not found to delete history entry", call.data.get("task_id") or call.data.get("task_title") or call.data.get("entity_id"))

    async def handle_adjust_part_stock(call: ServiceCall) -> None:
        """Handle adjusting or setting part stock via service."""
        part_id = call.data["part_id"]
        stock = call.data.get("stock")
        delta = call.data.get("delta")
        await storage.async_adjust_part_stock(part_id, delta=delta, stock=stock)

    async def handle_save_part(call: ServiceCall) -> None:
        """Handle creating or updating part via service."""
        part_data = dict(call.data)
        if part_data.get("id"):
            await storage.async_update_part(part_data["id"], part_data)
        else:
            await storage.async_create_part(part_data)

    async def handle_delete_part(call: ServiceCall) -> None:
        """Handle deleting part via service."""
        part_id = call.data["part_id"]
        await storage.async_delete_part(part_id)

    async def handle_set_last_done_date(call: ServiceCall) -> None:
        """Handle setting the last completion date explicitly via service."""
        target_id = resolve_task_id(call.data, storage, hass)
        date_str = call.data["date"]
        if target_id:
            await storage.async_set_last_done_date(target_id, date_str)
        else:
            _LOGGER.warning("Task Manager: Task '%s' not found to set last done date", call.data.get("task_id") or call.data.get("task_title") or call.data.get("entity_id"))

    async def handle_pause_task(call: ServiceCall) -> None:
        """Handle pausing a task via service."""
        target_id = resolve_task_id(call.data, storage, hass)
        if target_id:
            await storage.async_pause_task(target_id)
        else:
            _LOGGER.warning("Task Manager: Task '%s' not found to pause", call.data.get("task_id") or call.data.get("task_title") or call.data.get("entity_id"))

    async def handle_resume_task(call: ServiceCall) -> None:
        """Handle resuming a paused task via service."""
        target_id = resolve_task_id(call.data, storage, hass)
        if target_id:
            await storage.async_resume_task(target_id)
        else:
            _LOGGER.warning("Task Manager: Task '%s' not found to resume", call.data.get("task_id") or call.data.get("task_title") or call.data.get("entity_id"))

    async def handle_reset_task(call: ServiceCall) -> None:
        """Handle resetting/reopening a task via service."""
        assigned_person = call.data.get("assigned_person") or call.data.get("user_id")
        tag = call.data.get("tag")

        if assigned_person or tag:
            all_tasks = storage.data.get_all_tasks(include_external=True)
            for t in all_tasks:
                if t.get("status") == "completed":
                    matches_person = not assigned_person or (
                        t.get("current_assignee") == assigned_person or assigned_person in t.get("assignees", [])
                    )
                    matches_tag = not tag or (tag in t.get("labels", []) or tag in t.get("tags", []))
                    if matches_person and matches_tag:
                        await storage.async_reset_task(t["id"])
            return

        target_id = resolve_task_id(call.data, storage, hass)
        if target_id:
            await storage.async_reset_task(target_id)

    async def handle_assign_task(call: ServiceCall) -> None:
        """Handle assigning a task to a person."""
        target_id = resolve_task_id(call.data, storage, hass)
        person = call.data.get("person") or call.data.get("assignee") or call.data.get("assigned_person")

        all_tasks = storage.data.get_all_tasks(include_external=True)
        if target_id:
            task = next((t for t in all_tasks if t["id"] == target_id), None)
            if task:
                task_copy = dict(task)
                task_copy["current_assignee"] = person
                if person and person not in task_copy.get("assignees", []):
                    task_copy["assignees"] = list(task_copy.get("assignees", [])) + [person]
                await storage.async_save_task(task_copy)
        else:
            _LOGGER.warning("Task Manager: Task not found to assign")

    async def handle_duplicate_task(call: ServiceCall) -> None:
        """Handle duplicating a task via service."""
        target_id = resolve_task_id(call.data, storage, hass)
        if target_id:
            await storage.async_duplicate_task(target_id)
        else:
            _LOGGER.warning("Task Manager: Task not found to duplicate")

    async def handle_move_task(call: ServiceCall) -> None:
        """Handle moving a task to another provider or list via service."""
        target_id = resolve_task_id(call.data, storage, hass)
        target_provider = call.data.get("target_provider") or call.data.get("target_entity_id") or "task_manager"

        if target_id:
            await storage.async_move_task(target_id, target_provider)
        else:
            _LOGGER.warning("Task Manager: Task not found to move")

    async def handle_delete_task(call: ServiceCall) -> None:
        """Handle deleting a task via service."""
        target_id = resolve_task_id(call.data, storage, hass)
        if target_id and storage.data.delete_task(target_id):
            await storage.async_save()

    async def handle_update_thing(call: ServiceCall) -> None:
        """Handle updating or resetting a Thing via service."""
        target_ids = resolve_thing_ids(call.data, storage, hass)
        if not target_ids and "thing_id" in call.data:
            target_ids = [str(call.data["thing_id"])]

        if not target_ids:
            _LOGGER.warning("Task Manager: No target Thing found to update (call data: %s)", call.data)
            return

        prop_updates = {}
        for k in ("target_value", "threshold_value", "threshold_operator", "external_entity_id", "script_entity_id"):
            if k in call.data:
                prop_updates[k] = call.data[k]

        delta = call.data.get("delta")
        if delta is None and "amount" in call.data:
            delta = call.data.get("amount")

        updated = False
        for thing_id in target_ids:
            if prop_updates:
                storage.data.update_thing(thing_id, prop_updates)
                updated = True

            if any(k in call.data for k in ("value", "delta", "amount", "reset")):
                res = storage.data.update_thing_value(
                    thing_id=thing_id,
                    value=call.data.get("value"),
                    delta=delta,
                    reset=call.data.get("reset", False),
                )
                if res:
                    updated = True

        if updated:
            await storage.async_save()

    async def handle_increment_thing(call: ServiceCall) -> None:
        """Handle incrementing a Thing's counter/meter via service."""
        target_ids = resolve_thing_ids(call.data, storage, hass)
        if not target_ids:
            _LOGGER.warning("Task Manager: No target Thing found to increment (call data: %s)", call.data)
            return

        delta = 1.0
        if "delta" in call.data and call.data["delta"] is not None:
            delta = float(call.data["delta"])
        elif "amount" in call.data and call.data["amount"] is not None:
            delta = float(call.data["amount"])
        elif "step" in call.data and call.data["step"] is not None:
            delta = float(call.data["step"])

        updated = False
        for thing_id in target_ids:
            res = storage.data.update_thing_value(thing_id=thing_id, delta=delta)
            if res:
                updated = True

        if updated:
            await storage.async_save()

    async def handle_award_points(call: ServiceCall) -> None:
        """Handle awarding points to a user via service."""
        user_id = call.data["user_id"]
        points = call.data["points"]
        reason = call.data.get("reason", "")
        storage.data.award_points(user_id, points, reason)
        await storage.async_save()

    hass.services.async_register(DOMAIN, SERVICE_CREATE_TASK, handle_create_task, schema=SCHEMA_CREATE_TASK)
    hass.services.async_register(DOMAIN, SERVICE_ADD_TASK, handle_create_task, schema=SCHEMA_CREATE_TASK)
    hass.services.async_register(DOMAIN, SERVICE_COMPLETE_TASK, handle_complete_task, schema=SCHEMA_COMPLETE_TASK)
    hass.services.async_register(DOMAIN, SERVICE_SKIP_TASK, handle_skip_task, schema=SCHEMA_SKIP_TASK)
    hass.services.async_register(DOMAIN, SERVICE_RECORD_READING, handle_record_reading, schema=SCHEMA_RECORD_READING)
    hass.services.async_register(DOMAIN, SERVICE_DELETE_TASK_HISTORY_ENTRY, handle_delete_task_history_entry, schema=SCHEMA_DELETE_TASK_HISTORY_ENTRY)
    hass.services.async_register(DOMAIN, SERVICE_ADJUST_PART_STOCK, handle_adjust_part_stock, schema=SCHEMA_ADJUST_PART_STOCK)
    hass.services.async_register(DOMAIN, SERVICE_SAVE_PART, handle_save_part, schema=SCHEMA_SAVE_PART)
    hass.services.async_register(DOMAIN, SERVICE_DELETE_PART, handle_delete_part, schema=SCHEMA_DELETE_PART)
    hass.services.async_register(DOMAIN, SERVICE_MARK_AS_DONE, handle_complete_task, schema=SCHEMA_COMPLETE_TASK)
    hass.services.async_register(DOMAIN, SERVICE_SET_LAST_DONE_DATE, handle_set_last_done_date, schema=SCHEMA_SET_LAST_DONE_DATE)
    hass.services.async_register(DOMAIN, SERVICE_PAUSE_TASK, handle_pause_task, schema=SCHEMA_PAUSE_RESUME_TASK)
    hass.services.async_register(DOMAIN, SERVICE_RESUME_TASK, handle_resume_task, schema=SCHEMA_PAUSE_RESUME_TASK)
    hass.services.async_register(DOMAIN, SERVICE_RESET_TASK, handle_reset_task, schema=SCHEMA_RESET_TASK)
    hass.services.async_register(DOMAIN, SERVICE_REOPEN_TASK, handle_reset_task, schema=SCHEMA_RESET_TASK)
    hass.services.async_register(DOMAIN, SERVICE_ASSIGN_TASK, handle_assign_task, schema=SCHEMA_ASSIGN_TASK)
    hass.services.async_register(DOMAIN, SERVICE_MOVE_TASK, handle_move_task, schema=SCHEMA_MOVE_TASK)
    hass.services.async_register(DOMAIN, SERVICE_DUPLICATE_TASK, handle_duplicate_task, schema=SCHEMA_DUPLICATE_TASK)
    hass.services.async_register(DOMAIN, SERVICE_DELETE_TASK, handle_delete_task, schema=SCHEMA_DELETE_TASK)
    hass.services.async_register(DOMAIN, SERVICE_UPDATE_THING, handle_update_thing, schema=SCHEMA_UPDATE_THING)
    hass.services.async_register(DOMAIN, SERVICE_INCREMENT_THING, handle_increment_thing, schema=SCHEMA_INCREMENT_THING)
    hass.services.async_register(DOMAIN, SERVICE_AWARD_POINTS, handle_award_points, schema=SCHEMA_AWARD_POINTS)


def async_unregister_services(hass: HomeAssistant) -> None:
    """Unregister all integration services."""
    services = [
        SERVICE_CREATE_TASK,
        SERVICE_ADD_TASK,
        SERVICE_COMPLETE_TASK,
        SERVICE_SKIP_TASK,
        SERVICE_RECORD_READING,
        SERVICE_DELETE_TASK_HISTORY_ENTRY,
        SERVICE_ADJUST_PART_STOCK,
        SERVICE_SAVE_PART,
        SERVICE_DELETE_PART,
        SERVICE_MARK_AS_DONE,
        SERVICE_SET_LAST_DONE_DATE,
        SERVICE_PAUSE_TASK,
        SERVICE_RESUME_TASK,
        SERVICE_RESET_TASK,
        SERVICE_REOPEN_TASK,
        SERVICE_ASSIGN_TASK,
        SERVICE_MOVE_TASK,
        SERVICE_DUPLICATE_TASK,
        SERVICE_DELETE_TASK,
        SERVICE_UPDATE_THING,
        SERVICE_INCREMENT_THING,
        SERVICE_AWARD_POINTS,
    ]
    for s in services:
        hass.services.async_remove(DOMAIN, s)
