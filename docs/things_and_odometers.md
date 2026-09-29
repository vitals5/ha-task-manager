# Things & Odometer Tracking

In Task Manager, **"Things"** represent non-task physical appliances, machinery, vehicles, filters, and consumables that require maintenance after a certain amount of use or wear.

---

## Table of Contents

- [What is a "Thing"?](#what-is-a-thing)
- [Counter Types: Up vs. Down](#counter-types-up-vs-down)
- [Continuous Counter / Odometer Mode](#continuous-counter--odometer-mode)
  - [The Monotonic Meter Problem](#the-monotonic-meter-problem)
  - [How Odometer Mode Works](#how-odometer-mode-works)
  - [Real-World Example: Car Maintenance (Every 30,000 km or 24 Months)](#real-world-example-car-maintenance-every-30000-km-or-24-months)
- [External Home Assistant Sensor Linkage](#external-home-assistant-sensor-linkage)
- [Threshold Operators & Conditional Due Dates](#threshold-operators--conditional-due-dates)
- [Completion Scripts](#completion-scripts)
- [Interactive Controls & Services](#interactive-controls--services)

---

## What is a "Thing"?

While tasks represent actions (e.g. *"Replace water filter"*), Things represent the actual physical objects or meters being measured:
- **Coffee Machine**: Descaling needed every 150 brews.
- **Robot Vacuum**: Dustbin emptying needed every 5 cleaning runs; filter replacement every 150 hours.
- **Water Filter**: Cartridge replacement needed every 30 days or 500 liters.
- **Car / Vehicle**: Inspection due every 30,000 km or 24 months.
- **Lawnmower / Tractor**: Oil change due every 50 operating hours.
- **Water Softener**: Salt top-up needed when salt level falls below 10 kg.

---

## Counter Types: Up vs. Down

When creating a Thing in the **Things** tab, you choose the counting direction:

| Counter Type | Behavior | Example |
|---|---|---|
| **Counts Up (`counter`)** | Value increments over time until it reaches a maximum limit. Trigger condition: `>=` target. | Brew count (0 &rarr; 150 brews), robot vacuum cleaning runs (0 &rarr; 5 runs). |
| **Counts Down (`countdown`)** | Value decrements over time until it drops below a minimum threshold. Trigger condition: `<=` target. | Remaining filter life (100% &rarr; 10%), remaining salt in tank (50 kg &rarr; 10 kg). |

---

## Continuous Counter / Odometer Mode

### The Monotonic Meter Problem
Standard appliance counters assume the counter can be reset to `0` once maintenance is performed (e.g. brew count drops back to 0).

However, **car odometers, engine operating hours, electric car charge counters, and cumulative energy/water meters are monotonically increasing**—they never reset to zero. If your car has 45,000 km, you cannot set its odometer sensor back to 0.

### How Odometer Mode Works
When you enable **Fortlaufender Gesamtzähler (Odometer)** on a Thing:

1. **Total Reading Preserved (`current_value`)**:
   - The Thing continues to display and synchronize the true reading from your Home Assistant sensor (e.g. `45,000 km`).
2. **Reading at Last Maintenance Stored (`last_reset_value`)**:
   - Task Manager stores the exact reading when maintenance was last performed (e.g. `30,000 km`).
3. **Threshold Acts as an Interval**:
   - The configured target value (e.g. `30,000 km`) acts as the service interval.
   - The trigger condition evaluates the delta since the last reset:
     $$\Delta = \text{current\_value} - \text{last\_reset\_value} \ge \text{target\_value}$$
4. **Automatic Maintenance Reset**:
   - When the linked maintenance chore is completed with the action *Thing zurücksetzen (Reset Thing)*, `last_reset_value` is automatically updated to the current reading:
     $$\text{last\_reset\_value} \leftarrow \text{current\_value}$$
   - The physical sensor is untouched, and the delta begins counting from `0 km` again!
5. **Clear UI Progress**:
   - The Thing card displays both the progress toward the next maintenance (`15,000 / 30,000 km (seit Wartung)`) and the cumulative vehicle odometer (`Gesamt: 45,000 km`).

---

### Real-World Example: Car Maintenance (Every 30,000 km or 24 Months)

Here is how to set up the classic vehicle maintenance rule where inspection is due every 30,000 km or 24 months, whichever comes first:

#### Step 1: Create the Car Thing
1. Open the **Things** tab and click **New Thing**.
2. **Name**: `Car Service Odometer`
3. **Type**: `Counter (counts up)`
4. **Target / Threshold**: `30000`
5. **Unit**: `km`
6. **External Entity**: Select your car's odometer sensor (e.g. `sensor.car_odometer`).
7. **Continuous Counter (Odometer)**: Check the checkbox.
8. **Reading at Last Maintenance**: Enter the odometer reading at your last service (e.g. `30000`). If left blank, it starts from the current sensor reading.

#### Step 2: Create the Maintenance Task
1. Open the **Tasks** tab and click **New Task**.
2. **Title**: `Major Car Service & Inspection`
3. **Linked Thing**: Select `Car Service Odometer`.
4. **Thing Action on Completion**: Select `Reset Thing`.
5. **Recurrence**:
   - Mode: `Interval after completion`
   - Repeat Every: `24 Months`
6. **Due Date**: Set the calendar date 24 months after the last service.

#### How the Dual Trigger Operates:
- **Scenario A (Kilometers reached first)**: If you drive 30,000 km within 14 months, the Thing reaches its threshold. Task Manager immediately pulls the task's due date forward to **today** and marks it as due.
- **Scenario B (Time reached first)**: If 24 months pass and you have only driven 18,000 km, the calendar schedule triggers and the task becomes due.
- **Upon Completion**: When you check off the task, the next due date is scheduled for `today + 24 months`, and `last_reset_value` is set to the car's current mileage. Both countdowns start fresh!

---

## External Home Assistant Sensor Linkage

Things can be linked to any numeric Home Assistant entity:
- `sensor.*` (e.g. energy meters, temperature, humidity, operational hours, distances)
- `input_number.*`
- `counter.*`

Whenever the entity changes state in Home Assistant, Task Manager automatically updates the Thing's value and re-evaluates all trigger conditions in real time.

---

## Threshold Operators & Conditional Due Dates

When defining a Thing, choose the operator:
- `>=` Greater than or equal (standard for up-counters and odometers).
- `<=` Less than or equal (standard for countdowns and consumables).

### Dynamic Task Due Dates
When a Thing triggers:
- Any task linked to the Thing that has a future due date is automatically updated with a due date of **today**.
- A notification event `task_manager_task_due` is dispatched across Home Assistant.

---

## Completion Scripts

Under the Thing configuration or task configuration, you can select an optional Home Assistant `script.*` entity:
- When the chore is completed, Task Manager automatically executes the script.
- *Examples*:
  - Call a service to reset a robot vacuum's internal accessory state.
  - Send a command to a smart coffee machine.
  - Flash a smart light strip green to confirm maintenance completion.

---

## Interactive Controls & Services

Things can be controlled manually or via automations:
- **Interactive Buttons**: Each Thing card features quick `+1`, `-1`, and `Reset` action buttons.
- **Home Assistant Services**:
  - `task_manager.update_thing`: Set absolute value, adjust by delta, or reset.
  - `task_manager.increment_thing`: Convenience action to increment or decrement without knowing the ID.
- **Sensor Attributes**:
  The generated entity `sensor.task_manager_thing_<name>` exposes:
  ```yaml
  state: 15000
  attributes:
    target: 30000
    is_odometer: true
    last_reset_value: 30000
    delta_since_reset: 15000
    next_threshold_value: 60000
    percent: 50.0
    unit_of_measurement: "km"
  ```
