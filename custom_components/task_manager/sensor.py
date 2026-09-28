"""Sensor platform for Task Manager integration."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util, slugify

from .const import (
    DOMAIN,
    SIGNAL_TASK_MANAGER_UPDATED,
    TASK_STATE_DONE,
    TASK_STATE_DUE,
    TASK_STATE_DUE_SOON,
    TASK_STATE_INACTIVE,
)
from .storage import (
    TaskManagerStorage,
    get_warranty_status,
    is_part_low_stock,
    is_thing_threshold_reached,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Task Manager sensors."""
    storage: TaskManagerStorage = hass.data[DOMAIN][entry.entry_id]

    # Clean up orphaned sensors from entity registry on startup
    try:
        ent_reg = er.async_get(hass)
        current_uids = {f"{DOMAIN}_user_{u['id']}_points" for u in storage.data.users}
        current_tids = {f"{DOMAIN}_thing_{th['id']}" for th in storage.data.things}
        current_task_uids = {f"{DOMAIN}_task_{t['id']}_status" for t in storage.data.tasks}
        current_part_uids = {f"{DOMAIN}_part_{p['id']}_stock" for p in storage.data.parts}
        valid_uids = {
            f"{DOMAIN}_total_tasks",
            f"{DOMAIN}_pending_tasks",
            f"{DOMAIN}_overdue_tasks",
            f"{DOMAIN}_completed_today_tasks",
            f"{DOMAIN}_parts_low_stock",
        } | current_uids | current_tids | current_task_uids | current_part_uids

        for reg_entry in er.async_entries_for_config_entry(ent_reg, entry.entry_id):
            if reg_entry.domain == "sensor" and reg_entry.unique_id not in valid_uids:
                _LOGGER.info("Removing orphaned sensor entity from registry: %s", reg_entry.entity_id)
                ent_reg.async_remove(reg_entry.entity_id)
    except Exception as err:
        _LOGGER.debug("Could not cleanup orphaned sensor entities: %s", err)

    # Initial static summary sensors
    summary_sensors = [
        TaskManagerSummarySensor(storage, "total", "Task Manager Total Tasks", "mdi:clipboard-text-outline"),
        TaskManagerSummarySensor(storage, "pending", "Task Manager Pending Tasks", "mdi:clipboard-clock-outline"),
        TaskManagerSummarySensor(storage, "overdue", "Task Manager Overdue Tasks", "mdi:alert-circle-outline"),
        TaskManagerSummarySensor(storage, "completed_today", "Task Manager Completed Today", "mdi:check-circle-outline"),
        TaskManagerPartsLowSensor(storage),
    ]
    async_add_entities(summary_sensors)

    active_user_sensors: dict[str, TaskManagerUserSensor] = {}
    active_thing_sensors: dict[str, TaskManagerThingSensor] = {}
    active_task_sensors: dict[str, TaskManagerTaskSensor] = {}
    active_part_sensors: dict[str, TaskManagerPartStockSensor] = {}

    @callback
    def update_dynamic_sensors() -> None:
        """Add new sensors or remove deleted sensors for users, things, tasks, and parts."""
        new_entities = []
        current_user_ids = {u["id"] for u in storage.data.users}
        current_thing_ids = {th["id"] for th in storage.data.things}
        current_task_ids = {t["id"] for t in storage.data.tasks}
        current_part_ids = {p["id"] for p in storage.data.parts}

        # 1. Add new users
        for user in storage.data.users:
            uid = user["id"]
            if uid not in active_user_sensors:
                sensor = TaskManagerUserSensor(storage, uid)
                active_user_sensors[uid] = sensor
                new_entities.append(sensor)

        # 2. Remove deleted users
        for uid in list(active_user_sensors.keys()):
            if uid not in current_user_ids:
                sensor = active_user_sensors.pop(uid)
                hass.async_create_task(sensor.async_remove())
                try:
                    ent_reg = er.async_get(hass)
                    reg_id = ent_reg.async_get_entity_id("sensor", DOMAIN, f"{DOMAIN}_user_{uid}_points")
                    if reg_id:
                        ent_reg.async_remove(reg_id)
                except Exception as err:
                    _LOGGER.debug("Error removing user sensor from registry: %s", err)

        # 3. Add new things
        for thing in storage.data.things:
            th_id = thing["id"]
            if th_id not in active_thing_sensors:
                sensor = TaskManagerThingSensor(storage, th_id)
                active_thing_sensors[th_id] = sensor
                new_entities.append(sensor)

        # 4. Remove deleted things
        for th_id in list(active_thing_sensors.keys()):
            if th_id not in current_thing_ids:
                sensor = active_thing_sensors.pop(th_id)
                hass.async_create_task(sensor.async_remove())
                try:
                    ent_reg = er.async_get(hass)
                    reg_id = ent_reg.async_get_entity_id("sensor", DOMAIN, f"{DOMAIN}_thing_{th_id}")
                    if reg_id:
                        ent_reg.async_remove(reg_id)
                except Exception as err:
                    _LOGGER.debug("Error removing thing sensor from registry: %s", err)

        # 5. Add new task sensors
        for task in storage.data.tasks:
            t_id = task["id"]
            if t_id not in active_task_sensors:
                sensor = TaskManagerTaskSensor(storage, t_id)
                active_task_sensors[t_id] = sensor
                new_entities.append(sensor)

        # 6. Remove deleted task sensors
        for t_id in list(active_task_sensors.keys()):
            if t_id not in current_task_ids:
                sensor = active_task_sensors.pop(t_id)
                hass.async_create_task(sensor.async_remove())
                try:
                    ent_reg = er.async_get(hass)
                    reg_id = ent_reg.async_get_entity_id("sensor", DOMAIN, f"{DOMAIN}_task_{t_id}_status")
                    if reg_id:
                        ent_reg.async_remove(reg_id)
                except Exception as err:
                    _LOGGER.debug("Error removing task sensor from registry: %s", err)

        # 7. Add new part sensors
        for part in storage.data.parts:
            p_id = part["id"]
            if p_id not in active_part_sensors:
                sensor = TaskManagerPartStockSensor(storage, p_id)
                active_part_sensors[p_id] = sensor
                new_entities.append(sensor)

        # 8. Remove deleted part sensors
        for p_id in list(active_part_sensors.keys()):
            if p_id not in current_part_ids:
                sensor = active_part_sensors.pop(p_id)
                hass.async_create_task(sensor.async_remove())
                try:
                    ent_reg = er.async_get(hass)
                    reg_id = ent_reg.async_get_entity_id("sensor", DOMAIN, f"{DOMAIN}_part_{p_id}_stock")
                    if reg_id:
                        ent_reg.async_remove(reg_id)
                except Exception as err:
                    _LOGGER.debug("Error removing part sensor from registry: %s", err)

        if new_entities:
            async_add_entities(new_entities)

    update_dynamic_sensors()
    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_TASK_MANAGER_UPDATED, update_dynamic_sensors)
    )


