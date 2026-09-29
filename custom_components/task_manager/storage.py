"""Data storage and management for the Task Manager integration."""
from __future__ import annotations

import asyncio
import calendar
import copy
from datetime import date, datetime, timedelta
import logging
import random
from typing import Any
import uuid

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    DEFAULT_LABELS,
    DEFAULT_SETTINGS,
    DEFAULT_THINGS,
    DEFAULT_USERS,
    EVENT_PART_LOW_STOCK,
    EVENT_TASK_ASSIGNED,
    EVENT_TASK_COMPLETED,
    EVENT_TASK_CREATED,
    EVENT_TASK_DUE,
    EVENT_TASK_OVERDUE,
    EVENT_TASK_REMINDER,
    EVENT_TASK_REOPENED,
    EVENT_TASK_SKIPPED,
    FAR_FUTURE_DUE_DATE,
    PRIORITIES,
    PRIORITY_NONE,
    RECURRENCE_BASED_COMPLETION,
    RECURRENCE_BASED_DUE_DATE,
    RECURRENCE_CUSTOM_DAYS,
    RECURRENCE_DAILY,
    RECURRENCE_MONTHLY,
    RECURRENCE_NONE,
    RECURRENCE_WEEKLY,
    RECURRENCE_YEARLY,
    REPEAT_EVERY_WEEKDAY,
    REPEAT_EVERY_DAY_OF_MONTH,
    REPEAT_EVERY_WEEKDAY_OF_MONTH,
    REPEAT_EVERY_DAYS_BEFORE_END_OF_MONTH,
    REPEAT_MODE_AFTER,
    REPEAT_MODE_EVERY,
    ROTATION_LEAST_COMPLETED,
    ROTATION_NONE,
    ROTATION_RANDOM,
    ROTATION_ROUND_ROBIN,
    SIGNAL_TASK_MANAGER_UPDATED,
    STORAGE_KEY,
    STORAGE_VERSION,
    TASK_STATE_DONE,
    TASK_STATE_DUE,
    TASK_STATE_DUE_SOON,
    TASK_STATE_INACTIVE,
    TASK_TYPE_CHORE,
    TASK_TYPE_READING,
    TASK_TYPES,
    THING_ACTION_DECREMENT,
    THING_ACTION_INCREMENT,
    THING_ACTION_RESET,
    THRESHOLD_OP_GTE,
    THRESHOLD_OP_LTE,
    WARRANTY_STATUS_EXPIRED,
    WARRANTY_STATUS_EXPIRING_SOON,
    WARRANTY_STATUS_NONE,
    WARRANTY_STATUS_VALID,
)
from .providers import (
    async_create_external_task,
    async_delete_external_task,
    async_read_external_tasks,
    async_update_external_task,
)

_LOGGER = logging.getLogger(__name__)


def is_thing_threshold_reached(thing: dict[str, Any]) -> bool:
    """Check if the thing's current value meets or exceeds the trigger threshold."""
    operator = thing.get("threshold_operator", THRESHOLD_OP_GTE)
    try:
        threshold = float(thing.get("target_value", 0))
    except (ValueError, TypeError):
        threshold = 0.0

    try:
        current = float(thing.get("current_value", 0))
    except (ValueError, TypeError):
        current = 0.0

    if bool(thing.get("is_odometer", False)):
        base_val = thing.get("last_reset_value")
        if base_val is None:
            base_val = current
        else:
            try:
                base_val = float(base_val)
            except (ValueError, TypeError):
                base_val = current
        delta = current - base_val
        return delta >= threshold

    if operator in (THRESHOLD_OP_LTE, "lte", "down", "countdown", "<"):
        return current <= threshold
    return current >= threshold


def get_warranty_status(thing: dict[str, Any]) -> str:
    """Calculate warranty status for a thing: 'valid', 'expiring_soon', 'expired', or 'none'."""
    expiry_str = thing.get("warranty_expiry")
    if not expiry_str:
        return WARRANTY_STATUS_NONE
    try:
        expiry_date = datetime.strptime(str(expiry_str)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return WARRANTY_STATUS_NONE

    today = dt_util.now().date()
    days_left = (expiry_date - today).days
    if days_left < 0:
        return WARRANTY_STATUS_EXPIRED
    if days_left <= 30:
        return WARRANTY_STATUS_EXPIRING_SOON
    return WARRANTY_STATUS_VALID


def is_part_low_stock(part: dict[str, Any]) -> bool:
    """Return True if part stock is at or below min_stock / reorder_threshold."""
    try:
        stock = float(part.get("stock", 0))
        min_stock = float(part.get("min_stock", part.get("reorder_threshold", 0)))
        return stock <= min_stock
    except (ValueError, TypeError):
        return False


def add_months(d: date, months: int) -> date:
    """Add integer number of months to a date, clamping day to month length."""
    year = d.year + (d.month + months - 1) // 12
    month = (d.month + months - 1) % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    day = min(d.day, last_day)
    return date(year, month, day)


def weekday_number(name: str | int) -> int:
    """Convert weekday name or number to python weekday number (0=Mon, 6=Sun)."""
    if isinstance(name, int) or (isinstance(name, str) and name.isdigit()):
        return int(name) % 7
    mapping = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6,
        "mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6,
    }
    return mapping.get(str(name).lower(), 0)


def calc_next_weekday(last: date, weekday_name: str, weeks_interval: int = 1) -> date:
    """Return the next due date for 'every N weeks on weekday'."""
    target = weekday_number(weekday_name)
    days_ahead = (target - last.weekday()) % 7
    if days_ahead == 0:
        return last + timedelta(weeks=max(1, weeks_interval))
    return last + timedelta(days=days_ahead) + timedelta(weeks=max(0, weeks_interval - 1))


def calc_next_day_of_month(last: date, day: int, months_interval: int = 1) -> date:
    """Return the next occurrence of day of the month strictly after last."""
    months_interval = max(1, months_interval)
    if months_interval == 1:
        last_day = calendar.monthrange(last.year, last.month)[1]
        candidate = last.replace(day=min(day, last_day))
        if candidate > last:
            return candidate
    next_month = add_months(last.replace(day=1), months_interval)
    last_day = calendar.monthrange(next_month.year, next_month.month)[1]
    return next_month.replace(day=min(day, last_day))


def calc_next_days_before_end_of_month(last: date, days_before: int, months_interval: int = 1) -> date:
    """Return the next occurrence of (last day of month - days_before) strictly after last."""
    months_interval = max(1, months_interval)
    if months_interval == 1:
        last_day = calendar.monthrange(last.year, last.month)[1]
        candidate = last.replace(day=max(1, last_day - days_before))
        if candidate > last:
            return candidate
    next_month = add_months(last.replace(day=1), months_interval)
    last_day = calendar.monthrange(next_month.year, next_month.month)[1]
    return next_month.replace(day=max(1, last_day - days_before))


def get_nth_weekday_of_month(year: int, month: int, target_weekday: int, nth: int) -> date | None:
    """Return the nth occurrence of target_weekday in year/month (-1 for last)."""
    if nth == -1:
        last_day = calendar.monthrange(year, month)[1]
        d = date(year, month, last_day)
        while d.weekday() != target_weekday:
            d -= timedelta(days=1)
        return d
    first_day = date(year, month, 1)
    days_ahead = (target_weekday - first_day.weekday()) % 7
    first_occ = first_day + timedelta(days=days_ahead)
    res = first_occ + timedelta(weeks=nth - 1)
    return res if res.month == month else None


def calc_next_weekday_of_month(last: date, weekday_name: str, nth_str: str, months_interval: int = 1) -> date:
    """Return the next nth weekday-of-month occurrence strictly after last."""
    months_interval = max(1, months_interval)
    target = weekday_number(weekday_name)
    nth = -1 if str(nth_str).lower() == "last" else int(nth_str)
    if months_interval == 1:
        occ = get_nth_weekday_of_month(last.year, last.month, target, nth)
        if occ and occ > last:
            return occ
    candidate_month = add_months(last.replace(day=1), months_interval)
    for _ in range(24):
        occ = get_nth_weekday_of_month(candidate_month.year, candidate_month.month, target, nth)
        if occ:
            return occ
        candidate_month = add_months(candidate_month, months_interval)
    return add_months(last, months_interval)


def calc_most_recent_weekday_in_cycle(last_done: date, today: date, weekday_name: str, weeks_interval: int = 1) -> date:
    """Return most recent occurrence in cycle on or before today."""
    first_cycle = calc_next_weekday(last_done, weekday_name, weeks_interval)
    if first_cycle > today:
        return last_done
    days_elapsed = (today - first_cycle).days
    periods = days_elapsed // (max(1, weeks_interval) * 7)
    return first_cycle + timedelta(weeks=periods * max(1, weeks_interval))


def calc_most_recent_day_of_month(last_done: date, today: date, day: int, months_interval: int = 1) -> date:
    """Return most recent day of month occurrence on or before today."""
    months_interval = max(1, months_interval)
    if months_interval == 1:
        last_day = calendar.monthrange(today.year, today.month)[1]
        candidate = today.replace(day=min(day, last_day))
        if candidate <= today:
            return candidate
        prev_month = add_months(today.replace(day=1), -1)
        prev_last_day = calendar.monthrange(prev_month.year, prev_month.month)[1]
        return prev_month.replace(day=min(day, prev_last_day))
    current = calc_next_day_of_month(last_done, day, months_interval)
    if current > today:
        return last_done
    while True:
        nxt = calc_next_day_of_month(current, day, months_interval)
        if nxt > today:
            return current
        current = nxt


def calc_most_recent_days_before_end_of_month(last_done: date, today: date, days_before: int, months_interval: int = 1) -> date:
    """Return most recent days before month end occurrence on or before today."""
    months_interval = max(1, months_interval)
    if months_interval == 1:
        last_day = calendar.monthrange(today.year, today.month)[1]
        candidate = today.replace(day=max(1, last_day - days_before))
        if candidate <= today:
            return candidate
        prev_month = add_months(today.replace(day=1), -1)
        prev_last_day = calendar.monthrange(prev_month.year, prev_month.month)[1]
        return prev_month.replace(day=max(1, prev_last_day - days_before))
    current = calc_next_days_before_end_of_month(last_done, days_before, months_interval)
    if current > today:
        return last_done
    while True:
        nxt = calc_next_days_before_end_of_month(current, days_before, months_interval)
        if nxt > today:
            return current
        current = nxt


def calc_most_recent_weekday_of_month(last_done: date, today: date, weekday_name: str, nth_str: str, months_interval: int = 1) -> date:
    """Return most recent nth weekday of month occurrence on or before today."""
    months_interval = max(1, months_interval)
    target = weekday_number(weekday_name)
    nth = -1 if str(nth_str).lower() == "last" else int(nth_str)
    if months_interval == 1:
        occ = get_nth_weekday_of_month(today.year, today.month, target, nth)
        if occ and occ <= today:
            return occ
        candidate_month = add_months(today.replace(day=1), -1)
        for _ in range(24):
            occ = get_nth_weekday_of_month(candidate_month.year, candidate_month.month, target, nth)
            if occ and occ <= today:
                return occ
            candidate_month = add_months(candidate_month, -1)
        return today
    current = calc_next_weekday_of_month(last_done, weekday_name, nth_str, months_interval)
    if current > today:
        return last_done
    while True:
        nxt = calc_next_weekday_of_month(current, weekday_name, nth_str, months_interval)
        if nxt > today:
            return current
        current = nxt


def is_repeat_every(recurrence: dict[str, Any]) -> bool:
    """Return True if the recurrence configuration is in 'repeat_every' mode."""
    mode = recurrence.get("repeat_mode") or recurrence.get("mode")
    if mode in (REPEAT_MODE_EVERY, "every", "repeat_every"):
        return True
    if mode in (REPEAT_MODE_AFTER, "after", "repeat_after"):
        return False
    rec_type = recurrence.get("type")
    return rec_type in (
        REPEAT_EVERY_WEEKDAY,
        REPEAT_EVERY_DAY_OF_MONTH,
        REPEAT_EVERY_WEEKDAY_OF_MONTH,
        REPEAT_EVERY_DAYS_BEFORE_END_OF_MONTH,
        "repeat_every_weekday",
        "repeat_every_day_of_month",
        "repeat_every_weekday_of_month",
        "repeat_every_days_before_end_of_month",
    )


