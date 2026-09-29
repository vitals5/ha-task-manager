# Task Manager for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)
[![GitHub Release](https://img.shields.io/github/v/release/vitals5/ha-task-manager?color=blue)](https://github.com/vitals5/ha-task-manager/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blue.svg)](https://www.home-assistant.io/)

A modern, collaborative household task, chore, and maintenance manager for Home Assistant.

Task Manager combines powerful chore tracking, recurring cadences, appliance and vehicle maintenance ("Things" with Odometer mode), utility meter readings with consumption history, spare parts inventory management, gamification, and native Home Assistant platforms (To-do, Calendar, Sensors, Buttons, and Events) into an all-in-one productivity suite.

The entire workflow is managed within an integrated, mobile- and tablet-friendly **Sidebar Panel** and can be displayed on your dashboards using the auto-registered **Lovelace Dashboard Card** (`custom:task-manager-card`).

---

## ✨ Standout Features

- 📱 **Dedicated Sidebar Panel**: Fully responsive desktop, tablet, and mobile interface with native Home Assistant Dark/Light mode support.
- 📊 **Lovelace Dashboard Card**: Custom card (`custom:task-manager-card`) with visual GUI editor, auto-registered without manual YAML resource setup.
- 🚗 **Continuous Counters & Odometer Mode**: Track car mileage (e.g. maintenance every 30,000 km or 24 months), operating hours, or cumulative energy/water meters.
- ⚡ **External Entity Linkage & Conditional Due Dates**: Link Things directly to numeric sensors (`sensor.*`). When a threshold is met, the linked chore automatically becomes due today!
- ⏱️ **Utility & Meter Readings**: Special reading tasks supporting multi-register meters (e.g. Electricity Peak/Off-Peak/Feed-in, Water, Gas), reading history, consumption deltas, and CSV export.
- 🧰 **Spare Parts & Supplies Shelf**: Manage consumables (filters, vacuum bags, fluids, salt), track stock levels, receive low-stock alerts, and deduct parts upon chore completion.
- ⏸️ **Pause & Resume Tasks**: Temporarily pause seasonal or parked chores without losing schedules.
- 🏷️ **QR Code & Quick-Complete URL**: Generate and print QR code labels for physical appliances; scan with any smartphone camera to instantly complete chores.
- 🔄 **Advanced Recurrence & Rotation**: Repeat every N days/weeks/months/years, specific weekdays, scheduled vs. completion date cadence, and round-robin/least-completed assignee rotation.
- 🏆 **Optional Gamification**: Points rewards, streaks (🔥), leaderboard podium, completion sound, and confetti—or toggle **Clean Mode** to completely hide gamification for a distraction-free productivity tool.
- 🔗 **External Todo Sync**: Bi-directional sync with Google Tasks, Todoist, CalDAV/Nextcloud, Local To-do, Bring!, Shopping List, or any `todo.*` entity.
- 🤖 **Deep Home Assistant Integration**: Native `todo` and `calendar` platforms, sensors, binary sensors, button entities, events, services, and ready-to-use notification blueprints.
- 🌐 **100% Bilingual**: Complete English and German localization with zero hardcoded text.

---

## 📖 In-Depth Documentation Guides

Explore the dedicated documentation guides for detailed walkthroughs, real-world examples, and configuration references:

- 📋 [**Tasks & Chores Management**](docs/tasks_and_chores.md) – Recurrence cadences, subtasks, rotation, QR quick-completion, and pause/resume.
- ⚙️ [**Things & Odometer Tracking**](docs/things_and_odometers.md) – Monotonic counters, car maintenance (30,000 km or 24 months), and HA sensor linkage.
- 📟 [**Utility & Meter Readings**](docs/meter_readings.md) – Multi-register counters (HT/NT/Feed-in), consumption deltas, history editing, and CSV export.
- 🧰 [**Spare Parts & Inventory Shelf**](docs/spare_parts.md) – Parts inventory, reorder links, low-stock alerts, and appliance warranty tracking.
- 📊 [**Lovelace Dashboard Card**](docs/lovelace_card.md) – Custom card setup, visual editor, options, and YAML examples.
- 🤖 [**Actions & Services Reference**](docs/services_reference.md) – Exhaustive reference for all 18 Home Assistant services with parameter schemas.
- ⚡ [**Automations, Events & Blueprints**](docs/automations_and_events.md) – Event Bus triggers, precision reminders, mobile alerts, and daily digest blueprint.

---

## 📋 Core Capabilities

### 1. Chores & Maintenance Management
- **Task Types**: Standard maintenance chores or **Meter / Utility Readings** (`reading`).
- **Priorities (P1–P4)**: Organize chores into Urgent (P1 - Red), High (P2 - Orange), Medium (P3 - Blue), Low (P4 - Gray), or None.
- **Flexible Recurrence Patterns**:
  - **Schedule Modes**: *Calendar Schedule* (preserves fixed calendar intervals) vs. *Interval after completion* (calculates next due date from actual completion).
  - Repeat Daily, Weekly (select specific weekdays, e.g. every Tuesday and Friday), Monthly (day of month, Nth weekday), Yearly, or Custom intervals.
  - **Standalone Sensor Tasks**: Tasks linked to a Thing without time recurrence automatically wait for the next sensor threshold trigger.
- **Subtasks with Smart Reset**: Break down complex chores into checklists. When a recurring chore is completed, its subtasks automatically reset for the next cycle.
- **Assignee Rotation**:
  - **Fixed**: Assigned to a specific family member.
  - **Round-Robin**: Automatically cycles through selected assignees after each completion.
  - **Least Completed**: Automatically assigns the chore to whoever has completed the fewest chores.
  - **Random**: Randomly selects among household members.
- **Pause & Resume**: Temporarily freeze tasks (e.g. winter garden maintenance) and resume them whenever needed.
- **Skip Recurrence**: Advance to the next scheduled date without awarding points.
- **Detailed Work Logging**: Log duration in minutes, financial cost, notes, and consumed spare parts upon completion.
- **QR Code Quick-Completion**: Print QR labels attached to appliances or physical locations. Scanning the code opens Home Assistant and instantly marks the chore as done (`?complete_task=<id>`).

---

### 2. "Things" & Appliance / Vehicle Monitoring
Track non-task physical appliances, equipment, and consumables:
- **Counters & Countdowns**: Filter lifespans (days), robot vacuum dustbin cycles (runs), coffee machine descaling (brews), water softener salt (kg).
- **Continuous Counter / Odometer Mode (`is_odometer`)**:
  - Perfect for car mileage (odometer), lawnmower engine hours, or total utility consumption where the sensor never resets to zero.
  - Retains the absolute reading from Home Assistant, tracks the reading at last maintenance (`last_reset_value`), and checks the interval delta:
    $$\Delta = \text{current reading} - \text{last reset reading} \ge \text{target interval}$$
  - Completing the maintenance chore automatically advances `last_reset_value` to the current reading without modifying your physical sensor!
- **External HA Numeric Sensor Linkage**: Link any Thing directly to a Home Assistant entity (`sensor.*`). Values synchronize in real-time.
- **Trigger Conditions & Dynamic Due Dates**: Choose operators (`>=` or `<=`). When the threshold is reached, the linked task's due date is automatically pulled forward to **today**!
- **Completion Scripts**: Specify an optional Home Assistant script to execute when a linked task is completed (e.g. to send a reset command or notify an external device).
- **Manual Controls**: Interactive `+1`, `-1`, set, and reset controls on Thing cards.

---

### 3. Utility & Meter Reading Tasks
- **Single & Multi-Register Counters**: Record gas, water, or multi-tariff electricity meters (e.g. Peak / Off-Peak / Solar Feed-in: `1.8.1`, `1.8.2`, `2.8.0`).
- **Consumption Deltas**: Automatically calculates consumption and difference since the previous reading.
- **Reading History Table**: Inspect past readings, timestamps, and notes.
- **Entry Correction & Deletion**: Edit or remove erroneous entries directly from the history dialog with automatic rollback of previous readings.
- **CSV Export**: Download your full meter reading history as a CSV file for analysis or utility submission.

---

### 4. Spare Parts & Supplies Inventory ("Parts Shelf")
- **Inventory Tracking**: Manage replacement parts, filters, mop pads, descaling tablets, oils, and consumables.
- **Detailed Metadata**: Track Part Name, SKU / Part Number, Manufacturer, Model, Storage Location, Current Stock, Unit Price, Reorder URL, and Notes.
- **Thing Association**: Link spare parts directly to appliances (e.g. HEPA Filter linked to Robot Vacuum).
- **Minimum Stock Alerts**: Set a reorder threshold. Parts falling at or below this value display a **Low Stock!** warning.
- **Maintenance Consumption**: Select and deduct consumed spare parts directly when completing maintenance chores.
- **Warranty Tracking**: Record purchase/installation date and warranty expiry date with active/expiring/expired status badges.

---

### 5. Custom Lovelace Dashboard Card (`task-manager-card`)
A full-featured Lovelace card is included and automatically registered:
- **Auto-Registration**: The card resource `/task_manager_ui/task-manager-card.js` is automatically available in all Home Assistant dashboards.
- **Visual GUI Editor**: Configure the card directly inside Home Assistant's dashboard editor (`task-manager-card-editor`).
- **Interactive Checklists**: Check off chores with sounds and animations, view assignee avatars, priority indicators, subtasks, and linked Thing progress chips.
- **View Filters**: Quickly switch between *All*, *Due Today*, *Upcoming*, *Overdue*, *Completed*, or *Paused*.
- **Configurable Options**: Filter by member, category/tag, limit maximum items, and hide completed items.

```yaml
type: custom:task-manager-card
title: Household Tasks
default_filter: today
show_add: true
show_completed: true
show_assignee: true
show_priority: true
max_items: 15
```

---

### 6. Gamification & Clean Mode
- **Points & Streaks**: Earn customizable points per chore; maintain consecutive daily streaks (🔥).
- **Leaderboard Podium**: Friendly household competition showing top contributors and activity log.
- **Celebration Effects**: Confetti bursts and cheerful completion chimes.
- **Clean / Minimalist Mode**: Prefer a clean productivity tool without gamification? Simply turn off *Enable Gamification* in Settings to completely hide points, streaks, badges, sounds, confetti, and the leaderboard tab across the entire UI.

---

### 7. External Todo Providers & Sync
- **Supported Providers**:
  - Google Tasks (`google_tasks`)
  - Todoist (`todoist`)
  - CalDAV / Nextcloud (`caldav`)
  - Local To-do (`local_todo`)
  - Bring! Shopping (`bring`)
  - Shopping List (`shopping_list`)
  - Any generic Home Assistant `todo.*` entity
- **Panel-Based Administration**: Add, link, unlink, and synchronize external providers directly from the Settings tab.
- **Local Overlays**: Add points, rotation, members, subtasks, and linked Things to external tasks without modifying remote schemas.

---

### 8. Native Home Assistant Platform Entities
Task Manager automatically exposes native Home Assistant entities:

| Platform | Entity ID | Description |
|---|---|---|
| **To-do** | `todo.task_manager_all_chores` | Main household chore list |
| **To-do** | `todo.task_manager_<username>` | Personal chore list for each member |
| **Calendar** | `calendar.task_manager_chores` | Shared calendar with due and recurring chores |
| **Calendar** | `calendar.task_manager_<username>` | Member calendar |
| **Sensor** | `sensor.task_manager_total_tasks` | Total count of all tasks |
| **Sensor** | `sensor.task_manager_pending_tasks` | Count of pending tasks |
| **Sensor** | `sensor.task_manager_overdue_tasks` | Count of overdue tasks |
| **Sensor** | `sensor.task_manager_completed_today` | Count of tasks completed today |
| **Sensor** | `sensor.task_manager_<user>_points` | Points and streak metrics per user |
| **Sensor** | `sensor.task_manager_thing_<thing>` | Current value, target, delta, and percent of each Thing |
| **Sensor** | `sensor.task_manager_<task>` | Task state (`due`, `due_soon`, `pending`, `completed`, `paused`) |
| **Binary Sensor** | `binary_sensor.task_manager_has_overdue_tasks` | `on` if any tasks are overdue |
| **Binary Sensor** | `binary_sensor.task_manager_has_due_today` | `on` if any tasks are due today |
| **Button** | `button.task_manager_complete_<task>` | One-click button to mark task as completed |
| **Button** | `button.task_manager_reset_<task>` | One-click button to reset task |

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
5. The Lovelace dashboard card (`custom:task-manager-card`) is registered automatically.

---

## 🤖 Actions & Services Reference

Task Manager provides comprehensive Home Assistant actions/services:

| Action / Service | Description | Important Parameters |
|---|---|---|
| `task_manager.create_task` | Create a new chore or task (alias: `add_task`) | `title` (required), `description`, `due_date`, `due_time`, `priority`, `assignee`, `tags`, `reminders`, `points`, `linked_thing_id` |
| `task_manager.complete_task` | Mark a task as completed (alias: `mark_as_done`) | `task_id` or `task_title`, `user_id`, `cost`, `duration_minutes`, `notes`, `completed_at`, `reading_value` |
| `task_manager.set_last_done_date` | Manually set completion date and recalculate schedule | `task_id` or `task_title`, `date` (YYYY-MM-DD) |
| `task_manager.pause_task` | Temporarily pause a recurring task | `task_id` or `task_title` |
| `task_manager.resume_task` | Resume a paused task | `task_id` or `task_title` |
| `task_manager.skip_task` | Skip current recurrence without awarding points | `task_id` or `task_title` |
| `task_manager.reset_task` | Reopen a completed task (alias: `reopen_task`) | `task_id` or `task_title`, `assigned_person`, `tag` |
| `task_manager.assign_task` | Reassign a task to another user | `task_id` or `task_title`, `person` (required) |
| `task_manager.duplicate_task` | Duplicate an existing chore | `task_id` or `task_title` |
| `task_manager.move_task` | Move chore to another provider list | `task_id` or `task_title`, `target_provider` |
| `task_manager.delete_task` | Permanently delete a task | `task_id` (required) |
| `task_manager.update_thing` | Update, set, or reset a Thing | `thing_id` or `entity_id`, `value`, `delta`, `reset`, `is_odometer`, `last_reset_value` |
| `task_manager.increment_thing` | Increment or decrement a Thing counter | `thing_id` or `entity_id`, `amount` (e.g. +1, -1) |
| `task_manager.record_reading` | Record a meter reading and advance recurrence | `task_id` or `task_title`, `reading_value` (required), `notes`, `completed_at` |
| `task_manager.award_points` | Adjust points for a member | `user_id` (required), `points` (required), `reason` |
| `task_manager.save_part` | Create or update a spare part in inventory | `id`, `name` (required), `thing_id`, `stock`, `min_stock`, `unit_price`, `reorder_url` |
| `task_manager.adjust_part_stock` | Adjust stock quantity of a spare part | `part_id` (required), `stock` (absolute) or `delta` (+/-) |
| `task_manager.delete_part` | Delete a spare part from inventory | `part_id` (required) |

---

## 💡 Practical Automation Examples

### 1. Car Maintenance: Every 30,000 km or 24 Months (Whichever Comes First)
Configure a Thing in **Odometer Mode** linked to your car's odometer sensor with a threshold of `30000 km`. Link your "Car Service" task to this Thing with a 24-month recurrence.

If the mileage interval is reached first, the task is automatically pulled forward to today. When you complete the task in the panel, `last_reset_value` is set to the current odometer reading and the next scheduled date advances by 24 months!

```yaml
alias: "Car Maintenance: 30,000 km or 24 Months Alert"
trigger:
  - platform: state
    entity_id: sensor.task_manager_major_car_service
    to: "due"
action:
  - action: notify.notify
    data:
      title: "🚗 Car Inspection Due"
      message: "Major car service is due (odometer interval or 24-month schedule reached)!"
      data:
        url: "/task-manager"
```

---

### 2. Increment Vacuum Filter counter after each cleaning cycle
```yaml
alias: "Task Manager: Count Robot Vacuum Runs"
trigger:
  - platform: state
    entity_id: vacuum.robot_vacuum
    from: "cleaning"
    to: "docked"
action:
  - action: task_manager.increment_thing
    data:
      thing_id: "thing_robot_dustbin"
      amount: 1
```

---

### 3. Complete Chore via NFC Tag Scan or QR Code
Place an NFC tag on your water softener or coffee machine:
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

---

### 4. Low Stock Alert for Spare Parts & Consumables
Notify your mobile phone when water filters or vacuum bags are running low:
```yaml
alias: "Task Manager: Spare Part Low Stock Alert"
trigger:
  - platform: event
    event_type: task_manager_part_low_stock
action:
  - action: notify.notify
    data:
      title: "📦 Reorder Supplies"
      message: "The stock for {{ trigger.event.data.name }} is low ({{ trigger.event.data.stock }} left)."
```

---

### 5. Daily Task Reminders via Blueprint
Task Manager includes a ready-to-use automation blueprint:
- **File**: `blueprints/automation/task_manager/task_manager_notify.yaml`
- **Features**: Sends a daily digest at your chosen time for tasks that are due, overdue, or due soon, with optional tag and assignee filtering.

---

## 📊 Dashboard Cards Configuration

### Custom Task Manager Card
```yaml
type: custom:task-manager-card
title: Chores & Maintenance
default_filter: today
show_add: true
show_completed: true
show_assignee: true
show_priority: true
max_items: 10
```

### Native To-do List Card
```yaml
type: todo-list
entity: todo.task_manager_all_chores
title: Household Chores
```

### Native Calendar Card
```yaml
type: calendar
entities:
  - calendar.task_manager_chores
title: Maintenance Calendar
```

---

## ❓ FAQ & Troubleshooting

### Where is my data stored?
All tasks, things, spare parts, users, and settings are stored locally in Home Assistant's secure storage directory (`.storage/task_manager_data`). Your data never leaves your local network.

### How does Odometer Mode work for cars or machines?
Traditional counters assume the sensor is reset to 0 upon completion. However, car odometers or electricity meters only count up. When **Odometer Mode** is enabled on a Thing:
1. `current_value` continues to follow your external HA sensor (e.g. `65,400 km`).
2. `last_reset_value` stores the reading at the last service (e.g. `35,400 km`).
3. The delta $\Delta = 65,400 - 35,400 = 30,000 \text{ km}$ triggers the chore.
4. When marked as done, `last_reset_value` is updated to the current reading (`65,400 km`), and the cycle restarts.

### Can I turn off gamification completely?
Yes! In the sidebar panel, open **Settings** > **Preferences** and disable **Enable Gamification**. Points, streaks, badges, sounds, confetti, and the leaderboard tab will be hidden, providing a clean and minimalist maintenance manager.

### How do Subtask Smart Resets work?
Recurring chores with subtasks (e.g. *"Clean Kitchen"* with subtasks: *Wipe Countertops*, *Empty Sink*, *Mop Floor*) will have all subtasks automatically reset to unchecked once the parent chore is completed, ready for the next interval.

### How do I backup and restore?
Go to **Settings** > **Backup & Restore** in the Task Manager sidebar panel to export a complete JSON snapshot of all your tasks, Things, spare parts, and members. You can restore this backup anytime with a single click.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
