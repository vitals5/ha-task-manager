# Task Manager for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)
[![GitHub Release](https://img.shields.io/github/v/release/vitals5/ha-task-manager?color=blue)](https://github.com/vitals5/ha-task-manager/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blue.svg)](https://www.home-assistant.io/)

A modern, collaborative household task, chore, and maintenance manager for Home Assistant.

Task Manager brings powerful chore tracking, recurring cadences, assignee rotations, gamification, and physical appliance monitoring ("Things") into Home Assistant. The entire workflow—task management, administration, household members, categories, and settings—is handled directly within an integrated, mobile- and tablet-friendly **Sidebar Panel**.

---

## ✨ Features

### 📋 Chores & Task Management
- **Priorities (P1–P4)**: Organize your chores into Urgent (P1), High (P2), Medium (P3), Low (P4), and None.
- **Flexible Recurrence Patterns**:
  - Repeat Daily, Weekly (select specific weekdays), Monthly, Yearly, or Custom Day intervals.
  - **Recurrence Cadence**: Choose between *Scheduled Due Date* (preserves consistent calendar cadence) or *Actual Completion Date* (adaptive scheduling when chores are delayed).
- **Subtasks with Smart Reset**: Break down complex tasks into subtasks. When a recurring task is completed, subtasks automatically reset for the next cycle.
- **Assignee Rotation**:
  - **Fixed**: Assigned to a specific person.
  - **Round-Robin**: Automatically cycles through selected assignees after each completion.
  - **Least Completed**: Automatically assigns the chore to whoever has completed the fewest tasks.
  - **Random**: Randomly selects among members.

### ⚙️ "Things" Tracking
Track non-task household items and consumables that require maintenance over time:
- **Meters & Counters**: Water filter lifespans (days), robot vacuum dustbin cycles (runs), coffee machine descaling (brews), air purifier filters, or water softener salt.
- **Interactive Controls**: Increment (`+1`), decrement (`-1`), or reset (`↺`) counters directly on the card.
- **Auto-Task Creation**: Automatically generates a pending chore in your task list when a Thing reaches its target limit!
- **Chore Linkage**: Completing a maintenance task can automatically reset its linked Thing.

### 🏆 Gamification & Leaderboard
- **Points Reward**: Earn customizable points upon chore completion.
- **Streaks**: Keep consecutive daily chore streaks alive (🔥).
- **Leaderboard Podium**: Friendly household competition showing top contributors and statistics.
- **Celebration Effects**: Visual confetti burst and cheerful completion chimes (can be toggled in settings).
- **Activity Feed**: Timeline of recently completed chores and awarded points.

### 🌐 Multi-Language Support (English & German)
- **Automatic Localization**: Seamlessly detects and switches language according to your Home Assistant user profile or system language.
- **Manual Language Preference**: Set language to Auto (Home Assistant), English, or Deutsch in Settings.
- **100% Localized Experience**: All views, calendar months & weekdays, forms, modals, filter chips, badges, and alerts are fully translated with zero hardcoded strings.

### 📺 Wall Tablet & Mount Mode
- Switch to **Tablet Mode** with a single click in the header for wall-mounted touchscreens (e.g. in the kitchen or hallway).
- Features enlarged touch targets and a fast **Member Switcher** so any family member can walk up, select their avatar, and check off chores.

### 🏠 Deep Home Assistant Integration
- **Native To-do Platform (`todo`)**:
  - `todo.task_manager_all_chores`: Main shared household list.
  - `todo.task_manager_<username>`: Individual list for each member.
  - Full compatibility with Home Assistant's built-in To-do dashboard, Lovelace To-do cards, and **Voice Assist** (*"Add clean filter to chores"* / *"Mark vacuuming done"*).
- **Sensors (`sensor`)**:
  - `sensor.task_manager_total_tasks`, `pending_tasks`, `overdue_tasks`, `completed_today`.
  - Member sensors: `sensor.task_manager_<user>_points` (includes streak and tasks due attributes).
  - Thing sensors: `sensor.task_manager_thing_<thing>` (state = current value, target, percent).
- **Rich Automations & Services**:
  - Trigger chores when washing machines finish, reset Things when smart buttons/NFC tags are scanned, and send alerts when P1 chores are overdue.

---

## 🚀 Installation

### Method 1: Installation via HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed and active in your Home Assistant instance.
2. In Home Assistant, open **HACS** > **Integrations**.
3. Click the three dots `⋮` in the top right corner and choose **Custom repositories**.
4. Paste the repository URL:
   ```text
   https://github.com/vitals5/ha-task-manager
   ```
5. Select **Integration** as the Category and click **Add**.
6. Find **Task Manager** in the list and click **Download**.
7. Restart Home Assistant.

### Method 2: Manual Installation

1. Download the latest `task_manager.zip` release from the [Releases](https://github.com/vitals5/ha-task-manager/releases) page.
2. Unpack the ZIP archive.
3. Copy the `task_manager` folder into your Home Assistant directory under:
   ```text
   /config/custom_components/task_manager/
   ```
4. Restart Home Assistant.

---

## ⚙️ Configuration & Setup

1. In Home Assistant, navigate to **Settings** > **Devices & Services**.
2. Click **+ Add Integration** in the bottom right.
3. Search for **Task Manager** and follow the prompt to finish.
4. Once added, a new item named **Task Manager** with a checkmark icon will appear in your **Home Assistant sidebar**!

---

## 📱 Sidebar Panel Overview

Everything is managed within the dedicated sidebar panel:

1. **Tasks & Chores Tab**:
   - Quick filters: *All*, *Due Today*, *Upcoming*, *Overdue*, *Completed*.
   - Filter by Assignee, Category / Label, and Priority.
   - Expandable Subtask checklists.
   - Interactive checkbox with completion sound and confetti.
2. **Calendar Tab**:
   - Monthly grid overview showing due dates and priority color dots.
   - Click any date to inspect chores scheduled for that day.
3. **Things Tab**:
   - Monitor appliances and supplies with percentage progress bars.
   - Quick `+1` / `-1` / `Reset` action buttons.
4. **Leaderboard Tab**:
   - Member podium, points, streaks, and recent activity log.
5. **Settings Tab**:
   - **Members**: Add or edit household members (name, avatar, theme color, points).
   - **Labels**: Customize categories (Cleaning, Garden, Kitchen, Maintenance, Pets, etc.).
   - **Preferences**: Toggle gamification, sounds, confetti, default points, and select language (Auto, English, Deutsch).
   - **Backup & Restore**: Export and import complete JSON backups.

---

## 🤖 Automations & Services Reference

Task Manager provides dedicated actions/services that integrate into Home Assistant scripts and automations.

### Available Services

| Service | Description | Parameters |
|---|---|---|
| `task_manager.create_task` | Create a new chore or task | `title` (required), `description`, `due_date`, `priority`, `assignee`, `points`, `linked_thing_id` |
| `task_manager.complete_task` | Complete a task, award points, and calculate recurrence | `task_id` or `task_title`, `user_id` |
| `task_manager.reset_task` | Reset a completed task back to pending | `task_id` or `task_title` |
| `task_manager.delete_task` | Permanently delete a task | `task_id` (required) |
| `task_manager.update_thing` | Increment, decrement, set, or reset a Thing | `thing_id` (required), `value`, `delta`, `reset` |
| `task_manager.award_points` | Adjust points for a member | `user_id` (required), `points` (required), `reason` |

---

### Example Automations

#### 1. Increment Robot Vacuum Dustbin counter after every cleaning run
```yaml
alias: "Task Manager: Count Robot Vacuum Runs"
trigger:
  - platform: state
    entity_id: vacuum.robot_vacuum
    from: "cleaning"
    to: "docked"
action:
  - action: task_manager.update_thing
    data:
      thing_id: "thing_robot_dustbin"
      delta: 1
```

#### 2. Complete chore and reset Thing when an NFC Tag is scanned
Place an NFC tag near the coffee maker or water filter:
```yaml
alias: "Task Manager: NFC Coffee Machine Descaled"
trigger:
  - platform: tag
    tag_id: "e5a31bc0-4299-4d8b-967a-18bcf5061dc1"
action:
  - action: task_manager.complete_task
    data:
      task_title: "Descale Coffee Machine"
```

#### 3. Send Mobile Notification when an Urgent (P1) Chore is Overdue
```yaml
alias: "Task Manager: Overdue Chore Alert"
trigger:
  - platform: numeric_state
    entity_id: sensor.task_manager_overdue_tasks
    above: 0
action:
  - action: notify.notify
    data:
      title: "⚠️ Overdue Chores Alert"
      message: "You have {{ states('sensor.task_manager_overdue_tasks') }} overdue chore(s) waiting in Task Manager."
      data:
        url: "/task-manager"
```

#### 4. Auto-create a Chore when Washing Machine cycle finishes
```yaml
alias: "Task Manager: Empty Washing Machine"
trigger:
  - platform: state
    entity_id: sensor.washing_machine_status
    to: "finished"
action:
  - action: task_manager.create_task
    data:
      title: "Hang up Laundry"
      description: "Washing machine finished cycle."
      priority: "p2"
      points: 15
```

---

## 📊 Lovelace Dashboard Card Examples

### Standard To-do List Card
Display your Task Manager chores directly in any dashboard:
```yaml
type: todo-list
entity: todo.task_manager_all_chores
title: Household Chores
```

### Entity Summary Chips
```yaml
type: horizontal-stack
cards:
  - type: entity
    entity: sensor.task_manager_pending_tasks
    name: Pending
  - type: entity
    entity: sensor.task_manager_overdue_tasks
    name: Overdue
  - type: entity
    entity: sensor.task_manager_completed_today
    name: Done Today
```

---

## ❓ FAQ & Troubleshooting

### Where are my tasks stored?
All tasks, things, users, and settings are stored locally in Home Assistant's secure storage directory (`.storage/task_manager_data`). Your data never leaves your local network.

### How does Subtask Smart Reset work?
In Task Manager, recurring chores with subtask checklists (e.g. *"Clean Bathroom"* with steps: *Mirror*, *Sink*, *Toilet*, *Shower*) will have their subtasks automatically reset to unchecked once the parent chore is completed, ready for the next scheduled occurrence.

### How do I access the panel on a mobile device?
Open the Home Assistant Companion App and tap **Task Manager** in the sidebar. It is fully responsive and adjusts to screen sizes from phones to 4K wall panels.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
