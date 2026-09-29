"""Constants for the Task Manager integration."""
from __future__ import annotations

import os

DOMAIN = "task_manager"
PLATFORMS = ["binary_sensor", "button", "calendar", "sensor", "todo"]

URL_BASE = "/task_manager_ui"
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")

STORAGE_VERSION = 1
STORAGE_KEY = "task_manager_data"

SIGNAL_TASK_MANAGER_UPDATED = f"{DOMAIN}_updated"
DATA_REMINDER_TIMERS = f"{DOMAIN}_reminder_timers"

# Automation Events
EVENT_TASK_CREATED = f"{DOMAIN}_task_created"
EVENT_TASK_COMPLETED = f"{DOMAIN}_task_completed"
EVENT_TASK_REOPENED = f"{DOMAIN}_task_reopened"
EVENT_TASK_ASSIGNED = f"{DOMAIN}_task_assigned"
EVENT_TASK_DUE = f"{DOMAIN}_task_due"
EVENT_TASK_OVERDUE = f"{DOMAIN}_task_overdue"
EVENT_TASK_REMINDER = f"{DOMAIN}_task_reminder"

# Priority Levels
PRIORITY_P1 = "p1"      # Urgent (Red)
PRIORITY_P2 = "p2"      # High (Orange)
PRIORITY_P3 = "p3"      # Medium (Blue)
PRIORITY_P4 = "p4"      # Low (Gray)
PRIORITY_NONE = "none"  # No Priority

PRIORITIES = [
    PRIORITY_P1,
    PRIORITY_P2,
    PRIORITY_P3,
    PRIORITY_P4,
    PRIORITY_NONE,
]

# Rotation Modes for Assignees
ROTATION_NONE = "none"
ROTATION_ROUND_ROBIN = "round_robin"
ROTATION_LEAST_COMPLETED = "least_completed"
ROTATION_RANDOM = "random"

ROTATION_MODES = [
    ROTATION_NONE,
    ROTATION_ROUND_ROBIN,
    ROTATION_LEAST_COMPLETED,
    ROTATION_RANDOM,
]

# Recurrence Modes
REPEAT_MODE_AFTER = "repeat_after"
REPEAT_MODE_EVERY = "repeat_every"

# Repeat-Every Sub-Types
REPEAT_EVERY_WEEKDAY = "repeat_every_weekday"                             # every N weeks on a weekday
REPEAT_EVERY_DAY_OF_MONTH = "repeat_every_day_of_month"                   # Nth day of the month
REPEAT_EVERY_WEEKDAY_OF_MONTH = "repeat_every_weekday_of_month"           # Nth weekday of the month
REPEAT_EVERY_DAYS_BEFORE_END_OF_MONTH = "repeat_every_days_before_end_of_month" # N days before month end

# Recurrence Types
RECURRENCE_NONE = "none"
RECURRENCE_DAILY = "daily"
RECURRENCE_WEEKLY = "weekly"
RECURRENCE_MONTHLY = "monthly"
RECURRENCE_YEARLY = "yearly"
RECURRENCE_CUSTOM_DAYS = "custom_days"

RECURRENCE_TYPES = [
    RECURRENCE_NONE,
    RECURRENCE_DAILY,
    RECURRENCE_WEEKLY,
    RECURRENCE_MONTHLY,
    RECURRENCE_YEARLY,
    RECURRENCE_CUSTOM_DAYS,
    REPEAT_EVERY_WEEKDAY,
    REPEAT_EVERY_DAY_OF_MONTH,
    REPEAT_EVERY_WEEKDAY_OF_MONTH,
    REPEAT_EVERY_DAYS_BEFORE_END_OF_MONTH,
]

# Recurrence Cadence Base
RECURRENCE_BASED_DUE_DATE = "due_date"
RECURRENCE_BASED_COMPLETION = "completion_date"

RECURRENCE_BASES = [
    RECURRENCE_BASED_DUE_DATE,
    RECURRENCE_BASED_COMPLETION,
]

# Task States
TASK_STATE_DUE = "due"
TASK_STATE_DUE_SOON = "due_soon"
TASK_STATE_DONE = "done"
TASK_STATE_INACTIVE = "inactive"

# Thing Actions on Task Completion
THING_ACTION_NONE = "none"
THING_ACTION_RESET = "reset"
THING_ACTION_INCREMENT = "increment"
THING_ACTION_DECREMENT = "decrement"

# Thing Threshold Operators
THRESHOLD_OP_GTE = ">="
THRESHOLD_OP_LTE = "<="

THRESHOLD_OPERATORS = [
    THRESHOLD_OP_GTE,
    THRESHOLD_OP_LTE,
]

# Far Future Due Date for threshold-driven tasks without time schedule
FAR_FUTURE_DUE_DATE = "2099-12-31"

# Task Types
TASK_TYPE_CHORE = "chore"
TASK_TYPE_READING = "reading"