def find_most_recent_occurrence(last_done: date, today: date, recurrence: dict[str, Any]) -> date:
    """Find the most recent scheduled occurrence on or before today."""
    if is_repeat_every(recurrence):
        rec_type = recurrence.get("repeat_every_type") or recurrence.get("type", RECURRENCE_NONE)
    else:
        rec_type = recurrence.get("type") or recurrence.get("repeat_every_type", RECURRENCE_NONE)

    if rec_type in (REPEAT_EVERY_WEEKDAY, "repeat_every_weekday"):
        weekday = recurrence.get("repeat_every_weekday")
        if weekday is None:
            weekday = recurrence.get("repeat_weekday") or recurrence.get("weekday") or "monday"
        weeks = int(recurrence.get("repeat_weeks_interval") or recurrence.get("interval", 1))
        return calc_most_recent_weekday_in_cycle(last_done, today, weekday, weeks)
    if rec_type in (REPEAT_EVERY_DAY_OF_MONTH, "repeat_every_day_of_month"):
        day = recurrence.get("repeat_every_day_of_month")
        if day is None:
            day = recurrence.get("repeat_month_day") or recurrence.get("day", 1)
        months = int(recurrence.get("repeat_months_interval") or recurrence.get("interval", 1))
        return calc_most_recent_day_of_month(last_done, today, int(day), months)
    if rec_type in (REPEAT_EVERY_WEEKDAY_OF_MONTH, "repeat_every_weekday_of_month"):
        weekday = recurrence.get("repeat_every_weekday")
        if weekday is None:
            weekday = recurrence.get("repeat_weekday") or recurrence.get("weekday") or "monday"
        nth = str(recurrence.get("repeat_every_nth") or recurrence.get("repeat_nth_occurrence") or recurrence.get("occurrence", "1"))
        months = int(recurrence.get("repeat_months_interval") or recurrence.get("interval", 1))
        return calc_most_recent_weekday_of_month(last_done, today, weekday, nth, months)
    if rec_type in (REPEAT_EVERY_DAYS_BEFORE_END_OF_MONTH, "repeat_every_days_before_end_of_month"):
        days_before = recurrence.get("repeat_every_days_before_end_of_month")
        if days_before is None:
            days_before = recurrence.get("repeat_days_before_end") or recurrence.get("days_before", 0)
        months = int(recurrence.get("repeat_months_interval") or recurrence.get("interval", 1))
        return calc_most_recent_days_before_end_of_month(last_done, today, int(days_before), months)
    return today


