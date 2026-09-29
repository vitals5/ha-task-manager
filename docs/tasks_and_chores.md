# Tasks & Chores Management

Task Manager provides a rich task scheduling and management system tailored for households, vacation homes, and workshops.

---

## Table of Contents

- [Task Types](#task-types)
- [Priorities and Dates](#priorities-and-dates)
- [Recurrence Scheduling](#recurrence-scheduling)
  - [Calendar Schedule vs. Interval after Completion](#calendar-schedule-vs-interval-after-completion)
  - [Weekday Selection](#weekday-selection)
  - [Standalone Sensor-Triggered Tasks](#standalone-sensor-triggered-tasks)
- [Subtasks & Smart Reset](#subtasks--smart-reset)
- [Assignee Rotation Modes](#assignee-rotation-modes)
- [Pausing and Resuming Tasks](#pausing-and-resuming-tasks)
- [Skipping Recurrences](#skipping-recurrences)
- [QR Code Quick-Completion](#qr-code-quick-completion)
- [Detailed Work Logging](#detailed-work-logging)

---

## Task Types

When creating or editing a task, you can select between two fundamental task types:

| Task Type | Icon | Purpose |
|---|---|---|
| **Maintenance / Regular Chore** | 🧹 | Standard household chores, recurring cleaning, filter replacements, oil changes, or manual tasks. |
| **Meter / Utility Reading** | 📟 | Reading utility meters (electricity, gas, water, oil level, solar battery). Includes multi-register tracking, history tables, delta calculation, and CSV export. |

---

## Priorities and Dates

Tasks can be categorized into four distinct priority tiers or left unprioritized:

- **P1 (Urgent - Red)**: Critical maintenance or time-sensitive tasks. Triggers high-priority visual chips and is exposed to binary sensors.
- **P2 (High - Orange)**: Important regular maintenance (e.g. car inspection, water softener salt).
- **P3 (Medium - Blue)**: Standard household chores.
- **P4 (Low - Gray)**: Optional or low-impact chores.
- **None**: No priority color badge.

### Dates & Timed Chores
- **Due Date**: Specify the calendar due date (`YYYY-MM-DD`).
- **Due Time**: Optional time of day (`HH:MM`). When a due time is specified, Home Assistant Calendar displays the task as a timed event rather than an all-day event, and precision reminders trigger relative to this time. If omitted, `09:00` is used as the default time for reminder calculations.

---

## Recurrence Scheduling

Task Manager supports advanced recurring cadences designed for real life, where chores aren't always finished on the exact scheduled date.

### Calendar Schedule vs. Interval after Completion

When configuring recurrence, choose between two modes:

1. **Calendar Schedule (`repeat_every`)**:
   - Preserves a strict calendar cadence regardless of when you complete the task.
   - *Example*: Trash collection every 2 weeks on Thursday. If you take out the trash a day late (Friday), the next due date remains on the scheduled Thursday two weeks later.
2. **Interval after Completion (`repeat_after`)**:
   - Calculates the next due date relative to the actual day you complete the chore.
   - *Example*: Mop floors every 7 days. If you delay mopping until 10 days have passed, you don't want the next occurrence due in 4 days—you want a full 7 days from today.

### Weekday Selection
For weekly tasks, you can select specific weekdays on which the task should occur:
- Select **Monday**, **Wednesday**, and **Friday** for recurring workout or plant watering routines.
- When marked as done, Task Manager automatically advances the due date to the next matching active weekday.

### Standalone Sensor-Triggered Tasks
You can link a task to a **Thing** without setting any time recurrence schedule.
- When the Thing's counter reaches its target threshold (e.g. 50 coffee brews or 30,000 km), the linked task is automatically pulled forward to **today** and becomes due.
- After completing the task, it returns to a waiting state until the sensor triggers it again.

---

## Subtasks & Smart Reset

Large chores often involve multiple checklist items (e.g. *"Clean Bathroom"* &rarr; *Mirror*, *Sink*, *Toilet*, *Shower*).

- Add any number of subtasks in the task modal.
- Check off subtasks directly from the task card in the sidebar panel or dashboard card.
- **Smart Auto-Reset**: When the parent recurring chore is completed, all subtasks are automatically reset to unchecked, ready for the next cycle.

---

## Assignee Rotation Modes

Avoid disputes over who has to do the chore by choosing one of the automatic rotation modes:

| Rotation Mode | Behavior |
|---|---|
| **Fixed / None** | Always assigned to the specified household member. |
| **Round-Robin** | Automatically rotates to the next member in the household list after each completion. |
| **Least Completed** | Automatically assigns the chore to whichever household member has completed the fewest tasks total. |
| **Random** | Selects a member randomly among household members upon each completion. |

---

## Pausing and Resuming Tasks

Some chores are seasonal or temporarily inactive (e.g. mowing the lawn in winter, heating pellet refills during summer, or vehicle maintenance while a car is in storage).

- Click the **Pause button (`⏸️`)** on any task card.
- Paused tasks will not become due, will not trigger reminder notifications, and are hidden from active filters.
- Switch to the **Paused** filter tab in the panel or dashboard card to review and click **Resume (`▶️`)** at any time.

---

## Skipping Recurrences

If a chore does not need to be done for a specific interval (e.g. you were on vacation or the task was handled externally), you can advance the task schedule without awarding points or incrementing completion counters:

- Click the **Skip button (`⏭️`)** on the task card.
- The due date advances to the next scheduled interval immediately.

---

## QR Code Quick-Completion

Task Manager allows you to generate and print QR code labels physically attached to appliances, consumable containers, or room doors:

1. Click the **QR Code button (`📱`)** on any task card.
2. An interactive dialog renders a high-contrast QR code vector graphic.
3. Click **Print Label** to print a compact label directly to your label printer or standard printer.
4. Scanning the QR code with any smartphone camera or the Home Assistant Companion App opens the URL:
   ```text
   http://<ha-ip>:8123/task-manager?complete_task=<task_id>
   ```
5. Task Manager instantly checks off the chore, calculates the next recurrence, resets linked meters, and plays the completion sound!

> [!TIP]
> If you access Home Assistant via `localhost`, the QR code modal will show a friendly reminder to use your local network IP (e.g. `http://192.168.1.100:8123`) or public domain so mobile devices can reach the instance.

---

## Detailed Work Logging

Need to log maintenance details, replacement parts, or financial costs? Click the **Note button (`📝`)** on any task card to open the **Complete with Details** dialog:

- **Duration (minutes)**: Log how long the task took.
- **Total Cost (€ / $)**: Log money spent on parts, oil, or service.
- **Consumed Spare Parts**: Check off spare parts from your [Parts Shelf](spare_parts.md) to automatically deduct inventory.
- **Work Notes**: Enter notes or service remarks.
- **Completion Timestamp**: Backdate the completion timestamp if the work was performed earlier.
