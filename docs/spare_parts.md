# Spare Parts & Supplies Shelf

Task Manager features a dedicated **Parts Shelf** tab to track spare parts, consumables, filters, and maintenance supplies.

---

## Table of Contents

- [Overview](#overview)
- [Part Metadata & Fields](#part-metadata--fields)
- [Linking Parts to Things & Equipment](#linking-parts-to-things--equipment)
- [Minimum Stock & Low-Stock Warnings](#minimum-stock--low-stock-warnings)
- [Deducting Parts During Maintenance](#deducting-parts-during-maintenance)
- [Equipment Warranty Tracking](#equipment-warranty-tracking)
- [Spare Parts Services & Automation](#spare-parts-services--automation)

---

## Overview

Maintenance often fails simply because replacement supplies aren't available when needed (e.g. running out of water filter cartridges, descaling tablets, or vacuum bags).

The **Parts Shelf** allows you to:
- Track how many units are stored in your pantry, basement, or garage.
- Link parts directly to appliances and machines.
- Automatically receive low-stock alerts before supplies run out.
- Deduct consumed parts directly when checking off chores.
- Store direct web links to reorder items with one click.

---

## Part Metadata & Fields

When adding or editing a spare part in the **Spare Parts & Supplies** tab, you can track:

| Field | Description | Example |
|---|---|---|
| **Part Name** | Descriptive name of the consumable or part. | `HEPA Filter Set`, `Descaler Tablets` |
| **Part Number / SKU** | OEM or manufacturer article number. | `HF-2024-X`, `00311907` |
| **Manufacturer** | Brand or maker. | `Roborock`, `Bosch`, `Miele` |
| **Model** | Specific appliance model compatibility. | `S7 MaxV Ultra`, `Series 8` |
| **Current Stock** | Number of items currently in inventory. | `3` |
| **Minimum Stock** | Threshold that triggers a reorder warning. | `1` |
| **Unit** | Measurement unit. | `pcs`, `packs`, `liters`, `kg` |
| **Unit Price** | Cost per single unit. | `14.99 €` |
| **Storage Location** | Where the item is kept physically. | `Basement Shelf 2`, `Kitchen Under-sink` |
| **Reorder URL** | Direct hyperlink to purchase more. | `https://amazon.de/dp/...` |
| **Notes** | Additional instructions or OEM notes. | `Change every 6 months` |

---

## Linking Parts to Things & Equipment

Each spare part can be associated with a specific **Thing**:
- *HEPA Filter* &rarr; Linked to *Robot Vacuum*
- *Water Softener Salt (25kg)* &rarr; Linked to *Water Softener Plant*
- *Oil Filter HU 711/51 x* &rarr; Linked to *Family Car*

This linkage ensures that when you inspect an appliance or create maintenance tasks, the compatible parts are suggested automatically.

---

## Minimum Stock & Low-Stock Warnings

Whenever the **Current Stock** drops to or below the **Minimum Stock** value:
- The part card in the panel displays an orange **`⚠️ Low Stock!`** badge.
- A **Reorder** button appears on the card, linking directly to your configured store URL.
- Task Manager fires the event `task_manager_part_low_stock` on the Home Assistant Event Bus, enabling automatic notifications.

---

## Deducting Parts During Maintenance

When completing a chore that consumes supplies:

1. Click the note button `📝` (**Complete with Details**) on the task card.
2. In the **Consumed Spare Parts** section, check off the parts used (e.g. *1x HEPA Filter*).
3. If multiple units were used, adjust the quantity.
4. Click **Done (`✓`)**.
5. Task Manager records the work log and automatically decrements the inventory on your Parts Shelf.

---

## Equipment Warranty Tracking

For major appliances, power tools, or vehicles, you can track warranty status:

- **Installation / Purchase Date**: Date equipment was acquired.
- **Warranty Expiry Date**: Date factory or extended warranty expires.
- **Visual Status Badges**:
  - 🟢 **Warranty Valid**: Appliance is within warranty coverage.
  - 🟡 **Warranty Expiring Soon**: Within 30 days of expiration.
  - ⚪ **Warranty Expired**: Coverage has ended.

---

## Spare Parts Services & Automation

You can manage inventory via Home Assistant automations and scripts:

### Adjusting Inventory
```yaml
alias: "Water Softener: Salt Bag Added"
action:
  - action: task_manager.adjust_part_stock
    data:
      part_id: "part_salt_25kg"
      delta: 2   # Adds 2 bags to inventory
```

### Low Stock Mobile Notification
```yaml
alias: "Task Manager: Reorder Spare Part Alert"
trigger:
  - platform: event
    event_type: task_manager_part_low_stock
action:
  - action: notify.notify
    data:
      title: "📦 Supply Alert: {{ trigger.event.data.name }}"
      message: >
        Inventory is low: only {{ trigger.event.data.stock }} {{ trigger.event.data.unit }} left in {{ trigger.event.data.storage_location }}!
      data:
        url: "{{ trigger.event.data.reorder_url }}"
```
