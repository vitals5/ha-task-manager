# Task Manager Documentation

Welcome to the comprehensive documentation for **Task Manager for Home Assistant**.

Task Manager is an all-in-one household chore, appliance/vehicle maintenance, utility meter reading, and spare parts inventory platform designed natively for Home Assistant.

---

## 📚 Table of Contents

1. [**Tasks & Chores Management**](tasks_and_chores.md)
   - Task Types (Standard Chore vs. Meter Reading)
   - Priorities (P1–P4) & Due Dates
   - Flexible Recurrence Cadences (Calendar Schedule vs. After Completion)
   - Weekday Selection & Specific Scheduling
   - Subtasks with Smart Auto-Reset
   - Assignee Rotation (Fixed, Round-Robin, Least Completed, Random)
   - Pausing and Resuming Tasks
   - Skipping Recurrences
   - QR Code Labels & Quick-Complete URL (`?complete_task=<id>`)
   - Detailed Completion Logging (Durations, Costs, Notes, Parts)

2. [**Things & Odometer Tracking**](things_and_odometers.md)
   - What is a "Thing"?
   - Up-Counters vs. Down-Countdowns
   - **Continuous Counter / Odometer Mode** (Vehicle mileage, machine operating hours)
   - Linking Things to External Home Assistant Sensors (`sensor.*`)
   - Threshold Operators (`>=` and `<=`) & Conditional Task Due Dates
   - Completion Scripts (`script.*`)
   - Interactive Panel & Card Controls

3. [**Utility & Meter Reading Tasks**](meter_readings.md)
   - Configuring Meter Reading Tasks
   - Multi-Register Counters (e.g. Electricity Peak/Off-Peak/Feed-in, Water, Gas)
   - Recording Readings & Real-time Delta / Consumption Calculations
   - Dedicated Reading History Dialog & Task Card Quick-Access
   - Correcting & Deleting Erroneous Entries (Automatic Value Rollback)
   - Exporting History to CSV

4. [**Spare Parts & Inventory Shelf**](spare_parts.md)
   - Inventory Tracking for Consumables & Maintenance Parts
   - Item Metadata (SKU, Manufacturer, Model, Storage Location, Unit Price, Reorder URL)
   - Linking Spare Parts to Things
   - Minimum Stock Thresholds & Low-Stock Alerts
   - Automatic Stock Deduction on Chore Completion
   - Equipment Warranty Tracking

5. [**Lovelace Dashboard Card**](lovelace_card.md)
   - `custom:task-manager-card` Overview
   - Automatic Resource Registration
   - Visual GUI Card Editor
   - Filtering by View, Member, and Tags
   - Compact Mode & Gamification Visibility
   - Complete YAML Configuration Examples

6. [**Home Assistant Actions & Services**](services_reference.md)
   - Exhaustive Reference for all 18 Services
   - Parameter Tables, Data Types, and Defaults
   - YAML Service Call Examples for Automations & Scripts

7. [**Automations, Events & Blueprints**](automations_and_events.md)
   - Home Assistant Event Bus Triggers (`task_manager_task_reminder`, `due`, `overdue`, `completed`)
   - Precision Reminders (e.g. 1 hour before due time)
   - Ready-to-use Notification Blueprint (`task_manager_notify.yaml`)
   - Real-World Automation Examples (Car maintenance, NFC tags, vacuum cycles, low-stock warnings)

---

## 🚀 Quick Navigation Links

- **Need help setting up car maintenance (30,000 km or 24 months)?** See [Things & Odometer Tracking](things_and_odometers.md#real-world-example-car-maintenance-every-30000-km-or-24-months).
- **Need help setting up electricity meter readings (HT / NT / Feed-in)?** See [Utility & Meter Reading Tasks](meter_readings.md#multi-register-meters-electricity-gas-water).
- **Need help creating phone notifications for reminders?** See [Automations, Events & Blueprints](automations_and_events.md#task-reminders-event-task_manager_task_reminder).
- **Need help adding the card to your Lovelace dashboard?** See [Lovelace Dashboard Card](lovelace_card.md#yaml-configuration-examples).
