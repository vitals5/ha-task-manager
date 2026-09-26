"""Data storage and management for the Task Manager integration."""
from __future__ import annotations

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
    ROTATION_LEAST_COMPLETED,
    ROTATION_NONE,
    ROTATION_RANDOM,
    ROTATION_ROUND_ROBIN,
    SIGNAL_TASK_MANAGER_UPDATED,
    STORAGE_KEY,
    STORAGE_VERSION,
    THING_ACTION_DECREMENT,
    THING_ACTION_INCREMENT,
    THING_ACTION_RESET,
)
from .providers import (
    async_create_external_task,
    async_delete_external_task,
    async_read_external_tasks,
    async_update_external_task,
)

_LOGGER = logging.getLogger(__name__)


def calculate_next_due_date(
    current_due_date_str: str,
    recurrence: dict[str, Any],
    completion_date_str: str | None = None,
) -> str:
    """Calculate the next due date based on recurrence configuration."""
    rec_type = recurrence.get("type", RECURRENCE_NONE)
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
            # If the due date was in the past, calculate from the base date, but ensure it lands in the future if desired
        except ValueError:
            base_date = today

    if rec_type in (RECURRENCE_DAILY, RECURRENCE_CUSTOM_DAYS):
        next_date = base_date + timedelta(days=interval)
        # If based on due_date and still in the past, advance to next cycle >= today
        if based_on == RECURRENCE_BASED_DUE_DATE and next_date < today:
            days_behind = (today - next_date).days
            cycles = (days_behind // interval) + 1
            next_date += timedelta(days=cycles * interval)
        return next_date.strftime("%Y-%m-%d")

    if rec_type == RECURRENCE_WEEKLY:
        days_of_week = recurrence.get("days_of_week", [])  # 0=Monday, 6=Sunday
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
            self.activity_log: list[dict[str, Any]] = []
            self.providers: list[dict[str, Any]] = []
            self.external_overlays: dict[str, dict[str, Any]] = {}
        else:
            self.tasks = raw.get("tasks", [])
            self.things = raw.get("things", list(DEFAULT_THINGS))
            self.users = raw.get("users", list(DEFAULT_USERS))
            self.labels = raw.get("labels", list(DEFAULT_LABELS))
            self.settings = {**DEFAULT_SETTINGS, **raw.get("settings", {})}
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

        new_task = {
            "id": task_id,
            "title": task_data.get("title", "New Task"),
            "description": task_data.get("description", ""),
            "due_date": task_data.get("due_date", today_str),
            "due_time": task_data.get("due_time", ""),
            "priority": task_data.get("priority", PRIORITY_NONE),
            "status": "pending",
            "assignees": assignees,
            "current_assignee": current_assignee,
            "rotation_mode": task_data.get("rotation_mode", ROTATION_NONE),
            "labels": task_data.get("labels", []),
            "recurrence": task_data.get("recurrence", {
                "enabled": False,
                "type": RECURRENCE_NONE,
                "interval": 1,
                "days_of_week": [],
                "based_on": RECURRENCE_BASED_DUE_DATE,
            }),
            "subtasks": subtasks,
            "points": int(task_data.get("points", self.settings.get("default_points", 10))),
            "linked_thing_id": task_data.get("linked_thing_id"),
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
            else:
                task[key] = val

        self._log_activity("task_updated", {"task_id": task_id, "title": task["title"]})
        return task

    def complete_task(self, task_id: str, user_id: str | None = None) -> dict[str, Any] | None:
        """Mark a task complete, apply points, rotate assignee, and calculate recurrence."""
        task = self.get_task(task_id)
        if not task:
            return None

        now = dt_util.now()
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
                        diff_days = (now.date() - last_date).days
                        if diff_days == 1:
                            user["streak"] = user.get("streak", 0) + 1
                        elif diff_days > 1:
                            user["streak"] = 1
                    except ValueError:
                        user["streak"] = 1
                else:
                    user["streak"] = 1

                user["last_completed_date"] = today_date_str

        # 2. Record completion history
        task.setdefault("history", []).append({
            "completed_at": now_str,
            "user_id": effective_user_id,
            "points": points_awarded,
        })

        # 3. Linked "Thing" Action (e.g. Filter reset, Dustbin empty)
        linked_thing_id = task.get("linked_thing_id")
        thing_action = task.get("thing_action", THING_ACTION_RESET)
        if linked_thing_id:
            thing = self.get_thing(linked_thing_id)
            if thing:
                if thing_action == THING_ACTION_RESET:
                    thing["current_value"] = 0
                    thing["last_reset"] = now_str
                elif thing_action == THING_ACTION_INCREMENT:
                    thing["current_value"] = thing.get("current_value", 0) + 1
                elif thing_action == THING_ACTION_DECREMENT:
                    thing["current_value"] = max(0, thing.get("current_value", 0) - 1)

        # 4. Handle Recurrence & Subtasks Reset
        rec = task.get("recurrence", {})
        is_recurring = rec.get("enabled", False) and rec.get("type", RECURRENCE_NONE) != RECURRENCE_NONE

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
            task["due_date"] = calculate_next_due_date(
                current_due_date_str=task.get("due_date", today_date_str),
                recurrence=rec,
                completion_date_str=today_date_str,
            )
            task["status"] = "pending"
            task["completed_at"] = None
            task["completed_by"] = None
        else:
            task["status"] = "completed"
            task["completed_at"] = now_str
            task["completed_by"] = effective_user_id

        self._log_activity("task_completed", {
            "task_id": task_id,
            "title": task["title"],
            "user_id": effective_user_id,
            "points": points_awarded,
            "recurring": is_recurring,
        })
        return task

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
        new_thing = {
            "id": thing_id,
            "name": thing_data.get("name", "New Thing"),
            "category": thing_data.get("category", "General"),
            "icon": thing_data.get("icon", "mdi:chart-arc"),
            "current_value": float(thing_data.get("current_value", 0)),
            "target_value": float(thing_data.get("target_value", 100)),
            "unit": thing_data.get("unit", "units"),
            "auto_task_creation": bool(thing_data.get("auto_task_creation", False)),
            "auto_task_title": thing_data.get("auto_task_title", f"Maintain {thing_data.get('name', 'Thing')}"),
            "last_reset": thing_data.get("last_reset", ""),
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

        if reset:
            thing["current_value"] = 0
            thing["last_reset"] = now_str
        elif value is not None:
            thing["current_value"] = float(value)
        elif delta is not None:
            thing["current_value"] = max(0.0, float(thing.get("current_value", 0)) + float(delta))

        # Check threshold for auto task creation
        target = float(thing.get("target_value", 100))
        cur = float(thing.get("current_value", 0))
        if thing.get("auto_task_creation") and target > 0 and cur >= target:
            # Check if auto task already exists and is pending
            title = thing.get("auto_task_title") or f"Maintain {thing['name']}"
            existing = any(
                t.get("title") == title and t.get("status") == "pending"
                for t in self.tasks
            )
            if not existing:
                self.create_task({
                    "title": title,
                    "description": f"Automatically generated by Thing '{thing['name']}' (Reached {cur}/{target} {thing.get('unit')}).",
                    "priority": PRIORITIES[0],  # P1
                    "linked_thing_id": thing_id,
                    "thing_action": THING_ACTION_RESET,
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

    # ================= USER OPERATIONS =================

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


class TaskManagerStorage:
    """Home Assistant storage wrapper using JSON Store."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize storage."""
        self.hass = hass
        self.data = TaskManagerData()
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)

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
        """Fetch items from all configured external providers."""
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

    async def async_complete_task(
        self, task_id: str, user_id: str | None = None
    ) -> dict[str, Any] | None:
        """Complete an internal or external task."""
        if task_id.startswith("ext:"):
            parts = task_id.split(":", 2)
            if len(parts) < 3:
                return None
            e_id, uid = parts[1], parts[2]
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

            now_str = dt_util.now().isoformat()
            overlay["completed_at"] = now_str
            overlay["completed_by"] = effective_user
            overlay.setdefault("history", []).append({
                "completed_at": now_str,
                "user_id": effective_user,
                "points": points,
            })
            self.data.set_overlay(uid, overlay)

            linked_thing_id = overlay.get("linked_thing_id")
            thing_action = overlay.get("thing_action", THING_ACTION_RESET)
            if linked_thing_id:
                thing = self.data.get_thing(linked_thing_id)
                if thing:
                    if thing_action == THING_ACTION_RESET:
                        thing["current_value"] = 0
                        thing["last_reset"] = now_str
                    elif thing_action == THING_ACTION_INCREMENT:
                        thing["current_value"] = thing.get("current_value", 0) + 1
                    elif thing_action == THING_ACTION_DECREMENT:
                        thing["current_value"] = max(0, thing.get("current_value", 0) - 1)

            await self.async_save()
            for t in self.data.get_all_tasks(include_external=True):
                if t.get("id") == task_id:
                    return t
            return None

        # Internal task
        task = self.data.complete_task(task_id, user_id=user_id)
        if task:
            await self.async_save()
        return task

    async def async_reset_task(self, task_id: str) -> dict[str, Any] | None:
        """Reset an internal or external task."""
        if task_id.startswith("ext:"):
            parts = task_id.split(":", 2)
            if len(parts) < 3:
                return None
            e_id, uid = parts[1], parts[2]
            await async_update_external_task(self.hass, e_id, uid, status="needs_action")

            cached_items = self.data.external_tasks_cache.get(e_id, [])
            target_item = next((i for i in cached_items if str(i.get("uid")) == uid), None)
            if target_item:
                target_item["status"] = "pending"

            overlay = self.data.get_overlay(uid)
            overlay["completed_at"] = None
            overlay["completed_by"] = None
            self.data.set_overlay(uid, overlay)

            await self.async_save()
            for t in self.data.get_all_tasks(include_external=True):
                if t.get("id") == task_id:
                    return t
            return None

        task = self.data.reset_task(task_id)
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
                "points": int(task_data.get("points", self.data.settings.get("default_points", 10))),
                "linked_thing_id": task_data.get("linked_thing_id"),
                "thing_action": task_data.get("thing_action", THING_ACTION_RESET),
                "subtasks": task_data.get("subtasks", []),
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

        if task_id and self.data.get_task(task_id):
            result = self.data.update_task(task_id, task_data)
        else:
            result = self.data.create_task(task_data)
        await self.async_save()
        return result or {}
