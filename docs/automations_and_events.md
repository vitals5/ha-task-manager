# Automations, Events & Blueprints

Task Manager communicates natively with Home Assistant's event bus, allowing you to build rich automations, smart notifications, and sensor-driven workflows.

---

## Table of Contents

- [Event Bus Integration](#event-bus-integration)
- [Task Reminders (`task_manager_task_reminder`)](#task-reminders-event-task_manager_task_reminder)
- [Daily Digest Blueprint](#daily-digest-blueprint)
- [Practical Automation Recipes](#practical-automation-recipes)
  - [1. Push Notification 1 Hour Before Due Time](#1-push-notification-1-hour-before-due-time)
  - [2. Assignee-Targeted Mobile Notification](#2-assignee-targeted-mobile-notification)
  - [3. NFC Tag Quick-Completion (e.g. Coffee Descaling)](#3-nfc-tag-quick-completion-eg-coffee-descaling)
  - [4. Count Appliance Usage Cycles](#4-count-appliance-usage-cycles)
  - [5. Vehicle Maintenance Alert (30,000 km or 24 Months)](#5-vehicle-maintenance-alert-30000-km-or-24-months)
  - [6. Spare Part Low-Stock Warning](#6-spare-part-low-stock-warning)

---

## Event Bus Integration

Whenever key milestones occur, Task Manager dispatches standardized events to Home Assistant:

| Event Type | Trigger Moment | Key Payload Attributes |
|---|---|---|
| `task_manager_task_reminder` | Calculated reminder time reached (e.g. 15m, 1h, 1d before). | `task_title`, `due_date`, `due_time`, `assignee`, `reminder_offset_minutes` |
| `task_manager_task_due` | Midnight check: task is due today. | `task_id`, `task_title`, `priority`, `assignee` |
| `task_manager_task_overdue` | Midnight check: task is overdue. | `task_id`, `task_title`, `priority`, `due_date` |
| `task_manager_task_completed` | User or service marks chore done. | `task_title`, `completed_by`, `points`, `cost`, `duration_minutes` |
| `task_manager_part_low_stock` | Part quantity falls to/below minimum. | `name`, `stock`, `min_stock`, `storage_location`, `reorder_url` |

---

## Task Reminders (Event: `task_manager_task_reminder`)

When creating a task, you can select reminder offsets:
- `0` (At due time)
- `15` (15 minutes before)
- `60` (1 hour before)
- `1440` (1 day before)

### How It Works:
1. If you configure a due time of `18:00` and select **1 hour before**, Task Manager schedules an internal timer for `17:00:00`.
2. *(If no due time was entered, `09:00` is used by default).*
3. At `17:00:00`, Task Manager fires `task_manager_task_reminder`.
4. Your Home Assistant automation listens for this event and sends a notification to your phone, smartwatch, or smart speakers.

---

## Daily Digest Blueprint

Task Manager includes a pre-packaged automation blueprint:
- **Location**: `blueprints/automation/task_manager/task_manager_notify.yaml`
- **Features**:
  - Sends a consolidated notification at a scheduled hour (e.g. `09:00 AM`).
  - Summarizes all tasks that are **due today**, **overdue**, or **due soon**.
  - Includes overdue day counts (e.g. *Clean Gutters (Overdue by 3d)*).
  - Supports filtering by **Tag** or **Assignee** (great for sending personal digests to individual family members).

---

## Practical Automation Recipes

### 1. Push Notification 1 Hour Before Due Time
```yaml
alias: "Task Manager: 1-Hour Reminder to Phone"
trigger:
  - platform: event
    event_type: task_manager_task_reminder
    event_data:
      reminder_offset_minutes: 60
action:
  - action: notify.notify
    data:
      title: "⏰ Upcoming Chore: {{ trigger.event.data.task_title }}"
      message: >
        Due in 1 hour{% if trigger.event.data.due_time %} (at {{ trigger.event.data.due_time }}){% endif %}!
      data:
        url: "/task-manager"
```

---

### 2. Assignee-Targeted Mobile Notification
Route notifications directly to the assigned family member's device:
```yaml
alias: "Task Manager: Route Reminders to Member Device"
trigger:
  - platform: event
    event_type: task_manager_task_reminder
action:
  - choose:
      - conditions:
          - condition: template
            value_template: "{{ trigger.event.data.assignee == 'user_vitali' }}"
        sequence:
          - action: notify.mobile_app_vitali_phone
            data:
              title: "⏰ Chore Reminder: {{ trigger.event.data.task_title }}"
              message: "Due in {{ trigger.event.data.reminder_offset_minutes }} minutes!"
      - conditions:
          - condition: template
            value_template: "{{ trigger.event.data.assignee == 'user_sarah' }}"
        sequence:
          - action: notify.mobile_app_sarah_phone
            data:
              title: "⏰ Chore Reminder: {{ trigger.event.data.task_title }}"
              message: "Due in {{ trigger.event.data.reminder_offset_minutes }} minutes!"
```

---

### 3. NFC Tag Quick-Completion (e.g. Coffee Descaling)
Attach an adhesive NFC tag to your coffee machine or water filter:
```yaml
alias: "Task Manager: NFC Coffee Machine Descaled"
trigger:
  - platform: tag
    tag_id: "e5a31bc0-4299-4d8b-967a-18bcf5061dc1"
action:
  - action: task_manager.complete_task
    data:
      task_title: "Descale Coffee Machine"
  - action: notify.notify
    data:
      title: "✓ Coffee Machine Reset"
      message: "Coffee machine descaling marked done and counter reset to 0."
```

---

### 4. Count Appliance Usage Cycles
Automatically count robot vacuum cleaning runs or washing machine cycles:
```yaml
alias: "Task Manager: Count Robot Vacuum Cleaning Runs"
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

### 5. Vehicle Maintenance Alert (30,000 km or 24 Months)
Notify when your car's odometer interval or 24-month schedule triggers the task:
```yaml
alias: "Car: Major Inspection Alert"
trigger:
  - platform: state
    entity_id: sensor.task_manager_major_car_service
    to: "due"
action:
  - action: notify.notify
    data:
      title: "🚗 Vehicle Inspection Due"
      message: "The 30,000 km interval or 24-month schedule has arrived. Please schedule service!"
      data:
        url: "/task-manager"
```

---

### 6. Spare Part Low-Stock Warning
Receive an actionable notification with a direct reorder link when supplies are low:
```yaml
alias: "Task Manager: Reorder Spare Part Alert"
trigger:
  - platform: event
    event_type: task_manager_part_low_stock
action:
  - action: notify.notify
    data:
      title: "📦 Low Supplies: {{ trigger.event.data.name }}"
      message: >
        Only {{ trigger.event.data.stock }} left in {{ trigger.event.data.storage_location }}. Reorder now!
      data:
        url: "{{ trigger.event.data.reorder_url }}"
```