class TaskManagerSummarySensor(SensorEntity):
    """Summary sensor for task counts."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, storage: TaskManagerStorage, count_type: str, name: str, icon: str) -> None:
        """Initialize summary sensor."""
        self._storage = storage
        self._count_type = count_type
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{count_type}_tasks"
        self._attr_icon = icon

    async def async_added_to_hass(self) -> None:
        """Register listener."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_TASK_MANAGER_UPDATED, self._handle_update
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle state update."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        """Return the count."""
        tasks = self._storage.data.tasks
        today_str = dt_util.now().date().strftime("%Y-%m-%d")

        if self._count_type == "total":
            return len(tasks)

        if self._count_type == "pending":
            return sum(1 for t in tasks if t.get("status") == "pending")

        if self._count_type == "overdue":
            count = 0
            for t in tasks:
                if t.get("status") == "pending":
                    due = t.get("due_date", "")
                    if due and due < today_str:
                        count += 1
            return count

        if self._count_type == "completed_today":
            count = 0
            for t in tasks:
                if t.get("status") == "completed":
                    comp = t.get("completed_at", "")
                    if comp and comp[:10] == today_str:
                        count += 1
                for h in t.get("history", []):
                    comp = h.get("completed_at", "")
                    if comp and comp[:10] == today_str:
                        count += 1
            return count

        return 0


class TaskManagerUserSensor(SensorEntity):
    """Sensor for individual user points and stats."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, storage: TaskManagerStorage, user_id: str) -> None:
        """Initialize user sensor."""
        self._storage = storage
        self._user_id = user_id
        user = storage.data.get_user(user_id)
        user_name = user["name"] if user else user_id
        self._attr_name = f"Task Manager {user_name} Points"
        self._attr_unique_id = f"{DOMAIN}_user_{user_id}_points"
        self._attr_icon = "mdi:star-circle-outline"
        self._attr_native_unit_of_measurement = "pts"

    async def async_added_to_hass(self) -> None:
        """Register listener."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_TASK_MANAGER_UPDATED, self._handle_update
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle state update."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        """Return user points."""
        user = self._storage.data.get_user(self._user_id)
        return user.get("points", 0) if user else 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return user stats attributes."""
        user = self._storage.data.get_user(self._user_id)
        if not user:
            return {}

        today_str = dt_util.now().date().strftime("%Y-%m-%d")
        due_count = sum(
            1 for t in self._storage.data.tasks
            if t.get("status") == "pending"
            and (t.get("current_assignee") == self._user_id or self._user_id in t.get("assignees", []))
            and t.get("due_date", "") <= today_str
        )

        return {
            "user_id": self._user_id,
            "user_name": user.get("name"),
            "streak": user.get("streak", 0),
            "completed_count": user.get("completed_count", 0),
            "tasks_due": due_count,
            "last_completed_date": user.get("last_completed_date", ""),
        }


