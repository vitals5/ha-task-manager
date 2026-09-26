"""Constants for the Task Manager integration."""
from __future__ import annotations

import os

DOMAIN = "task_manager"
PLATFORMS = ["sensor", "todo"]

URL_BASE = "/task_manager_ui"
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")

STORAGE_VERSION = 1
STORAGE_KEY = "task_manager_data"

SIGNAL_TASK_MANAGER_UPDATED = f"{DOMAIN}_updated"

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
]

# Recurrence Cadence Base
RECURRENCE_BASED_DUE_DATE = "due_date"
RECURRENCE_BASED_COMPLETION = "completion_date"

RECURRENCE_BASES = [
    RECURRENCE_BASED_DUE_DATE,
    RECURRENCE_BASED_COMPLETION,
]

# Thing Actions on Task Completion
THING_ACTION_NONE = "none"
THING_ACTION_RESET = "reset"
THING_ACTION_INCREMENT = "increment"
THING_ACTION_DECREMENT = "decrement"

# Services
SERVICE_CREATE_TASK = "create_task"
SERVICE_UPDATE_TASK = "update_task"
SERVICE_COMPLETE_TASK = "complete_task"
SERVICE_RESET_TASK = "reset_task"
SERVICE_DELETE_TASK = "delete_task"
SERVICE_UPDATE_SUBTASK = "update_subtask"
SERVICE_CREATE_THING = "create_thing"
SERVICE_UPDATE_THING = "update_thing"
SERVICE_DELETE_THING = "delete_thing"
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
        "unit": "days",
        "auto_task_creation": True,
        "auto_task_title": "Replace Water Filter Cartridge",
        "last_reset": "",
    },
    {
        "id": "thing_robot_dustbin",
        "name": "Robot Vacuum Dustbin",
        "category": "Living Room",
        "icon": "mdi:robot-vacuum",
        "current_value": 0,
        "target_value": 7,
        "unit": "runs",
        "auto_task_creation": True,
        "auto_task_title": "Empty Robot Vacuum Bin",
        "last_reset": "",
    },
    {
        "id": "thing_coffee_descale",
        "name": "Coffee Machine Descaling",
        "category": "Kitchen",
        "icon": "mdi:coffee-maker",
        "current_value": 0,
        "target_value": 100,
        "unit": "brews",
        "auto_task_creation": True,
        "auto_task_title": "Descale Coffee Machine",
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
