# Utility & Meter Reading Tasks

Task Manager includes a dedicated **Meter Reading Task** system designed to replace external utility spreadsheets for tracking household electricity, water, gas, heating oil, and solar feed-in metrics.

---

## Table of Contents

- [Overview](#overview)
- [Multi-Register Meters (Electricity, Gas, Water)](#multi-register-meters-electricity-gas-water)
- [Recording a Reading](#recording-a-reading)
- [Reading History Dialog](#reading-history-dialog)
  - [Opening the History from the Task Card](#opening-the-history-from-the-task-card)
  - [Reviewing Consumption Deltas](#reviewing-consumption-deltas)
- [Correcting & Deleting Erroneous Entries](#correcting--deleting-erroneous-entries)
- [Exporting History to CSV](#exporting-history-to-csv)
- [Recording Readings via Service Call](#recording-readings-via-service-call)

---

## Overview

Unlike standard chores where a task is simply marked "Done", utility meters require you to input the exact numeric reading shown on your gauge.

When a task has its **Task Type** set to `📟 Meter / Utility Reading` (`task_type: "reading"`):
- The card displays the last recorded meter values.
- Checking off the task opens a specialized numerical entry dialog showing the previous reading and prompting for the new value.
- Real-time consumption differences ($\Delta$) are calculated automatically.
- Each reading is preserved in an immutable, timestamped history log.

---

## Multi-Register Meters (Electricity, Gas, Water)

Most modern electricity meters have multiple sub-registers (e.g. OBIS numbers):
- **1.8.1**: HT / Peak tariff (High tariff)
- **1.8.2**: NT / Off-peak tariff (Low tariff)
- **2.8.0**: Solar feed-in to the grid

Rather than creating three separate tasks that clutter your schedule, Task Manager lets you define multiple registers within a single task:

1. Create a task with type **Meter / Utility Reading**.
2. Click **+ Add Register** in the task form.
3. Define the sub-counters:
   - Register 1: Name: `HT (Peak)`, Unit: `kWh`
   - Register 2: Name: `NT (Off-Peak)`, Unit: `kWh`
   - Register 3: Name: `Feed-in`, Unit: `kWh`
4. Set your recurrence (e.g. Monthly on the 1st of the month).

---

## Recording a Reading

When a reading task becomes due:

1. Click the checkmark `✓` or the note icon `📝` on the task card.
2. The completion modal displays:
   - Each register name and unit.
   - The **Last Reading Value** for immediate reference.
   - An input field for the new meter value.
3. As you type your new reading, Task Manager displays the **Consumption / Delta** ($\Delta$) in real time (e.g. `+142 kWh`).
4. Optionally enter notes or adjustments.
5. Click **Done (`✓`)**.
6. The reading is recorded, the task advances to the next recurrence date, and points/streaks are awarded.

---

## Reading History Dialog

### Opening the History from the Task Card

You can review all historical readings at any time without having to open the task editor:

1. On the task card in the **Tasks** tab, click the **`📊 Reading History`** button located directly beneath the title.
2. *(Alternatively, click the cyan `📟 Reading (...)` badge or the `📊` button in the action bar).*
3. A clean, dedicated dialog opens showing the history table and metrics.

### Reviewing Consumption Deltas

The table displays:
- **Date & Time**: Exact timestamp of the recording.
- **Readings & Deltas**: Each register reading and the consumption delta relative to the previous entry:
  - Positive consumption is highlighted in cyan (e.g. `+185 kWh`).
  - Feed-in or negative adjustments are highlighted in orange.
- **User**: Which household member performed the reading.
- **Notes**: Notes entered during recording.
- **Action**: Delete / rollback button (`🗑️`).

---

## Correcting & Deleting Erroneous Entries

Typos happen. If an incorrect reading was entered:

1. Open the **Reading History** dialog.
2. Locate the incorrect entry.
3. Click the red trash can icon **`🗑️`** in the *Action* column.
4. Confirm deletion.
5. **Automatic Rollback**: Task Manager deletes the log entry and automatically restores the previous valid meter reading on the task and register states.

---

## Exporting History to CSV

Need your meter readings for Excel, tax filings, or utility billing?

1. Open the **Reading History** dialog.
2. Click **`📥 Export CSV`** in the top-right corner.
3. A UTF-8 encoded `.csv` file is generated and downloaded immediately:
   ```csv
   "Datum";"Zaehlwerk";"Zaehlerstand";"Einheit";"Differenz";"Benutzer";"Notizen"
   "2026-09-01 18:00:00";"HT (Peak)";"14500";"kWh";"210";"Vitali";"Monthly reading"
   "2026-09-01 18:00:00";"NT (Off-Peak)";"8200";"kWh";"115";"Vitali";""
   "2026-08-01 18:00:00";"HT (Peak)";"14290";"kWh";"195";"Vitali";""
   ```

---

## Recording Readings via Service Call

You can record readings automatically from Home Assistant automations or ESPHome smart meter readers (e.g. optical IR readers) using the `task_manager.record_reading` action:

```yaml
alias: "Smart Meter: Auto-Record Monthly Electricity Reading"
trigger:
  - platform: time
    at: "23:59:00"
condition:
  - condition: template
    value_template: "{{ now().day == 1 }}"
action:
  - action: task_manager.record_reading
    data:
      task_title: "Monthly Electricity Reading"
      reading_value: "{{ states('sensor.power_meter_total_energy') | float }}"
      notes: "Recorded automatically from smart optical meter"
```