class TaskManagerThingSensor(SensorEntity):
    """Sensor for household things/meters."""

    _attr_has_entity_name = True

    def __init__(self, storage: TaskManagerStorage, thing_id: str) -> None:
        """Initialize thing sensor."""
        self._storage = storage
        self._thing_id = thing_id
        thing = storage.data.get_thing(thing_id)
        thing_name = thing["name"] if thing else thing_id
        self._attr_name = f"Task Manager Thing {thing_name}"
        self._attr_unique_id = f"{DOMAIN}_thing_{thing_id}"
        self._attr_icon = thing.get("icon", "mdi:chart-arc") if thing else "mdi:chart-arc"

    async def async_added_to_hass(self) -> None:
        """Register listener."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_TASK_MANAGER_UPDATED, self._handle_update
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle state update."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> float | int:
        """Return current value."""
        thing = self._storage.data.get_thing(self._thing_id)
        return thing.get("current_value", 0) if thing else 0

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of measurement."""
        thing = self._storage.data.get_thing(self._thing_id)
        return thing.get("unit") if thing else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return thing metadata."""
        thing = self._storage.data.get_thing(self._thing_id)
        if not thing:
            return {}

        target = float(thing.get("target_value", 100))
        cur = float(thing.get("current_value", 0))
        pct = round((cur / target) * 100, 1) if target > 0 else 0.0

        return {
            "thing_id": self._thing_id,
            "category": thing.get("category", ""),
            "area_id": thing.get("area_id"),
            "manufacturer": thing.get("manufacturer", ""),
            "model": thing.get("model", ""),
            "serial_number": thing.get("serial_number", ""),
            "installation_date": thing.get("installation_date", ""),
            "warranty_expiry": thing.get("warranty_expiry", ""),
            "warranty_status": get_warranty_status(thing),
            "documentation_url": thing.get("documentation_url", ""),
            "notes": thing.get("notes", ""),
            "target_value": target,
            "threshold_operator": thing.get("threshold_operator", ">="),
            "external_entity_id": thing.get("external_entity_id"),
            "script_entity_id": thing.get("script_entity_id"),
            "threshold_reached": is_thing_threshold_reached(thing),
            "progress_percent": pct,
            "auto_task_creation": thing.get("auto_task_creation", False),
            "last_reset": thing.get("last_reset", ""),
        }


class TaskManagerTaskSensor(SensorEntity):
    """Sensor representing an individual task and its status/metrics."""

    _attr_has_entity_name = True

    def __init__(self, storage: TaskManagerStorage, task_id: str) -> None:
        """Initialize task sensor."""
        self._storage = storage
        self._task_id = task_id
        task = storage.data.get_task(task_id) or {}
        title = task.get("title", "Task")
        self._attr_name = f"Task {title}"
        self._attr_unique_id = f"{DOMAIN}_task_{task_id}_status"
        safe_title = slugify(title) or task_id[:8]
        self.entity_id = f"sensor.task_manager_{safe_title}"

    async def async_added_to_hass(self) -> None:
        """Register update listener."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_TASK_MANAGER_UPDATED, self._handle_update
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle state update."""
        self.async_write_ha_state()

    @property
    def icon(self) -> str:
        """Return icon depending on status."""
        state = self.native_value
        if state == TASK_STATE_INACTIVE:
            return "mdi:pause-circle-outline"
        if state == TASK_STATE_DONE:
            return "mdi:checkbox-marked-circle"
        if state == TASK_STATE_DUE_SOON:
            return "mdi:clock-alert-outline"
        return "mdi:alert-circle-outline"

    @property
    def native_value(self) -> str:
        """Return task state: due, due_soon, done, or inactive."""
        state, _ = self._storage.data.get_task_effective_state(self._task_id, self.hass)
        return state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return task attributes."""
        _, attrs = self._storage.data.get_task_effective_state(self._task_id, self.hass)
        return attrs