def calculate_next_due_date(
    current_due_date_str: str,
    recurrence: dict[str, Any],
    completion_date_str: str | None = None,
) -> str:
    """Calculate the next due date based on recurrence configuration."""
    if is_repeat_every(recurrence):
        rec_type = recurrence.get("repeat_every_type") or recurrence.get("type", RECURRENCE_NONE)
    else:
        rec_type = recurrence.get("type") or recurrence.get("repeat_every_type", RECURRENCE_NONE)

    interval = max(1, int(recurrence.get("interval", 1)))
    based_on = recurrence.get("based_on", RECURRENCE_BASED_DUE_DATE)

    today = dt_util.now().date()

    if based_on == RECURRENCE_BASED_COMPLETION:
        if completion_date_str:
            try:
                base_date = datetime.strptime(completion_date_str[:10], "%Y-%m-%d").date()
            except ValueError:
                base_date = today
        else:
            base_date = today
    else:
        # based on due date
        try:
            base_date = datetime.strptime(current_due_date_str[:10], "%Y-%m-%d").date()
        except ValueError:
            base_date = today

    # Repeat-Every Sub-Types (Fixed Calendar Schedules)
    if rec_type in (REPEAT_EVERY_WEEKDAY, "repeat_every_weekday"):
        weekday = recurrence.get("repeat_every_weekday")
        if weekday is None:
            weekday = recurrence.get("repeat_weekday") or recurrence.get("weekday") or "monday"
        weeks = int(recurrence.get("repeat_weeks_interval") or recurrence.get("interval", 1))
        return calc_next_weekday(base_date, weekday, weeks).strftime("%Y-%m-%d")

    if rec_type in (REPEAT_EVERY_DAY_OF_MONTH, "repeat_every_day_of_month"):
        day = recurrence.get("repeat_every_day_of_month")
        if day is None:
            day = recurrence.get("repeat_month_day") or recurrence.get("day", 1)
        months = int(recurrence.get("repeat_months_interval") or recurrence.get("interval", 1))
        return calc_next_day_of_month(base_date, int(day), months).strftime("%Y-%m-%d")

    if rec_type in (REPEAT_EVERY_WEEKDAY_OF_MONTH, "repeat_every_weekday_of_month"):
        weekday = recurrence.get("repeat_every_weekday")
        if weekday is None:
            weekday = recurrence.get("repeat_weekday") or recurrence.get("weekday") or "monday"
        nth = str(recurrence.get("repeat_every_nth") or recurrence.get("repeat_nth_occurrence") or recurrence.get("occurrence", "1"))
        months = int(recurrence.get("repeat_months_interval") or recurrence.get("interval", 1))
        return calc_next_weekday_of_month(base_date, weekday, nth, months).strftime("%Y-%m-%d")

    if rec_type in (REPEAT_EVERY_DAYS_BEFORE_END_OF_MONTH, "repeat_every_days_before_end_of_month"):
        days_before = recurrence.get("repeat_every_days_before_end_of_month")
        if days_before is None:
            days_before = recurrence.get("repeat_days_before_end") or recurrence.get("days_before", 0)
        months = int(recurrence.get("repeat_months_interval") or recurrence.get("interval", 1))
        return calc_next_days_before_end_of_month(base_date, int(days_before), months).strftime("%Y-%m-%d")

    # Standard Recurrence Types
    if rec_type in (RECURRENCE_DAILY, RECURRENCE_CUSTOM_DAYS):
        next_date = base_date + timedelta(days=interval)
        # If based on due_date and still in the past, advance to next cycle >= today
        if based_on == RECURRENCE_BASED_DUE_DATE and next_date < today:
            days_behind = (today - next_date).days
            cycles = (days_behind // interval) + 1
            next_date += timedelta(days=cycles * interval)
        return next_date.strftime("%Y-%m-%d")

    if rec_type == RECURRENCE_WEEKLY:
        days_of_week = recurrence.get("days_of_week") or recurrence.get("weekdays") or []  # 0=Monday, 6=Sunday
        if days_of_week:
            # Sort target days
            sorted_days = sorted([int(d) for d in days_of_week if 0 <= int(d) <= 6])
            if sorted_days:
                # Find next weekday
                cur_day = base_date.weekday()
                next_day_candidates = [d for d in sorted_days if d > cur_day]
                if next_day_candidates:
                    days_ahead = next_day_candidates[0] - cur_day
                    next_date = base_date + timedelta(days=days_ahead)
                else:
                    # Wraparound to first candidate in next interval week
                    days_ahead = (7 - cur_day) + sorted_days[0] + (interval - 1) * 7
                    next_date = base_date + timedelta(days=days_ahead)

                # If based on due_date and still in the past (overdue), advance cycles until strictly > today
                if based_on == RECURRENCE_BASED_DUE_DATE and next_date <= today:
                    while next_date <= today:
                        cur_day = next_date.weekday()
                        next_day_candidates = [d for d in sorted_days if d > cur_day]
                        if next_day_candidates:
                            days_ahead = next_day_candidates[0] - cur_day
                            next_date = next_date + timedelta(days=days_ahead)
                        else:
                            days_ahead = (7 - cur_day) + sorted_days[0] + (interval - 1) * 7
                            next_date = next_date + timedelta(days=days_ahead)

                return next_date.strftime("%Y-%m-%d")

        # Standard weekly without specific weekdays
        next_date = base_date + timedelta(weeks=interval)
        if based_on == RECURRENCE_BASED_DUE_DATE and next_date < today:
            weeks_behind = (today - next_date).days // 7
            cycles = (weeks_behind // interval) + 1
            next_date += timedelta(weeks=cycles * interval)
        return next_date.strftime("%Y-%m-%d")

    if rec_type == RECURRENCE_MONTHLY:
        # Add interval months
        year = base_date.year
        month = base_date.month + interval
        day = base_date.day

        year += (month - 1) // 12
        month = ((month - 1) % 12) + 1

        # Adjust for end of month clamp
        max_days = [31, 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28,
                    31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
        day = min(day, max_days)
        next_date = date(year, month, day)
        return next_date.strftime("%Y-%m-%d")

    if rec_type == RECURRENCE_YEARLY:
        year = base_date.year + interval
        month = base_date.month
        day = min(base_date.day, 28 if month == 2 else 30)
        next_date = date(year, month, day)
        return next_date.strftime("%Y-%m-%d")

    return current_due_date_str


class TaskManagerData:
    """In-memory data representation for tasks, users, things, labels, and settings."""

    def __init__(self, raw: dict[str, Any] | None = None) -> None:
        """Initialize data container."""
        if not raw:
            self.tasks: list[dict[str, Any]] = []
            self.things: list[dict[str, Any]] = list(DEFAULT_THINGS)
            self.users: list[dict[str, Any]] = list(DEFAULT_USERS)
            self.labels: list[dict[str, Any]] = list(DEFAULT_LABELS)
            self.settings: dict[str, Any] = dict(DEFAULT_SETTINGS)
            self.parts: list[dict[str, Any]] = []
            self.activity_log: list[dict[str, Any]] = []
            self.providers: list[dict[str, Any]] = []
            self.external_overlays: dict[str, dict[str, Any]] = {}
        else:
            self.tasks = raw.get("tasks", [])
            self.things = raw.get("things", list(DEFAULT_THINGS))
            self.users = raw.get("users", list(DEFAULT_USERS))
            self.labels = raw.get("labels", list(DEFAULT_LABELS))
            self.settings = {**DEFAULT_SETTINGS, **raw.get("settings", {})}
            self.parts = raw.get("parts", [])
            self.activity_log = raw.get("activity_log", [])
            self.providers = raw.get("providers", [])
            self.external_overlays = raw.get("external_overlays", {})

        self.external_tasks_cache: dict[str, list[dict[str, Any]]] = {}

    def to_dict(self) -> dict[str, Any]:
        """Convert all data to serializable dict."""
        return {
            "tasks": self.tasks,
            "things": self.things,
            "users": self.users,
            "labels": self.labels,
            "settings": self.settings,
            "parts": self.parts,
            "activity_log": self.activity_log[-100:],  # keep last 100 activity entries
            "providers": self.providers,
            "external_overlays": self.external_overlays,
        }

    def _log_activity(self, action: str, details: dict[str, Any]) -> None:
        """Log a recent activity."""
        entry = {
            "id": str(uuid.uuid4()),
            "action": action,
            "timestamp": dt_util.now().isoformat(),
            **details,
        }
        self.activity_log.append(entry)
        if len(self.activity_log) > 100:
            self.activity_log.pop(0)

    # ================= TASK OPERATIONS =================

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """Retrieve task by id."""
        for t in self.tasks:
            if t.get("id") == task_id:
                return t
        if task_id.startswith("ext:"):
            for t in self.get_all_tasks(include_external=True):
                if t.get("id") == task_id:
                    return t
        return None

    def create_task(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new task."""
        now = dt_util.now()
        task_id = task_data.get("id") or str(uuid.uuid4())
        today_str = now.date().strftime("%Y-%m-%d")

        assignees = task_data.get("assignees", [])
        current_assignee = task_data.get("current_assignee")
        if not current_assignee and assignees:
            current_assignee = assignees[0]

        subtasks = []
        for st in task_data.get("subtasks", []):
            if isinstance(st, str):
                subtasks.append({"id": str(uuid.uuid4()), "title": st, "completed": False})
            elif isinstance(st, dict):
                subtasks.append({
                    "id": st.get("id") or str(uuid.uuid4()),
                    "title": st.get("title", ""),
                    "completed": bool(st.get("completed", False)),
                })

        linked_thing_id = task_data.get("linked_thing_id")
        rec = task_data.get("recurrence")
        if rec is None:
            rec = {
                "enabled": False,
                "type": RECURRENCE_NONE,
                "interval": 1,
                "days_of_week": [],
                "based_on": RECURRENCE_BASED_DUE_DATE,
            }
        else:
            rec = dict(rec)
            if "enabled" not in rec and rec.get("type", RECURRENCE_NONE) not in (RECURRENCE_NONE, "none", ""):
                rec["enabled"] = True
        has_time_fallback = (
            rec.get("enabled", False)
            and rec.get("type", RECURRENCE_NONE) not in (RECURRENCE_NONE, "none", "")
            and int(rec.get("interval", 1)) > 0
        )

        initial_due_date = task_data.get("due_date", today_str)
        if linked_thing_id:
            thing = self.get_thing(linked_thing_id)
            if thing and is_thing_threshold_reached(thing):
                initial_due_date = today_str
            elif not has_time_fallback:
                # Without a time schedule fallback, due date is set to far future until threshold triggers!
                initial_due_date = FAR_FUTURE_DUE_DATE

        new_task = {
            "id": task_id,
            "title": task_data.get("title", "New Task"),
            "description": task_data.get("description", ""),
            "due_date": initial_due_date,
            "due_time": task_data.get("due_time", ""),
            "priority": task_data.get("priority", PRIORITY_NONE),
            "status": "pending",
            "assignees": assignees,
            "current_assignee": current_assignee,
            "rotation_mode": task_data.get("rotation_mode", ROTATION_NONE),
            "labels": task_data.get("labels", []),
            "tags": [str(t).strip() for t in task_data.get("tags", []) if str(t).strip()],
            "is_active": bool(task_data.get("is_active", task_data.get("active", True))),
            "active_override": task_data.get("active_override") or None,
            "task_interval_override": task_data.get("task_interval_override") or None,
            "due_soon_override": task_data.get("due_soon_override") or None,
            "due_soon_days": max(0, int(task_data.get("due_soon_days", 0))),
            "notification_interval": max(1, int(task_data.get("notification_interval", 1))),
            "dependencies": [str(d).strip() for d in task_data.get("dependencies", []) if str(d).strip()],
            "times_completed": int(task_data.get("times_completed", 0)),
            "last_done_date": task_data.get("last_done_date", ""),
            "recurrence": rec,
            "subtasks": subtasks,
            "reminders": task_data.get("reminders", []),
            "repetition_count": int(task_data.get("repetition_count", 0)),
            "points": int(task_data.get("points", self.settings.get("default_points", 10))),
            "task_type": task_data.get("task_type", TASK_TYPE_CHORE),
            "reading_unit": task_data.get("reading_unit", ""),
            "last_reading_value": (
                task_data.get("last_reading_value")
                if task_data.get("last_reading_value") is not None
                else (
                    next((reg.get("last_value") for reg in task_data.get("registers", []) if isinstance(reg, dict) and reg.get("last_value") is not None), None)
                )
            ),
            "registers": [
                {
                    "id": str(reg.get("id") or uuid.uuid4())[:8],
                    "name": str(reg.get("name", "")).strip(),
                    "unit": str(reg.get("unit", "")).strip(),
                    "last_value": float(reg["last_value"]) if reg.get("last_value") is not None and str(reg.get("last_value")).strip() not in ("", "None", "null") else None,
                }
                for reg in task_data.get("registers", [])
                if isinstance(reg, dict) and (reg.get("name") or reg.get("id"))
            ],
            "consumed_parts": task_data.get("consumed_parts", []),
            "on_complete_entity_id": task_data.get("on_complete_entity_id") or None,
            "require_tag_scan": bool(task_data.get("require_tag_scan", False)),
            "default_duration_minutes": max(0, int(task_data.get("default_duration_minutes", 0))),
            "default_cost": float(task_data.get("default_cost", 0.0)),
            "linked_thing_id": linked_thing_id,
            "thing_action": task_data.get("thing_action", THING_ACTION_RESET),
            "completion_restriction": task_data.get("completion_restriction", {
                "enabled": False,
                "hours_before_due": 12,
            }),
            "created_at": now.isoformat(),
            "completed_at": None,
            "completed_by": None,
            "history": [],
        }

        self.tasks.append(new_task)
        self._log_activity("task_created", {"task_id": task_id, "title": new_task["title"]})
        return new_task

    def update_task(self, task_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        """Update an existing task."""
        task = self.get_task(task_id)
        if not task:
            return None

        for key, val in updates.items():
            if key in ("id", "created_at", "history"):
                continue
            if key == "subtasks" and isinstance(val, list):
                clean_st = []
                for st in val:
                    if isinstance(st, str):
                        clean_st.append({"id": str(uuid.uuid4()), "title": st, "completed": False})
                    elif isinstance(st, dict):
                        clean_st.append({
                            "id": st.get("id") or str(uuid.uuid4()),
                            "title": st.get("title", ""),
                            "completed": bool(st.get("completed", False)),
                        })
                task["subtasks"] = clean_st
            elif key == "tags" and isinstance(val, list):
                task["tags"] = [str(t).strip() for t in val if str(t).strip()]
            elif key in ("active", "is_active"):
                task["is_active"] = bool(val)
            elif key in ("due_soon_days", "notification_interval", "times_completed"):
                try:
                    task[key] = max(0, int(val))
                except (ValueError, TypeError):
                    pass
            elif key == "dependencies" and isinstance(val, list):
                task["dependencies"] = [str(d).strip() for d in val if str(d).strip()]
            elif key == "registers" and isinstance(val, list):
                task["registers"] = [
                    {
                        "id": str(reg.get("id") or uuid.uuid4())[:8],
                        "name": str(reg.get("name", "")).strip(),
                        "unit": str(reg.get("unit", "")).strip(),
                        "last_value": float(reg["last_value"]) if reg.get("last_value") is not None and str(reg.get("last_value")).strip() not in ("", "None", "null") else None,
                    }
                    for reg in val
                    if isinstance(reg, dict) and (reg.get("name") or reg.get("id"))
                ]
            else:
                task[key] = val

        # Handle linked thing due date adjustment
        linked_thing_id = task.get("linked_thing_id")
        if linked_thing_id and task.get("status") == "pending":
            thing = self.get_thing(linked_thing_id)
            rec = task.get("recurrence", {})
            has_time_fallback = (
                rec.get("enabled", False)
                and rec.get("type", RECURRENCE_NONE) not in (RECURRENCE_NONE, "none", "")
                and int(rec.get("interval", 1)) > 0
            )
            today_str = dt_util.now().date().strftime("%Y-%m-%d")
            if thing and is_thing_threshold_reached(thing):
                task["due_date"] = today_str
            elif not has_time_fallback and "due_date" not in updates and task.get("due_date", "") < FAR_FUTURE_DUE_DATE:
                task["due_date"] = FAR_FUTURE_DUE_DATE

        self._log_activity("task_updated", {"task_id": task_id, "title": task["title"]})
        return task

    def duplicate_task(self, task_id: str) -> dict[str, Any] | None:
        """Duplicate an existing task with clean state."""
        orig = self.get_task(task_id)
        if not orig:
            return None

        clone_data = copy.deepcopy(orig)
        clone_data.pop("id", None)
        clone_data.pop("created_at", None)
        clone_data.pop("completed_at", None)
        clone_data.pop("completed_by", None)
        clone_data.pop("history", None)
        clone_data["title"] = f"{orig.get('title', 'Task')} (Copy)"
        clone_data["status"] = "pending"
        for st in clone_data.get("subtasks", []):
            st["completed"] = False
            st["id"] = str(uuid.uuid4())
        return self.create_task(clone_data)

    def complete_task(
        self,
        task_id: str,
        user_id: str | None = None,
        cost: float | None = None,
        duration_minutes: int | None = None,
        notes: str | None = None,
        completed_at: str | None = None,
        reading_value: float | None = None,
        consumed_parts: list[dict[str, Any]] | None = None,
        hass: HomeAssistant | None = None,
        readings: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any] | None:
        """Mark a task complete, apply points, rotate assignee, and calculate recurrence."""
        task = self.get_task(task_id)
        if not task:
            return None

        now = dt_util.now()
        if completed_at:
            try:
                comp_dt = datetime.fromisoformat(completed_at)
                now_str = comp_dt.isoformat()
                today_date_str = comp_dt.date().strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                now_str = str(completed_at)
                today_date_str = str(completed_at)[:10]
        else:
            now_str = now.isoformat()
            today_date_str = now.date().strftime("%Y-%m-%d")

        effective_user_id = user_id or task.get("current_assignee")
        points_awarded = int(task.get("points", self.settings.get("default_points", 10)))

        # 1. Award Gamification Points & Update Streak for User
        if effective_user_id and self.settings.get("gamification_enabled", True):
            user = self.get_user(effective_user_id)
            if user:
                user["points"] = user.get("points", 0) + points_awarded
                user["completed_count"] = user.get("completed_count", 0) + 1

                # Streak calculation
                last_completed = user.get("last_completed_date", "")
                if last_completed:
                    try:
                        last_date = datetime.strptime(last_completed, "%Y-%m-%d").date()
                        diff_days = (datetime.strptime(today_date_str, "%Y-%m-%d").date() - last_date).days
                        if diff_days == 1:
                            user["streak"] = user.get("streak", 0) + 1
                        elif diff_days > 1:
                            user["streak"] = 1
                    except ValueError:
                        user["streak"] = 1
                else:
                    user["streak"] = 1

                user["last_completed_date"] = today_date_str

        # Reading Task calculation (Single or Multi-Register)
        recorded_readings: list[dict[str, Any]] = []
        reading_entry = None
        reading_delta = None
        task_registers = task.get("registers") or []

        if readings and isinstance(readings, list):
            for r_item in readings:
                if not isinstance(r_item, dict):
                    continue
                reg_id = r_item.get("id")
                reg_name = str(r_item.get("name") or "").strip()
                reg_unit = str(r_item.get("unit") or "").strip()
                val_raw = r_item.get("value")
                if val_raw is None:
                    val_raw = r_item.get("reading_value")
                if val_raw is None or str(val_raw).strip() == "":
                    continue

                try:
                    cur_val = float(val_raw)
                except (ValueError, TypeError):
                    continue

                # Match against task registers
                matched_reg = None
                for reg in task_registers:
                    if reg_id and reg.get("id") == reg_id:
                        matched_reg = reg
                        break
                    if reg_name and reg.get("name") == reg_name:
                        matched_reg = reg
                        break

                if matched_reg:
                    prev_val = matched_reg.get("last_value")
                    delta = round(cur_val - float(prev_val), 4) if prev_val is not None else 0.0
                    matched_reg["last_value"] = cur_val
                    unit = matched_reg.get("unit") or reg_unit or task.get("reading_unit", "")
                    name = matched_reg.get("name") or reg_name
                    reg_id = matched_reg.get("id") or reg_id
                else:
                    delta = 0.0
                    unit = reg_unit or task.get("reading_unit", "")
                    name = reg_name or "Reading"

                recorded_readings.append({
                    "id": reg_id,
                    "name": name,
                    "unit": unit,
                    "value": cur_val,
                    "delta": delta,
                })

            if recorded_readings:
                reading_entry = recorded_readings[0]["value"]
                reading_delta = recorded_readings[0]["delta"]
                task["last_reading_value"] = reading_entry

        elif reading_value is not None:
            try:
                cur_val = float(reading_value)
                prev_val = task.get("last_reading_value")
                if prev_val is not None:
                    reading_delta = round(cur_val - float(prev_val), 4)
                else:
                    reading_delta = 0.0
                task["last_reading_value"] = cur_val
                reading_entry = cur_val

                if len(task_registers) == 1:
                    task_registers[0]["last_value"] = cur_val
                    recorded_readings.append({
                        "id": task_registers[0].get("id"),
                        "name": task_registers[0].get("name", "Reading"),
                        "unit": task_registers[0].get("unit", task.get("reading_unit", "")),
                        "value": cur_val,
                        "delta": reading_delta,
                    })
            except (ValueError, TypeError):
                pass

        # Consumed Parts Inventory Deduction & Cost
        actual_consumed = consumed_parts if consumed_parts is not None else task.get("consumed_parts", [])
        calculated_cost = 0.0
        used_parts_list = []
        if actual_consumed:
            for item in actual_consumed:
                p_id = item.get("part_id") if isinstance(item, dict) else item
                qty = float(item.get("quantity", item.get("qty", 1))) if isinstance(item, dict) else 1.0
                part = self.get_part(p_id)
                if part:
                    part["stock"] = max(0.0, float(part.get("stock", 0)) - qty)
                    unit_p = float(part.get("unit_price", part.get("unit_cost", 0.0)))
                    calculated_cost += (unit_p * qty)
                    used_parts_list.append({
                        "part_id": p_id,
                        "name": part.get("name", ""),
                        "quantity": qty,
                        "unit_price": unit_p,
                    })
                    if hass and is_part_low_stock(part):
                        hass.bus.async_fire(EVENT_PART_LOW_STOCK, {
                            "part_id": part["id"],
                            "name": part["name"],
                            "stock": part["stock"],
                            "min_stock": part.get("min_stock", 0),
                        })

        final_cost = cost if cost is not None else round(calculated_cost + float(task.get("default_cost", 0.0)), 2)
        final_duration = duration_minutes if duration_minutes is not None else int(task.get("default_duration_minutes", 0))

        # 2. Record completion history
        history_item: dict[str, Any] = {
            "completed_at": now_str,
            "user_id": effective_user_id,
            "points": points_awarded,
        }
        if final_cost:
            history_item["cost"] = round(final_cost, 2)
        if final_duration:
            history_item["duration_minutes"] = final_duration
        if notes:
            history_item["notes"] = notes
        if reading_entry is not None:
            history_item["reading_value"] = reading_entry
            history_item["reading_delta"] = reading_delta
            history_item["reading_unit"] = task.get("reading_unit", "")
        if recorded_readings:
            history_item["readings"] = recorded_readings
        if used_parts_list:
            history_item["consumed_parts"] = used_parts_list

        task.setdefault("history", []).append(history_item)

        # 3. Linked "Thing" Action (e.g. Filter reset, Dustbin empty)
        linked_thing_id = task.get("linked_thing_id")
        thing_action = task.get("thing_action", THING_ACTION_RESET)
        if linked_thing_id:
            thing = self.get_thing(linked_thing_id)
            if thing:
                if thing_action == THING_ACTION_RESET:
                    if bool(thing.get("is_odometer", False)):
                        thing["last_reset_value"] = float(thing.get("current_value", 0))
                        thing["last_reset"] = now_str
                    else:
                        operator = thing.get("threshold_operator", THRESHOLD_OP_GTE)
                        if operator in (THRESHOLD_OP_LTE, "lte", "down", "countdown", "<"):
                            thing["current_value"] = float(thing.get("initial_value", 100))
                        else:
                            thing["current_value"] = 0.0
                        thing["last_reset"] = now_str
                elif thing_action == THING_ACTION_INCREMENT:
                    thing["current_value"] = float(thing.get("current_value", 0)) + 1
                elif thing_action == THING_ACTION_DECREMENT:
                    thing["current_value"] = max(0.0, float(thing.get("current_value", 0)) - 1)

        # 4. Handle Recurrence & Subtasks Reset
        rec = task.get("recurrence", {})
        has_time_fallback = (
            rec.get("enabled", False)
            and rec.get("type", RECURRENCE_NONE) not in (RECURRENCE_NONE, "none", "")
            and int(rec.get("interval", 1)) > 0
        )
        is_recurring = (rec.get("enabled", False) and has_time_fallback) or bool(linked_thing_id)

        if is_recurring:
            # Smart Subtasks Reset: reset all subtasks when recurring task completes
            for st in task.get("subtasks", []):
                st["completed"] = False

            # Assignee Rotation
            rotation_mode = task.get("rotation_mode", ROTATION_NONE)
            assignees = task.get("assignees", [])

            if assignees and rotation_mode != ROTATION_NONE:
                if rotation_mode == ROTATION_ROUND_ROBIN and len(assignees) > 1:
                    cur_idx = assignees.index(task["current_assignee"]) if task.get("current_assignee") in assignees else 0
                    next_idx = (cur_idx + 1) % len(assignees)
                    task["current_assignee"] = assignees[next_idx]
                elif rotation_mode == ROTATION_LEAST_COMPLETED and len(assignees) > 1:
                    # Pick assignee with lowest completed_count
                    least_user = None
                    lowest_count = float("inf")
                    for a_id in assignees:
                        u = self.get_user(a_id)
                        count = u.get("completed_count", 0) if u else 0
                        if count < lowest_count:
                            lowest_count = count
                            least_user = a_id
                    if least_user:
                        task["current_assignee"] = least_user
                elif rotation_mode == ROTATION_RANDOM and len(assignees) > 1:
                    candidates = [a for a in assignees if a != task.get("current_assignee")]
                    task["current_assignee"] = random.choice(candidates if candidates else assignees)

            # Recalculate next due date
            rep_count = task.get("repetition_count", 0) + 1
            task["repetition_count"] = rep_count
            task["times_completed"] = task.get("times_completed", 0) + 1
            task["last_done_date"] = today_date_str
            max_reps = rec.get("max_repetitions")
            end_date = rec.get("end_date")

            if linked_thing_id and not has_time_fallback:
                # No schedule fallback configured: next due date is set to far future until threshold triggers!
                next_due = FAR_FUTURE_DUE_DATE
            else:
                if is_repeat_every(rec):
                    cur_due = task.get("due_date", today_date_str)
                    try:
                        cur_due_dt = datetime.strptime(cur_due[:10], "%Y-%m-%d").date()
                    except ValueError:
                        cur_due_dt = now.date()
                    due_in = (cur_due_dt - now.date()).days if cur_due_dt > now.date() else 0
                    due_soon_days = int(task.get("due_soon_days", 0))

                    if 0 < due_in <= due_soon_days:
                        # Early completion within due_soon window
                        task["last_done_date"] = cur_due_dt.strftime("%Y-%m-%d")
                        base_calc_date = cur_due_dt
                    else:
                        # Due or overdue: catch up to most recent occurrence
                        recent = find_most_recent_occurrence(cur_due_dt, now.date(), rec)
                        task["last_done_date"] = recent.strftime("%Y-%m-%d")
                        base_calc_date = recent

                    next_due = calculate_next_due_date(
                        current_due_date_str=base_calc_date.strftime("%Y-%m-%d"),
                        recurrence=rec,
                        completion_date_str=task["last_done_date"],
                    )
                else:
                    next_due = calculate_next_due_date(
                        current_due_date_str=task.get("due_date", today_date_str),
                        recurrence=rec,
                        completion_date_str=today_date_str,
                    )

            # Check if recurrence expired
            recurrence_expired = False
            if max_reps and rep_count >= int(max_reps):
                recurrence_expired = True
            elif end_date and next_due and next_due > str(end_date):
                recurrence_expired = True

            if recurrence_expired:
                rec["enabled"] = False
                task["status"] = "completed"
                task["completed_at"] = now_str
                task["completed_by"] = effective_user_id
            else:
                task["due_date"] = next_due
                task["status"] = "pending"
                task["completed_at"] = None
                task["completed_by"] = None
        else:
            task["status"] = "completed"
            task["completed_at"] = now_str
            task["completed_by"] = effective_user_id
            task["times_completed"] = task.get("times_completed", 0) + 1
            task["last_done_date"] = today_date_str

        self._log_activity("task_completed", {
            "task_id": task_id,
            "title": task["title"],
            "user_id": effective_user_id,
            "points": points_awarded,
            "recurring": is_recurring,
        })
        return task

    def skip_task(self, task_id: str) -> dict[str, Any] | None:
        """Skip the current recurrence of a task without awarding points."""
        task = self.get_task(task_id)
        if not task:
            return None

        now = dt_util.now()
        now_str = now.isoformat()
        today_date_str = now.date().strftime("%Y-%m-%d")

        rec = task.get("recurrence", {})
        rec_enabled = rec.get("enabled", rec.get("type", RECURRENCE_NONE) not in (RECURRENCE_NONE, "none", ""))
        has_time_fallback = (
            rec_enabled
            and rec.get("type", RECURRENCE_NONE) not in (RECURRENCE_NONE, "none", "")
            and int(rec.get("interval", 1)) > 0
        )
        is_recurring = (rec_enabled and has_time_fallback) or bool(task.get("linked_thing_id"))

        prev_due = task.get("due_date", today_date_str)
        if is_recurring:
            next_due = calculate_next_due_date(
                current_due_date_str=prev_due,
                recurrence=rec,
                completion_date_str=today_date_str,
            )
            task["due_date"] = next_due
            task["status"] = "pending"
        else:
            task["status"] = "completed"
            task["completed_at"] = now_str

        task.setdefault("history", []).append({
            "action": "skipped",
            "completed_at": now_str,
            "skipped_at": now_str,
            "previous_due_date": prev_due,
        })

        self._log_activity("task_skipped", {
            "task_id": task_id,
            "title": task.get("title", ""),
            "new_due_date": task.get("due_date"),
        })
        return task

    def set_last_done_date(self, task_id: str, new_date_str: str) -> dict[str, Any] | None:
        """Set the last done date of a task explicitly and recalculate the next due date."""
        task = self.get_task(task_id)
        if not task:
            return None
        try:
            valid_date = datetime.strptime(new_date_str[:10], "%Y-%m-%d").date().strftime("%Y-%m-%d")
        except ValueError:
            valid_date = new_date_str[:10]

        task["last_done_date"] = valid_date
        task["times_completed"] = task.get("times_completed", 0) + 1
        rec = task.get("recurrence", {})
        if rec.get("enabled", False) and rec.get("type", RECURRENCE_NONE) not in (RECURRENCE_NONE, "none", ""):
            next_due = calculate_next_due_date(
                current_due_date_str=valid_date,
                recurrence=rec,
                completion_date_str=valid_date,
            )
            task["due_date"] = next_due
            task["status"] = "pending"
        self._log_activity("task_set_last_done", {"task_id": task_id, "last_done": valid_date})
        return task

    def pause_task(self, task_id: str) -> dict[str, Any] | None:
        """Pause / deactivate a task."""
        if task_id.startswith("ext:"):
            parts = task_id.split(":", 2)
            if len(parts) >= 3:
                uid = parts[2]
                self.set_overlay(uid, {"is_active": False})
                self._log_activity("task_paused", {"task_id": task_id, "title": ""})
                for t in self.get_all_tasks(include_external=True):
                    if t.get("id") == task_id:
                        return t
            return None
        task = self.get_task(task_id)
        if not task:
            return None
        task["is_active"] = False
        self._log_activity("task_paused", {"task_id": task_id, "title": task.get("title", "")})
        return task

    def resume_task(self, task_id: str) -> dict[str, Any] | None:
        """Resume / activate a paused task."""
        if task_id.startswith("ext:"):
            parts = task_id.split(":", 2)
            if len(parts) >= 3:
                uid = parts[2]
                self.set_overlay(uid, {"is_active": True})
                self._log_activity("task_resumed", {"task_id": task_id, "title": ""})
                for t in self.get_all_tasks(include_external=True):
                    if t.get("id") == task_id:
                        return t
            return None
        task = self.get_task(task_id)
        if not task:
            return None
        task["is_active"] = True
        self._log_activity("task_resumed", {"task_id": task_id, "title": task.get("title", "")})
        return task

    def get_task_effective_state(
        self,
        task_id: str,
        hass: HomeAssistant | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """Calculate the effective state and metrics for a task.

        Returns (state, attributes) where state is one of:
        - "inactive": task is paused or active_override is off
        - "done": task is completed or not yet due
        - "due_soon": within due_soon_days window
        - "due": due today or overdue

        Also resolves dependencies:
        Urgency rank: done (0) < due_soon (1) < due (2).
        A task's rank is clamped to the minimum rank among its dependencies.
        """
        task = self.get_task(task_id)
        if not task:
            return TASK_STATE_DONE, {}

        now = dt_util.now()
        if hasattr(now, "date") and callable(now.date):
            d = now.date()
            today = d if isinstance(d, date) else date.today()
        else:
            today = date.today()
        today_str = today.strftime("%Y-%m-%d")

        # 1. Effective active
        effective_active = bool(task.get("is_active", True))
        active_override = task.get("active_override")
        if active_override and hass:
            state_obj = hass.states.get(active_override)
            if state_obj is not None and state_obj.state not in ("unavailable", "unknown"):
                effective_active = (state_obj.state == "on")

        # 2. Effective due_soon_days
        effective_due_soon_days = int(task.get("due_soon_days", 0))
        due_soon_override = task.get("due_soon_override")
        if due_soon_override and hass:
            state_obj = hass.states.get(due_soon_override)
            if state_obj is not None and state_obj.state not in ("unavailable", "unknown"):
                try:
                    effective_due_soon_days = max(0, int(float(state_obj.state)))
                except (ValueError, TypeError):
                    pass

        # 3. Due date & days until/overdue
        due_date_str = task.get("due_date", today_str)
        try:
            due_date = datetime.strptime(due_date_str[:10], "%Y-%m-%d").date()
        except ValueError:
            due_date = today

        due_in = (due_date - today).days if due_date > today else 0
        overdue_by = (today - due_date).days if due_date < today else 0

        # Base state calculation
        if not effective_active:
            native_state = TASK_STATE_INACTIVE
        elif task.get("status") == "completed":
            native_state = TASK_STATE_DONE
        elif due_in == 0:
            native_state = TASK_STATE_DUE
        elif due_in <= effective_due_soon_days:
            native_state = TASK_STATE_DUE_SOON
        else:
            native_state = TASK_STATE_DONE

        # 4. Dependency constraint gating
        dependencies = task.get("dependencies", [])
        if native_state in (TASK_STATE_DUE, TASK_STATE_DUE_SOON) and dependencies:
            state_rank = {TASK_STATE_DONE: 0, TASK_STATE_DUE_SOON: 1, TASK_STATE_DUE: 2}
            own_rank = state_rank.get(native_state, 2)
            min_dep_rank = own_rank

            for dep_id in dependencies:
                # Find by task id or entity_id or title
                dep_task = self.get_task(dep_id)
                if not dep_task:
                    for t in self.tasks:
                        if t.get("id") == dep_id or t.get("title") == dep_id:
                            dep_task = t
                            break

                if dep_task:
                    dep_state, _ = self.get_task_effective_state(dep_task["id"], hass)
                    dep_rank = state_rank.get(dep_state, 0)
                elif hass:
                    dep_state_obj = hass.states.get(dep_id)
                    dep_rank = state_rank.get(dep_state_obj.state if dep_state_obj else None, 0)
                else:
                    dep_rank = 0

                if dep_rank < min_dep_rank:
                    min_dep_rank = dep_rank

            if min_dep_rank < own_rank:
                rank_state = {0: TASK_STATE_DONE, 1: TASK_STATE_DUE_SOON, 2: TASK_STATE_DUE}
                native_state = rank_state[min_dep_rank]

        attrs = {
            "task_id": task["id"],
            "title": task.get("title", ""),
            "due_date": due_date_str,
            "due_in": due_in,
            "overdue_by": overdue_by,
            "due_soon_days": effective_due_soon_days,
            "last_done": task.get("last_done_date", ""),
            "times_completed": task.get("times_completed", 0),
            "notification_interval": task.get("notification_interval", 1),
            "tags": task.get("tags", []),
            "dependencies": dependencies,
            "is_active": effective_active,
            "priority": task.get("priority", PRIORITY_NONE),
            "assignee": task.get("current_assignee"),
            "points": task.get("points", 10),
            "recurrence": task.get("recurrence", {}),
            "task_type": task.get("task_type", TASK_TYPE_CHORE),
            "reading_unit": task.get("reading_unit", ""),
            "last_reading_value": task.get("last_reading_value"),
            "registers": task.get("registers", []),
            "readings": {r["name"]: r.get("last_value") for r in task.get("registers", []) if r.get("name")},
            "consumed_parts": task.get("consumed_parts", []),
            "on_complete_entity_id": task.get("on_complete_entity_id"),
            "require_tag_scan": task.get("require_tag_scan", False),
            "default_duration_minutes": task.get("default_duration_minutes", 0),
            "default_cost": task.get("default_cost", 0.0),
            "linked_thing_id": task.get("linked_thing_id"),
        }
        return native_state, attrs

    def reset_task(self, task_id: str) -> dict[str, Any] | None:
        """Reset a completed task back to pending."""
        task = self.get_task(task_id)
        if not task:
            return None

        task["status"] = "pending"
        task["completed_at"] = None
        task["completed_by"] = None

        self._log_activity("task_reset", {"task_id": task_id, "title": task["title"]})
        return task

    def delete_task(self, task_id: str) -> bool:
        """Delete task by id."""
        for i, t in enumerate(self.tasks):
            if t.get("id") == task_id:
                title = t.get("title", "")
                self.tasks.pop(i)
                self._log_activity("task_deleted", {"task_id": task_id, "title": title})
                return True
        return False

    def delete_task_history_entry(
        self,
        task_id: str,
        entry_index: int | None = None,
        completed_at: str | None = None,
    ) -> bool:
        """Delete a history entry from a task and restore previous state/readings if needed."""
        task = self.get_task(task_id)
        if not task:
            return False

        history = task.get("history", [])
        if not history:
            return False

        idx_to_remove: int | None = None
        if completed_at:
            for i, h in enumerate(history):
                if h.get("completed_at") == completed_at:
                    idx_to_remove = i
                    break
        elif entry_index is not None:
            if -len(history) <= entry_index < len(history):
                idx_to_remove = entry_index if entry_index >= 0 else len(history) + entry_index

        if idx_to_remove is None:
            return False

        removed = history.pop(idx_to_remove)

        # Decrement times_completed if > 0
        task["times_completed"] = max(0, int(task.get("times_completed", 1)) - 1)
        if task.get("repetition_count", 0) > 0:
            task["repetition_count"] = max(0, int(task.get("repetition_count", 1)) - 1)

        # Restore last done date
        remaining_completed = [
            h.get("completed_at")[:10] for h in history if h.get("completed_at")
        ]
        if remaining_completed:
            task["last_done_date"] = remaining_completed[-1]
        else:
            task["last_done_date"] = None

        # Restore reading values if this was a reading task or has registers
        if task.get("task_type") == TASK_TYPE_READING or task.get("registers") or task.get("last_reading_value") is not None:
            prev_reading_val = None
            for h in reversed(history):
                if "reading_value" in h and h["reading_value"] is not None:
                    prev_reading_val = h["reading_value"]
                    break
                elif "readings" in h and isinstance(h["readings"], list) and h["readings"]:
                    first_r = h["readings"][0]
                    if isinstance(first_r, dict) and first_r.get("value") is not None:
                        prev_reading_val = first_r["value"]
                        break
            task["last_reading_value"] = prev_reading_val

            for reg in task.get("registers", []):
                reg_id = reg.get("id")
                reg_name = reg.get("name")
                found_val = None
                for h in reversed(history):
                    if "readings" in h and isinstance(h["readings"], list):
                        for rh in h["readings"]:
                            if isinstance(rh, dict):
                                if (reg_id and rh.get("id") == reg_id) or (reg_name and rh.get("name") == reg_name):
                                    found_val = rh.get("value")
                                    break
                        if found_val is not None:
                            break
                reg["last_value"] = found_val

        self._log_activity("task_history_entry_deleted", {
            "task_id": task_id,
            "title": task.get("title", ""),
            "deleted_completed_at": removed.get("completed_at"),
        })
        return True

    def update_subtask(self, task_id: str, subtask_id: str, completed: bool) -> bool:
        """Toggle or set subtask completed state."""
        task = self.get_task(task_id)
        if not task:
            return False
        for st in task.get("subtasks", []):
            if st.get("id") == subtask_id:
                st["completed"] = completed
                return True
        return False

    # ================= "THINGS" OPERATIONS =================

    def get_thing(self, thing_id: str) -> dict[str, Any] | None:
        """Retrieve thing by id."""
        for th in self.things:
            if th.get("id") == thing_id:
                return th
        return None

    def create_thing(self, thing_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new tracked thing/meter."""
        thing_id = thing_data.get("id") or str(uuid.uuid4())
        threshold_val = thing_data.get("threshold_value", thing_data.get("target_value", 100))
        try:
            target_value = float(threshold_val)
        except (ValueError, TypeError):
            target_value = 100.0

        cur_val = thing_data.get("current_value", 0)
        try:
            current_value = float(cur_val)
        except (ValueError, TypeError):
            current_value = 0.0

        operator = thing_data.get("threshold_operator", THRESHOLD_OP_GTE)
        if operator not in (THRESHOLD_OP_GTE, THRESHOLD_OP_LTE):
            operator = THRESHOLD_OP_GTE

        is_odometer = bool(thing_data.get("is_odometer", False))
        last_reset_val = thing_data.get("last_reset_value")
        if last_reset_val is not None and str(last_reset_val).strip() not in ("", "None", "null"):
            try:
                last_reset_val = float(last_reset_val)
            except (ValueError, TypeError):
                last_reset_val = current_value if is_odometer else None
        elif is_odometer:
            last_reset_val = current_value
        else:
            last_reset_val = None

        new_thing = {
            "id": thing_id,
            "name": thing_data.get("name", "New Thing"),
            "category": thing_data.get("category", "General"),
            "icon": thing_data.get("icon", "mdi:chart-arc"),
            "current_value": current_value,
            "target_value": target_value,
            "threshold_operator": operator,
            "external_entity_id": thing_data.get("external_entity_id") or None,
            "script_entity_id": thing_data.get("script_entity_id") or None,
            "initial_value": float(thing_data.get("initial_value", 100 if operator == THRESHOLD_OP_LTE else 0)),
            "unit": thing_data.get("unit", "units"),
            "area_id": thing_data.get("area_id") or None,
            "manufacturer": thing_data.get("manufacturer", ""),
            "model": thing_data.get("model", ""),
            "serial_number": thing_data.get("serial_number", ""),
            "installation_date": thing_data.get("installation_date", ""),
            "warranty_expiry": thing_data.get("warranty_expiry", ""),
            "documentation_url": thing_data.get("documentation_url", ""),
            "notes": thing_data.get("notes", ""),
            "auto_task_creation": bool(thing_data.get("auto_task_creation", False)),
            "auto_task_title": thing_data.get("auto_task_title", f"Maintain {thing_data.get('name', 'Thing')}"),
            "last_reset": thing_data.get("last_reset", ""),
            "is_odometer": is_odometer,
            "last_reset_value": last_reset_val,
        }
        self.things.append(new_thing)
        self._log_activity("thing_created", {"thing_id": thing_id, "name": new_thing["name"]})
        return new_thing

    def update_thing(self, thing_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        """Update thing properties."""
        thing = self.get_thing(thing_id)
        if not thing:
            return None
        for key, val in updates.items():
            if key != "id":
                thing[key] = val

        if "threshold_value" in updates and "target_value" not in updates:
            try:
                thing["target_value"] = float(updates["threshold_value"])
            except (ValueError, TypeError):
                pass

        if "external_entity_id" in updates:
            thing["external_entity_id"] = updates["external_entity_id"] or None

        if "script_entity_id" in updates:
            thing["script_entity_id"] = updates["script_entity_id"] or None

        if "is_odometer" in updates:
            thing["is_odometer"] = bool(updates["is_odometer"])
            if thing["is_odometer"] and thing.get("last_reset_value") is None:
                thing["last_reset_value"] = float(thing.get("current_value", 0))

        if "last_reset_value" in updates:
            l_val = updates["last_reset_value"]
            if l_val is not None and str(l_val).strip() not in ("", "None", "null"):
                try:
                    thing["last_reset_value"] = float(l_val)
                except (ValueError, TypeError):
                    pass
            elif thing.get("is_odometer"):
                thing["last_reset_value"] = float(thing.get("current_value", 0))
            else:
                thing["last_reset_value"] = None

        if is_thing_threshold_reached(thing):
            today_str = dt_util.now().date().strftime("%Y-%m-%d")
            for task in self.tasks:
                if task.get("linked_thing_id") == thing_id and task.get("status") == "pending":
                    if task.get("due_date") != today_str:
                        task["due_date"] = today_str
                        self._log_activity("task_threshold_triggered", {
                            "task_id": task["id"],
                            "title": task["title"],
                            "thing_id": thing_id,
                            "due_date": today_str,
                        })
        return thing

    def update_thing_value(
        self,
        thing_id: str,
        value: float | None = None,
        delta: float | None = None,
        reset: bool = False,
    ) -> dict[str, Any] | None:
        """Update or reset a thing's value."""
        thing = self.get_thing(thing_id)
        if not thing:
            return None

        now_str = dt_util.now().isoformat()
        today_str = dt_util.now().date().strftime("%Y-%m-%d")

        if reset:
            if bool(thing.get("is_odometer", False)):
                thing["last_reset_value"] = float(thing.get("current_value", 0))
                thing["last_reset"] = now_str
            else:
                operator = thing.get("threshold_operator", THRESHOLD_OP_GTE)
                if operator in (THRESHOLD_OP_LTE, "lte", "down", "countdown", "<"):
                    thing["current_value"] = float(thing.get("initial_value", 100))
                else:
                    thing["current_value"] = 0.0
                thing["last_reset"] = now_str
        elif value is not None:
            thing["current_value"] = float(value)
            if bool(thing.get("is_odometer", False)) and thing.get("last_reset_value") is None:
                thing["last_reset_value"] = float(value)
        elif delta is not None:
            cur = float(thing.get("current_value", 0))
            thing["current_value"] = max(0.0, cur + float(delta))
            if bool(thing.get("is_odometer", False)) and thing.get("last_reset_value") is None:
                thing["last_reset_value"] = thing["current_value"]

        # Check threshold
        if is_thing_threshold_reached(thing):
            # 1. Update any existing pending tasks linked to this thing
            for task in self.tasks:
                if task.get("linked_thing_id") == thing_id and task.get("status") == "pending":
                    if task.get("due_date") != today_str:
                        task["due_date"] = today_str
                        self._log_activity("task_threshold_triggered", {
                            "task_id": task["id"],
                            "title": task["title"],
                            "thing_id": thing_id,
                            "due_date": today_str,
                        })

            # 2. Update external overlays linked to this thing
            for uid, overlay in self.external_overlays.items():
                if overlay.get("linked_thing_id") == thing_id:
                    overlay["due_date"] = today_str

            # 3. Auto-task creation if enabled
            if thing.get("auto_task_creation"):
                title = thing.get("auto_task_title") or f"Maintain {thing['name']}"
                existing = any(
                    (t.get("linked_thing_id") == thing_id or t.get("title") == title)
                    and t.get("status") == "pending"
                    for t in self.tasks
                )
                if not existing:
                    cur = float(thing.get("current_value", 0))
                    target = float(thing.get("target_value", 0))
                    self.create_task({
                        "title": title,
                        "description": f"Automatically generated by Thing '{thing['name']}' (Reached {cur}/{target} {thing.get('unit', '')}).",
                        "priority": PRIORITIES[0],  # P1
                        "linked_thing_id": thing_id,
                        "thing_action": THING_ACTION_RESET,
                        "due_date": today_str,
                    })

        self._log_activity("thing_value_updated", {
            "thing_id": thing_id,
            "name": thing["name"],
            "current_value": thing["current_value"],
        })
        return thing

    def delete_thing(self, thing_id: str) -> bool:
        """Delete thing by id."""
        for i, th in enumerate(self.things):
            if th.get("id") == thing_id:
                name = th.get("name", "")
                self.things.pop(i)
                self._log_activity("thing_deleted", {"thing_id": thing_id, "name": name})
                return True
        return False

    # ================= PARTS OPERATIONS =================

    def get_parts(self, thing_id: str | None = None) -> list[dict[str, Any]]:
        """Retrieve all parts, optionally filtered by thing_id."""
        if thing_id is not None:
            return [p for p in self.parts if p.get("thing_id") == thing_id]
        return list(self.parts)

    def get_part(self, part_id: str) -> dict[str, Any] | None:
        """Retrieve part by id."""
        for p in self.parts:
            if p.get("id") == part_id:
                return p
        return None

    def create_part(self, part_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new spare part or consumable."""
        part_id = part_data.get("id") or str(uuid.uuid4())
        try:
            stock = float(part_data.get("stock", 0))
        except (ValueError, TypeError):
            stock = 0.0

        try:
            min_stock = float(part_data.get("min_stock", part_data.get("reorder_threshold", 1)))
        except (ValueError, TypeError):
            min_stock = 1.0

        raw_unit_price = part_data.get("unit_price")
        if raw_unit_price is None:
            raw_unit_price = part_data.get("unit_cost", 0.0)
        try:
            unit_price = float(raw_unit_price)
        except (ValueError, TypeError):
            unit_price = 0.0

        new_part = {
            "id": part_id,
            "name": part_data.get("name", "New Part"),
            "thing_id": part_data.get("thing_id") or None,
            "part_number": part_data.get("part_number", ""),
            "stock": stock,
            "min_stock": min_stock,
            "unit": part_data.get("unit", "pcs"),
            "unit_price": unit_price,
            "storage_location": part_data.get("storage_location", ""),
            "reorder_url": part_data.get("reorder_url", ""),
            "notes": part_data.get("notes", ""),
        }
        self.parts.append(new_part)
        self._log_activity("part_created", {"part_id": part_id, "name": new_part["name"]})
        return new_part

    def update_part(self, part_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        """Update part details."""
        part = self.get_part(part_id)
        if not part:
            return None
        for key, val in updates.items():
            if key != "id":
                if key in ("stock", "min_stock", "unit_price", "unit_cost"):
                    target_key = "unit_price" if key == "unit_cost" else key
                    try:
                        part[target_key] = float(val)
                    except (ValueError, TypeError):
                        pass
                else:
                    part[key] = val
        self._log_activity("part_updated", {"part_id": part_id, "name": part.get("name")})
        return part

    def delete_part(self, part_id: str) -> bool:
        """Delete part by id."""
        for i, p in enumerate(self.parts):
            if p.get("id") == part_id:
                name = p.get("name", "")
                self.parts.pop(i)
                self._log_activity("part_deleted", {"part_id": part_id, "name": name})
                return True
        return False

    def adjust_part_stock(
        self,
        part_id: str,
        delta: float | None = None,
        stock: float | None = None,
    ) -> dict[str, Any] | None:
        """Adjust or set part stock directly."""
        part = self.get_part(part_id)
        if not part:
            return None
        if stock is not None:
            part["stock"] = max(0.0, float(stock))
        elif delta is not None:
            part["stock"] = max(0.0, float(part.get("stock", 0)) + float(delta))
        self._log_activity("part_stock_adjusted", {
            "part_id": part_id,
            "name": part.get("name"),
            "stock": part.get("stock"),
        })
        return part

    # ================= USER OPERATIONS =================

    def get_users(self) -> list[dict[str, Any]]:
        """Retrieve all users."""
        return list(self.users)

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        """Retrieve user by id."""
        for u in self.users:
            if u.get("id") == user_id:
                return u
        return None

    def create_user(self, user_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new user/household member."""
        user_id = user_data.get("id") or str(uuid.uuid4())
        new_user = {
            "id": user_id,
            "name": user_data.get("name", "User"),
            "color": user_data.get("color", "#3b82f6"),
            "avatar": user_data.get("avatar", "mdi:account"),
            "points": int(user_data.get("points", 0)),
            "streak": int(user_data.get("streak", 0)),
            "last_completed_date": "",
            "completed_count": 0,
        }
        self.users.append(new_user)
        self._log_activity("user_created", {"user_id": user_id, "name": new_user["name"]})
        return new_user

    def update_user(self, user_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        """Update existing user properties."""
        user = self.get_user(user_id)
        if not user:
            return None
        for key, val in updates.items():
            if key != "id":
                user[key] = val
        return user

    def award_points(self, user_id: str, points: int, reason: str = "") -> dict[str, Any] | None:
        """Manually award or deduct points for a user."""
        user = self.get_user(user_id)
        if not user:
            return None
        user["points"] = max(0, user.get("points", 0) + points)
        self._log_activity("points_awarded", {
            "user_id": user_id,
            "name": user["name"],
            "points": points,
            "reason": reason,
        })
        return user

    def delete_user(self, user_id: str) -> bool:
        """Delete user by id."""
        for i, u in enumerate(self.users):
            if u.get("id") == user_id:
                name = u.get("name", "")
                self.users.pop(i)
                # Remove user from current_assignee if assigned
                for t in self.tasks:
                    if t.get("current_assignee") == user_id:
                        t["current_assignee"] = None
                    if user_id in t.get("assignees", []):
                        t["assignees"] = [a for a in t["assignees"] if a != user_id]
                self._log_activity("user_deleted", {"user_id": user_id, "name": name})
                return True
        return False

    # ================= LABEL OPERATIONS =================

    def get_label(self, label_id: str) -> dict[str, Any] | None:
        """Retrieve label by id."""
        for lb in self.labels:
            if lb.get("id") == label_id:
                return lb
        return None

    def create_label(self, label_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new label."""
        label_id = label_data.get("id") or str(uuid.uuid4())
        new_label = {
            "id": label_id,
            "name": label_data.get("name", "New Label"),
            "color": label_data.get("color", "#64748b"),
            "icon": label_data.get("icon", "mdi:tag"),
        }
        self.labels.append(new_label)
        return new_label

    def update_label(self, label_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        """Update label properties."""
        label = self.get_label(label_id)
        if not label:
            return None
        for key, val in updates.items():
            if key != "id":
                label[key] = val
        return label

    def delete_label(self, label_id: str) -> bool:
        """Delete label by id."""
        for i, lb in enumerate(self.labels):
            if lb.get("id") == label_id:
                self.labels.pop(i)
                # Remove label from tasks
                for t in self.tasks:
                    if label_id in t.get("labels", []):
                        t["labels"] = [l for l in t["labels"] if l != label_id]
                return True
        return False

    # ================= PROVIDER OPERATIONS =================

    def get_providers(self) -> list[dict[str, Any]]:
        """Get all configured external providers."""
        return list(self.providers)

    def add_provider(
        self,
        entity_id: str,
        name: str = "",
        provider_type: str = "generic",
        icon: str = "mdi:format-list-checks",
    ) -> dict[str, Any]:
        """Add or update an external provider."""
        for p in self.providers:
            if p.get("entity_id") == entity_id:
                p["name"] = name or p.get("name", entity_id)
                p["provider_type"] = provider_type or p.get("provider_type", "generic")
                p["icon"] = icon or p.get("icon", "mdi:format-list-checks")
                self._log_activity("provider_updated", {"entity_id": entity_id, "name": p["name"]})
                return p

        provider = {
            "entity_id": entity_id,
            "name": name or entity_id,
            "provider_type": provider_type,
            "icon": icon,
        }
        self.providers.append(provider)
        self._log_activity("provider_added", {"entity_id": entity_id, "name": provider["name"]})
        return provider

    def remove_provider(self, entity_id: str) -> bool:
        """Remove a linked provider."""
        for i, p in enumerate(self.providers):
            if p.get("entity_id") == entity_id:
                self.providers.pop(i)
                self.external_tasks_cache.pop(entity_id, None)
                self._log_activity("provider_removed", {"entity_id": entity_id})
                return True
        return False

    def get_overlay(self, uid: str) -> dict[str, Any]:
        """Get local overlay data for an external task."""
        return self.external_overlays.get(uid, {})

    def set_overlay(self, uid: str, overlay: dict[str, Any]) -> None:
        """Set or update overlay data for an external task."""
        cur = self.external_overlays.setdefault(uid, {})
        cur.update(overlay)

    def delete_overlay(self, uid: str) -> None:
        """Delete overlay for an external task."""
        self.external_overlays.pop(uid, None)

    def get_all_tasks(self, include_external: bool = True) -> list[dict[str, Any]]:
        """Return all tasks, optionally merging external provider tasks."""
        all_tasks = [dict(t) for t in self.tasks]
        if not include_external:
            return all_tasks

        for provider in self.providers:
            e_id = provider.get("entity_id", "")
            raw_items = self.external_tasks_cache.get(e_id, [])
            for item in raw_items:
                uid = str(item.get("uid", ""))
                overlay = self.external_overlays.get(uid, {})
                merged = {
                    "id": f"ext:{e_id}:{uid}",
                    "external_uid": uid,
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "status": item.get("status", "pending"),
                    "due_date": item.get("due_date"),
                    "due_time": item.get("due_time"),
                    "is_external": True,
                    "provider_entity_id": e_id,
                    "provider_name": provider.get("name", e_id),
                    "provider_type": provider.get("provider_type", "generic"),
                    "provider_icon": provider.get("icon", "mdi:format-list-checks"),
                    "priority": overlay.get("priority", PRIORITY_NONE),
                    "assignees": overlay.get("assignees", []),
                    "current_assignee": overlay.get("current_assignee"),
                    "rotation_mode": overlay.get("rotation_mode", ROTATION_NONE),
                    "labels": overlay.get("labels", []),
                    "tags": overlay.get("tags", []),
                    "is_active": overlay.get("is_active", True),
                    "active_override": overlay.get("active_override"),
                    "task_interval_override": overlay.get("task_interval_override"),
                    "due_soon_override": overlay.get("due_soon_override"),
                    "due_soon_days": int(overlay.get("due_soon_days", 0)),
                    "notification_interval": int(overlay.get("notification_interval", 1)),
                    "dependencies": overlay.get("dependencies", []),
                    "times_completed": int(overlay.get("times_completed", 0)),
                    "last_done_date": overlay.get("last_done_date", ""),
                    "subtasks": overlay.get("subtasks", []),
                    "points": int(overlay.get("points", self.settings.get("default_points", 10))),
                    "linked_thing_id": overlay.get("linked_thing_id"),
                    "thing_action": overlay.get("thing_action", THING_ACTION_RESET),
                    "recurrence": overlay.get("recurrence", {
                        "enabled": False,
                        "type": RECURRENCE_NONE,
                        "interval": 1,
                        "days_of_week": [],
                        "based_on": RECURRENCE_BASED_DUE_DATE,
                    }),
                    "created_at": overlay.get("created_at", ""),
                    "completed_at": overlay.get("completed_at"),
                    "completed_by": overlay.get("completed_by"),
                    "history": overlay.get("history", []),
                    "reminders": overlay.get("reminders", []),
                    "repetition_count": overlay.get("repetition_count", 0),
                }
                all_tasks.append(merged)

        return all_tasks

    # ================= SETTINGS & IMPORT =================

    def update_settings(self, new_settings: dict[str, Any]) -> dict[str, Any]:
        """Update application settings."""
        self.settings.update(new_settings)
        return self.settings

    def import_data(self, data: dict[str, Any], merge: bool = False) -> None:
        """Import full backup data."""
        if not merge:
            self.tasks = data.get("tasks", [])
            self.things = data.get("things", [])
            self.users = data.get("users", [])
            self.labels = data.get("labels", [])
            self.settings = {**DEFAULT_SETTINGS, **data.get("settings", {})}
            self.parts = data.get("parts", [])
            self.activity_log = data.get("activity_log", [])
            self.providers = data.get("providers", [])
            self.external_overlays = data.get("external_overlays", {})
        else:
            # Merge tasks by id
            existing_task_ids = {t["id"] for t in self.tasks}
            for t in data.get("tasks", []):
                if t.get("id") not in existing_task_ids:
                    self.tasks.append(t)
            # Merge things
            existing_thing_ids = {th["id"] for th in self.things}
            for th in data.get("things", []):
                if th.get("id") not in existing_thing_ids:
                    self.things.append(th)
            # Merge parts
            existing_part_ids = {p["id"] for p in self.parts}
            for p in data.get("parts", []):
                if p.get("id") not in existing_part_ids:
                    self.parts.append(p)


class TaskManagerStorage:
    """Home Assistant storage wrapper using JSON Store."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize storage."""
        self.hass = hass
        self.data = TaskManagerData()
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._sync_lock: asyncio.Lock | None = None
        self._sync_pending = False

    async def async_load(self) -> None:
        """Load stored data from disk."""
        try:
            raw = await self._store.async_load()
            if raw:
                self.data = TaskManagerData(raw)
                _LOGGER.info(
                    "Task Manager storage loaded (%d tasks, %d things, %d providers)",
                    len(self.data.tasks),
                    len(self.data.things),
                    len(self.data.providers),
                )
            else:
                self.data = TaskManagerData()
                await self.async_save()
                _LOGGER.info("Task Manager initialized with default dataset")
        except Exception as err:
            _LOGGER.error("Failed to load Task Manager storage: %s", err)
            self.data = TaskManagerData()

    async def async_save(self) -> None:
        """Save data to disk and notify listening platforms."""
        try:
            await self._store.async_save(self.data.to_dict())
            async_dispatcher_send(self.hass, SIGNAL_TASK_MANAGER_UPDATED)
        except Exception as err:
            _LOGGER.error("Failed to save Task Manager storage: %s", err)

    def get_all_tasks(self, include_external: bool = True) -> list[dict[str, Any]]:
        """Get all tasks, including external if requested."""
        return self.data.get_all_tasks(include_external=include_external)

    def get_view_data(self) -> dict[str, Any]:
        """Return view data with merged external tasks for UI and WebSocket."""
        data = self.data.to_dict()
        data["tasks"] = self.data.get_all_tasks(include_external=True)
        return data

    async def async_sync_providers(self) -> None:
        """Fetch items from all configured external providers with concurrency control."""
        if not hasattr(self, "_sync_lock") or self._sync_lock is None:
            self._sync_lock = asyncio.Lock()

        if self._sync_lock.locked():
            self._sync_pending = True
            return

        async with self._sync_lock:
            while True:
                self._sync_pending = False
                for provider in self.data.providers:
                    e_id = provider.get("entity_id")
                    if not e_id:
                        continue
                    try:
                        items = await async_read_external_tasks(self.hass, e_id)
                        self.data.external_tasks_cache[e_id] = items
                    except Exception as err:
                        _LOGGER.error("Error syncing provider %s: %s", e_id, err)
                async_dispatcher_send(self.hass, SIGNAL_TASK_MANAGER_UPDATED)
                if not getattr(self, "_sync_pending", False):
                    break

    def fire_task_event(
        self,
        event_type: str,
        task: dict[str, Any],
        extra: dict[str, Any] | None = None,
    ) -> None:
        """Fire a standardized task event to Home Assistant's event bus."""
        if not self.hass:
            return
        event_data = {
            "task_id": task.get("id"),
            "task_title": task.get("title", ""),
            "due_date": task.get("due_date"),
            "due_time": task.get("due_time"),
            "priority": task.get("priority", PRIORITY_NONE),
            "status": task.get("status", "pending"),
            "assignee": task.get("current_assignee"),
            "points": task.get("points", 0),
            "tags": task.get("labels", []),
            "reminders": task.get("reminders", []),
            "is_external": bool(task.get("is_external", False)),
        }
        if task.get("is_external"):
            event_data["provider_entity_id"] = task.get("provider_entity_id")
            event_data["provider_name"] = task.get("provider_name")
        if extra:
            event_data.update(extra)
        self.hass.bus.async_fire(event_type, event_data)

    async def async_duplicate_task(self, task_id: str) -> dict[str, Any] | None:
        """Duplicate an internal or external task and persist."""
        all_tasks = self.data.get_all_tasks(include_external=True)
        task = next((t for t in all_tasks if t.get("id") == task_id or t.get("title", "").strip().lower() == task_id.strip().lower()), None)
        if not task:
            return None

        # If external, clone into local task
        if task.get("is_external"):
            clone_payload = {
                "title": f"{task.get('title', 'Task')} (Copy)",
                "description": task.get("description", ""),
                "due_date": task.get("due_date"),
                "due_time": task.get("due_time"),
                "priority": task.get("priority", PRIORITY_NONE),
                "assignees": task.get("assignees", []),
                "current_assignee": task.get("current_assignee"),
                "rotation_mode": task.get("rotation_mode", ROTATION_NONE),
                "labels": task.get("labels", []),
                "subtasks": [{"id": str(uuid.uuid4()), "title": st.get("title", ""), "completed": False} for st in task.get("subtasks", [])],
                "points": task.get("points", 10),
                "recurrence": copy.deepcopy(task.get("recurrence", {})),
                "reminders": list(task.get("reminders", [])),
            }
            new_task = self.data.create_task(clone_payload)
            await self.async_save()
            self.fire_task_event(EVENT_TASK_CREATED, new_task)
            return new_task

        new_task = self.data.duplicate_task(task["id"])
        if new_task:
            await self.async_save()
            self.fire_task_event(EVENT_TASK_CREATED, new_task)
        return new_task

    async def async_move_task(self, task_id: str, target_provider: str) -> dict[str, Any] | None:
        """Move a task to another provider or back to task_manager."""
        all_tasks = self.data.get_all_tasks(include_external=True)
        task = next((t for t in all_tasks if t.get("id") == task_id or t.get("title", "").strip().lower() == task_id.strip().lower()), None)
        if not task:
            return None

        title = task.get("title", "")
        description = task.get("description", "")
        due_date = task.get("due_date")
        due_time = task.get("due_time")
        priority = task.get("priority", PRIORITY_NONE)
        assignees = task.get("assignees", [])
        current_assignee = task.get("current_assignee")
        labels = task.get("labels", [])
        subtasks = task.get("subtasks", [])
        points = task.get("points", 10)
        recurrence = task.get("recurrence", {})
        reminders = task.get("reminders", [])

        # 1. Delete from old location
        await self.async_delete_task(task["id"])

        # 2. Create in new location
        if target_provider and target_provider != "task_manager":
            created_res = await async_create_external_task(
                self.hass,
                target_provider,
                title=title,
                due_date=due_date,
                due_time=due_time,
                description=description,
            )
            await self.async_sync_providers()
            if isinstance(created_res, dict) and created_res.get("uid"):
                self.data.set_overlay(str(created_res["uid"]), {
                    "priority": priority,
                    "assignees": assignees,
                    "current_assignee": current_assignee,
                    "labels": labels,
                    "subtasks": subtasks,
                    "points": points,
                    "recurrence": recurrence,
                    "reminders": reminders,
                })
                await self.async_save()
            return {"title": title, "destination": target_provider}
        else:
            new_task = self.data.create_task({
                "title": title,
                "description": description,
                "due_date": due_date,
                "due_time": due_time,
                "priority": priority,
                "assignees": assignees,
                "current_assignee": current_assignee,
                "labels": labels,
                "subtasks": subtasks,
                "points": points,
                "recurrence": recurrence,
                "reminders": reminders,
            })
            await self.async_save()
            self.fire_task_event(EVENT_TASK_CREATED, new_task)
            return new_task

    async def async_complete_task(
        self,
        task_id: str,
        user_id: str | None = None,
        cost: float | None = None,
        duration_minutes: int | None = None,
        notes: str | None = None,
        completed_at: str | None = None,
        reading_value: float | None = None,
        consumed_parts: list[dict[str, Any]] | None = None,
        readings: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any] | None:
        """Complete an internal or external task."""
        if task_id.startswith("ext:"):
            parts = task_id.split(":", 2)
            if len(parts) < 3:
                return None
            e_id, uid = parts[1], parts[2]

            existing_task = None
            for t in self.data.get_all_tasks(include_external=True):
                if t.get("id") == task_id:
                    existing_task = dict(t)
                    break

            if not existing_task:
                cached_items = self.data.external_tasks_cache.get(e_id, [])
                target_item = next((i for i in cached_items if str(i.get("uid")) == uid), None)
                provider = next((p for p in self.data.providers if p.get("entity_id") == e_id), {})
                overlay = self.data.get_overlay(uid)
                if target_item or overlay or provider:
                    existing_task = {
                        "id": task_id,
                        "external_uid": uid,
                        "title": target_item.get("title", "") if target_item else overlay.get("title", "External Task"),
                        "description": target_item.get("description", "") if target_item else "",
                        "status": "pending",
                        "due_date": target_item.get("due_date") if target_item else None,
                        "due_time": target_item.get("due_time") if target_item else None,
                        "is_external": True,
                        "provider_entity_id": e_id,
                        "provider_name": provider.get("name", e_id),
                        "provider_type": provider.get("provider_type", "generic"),
                        "provider_icon": provider.get("icon", "mdi:format-list-checks"),
                        "priority": overlay.get("priority", PRIORITY_NONE),
                        "assignees": overlay.get("assignees", []),
                        "current_assignee": overlay.get("current_assignee"),
                    }
                else:
                    return None

            await async_update_external_task(self.hass, e_id, uid, status="completed")

            cached_items = self.data.external_tasks_cache.get(e_id, [])
            target_item = next((i for i in cached_items if str(i.get("uid")) == uid), None)
            if target_item:
                target_item["status"] = "completed"

            overlay = self.data.get_overlay(uid)
            effective_user = user_id or overlay.get("current_assignee")
            points = int(overlay.get("points", self.data.settings.get("default_points", 10)))

            if effective_user and self.data.settings.get("gamification_enabled", True):
                u = self.data.get_user(effective_user)
                if u:
                    u["points"] = u.get("points", 0) + points
                    u["completed_count"] = u.get("completed_count", 0) + 1

            now_str = completed_at or dt_util.now().isoformat()
            overlay["completed_at"] = now_str
            overlay["completed_by"] = effective_user
            hist_item = {
                "completed_at": now_str,
                "user_id": effective_user,
                "points": points,
            }
            if cost is not None:
                hist_item["cost"] = cost
            if duration_minutes is not None:
                hist_item["duration_minutes"] = duration_minutes
            if notes:
                hist_item["notes"] = notes
            overlay.setdefault("history", []).append(hist_item)
            self.data.set_overlay(uid, overlay)

            linked_thing_id = overlay.get("linked_thing_id")
            thing_action = overlay.get("thing_action", THING_ACTION_RESET)
            if linked_thing_id:
                thing = self.data.get_thing(linked_thing_id)
                if thing:
                    if thing_action == THING_ACTION_RESET:
                        operator = thing.get("threshold_operator", THRESHOLD_OP_GTE)
                        if operator in (THRESHOLD_OP_LTE, "lte", "down", "countdown", "<"):
                            thing["current_value"] = float(thing.get("initial_value", 100))
                        else:
                            thing["current_value"] = 0.0
                        thing["last_reset"] = now_str
                    elif thing_action == THING_ACTION_INCREMENT:
                        thing["current_value"] = thing.get("current_value", 0) + 1
                    elif thing_action == THING_ACTION_DECREMENT:
                        thing["current_value"] = max(0, thing.get("current_value", 0) - 1)
                    if thing.get("script_entity_id"):
                        await self._async_run_thing_script(thing.get("script_entity_id"), thing)

            await self.async_save()

            completed_task = dict(existing_task)
            completed_task["status"] = "completed"
            completed_task["completed_at"] = now_str
            completed_task["completed_by"] = effective_user

            for t in self.data.get_all_tasks(include_external=True):
                if t.get("id") == task_id:
                    completed_task = t
                    break

            self.fire_task_event(EVENT_TASK_COMPLETED, completed_task, {"user_id": effective_user})
            return completed_task

        # Internal task
        task = self.data.complete_task(
            task_id,
            user_id=user_id,
            cost=cost,
            duration_minutes=duration_minutes,
            notes=notes,
            completed_at=completed_at,
            reading_value=reading_value,
            consumed_parts=consumed_parts,
            hass=self.hass,
            readings=readings,
        )
        if task:
            linked_thing_id = task.get("linked_thing_id")
            if linked_thing_id:
                thing = self.data.get_thing(linked_thing_id)
                if thing and thing.get("script_entity_id"):
                    await self._async_run_thing_script(thing.get("script_entity_id"), thing)
            if task.get("on_complete_entity_id"):
                await self._async_trigger_entity_action(task.get("on_complete_entity_id"))
            await self.async_save()
            self.fire_task_event(EVENT_TASK_COMPLETED, task, {"user_id": user_id or task.get("current_assignee")})
        return task

    async def _async_run_thing_script(self, script_entity_id: str, thing: dict[str, Any]) -> None:
        """Execute the configured Home Assistant script for a thing upon task completion."""
        if not script_entity_id or not self.hass or not hasattr(self.hass, "services"):
            return
        script_eid = script_entity_id.strip()
        _LOGGER.info(
            "Task Manager: Triggering script '%s' after completing task for thing '%s'",
            script_eid,
            thing.get("name"),
        )
        try:
            if script_eid.startswith("script."):
                await self.hass.services.async_call(
                    "script", "turn_on", {"entity_id": script_eid}, blocking=False
                )
            else:
                await self.hass.services.async_call("script", script_eid, {}, blocking=False)
            self.data._log_activity("thing_script_triggered", {
                "thing_id": thing.get("id"),
                "thing_name": thing.get("name"),
                "script_entity_id": script_eid,
            })
        except Exception as err:
            _LOGGER.error("Task Manager: Failed to run completion script '%s': %s", script_eid, err)

    async def _async_trigger_entity_action(self, entity_id: str) -> None:
        """Trigger an entity action (press button, run script, turn on switch) on completion."""
        if not entity_id or not self.hass or not hasattr(self.hass, "services"):
            return
        entity_id = entity_id.strip()
        try:
            domain = entity_id.split(".", 1)[0]
            if domain == "button":
                await self.hass.services.async_call("button", "press", {"entity_id": entity_id}, blocking=False)
            elif domain == "script":
                await self.hass.services.async_call("script", "turn_on", {"entity_id": entity_id}, blocking=False)
            elif domain == "input_button":
                await self.hass.services.async_call("input_button", "press", {"entity_id": entity_id}, blocking=False)
            else:
                await self.hass.services.async_call("homeassistant", "turn_on", {"entity_id": entity_id}, blocking=False)
        except Exception as err:
            _LOGGER.error("Task Manager: Failed to trigger on_complete action '%s': %s", entity_id, err)

    async def async_skip_task(self, task_id: str) -> dict[str, Any] | None:
        """Skip the current recurrence of a task."""
        task = self.data.skip_task(task_id)
        if task:
            await self.async_save()
            self.fire_task_event(EVENT_TASK_SKIPPED, task)
        return task

    async def async_record_reading(
        self,
        task_id: str,
        reading_value: float | None = None,
        notes: str | None = None,
        completed_at: str | None = None,
        user_id: str | None = None,
        readings: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any] | None:
        """Record reading and complete task recurrence."""
        return await self.async_complete_task(
            task_id=task_id,
            user_id=user_id,
            notes=notes,
            completed_at=completed_at,
            reading_value=reading_value,
            readings=readings,
        )

    async def async_delete_task_history_entry(
        self,
        task_id: str,
        entry_index: int | None = None,
        completed_at: str | None = None,
    ) -> bool:
        """Delete a history entry and persist."""
        res = self.data.delete_task_history_entry(task_id, entry_index=entry_index, completed_at=completed_at)
        if res:
            await self.async_save()
        return res

    async def async_create_part(self, part_data: dict[str, Any]) -> dict[str, Any]:
        """Create part and persist."""
        part = self.data.create_part(part_data)
        await self.async_save()
        if is_part_low_stock(part) and self.hass:
            self.hass.bus.async_fire(EVENT_PART_LOW_STOCK, {
                "part_id": part["id"],
                "name": part["name"],
                "stock": part["stock"],
                "min_stock": part["min_stock"],
            })
        return part

    async def async_update_part(self, part_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        """Update part and persist."""
        part = self.data.update_part(part_id, updates)
        if part:
            await self.async_save()
            if is_part_low_stock(part) and self.hass:
                self.hass.bus.async_fire(EVENT_PART_LOW_STOCK, {
                    "part_id": part["id"],
                    "name": part["name"],
                    "stock": part["stock"],
                    "min_stock": part["min_stock"],
                })
        return part

    async def async_delete_part(self, part_id: str) -> bool:
        """Delete part and persist."""
        res = self.data.delete_part(part_id)
        if res:
            await self.async_save()
        return res

    async def async_adjust_part_stock(
        self,
        part_id: str,
        delta: float | None = None,
        stock: float | None = None,
    ) -> dict[str, Any] | None:
        """Adjust part stock and persist."""
        part = self.data.adjust_part_stock(part_id, delta=delta, stock=stock)
        if part:
            await self.async_save()
            if is_part_low_stock(part) and self.hass:
                self.hass.bus.async_fire(EVENT_PART_LOW_STOCK, {
                    "part_id": part["id"],
                    "name": part["name"],
                    "stock": part["stock"],
                    "min_stock": part["min_stock"],
                })
        return part

    async def async_reset_task(self, task_id: str) -> dict[str, Any] | None:
        """Reset an internal or external task."""
        if task_id.startswith("ext:"):
            parts = task_id.split(":", 2)
            if len(parts) < 3:
                return None
            e_id, uid = parts[1], parts[2]

            existing_task = None
            for t in self.data.get_all_tasks(include_external=True):
                if t.get("id") == task_id:
                    existing_task = dict(t)
                    break

            if not existing_task:
                cached_items = self.data.external_tasks_cache.get(e_id, [])
                target_item = next((i for i in cached_items if str(i.get("uid")) == uid), None)
                provider = next((p for p in self.data.providers if p.get("entity_id") == e_id), {})
                overlay = self.data.get_overlay(uid)
                if target_item or overlay or provider:
                    existing_task = {
                        "id": task_id,
                        "external_uid": uid,
                        "title": target_item.get("title", "") if target_item else overlay.get("title", "External Task"),
                        "description": target_item.get("description", "") if target_item else "",
                        "status": "completed",
                        "due_date": target_item.get("due_date") if target_item else None,
                        "due_time": target_item.get("due_time") if target_item else None,
                        "is_external": True,
                        "provider_entity_id": e_id,
                        "provider_name": provider.get("name", e_id),
                        "provider_type": provider.get("provider_type", "generic"),
                        "provider_icon": provider.get("icon", "mdi:format-list-checks"),
                        "priority": overlay.get("priority", PRIORITY_NONE),
                        "assignees": overlay.get("assignees", []),
                        "current_assignee": overlay.get("current_assignee"),
                    }
                else:
                    return None

            await async_update_external_task(self.hass, e_id, uid, status="needs_action")

            cached_items = self.data.external_tasks_cache.get(e_id, [])
            target_item = next((i for i in cached_items if str(i.get("uid")) == uid), None)
            if target_item:
                target_item["status"] = "pending"
            elif existing_task:
                self.data.external_tasks_cache.setdefault(e_id, []).append({
                    "uid": uid,
                    "title": existing_task.get("title", ""),
                    "description": existing_task.get("description", ""),
                    "status": "pending",
                    "due_date": existing_task.get("due_date"),
                    "due_time": existing_task.get("due_time"),
                })

            overlay = self.data.get_overlay(uid)
            overlay["completed_at"] = None
            overlay["completed_by"] = None
            self.data.set_overlay(uid, overlay)

            await self.async_save()

            reset_task = dict(existing_task)
            reset_task["status"] = "pending"
            reset_task["completed_at"] = None
            reset_task["completed_by"] = None

            for t in self.data.get_all_tasks(include_external=True):
                if t.get("id") == task_id:
                    reset_task = t
                    break

            self.fire_task_event(EVENT_TASK_REOPENED, reset_task)
            return reset_task

        task = self.data.reset_task(task_id)
        if task:
            await self.async_save()
            self.fire_task_event(EVENT_TASK_REOPENED, task)
        return task

    async def async_set_last_done_date(self, task_id: str, new_date: str) -> dict[str, Any] | None:
        """Set the last done date of a task explicitly and recalculate the next due date."""
        task = self.data.set_last_done_date(task_id, new_date)
        if task:
            await self.async_save()
            self.fire_task_event(EVENT_TASK_COMPLETED, task, {"manual_date": new_date})
        return task

    async def async_pause_task(self, task_id: str) -> dict[str, Any] | None:
        """Pause / deactivate a task."""
        task = self.data.pause_task(task_id)
        if task:
            await self.async_save()
        return task

    async def async_resume_task(self, task_id: str) -> dict[str, Any] | None:
        """Resume / activate a task."""
        task = self.data.resume_task(task_id)
        if task:
            await self.async_save()
        return task

    async def async_delete_task(self, task_id: str) -> bool:
        """Delete an internal or external task."""
        if task_id.startswith("ext:"):
            parts = task_id.split(":", 2)
            if len(parts) < 3:
                return False
            e_id, uid = parts[1], parts[2]
            await async_delete_external_task(self.hass, e_id, uid)
            self.data.delete_overlay(uid)
            cached_items = self.data.external_tasks_cache.get(e_id, [])
            self.data.external_tasks_cache[e_id] = [i for i in cached_items if str(i.get("uid")) != uid]
            await self.async_save()
            return True

        ok = self.data.delete_task(task_id)
        if ok:
            await self.async_save()
        return ok

    async def async_save_task(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Save (create or update) a task, routing to external provider if applicable."""
        task_id = task_data.get("id", "")
        dest_provider = task_data.get("destination_provider")

        if task_id.startswith("ext:"):
            parts = task_id.split(":", 2)
            e_id, uid = parts[1], parts[2]
            await async_update_external_task(
                self.hass,
                e_id,
                uid,
                title=task_data.get("title"),
                due_date=task_data.get("due_date"),
                due_time=task_data.get("due_time"),
                description=task_data.get("description"),
            )
            overlay = {
                "priority": task_data.get("priority", PRIORITY_NONE),
                "assignees": task_data.get("assignees", []),
                "current_assignee": task_data.get("current_assignee"),
                "rotation_mode": task_data.get("rotation_mode", ROTATION_NONE),
                "labels": task_data.get("labels", []),
                "tags": task_data.get("tags", []),
                "is_active": task_data.get("is_active", True),
                "active_override": task_data.get("active_override"),
                "task_interval_override": task_data.get("task_interval_override"),
                "due_soon_override": task_data.get("due_soon_override"),
                "due_soon_days": int(task_data.get("due_soon_days", 0)),
                "notification_interval": int(task_data.get("notification_interval", 1)),
                "dependencies": task_data.get("dependencies", []),
                "times_completed": int(task_data.get("times_completed", 0)),
                "last_done_date": task_data.get("last_done_date", ""),
                "points": int(task_data.get("points", self.data.settings.get("default_points", 10))),
                "linked_thing_id": task_data.get("linked_thing_id"),
                "thing_action": task_data.get("thing_action", THING_ACTION_RESET),
                "subtasks": task_data.get("subtasks", []),
                "reminders": task_data.get("reminders", []),
                "recurrence": task_data.get("recurrence", {
                    "enabled": False,
                    "type": RECURRENCE_NONE,
                    "interval": 1,
                    "days_of_week": [],
                    "based_on": RECURRENCE_BASED_DUE_DATE,
                }),
            }
            self.data.set_overlay(uid, overlay)
            await self.async_save()
            await self.async_sync_providers()
            for t in self.data.get_all_tasks(include_external=True):
                if t.get("id") == task_id:
                    return t
            return task_data

        if dest_provider and dest_provider != "task_manager":
            await async_create_external_task(
                self.hass,
                dest_provider,
                title=task_data.get("title", "New Task"),
                due_date=task_data.get("due_date"),
                due_time=task_data.get("due_time"),
                description=task_data.get("description"),
            )
            await self.async_sync_providers()
            return {"title": task_data.get("title", ""), "is_external": True}

        is_new = not bool(task_id and self.data.get_task(task_id))
        old_task = self.data.get_task(task_id) if not is_new else None
        old_assignee = old_task.get("current_assignee") if old_task else None

        if not is_new:
            result = self.data.update_task(task_id, task_data)
        else:
            result = self.data.create_task(task_data)
        await self.async_save()

        if result:
            if is_new:
                self.fire_task_event(EVENT_TASK_CREATED, result)
            if result.get("current_assignee") != old_assignee:
                self.fire_task_event(EVENT_TASK_ASSIGNED, result, {"previous_assignee": old_assignee, "new_assignee": result.get("current_assignee")})

        return result or {}