TASK_TYPES = [
    TASK_TYPE_CHORE,
    TASK_TYPE_READING,
]

# Warranty Statuses
WARRANTY_STATUS_VALID = "valid"
WARRANTY_STATUS_EXPIRING_SOON = "expiring_soon"
WARRANTY_STATUS_EXPIRED = "expired"
WARRANTY_STATUS_NONE = "none"

# Additional Automation Events
EVENT_TASK_SKIPPED = f"{DOMAIN}_task_skipped"
EVENT_PART_LOW_STOCK = f"{DOMAIN}_part_low_stock"

# Services
SERVICE_CREATE_TASK = "create_task"
SERVICE_ADD_TASK = "add_task"
SERVICE_UPDATE_TASK = "update_task"
SERVICE_COMPLETE_TASK = "complete_task"
SERVICE_SKIP_TASK = "skip_task"
SERVICE_RECORD_READING = "record_reading"
SERVICE_DELETE_TASK_HISTORY_ENTRY = "delete_task_history_entry"
SERVICE_RESET_TASK = "reset_task"
SERVICE_REOPEN_TASK = "reopen_task"
SERVICE_MARK_AS_DONE = "mark_as_done"
SERVICE_SET_LAST_DONE_DATE = "set_last_done_date"
SERVICE_PAUSE_TASK = "pause_task"
SERVICE_RESUME_TASK = "resume_task"
SERVICE_ASSIGN_TASK = "assign_task"
SERVICE_MOVE_TASK = "move_task"
SERVICE_DUPLICATE_TASK = "duplicate_task"
SERVICE_DELETE_TASK = "delete_task"
SERVICE_UPDATE_SUBTASK = "update_subtask"
SERVICE_CREATE_THING = "create_thing"
SERVICE_UPDATE_THING = "update_thing"
SERVICE_INCREMENT_THING = "increment_thing"
SERVICE_DELETE_THING = "delete_thing"
SERVICE_ADJUST_PART_STOCK = "adjust_part_stock"
SERVICE_SAVE_PART = "save_part"
SERVICE_DELETE_PART = "delete_part"
SERVICE_AWARD_POINTS = "award_points"
SERVICE_IMPORT_DATA = "import_data"

# Default Labels
DEFAULT_LABELS = [
    {"id": "label_cleaning", "name": "Cleaning", "color": "#0ea5e9", "icon": "mdi:broom"},
    {"id": "label_kitchen", "name": "Kitchen", "color": "#f97316", "icon": "mdi:silverware-fork-knife"},
    {"id": "label_garden", "name": "Garden", "color": "#10b981", "icon": "mdi:flower"},
    {"id": "label_maintenance", "name": "Maintenance", "color": "#6366f1", "icon": "mdi:wrench"},
    {"id": "label_shopping", "name": "Shopping", "color": "#ec4899", "icon": "mdi:cart"},
    {"id": "label_pets", "name": "Pets", "color": "#8b5cf6", "icon": "mdi:paw"},
]

# Default Users / Members
DEFAULT_USERS = [
    {
        "id": "user_household",
        "name": "Household",
        "color": "#3b82f6",
        "avatar": "mdi:home",
        "points": 0,
        "streak": 0,
        "last_completed_date": "",
        "completed_count": 0,
    }
]

# Default "Things" (Appliance and household item counters)
DEFAULT_THINGS = [
    {
        "id": "thing_water_filter",
        "name": "Water Filter Pitcher",
        "category": "Kitchen",
        "icon": "mdi:water-filter",
        "current_value": 0,
        "target_value": 60,
        "threshold_operator": ">=",
        "unit": "days",
        "script_entity_id": None,
        "auto_task_creation": False,
        "auto_task_title": "",
        "last_reset": "",
    },
    {
        "id": "thing_robot_dustbin",
        "name": "Robot Vacuum Dustbin",
        "category": "Living Room",
        "icon": "mdi:robot-vacuum",
        "current_value": 0,
        "target_value": 7,
        "threshold_operator": ">=",
        "unit": "runs",
        "script_entity_id": None,
        "auto_task_creation": False,
        "auto_task_title": "",
        "last_reset": "",
    },
    {
        "id": "thing_coffee_descale",
        "name": "Coffee Machine Descaling",
        "category": "Kitchen",
        "icon": "mdi:coffee-maker",
        "current_value": 0,
        "target_value": 100,
        "threshold_operator": ">=",
        "unit": "brews",
        "script_entity_id": None,
        "auto_task_creation": False,
        "auto_task_title": "",
        "last_reset": "",
    },
]

# Default Settings
DEFAULT_SETTINGS = {
    "gamification_enabled": True,
    "sound_enabled": True,
    "confetti_enabled": True,
    "default_points": 10,
    "tablet_mount_mode": False,
    "first_day_of_week": 1,  # 1 = Monday, 0 = Sunday
    "theme_mode": "auto",
    "language": "auto",
}
