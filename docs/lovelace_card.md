# Lovelace Dashboard Card

Task Manager includes a custom Lovelace dashboard card (`custom:task-manager-card`) allowing you to display, filter, and complete chores directly on your Home Assistant dashboards.

---

## Table of Contents

- [Overview & Auto-Registration](#overview--auto-registration)
- [Visual GUI Card Editor](#visual-gui-card-editor)
- [Card Configuration Reference](#card-configuration-reference)
- [Interactive Features](#interactive-features)
- [YAML Configuration Examples](#yaml-configuration-examples)
  - [1. Standard Household Tasks Card](#1-standard-household-tasks-card)
  - [2. "Due Today" Minimalist Card](#2-due-today-minimalist-card)
  - [3. Wall Tablet / Kitchen Kiosk Card](#3-wall-tablet--kitchen-kiosk-card)
  - [4. Member-Specific Card](#4-member-specific-card)

---

## Overview & Auto-Registration

Unlike third-party Lovelace cards that require manual installation and YAML resource configuration, Task Manager's card is **automatically registered** as a dashboard resource when the integration is installed:

- **Resource URL**: `/task_manager_ui/task-manager-card.js`
- **Resource Type**: JavaScript Module
- **Card Type**: `custom:task-manager-card`

No edits to `ui-lovelace.yaml` or manual entries in **Settings** > **Dashboards** > **Resources** are required!

---

## Visual GUI Card Editor

When editing any dashboard in Home Assistant:
1. Click **+ Add Card**.
2. Search for **Task Manager Card**.
3. A visual editor (`task-manager-card-editor`) appears allowing you to toggle options, adjust item limits, and preview the card in real time.

---

## Card Configuration Reference

The card supports the following configuration options:

| Option | Type | Default | Description |
|---|---|---|---|
| `type` | string | **Required** | Must be `custom:task-manager-card`. |
| `title` | string | `"Task Manager"` | Card header title. |
| `default_filter` | string | `"all"` | Default filter tab selected on load: `all`, `today`, `due_soon`, `overdue`, `completed`, `inactive`. |
| `show_add` | boolean | `true` | Show inline "+ Add chore" input field at the bottom. |
| `show_completed` | boolean | `true` | Include the "Completed" filter button. |
| `show_assignee` | boolean | `true` | Display member avatars and names. |
| `show_priority` | boolean | `true` | Display priority colored dots and chips (P1–P4). |
| `max_items` | number | `20` | Maximum number of tasks to display at once. |

---

## Interactive Features

The dashboard card provides full interactivity:

- **Direct Checkbox Completion**: Click the circle checkmark to complete chores with celebration chimes and confetti bursts.
- **Meter Reading Prompts**: Clicking completion on a `reading` task automatically prompts for current meter values.
- **Subtask Checklists**: Expand subtask checklists directly inside the card and check off individual subtask items.
- **Odometer & Thing Badges**: Linked Things display live progress chips (e.g. `🚗 Car: 12,500 / 30,000 km`).
- **Skip Button (`⏭️`)**: Advance recurrence directly from the card.
- **Clean Mode Compliance**: If gamification is turned off in Settings, points and confetti are hidden automatically for a clean look.
- **Theme Compliance**: Adapts seamlessly to Home Assistant Light and Dark modes.

---

## YAML Configuration Examples

### 1. Standard Household Tasks Card
```yaml
type: custom:task-manager-card
title: Household Chores
default_filter: today
show_add: true
show_completed: true
show_assignee: true
show_priority: true
max_items: 15
```

### 2. "Due Today" Minimalist Card
A compact widget displaying only chores due today:
```yaml
type: custom:task-manager-card
title: Today's Tasks
default_filter: today
show_add: false
show_completed: false
max_items: 5
```

### 3. Wall Tablet / Kitchen Kiosk Card
Ideal for a wall-mounted touchscreen in the kitchen or hallway:
```yaml
type: custom:task-manager-card
title: Family Chores Board
default_filter: all
show_add: true
show_completed: true
show_assignee: true
show_priority: true
max_items: 25
```

### 4. Member-Specific Card
Combined with Home Assistant's native To-do card for a dedicated user dashboard:
```yaml
type: vertical-stack
cards:
  - type: custom:task-manager-card
    title: My Assigned Chores
    default_filter: today
    max_items: 10
  - type: todo-list
    entity: todo.task_manager_user_vitali
    title: Personal Checklist
```
