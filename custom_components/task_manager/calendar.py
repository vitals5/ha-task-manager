"""Calendar platform for Task Manager integration."""
from __future__ import annotations

from datetime import date, datetime, timedelta
import logging
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    SIGNAL_TASK_MANAGER_UPDATED,
    RECURRENCE_NONE,
)
from .storage import TaskManagerStorage, calculate_next_due_date

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Task Manager calendar entities."""
    storage: TaskManagerStorage = hass.data[DOMAIN][entry.entry_id]

    entities = [
        TaskManagerCalendarEntity(storage, "all", "Task Manager Chores"),
    ]

    for user in storage.data.users:
        entities.append(
            TaskManagerCalendarEntity(storage, user["id"], f"Task Manager ({user['name']})")
        )

    async_add_entities(entities)


def _task_to_event(task: dict[str, Any], target_date: date | None = None) -> CalendarEvent | None:
    """Convert a task dictionary to a Home Assistant CalendarEvent."""
    due_date_str = task.get("due_date")
    if not due_date_str and not target_date:
        return None

    try:
        d = target_date if target_date else date.fromisoformat(due_date_str)
    except (ValueError, TypeError):
        return None

    due_time_str = task.get("due_time")
    timed = bool(due_time_str)

    tz = dt_util.DEFAULT_TIME_ZONE
    title = task.get("title", "Task")
    description = task.get("description", "") or ""

    if timed:
        try:
            parts = due_time_str.split(":")
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
            start_dt = datetime(d.year, d.month, d.day, hour, minute, tzinfo=tz)
            end_dt = start_dt + timedelta(minutes=30)
            return CalendarEvent(
                start=start_dt,
                end=end_dt,
                summary=title,
                description=description,
                uid=f"{task.get('id', '')}_{d.isoformat()}",
            )
        except Exception:
            pass

    start_d = d
    end_d = d + timedelta(days=1)
    return CalendarEvent(
        start=start_d,
        end=end_d,
        summary=title,
        description=description,
        uid=f"{task.get('id', '')}_{d.isoformat()}",
    )


def _expand_task_occurrences(
    task: dict[str, Any], range_start: datetime, range_end: datetime
) -> list[CalendarEvent]:
    """Expand regular or recurring task into CalendarEvents within range."""
    due_date_str = task.get("due_date")
    if not due_date_str:
        return []

    try:
        base_date = date.fromisoformat(due_date_str)
    except (ValueError, TypeError):
        return []

    rec = task.get("recurrence", {})
    is_recurring = rec.get("enabled", False) and rec.get("type", RECURRENCE_NONE) != RECURRENCE_NONE

    start_d = range_start.date() if isinstance(range_start, datetime) else range_start
    end_d = range_end.date() if isinstance(range_end, datetime) else range_end

    events: list[CalendarEvent] = []

    if not is_recurring:
        if start_d <= base_date <= end_d:
            evt = _task_to_event(task, base_date)
            if evt:
                events.append(evt)
        return events

    # Recurring task: project occurrences across the window
    curr_date_str = due_date_str
    curr_date = base_date
    max_iterations = 100

    # Advance until we enter window or exceed max iterations
    while curr_date < start_d and max_iterations > 0:
        max_iterations -= 1
        next_str = calculate_next_due_date(curr_date_str, rec)
        if next_str <= curr_date_str:
            break
        curr_date_str = next_str
        try:
            curr_date = date.fromisoformat(curr_date_str)
        except Exception:
            break

    # Collect occurrences inside the window
    while curr_date <= end_d and max_iterations > 0:
        max_iterations -= 1
        if curr_date >= start_d:
            evt = _task_to_event(task, curr_date)
            if evt:
                events.append(evt)
        next_str = calculate_next_due_date(curr_date_str, rec)
        if next_str <= curr_date_str:
            break
        curr_date_str = next_str
        try:
            curr_date = date.fromisoformat(curr_date_str)
        except Exception:
            break

    return events


class TaskManagerCalendarEntity(CalendarEntity):
    """Calendar entity for Task Manager chores and tasks."""

    _attr_has_entity_name = True

    def __init__(self, storage: TaskManagerStorage, user_id: str, name: str) -> None:
        """Initialize calendar entity."""
        self._storage = storage
        self._user_id = user_id
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_calendar_{user_id}"

    async def async_added_to_hass(self) -> None:
        """Register dispatcher listener."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_TASK_MANAGER_UPDATED, self._handle_update
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle data updates."""
        self.async_write_ha_state()

    def _get_applicable_tasks(self) -> list[dict[str, Any]]:
        """Get all pending tasks applicable to this calendar."""
        all_tasks = self._storage.get_all_tasks(include_external=True)
        tasks: list[dict[str, Any]] = []
        for t in all_tasks:
            # Exclude non-recurring completed tasks
            rec = t.get("recurrence", {})
            is_rec = rec.get("enabled", False) and rec.get("type", RECURRENCE_NONE) != RECURRENCE_NONE
            if t.get("status") == "completed" and not is_rec:
                continue

            if not t.get("due_date"):
                continue

            if self._user_id != "all":
                cur_assignee = t.get("current_assignee")
                assignees = t.get("assignees", [])
                if cur_assignee != self._user_id and self._user_id not in assignees:
                    continue

            tasks.append(t)
        return tasks

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming calendar event."""
        now = dt_util.now()
        horizon = now + timedelta(days=365)
        best_evt: CalendarEvent | None = None
        best_time: datetime | None = None

        for task in self._get_applicable_tasks():
            events = _expand_task_occurrences(task, now, horizon)
            for evt in events:
                if isinstance(evt.end, datetime):
                    if evt.end < now:
                        continue
                    evt_time = evt.start
                else:
                    if evt.end <= now.date():
                        continue
                    evt_time = datetime.combine(evt.start, datetime.min.time(), tzinfo=now.tzinfo)

                if best_time is None or evt_time < best_time:
                    best_time = evt_time
                    best_evt = evt

        return best_evt

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return all task calendar events in the requested window."""
        results: list[CalendarEvent] = []
        for task in self._get_applicable_tasks():
            results.extend(_expand_task_occurrences(task, start_date, end_date))
        return results
