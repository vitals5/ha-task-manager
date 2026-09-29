# Home Assistant Actions & Services Reference

Task Manager provides 18 dedicated actions (services) allowing full control from Home Assistant scripts, automations, NFC tags, voice commands, and external integrations.

---

## Table of Contents

- [Task Management Services](#task-management-services)
  - [`task_manager.create_task`](#task_managercreate_task)
  - [`task_manager.complete_task`](#task_managercomplete_task)
  - [`task_manager.reset_task`](#task_managerreset_task)
  - [`task_manager.set_last_done_date`](#task_managerset_last_done_date)
  - [`task_manager.pause_task`](#task_managerpause_task)
  - [`task_manager.resume_task`](#task_managerresume_task)
  - [`task_manager.skip_task`](#task_managerskip_task)
  - [`task_manager.assign_task`](#task_managerassign_task)
  - [`task_manager.duplicate_task`](#task_managerduplicate_task)
  - [`task_manager.move_task`](#task_managermove_task)
  - [`task_manager.delete_task`](#task_managerdelete_task)
- [Things & Appliance Tracking Services](#things--appliance-tracking-services)
  - [`task_manager.update_thing`](#task_managerupdate_thing)
  - [`task_manager.increment_thing`](#task_managerincrement_thing)
- [Meter Reading Services](#meter-reading-services)
  - [`task_manager.record_reading`](#task_managerrecord_reading)
- [Gamification Services](#gamification-services)
  - [`task_manager.award_points`](#task_manageraward_points)
- [Spare Parts Inventory Services](#spare-parts-inventory-services)
  - [`task_manager.save_part`](#task_managersave_part)
  - [`task_manager.adjust_part_stock`](#task_manageradjust_part_stock)
  - [`task_manager.delete_part`](#task_managerdelete_part)

---

## Task Management Services

### `task_manager.create_task`
*Alias: `task_manager.add_task`*

Creates a new chore or maintenance task in Task Manager.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `title` | string | **Yes** | Title or name of the task. |
| `description` | string | No | Additional notes, instructions, or links. |
| `due_date` | string | No | Due date in `YYYY-MM-DD` format (defaults to today). |
| `due_time` | string | No | Due time in `HH:MM` format (defaults to `09:00`). |
| `priority` | string | No | Priority level: `p1`, `p2`, `p3`, `p4`, `none` (default: `none`). |
| `assignee` | string | No | User ID of the assigned member. |
| `tags` | string | No | Comma-separated list of tags (e.g. `kitchen, daily`). |
| `reminders` | string | No | Comma-separated minute offsets before due time (e.g. `0, 15, 60`). |
| `points` | number | No | Points awarded upon completion (default: `10`). |
| `linked_thing_id` | string | No | ID of a Thing linked to this task. |

```yaml
action: task_manager.create_task
data:
  title: "Hang up Laundry"
  description: "Washing machine cycle finished."
  priority: "p2"
  due_date: "2026-09-30"
  due_time: "18:30"
  points: 15
```

---

### `task_manager.complete_task`
*Alias: `task_manager.mark_as_done`*

Marks a task as completed, awards points, advances recurrence, rotates assignee, and resets linked Things.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `task_id` | string | Either | Unique ID of the task. |
| `task_title` | string | Either | Match task by exact title. |
| `entity_id` | string | Either | Sensor entity or button entity ID of the task. |
| `user_id` | string | No | User who receives completion credit (defaults to active assignee). |
| `cost` | number | No | Financial cost spent on this task/maintenance. |
| `duration_minutes` | number | No | Time spent performing the task. |
| `notes` | string | No | Completion notes recorded in history. |
| `completed_at` | string | No | ISO timestamp to backdate completion. |
| `reading_value` | number | No | Numeric reading value if completing a reading task. |

```yaml
action: task_manager.complete_task
data:
  task_title: "Descale Coffee Machine"
  duration_minutes: 20
  notes: "Used 2 tablets"
```

---

### `task_manager.reset_task`
*Alias: `task_manager.reopen_task`*

Resets a completed task back to pending.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `task_id` | string | Either | Unique ID of the task. |
| `task_title` | string | Either | Title of the task to reopen. |
| `assigned_person` | string | No | Reopen all completed tasks for this user. |
| `tag` | string | No | Reopen all completed tasks matching this tag. |

```yaml
action: task_manager.reset_task
data:
  task_title: "Clean Kitchen Counter"
```

---

### `task_manager.set_last_done_date`

Manually overrides the last completion date of a recurring task and recalculates its due date.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `date` | string | **Yes** | Date in `YYYY-MM-DD` format. |
| `task_id` | string | Either | Unique ID of the task. |
| `task_title` | string | Either | Title of the task. |

```yaml
action: task_manager.set_last_done_date
data:
  task_title: "Oil Change"
  date: "2026-09-15"
```

---

### `task_manager.pause_task`

Temporarily suspends a task so it will not become due until resumed.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `task_id` | string | Either | Unique ID of the task. |
| `task_title` | string | Either | Title of the task to pause. |

```yaml
action: task_manager.pause_task
data:
  task_title: "Mow the Lawn"
```

---

### `task_manager.resume_task`

Resumes a paused task, setting it back to active.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `task_id` | string | Either | Unique ID of the task. |
| `task_title` | string | Either | Title of the task to resume. |

```yaml
action: task_manager.resume_task
data:
  task_title: "Mow the Lawn"
```

---

### `task_manager.skip_task`

Skips the current recurrence of a task without awarding points, advancing its due date to the next interval.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `task_id` | string | Either | Unique ID of the task. |
| `task_title` | string | Either | Title of the task to skip. |

```yaml
action: task_manager.skip_task
data:
  task_title: "Weekly Vacuuming"
```

---

### `task_manager.assign_task`

Assigns or reassigns a task to another household user.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `person` | string | **Yes** | User ID or person entity ID to assign. |
| `task_id` | string | Either | Unique ID of the task. |
| `task_title` | string | Either | Title of the task. |

---

### `task_manager.duplicate_task`

Clones an existing task with all attributes.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `task_id` | string | Either | Unique ID of the task to clone. |
| `task_title` | string | Either | Title of the task to clone. |

---

### `task_manager.move_task`

Moves a task to another external provider list or back to native storage.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `target_provider` | string | No | Entity ID of target provider or `'task_manager'`. |
| `task_id` | string | Either | Unique ID of the task. |
| `task_title` | string | Either | Title of the task. |

---

### `task_manager.delete_task`

Permanently deletes a task.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `task_id` | string | **Yes** | Unique identifier of the task. |

---

## Things & Appliance Tracking Services

### `task_manager.update_thing`

Updates, increments, sets, or resets a Thing counter or meter.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `thing_id` | string | Either | Unique ID of the Thing. |
| `entity_id` | string | Either | Sensor entity of the Thing (`sensor.task_manager_thing_*`). |
| `value` | number | No | Set absolute value directly. |
| `delta` | number | No | Increment or decrement value by this amount. |
| `reset` | boolean | No | Reset current value back to 0 (or advance last reset value in odometer mode). |
| `target_value` | number | No | Change threshold target value. |
| `threshold_operator` | string | No | Threshold condition: `>=` or `<=`. |
| `is_odometer` | boolean | No | Enable/disable continuous counter (odometer) mode. |
| `last_reset_value` | number | No | Update counter reading at last maintenance. |

```yaml
action: task_manager.update_thing
data:
  thing_id: "thing_coffee_machine"
  delta: 1
```

---

### `task_manager.increment_thing`

Convenience action to increment or decrement a Thing counter without needing to know its exact ID.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `amount` | number | No | Amount to change by (default: `1.0`). Use negative numbers to decrement. |
| `thing_name` | string | Either | Name of the Thing. |
| `thing_id` | string | Either | ID of the Thing. |
| `entity_id` | string | Either | Sensor entity of the Thing. |

```yaml
action: task_manager.increment_thing
data:
  thing_name: "Water Softener Salt"
  amount: -1.5
```

---

## Meter Reading Services

### `task_manager.record_reading`

Records a counter or meter reading for a reading task and advances recurrence.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `reading_value` | number | **Yes** | Numeric value read from gauge. |
| `task_id` | string | Either | Unique ID of the task. |
| `task_title` | string | Either | Title of the task. |
| `notes` | string | No | Notes or remarks for this reading. |
| `completed_at` | string | No | Timestamp if backdating. |
| `user_id` | string | No | User who took the reading. |

```yaml
action: task_manager.record_reading
data:
  task_title: "Water Meter"
  reading_value: 342.85
  notes: "End of month reading"
```

---

## Gamification Services

### `task_manager.award_points`

Awards or adjusts gamification points for a household member.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | **Yes** | Target user ID. |
| `points` | number | **Yes** | Points to award. |
| `reason` | string | No | Optional note or bonus reason. |

```yaml
action: task_manager.award_points
data:
  user_id: "user_vitali"
  points: 50
  reason: "Spring deep clean bonus"
```

---

## Spare Parts Inventory Services

### `task_manager.save_part`

Creates or updates a spare part in the inventory shelf.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | **Yes** | Part name. |
| `id` | string | No | Unique ID (omit to create a new part). |
| `thing_id` | string | No | Linked Thing ID. |
| `part_number` | string | No | SKU / OEM article number. |
| `stock` | number | No | Current stock quantity (default: `0`). |
| `min_stock` | number | No | Reorder threshold (default: `1`). |
| `unit` | string | No | Unit of measure (default: `pcs`). |
| `unit_price` | number | No | Estimated cost per unit. |
| `storage_location` | string | No | Where the item is stored. |
| `reorder_url` | string | No | Web purchase URL. |

---

### `task_manager.adjust_part_stock`

Adjusts the quantity of a spare part in inventory.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `part_id` | string | **Yes** | Unique ID of the part. |
| `stock` | number | Either | Set new absolute stock count. |
| `delta` | number | Either | Relative change (+/-). |

```yaml
action: task_manager.adjust_part_stock
data:
  part_id: "part_hepa_filter"
  delta: -1
```

---

### `task_manager.delete_part`

Permanently removes a spare part from the inventory.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `part_id` | string | **Yes** | Unique ID of the part to remove. |