class TaskManagerPartsLowSensor(SensorEntity):
    """Sensor tracking the count of parts requiring reorder."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:package-variant-closed-alert"

    def __init__(self, storage: TaskManagerStorage) -> None:
        """Initialize parts low sensor."""
        self._storage = storage
        self._attr_name = "Task Manager Parts Low Stock"
        self._attr_unique_id = f"{DOMAIN}_parts_low_stock"
        self._attr_native_unit_of_measurement = "parts"

    async def async_added_to_hass(self) -> None:
        """Register listener."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_TASK_MANAGER_UPDATED, self._handle_update
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle state update."""
        self.async_write_ha_state()

    def _get_low_parts(self) -> list[dict[str, Any]]:
        """Return parts at or below min_stock threshold."""
        return [p for p in self._storage.data.parts if is_part_low_stock(p)]

    @property
    def native_value(self) -> int:
        """Return count of low stock parts."""
        return len(self._get_low_parts())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return details of low stock parts."""
        low = self._get_low_parts()
        return {
            "low_stock_parts": [
                {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "stock": p.get("stock"),
                    "min_stock": p.get("min_stock"),
                    "storage_location": p.get("storage_location"),
                    "reorder_url": p.get("reorder_url"),
                }
                for p in low
            ],
            "total_parts": len(self._storage.data.parts),
        }


class TaskManagerPartStockSensor(SensorEntity):
    """Sensor tracking the stock of an individual part/consumable."""

    _attr_has_entity_name = True

    def __init__(self, storage: TaskManagerStorage, part_id: str) -> None:
        """Initialize part stock sensor."""
        self._storage = storage
        self._part_id = part_id
        part = storage.data.get_part(part_id) or {}
        name = part.get("name", "Part")
        self._attr_name = f"Part {name} Stock"
        self._attr_unique_id = f"{DOMAIN}_part_{part_id}_stock"
        self._attr_icon = "mdi:archive-cog"
        safe_name = slugify(name) or part_id[:8]
        self.entity_id = f"sensor.task_manager_part_{safe_name}_stock"

    async def async_added_to_hass(self) -> None:
        """Register listener."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_TASK_MANAGER_UPDATED, self._handle_update
            )
        )

    @callback
    def _handle_update(self) -> None:
        """Handle state update."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> float | int:
        """Return current stock."""
        part = self._storage.data.get_part(self._part_id)
        return part.get("stock", 0) if part else 0

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return stock unit."""
        part = self._storage.data.get_part(self._part_id)
        return part.get("unit", "pcs") if part else "pcs"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return part attributes."""
        part = self._storage.data.get_part(self._part_id)
        if not part:
            return {}
        return {
            "part_id": self._part_id,
            "name": part.get("name", ""),
            "thing_id": part.get("thing_id"),
            "part_number": part.get("part_number", ""),
            "min_stock": part.get("min_stock", 0),
            "unit_price": part.get("unit_price", 0.0),
            "storage_location": part.get("storage_location", ""),
            "reorder_url": part.get("reorder_url", ""),
            "notes": part.get("notes", ""),
            "is_low_stock": is_part_low_stock(part),
        }


