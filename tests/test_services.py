"""Unit tests for Task Manager Services."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Mock homeassistant module hierarchy using types.ModuleType for package containers
ha_mod = types.ModuleType("homeassistant")
ha_mod.__path__ = []

core_mod = types.ModuleType("homeassistant.core")
def dummy_callback(func):
    return func
core_mod.callback = dummy_callback
core_mod.HomeAssistant = MagicMock
core_mod.ServiceCall = MagicMock

const_mod = types.ModuleType("homeassistant.const")
const_mod.EVENT_HOMEASSISTANT_STARTED = "homeassistant_started"
const_mod.EVENT_STATE_CHANGED = "state_changed"

helpers_mod = types.ModuleType("homeassistant.helpers")
helpers_mod.__path__ = []

components_mod = sys.modules.get("homeassistant.components") or types.ModuleType("homeassistant.components")
components_mod.__path__ = getattr(components_mod, "__path__", [])
panel_custom_mock = sys.modules.get("homeassistant.components.panel_custom") or MagicMock()
ws_api_mock = sys.modules.get("homeassistant.components.websocket_api") or MagicMock()
if not hasattr(ws_api_mock, "websocket_command"):
    ws_api_mock.websocket_command = lambda schema: (lambda f: f)
if not hasattr(ws_api_mock, "async_response"):
    ws_api_mock.async_response = lambda f: f
components_mod.panel_custom = panel_custom_mock
components_mod.websocket_api = ws_api_mock
components_mod.http = getattr(components_mod, "http", MagicMock())
sys.modules["homeassistant.components"] = components_mod
sys.modules["homeassistant.components.panel_custom"] = panel_custom_mock
sys.modules["homeassistant.components.websocket_api"] = ws_api_mock
sys.modules["homeassistant.components.http"] = components_mod.http

sys.modules["homeassistant"] = ha_mod
sys.modules["homeassistant.core"] = core_mod
sys.modules["homeassistant.const"] = const_mod
sys.modules["homeassistant.helpers"] = helpers_mod
sys.modules["homeassistant.components"] = components_mod

ha_mod.core = core_mod
ha_mod.const = const_mod
ha_mod.helpers = helpers_mod
ha_mod.components = components_mod
ha_mod.callback = dummy_callback

helpers_mod.config_validation = MagicMock()
sys.modules["homeassistant.helpers.config_validation"] = helpers_mod.config_validation
helpers_mod.entity_registry = MagicMock()
sys.modules["homeassistant.helpers.entity_registry"] = helpers_mod.entity_registry
helpers_mod.dispatcher = MagicMock()
sys.modules["homeassistant.helpers.dispatcher"] = helpers_mod.dispatcher
helpers_mod.storage = MagicMock()
sys.modules["homeassistant.helpers.storage"] = helpers_mod.storage
helpers_mod.event = MagicMock()
sys.modules["homeassistant.helpers.event"] = helpers_mod.event

sys.modules.setdefault("homeassistant.config_entries", MagicMock())
sys.modules.setdefault("voluptuous", MagicMock())

util_mod = types.ModuleType("homeassistant.util")
def mock_slugify(val):
    import re
    return re.sub(r"[^a-zA-Z0-9_]+", "_", str(val).lower()).strip("_")
util_mod.slugify = mock_slugify
sys.modules["homeassistant.util"] = util_mod
ha_mod.util = util_mod

dt_mock = MagicMock()
dt_mock.now.return_value = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)
sys.modules["homeassistant.util.dt"] = dt_mock
util_mod.dt = dt_mock

registered_services = {}

def mock_register_service(domain, service_name, handler, schema=None):
    registered_services[service_name] = handler

def mock_remove_service(domain, service_name):
    registered_services.pop(service_name, None)

services_mock = MagicMock()
services_mock.async_register = mock_register_service
services_mock.async_remove = mock_remove_service

project_root = Path(__file__).resolve().parent.parent
pkg_path = project_root / "custom_components"
if str(pkg_path) not in sys.path:
    sys.path.insert(0, str(pkg_path))

from task_manager.services import (
    async_register_services,
    async_unregister_services,
    resolve_task_id,
)
from task_manager.const import (
    DOMAIN,
    SERVICE_COMPLETE_TASK,
    SERVICE_MARK_AS_DONE,
    SERVICE_PAUSE_TASK,
    SERVICE_RESUME_TASK,
    SERVICE_SET_LAST_DONE_DATE,
)
from task_manager.storage import TaskManagerStorage, TaskManagerData


class TestTaskManagerServices(unittest.IsolatedAsyncioTestCase):
    """Test suite for Task Manager Services."""

    async def asyncSetUp(self):
        """Set up test environment."""
        self.hass = MagicMock()
        self.hass.services = services_mock

        self.storage = MagicMock(spec=TaskManagerStorage)
        self.storage.data = TaskManagerData()
        self.storage.data.tasks.clear()
        self.storage.async_complete_task = AsyncMock()
        self.storage.async_set_last_done_date = AsyncMock()
        self.storage.async_pause_task = AsyncMock()
        self.storage.async_resume_task = AsyncMock()
        self.storage.async_save_task = AsyncMock()
        self.storage.async_save = AsyncMock()

        registered_services.clear()
        async_register_services(self.hass, self.storage)

    def tearDown(self):
        """Clean up services."""
        async_unregister_services(self.hass)

    async def test_resolve_task_id(self):
        """Test resolving task ID by task_id, entity_id slug, or task_title."""
        t1 = self.storage.data.create_task({"title": "Clean Garage"})

        # By direct ID
        self.assertEqual(resolve_task_id({"task_id": t1["id"]}, self.storage, self.hass), t1["id"])

        # By task title (case-insensitive)
        self.assertEqual(resolve_task_id({"task_title": "clean garage"}, self.storage, self.hass), t1["id"])

        # By entity_id slug
        self.assertEqual(resolve_task_id({"entity_id": "sensor.task_manager_clean_garage"}, self.storage, self.hass), t1["id"])

    async def test_service_mark_as_done(self):
        """Test calling mark_as_done service."""
        t1 = self.storage.data.create_task({"title": "Sweep Porch"})
        call = MagicMock()
        call.data = {"task_title": "Sweep Porch", "user_id": "u1"}

        handler = registered_services.get(SERVICE_MARK_AS_DONE)
        self.assertIsNotNone(handler)
        await handler(call)
        self.storage.async_complete_task.assert_awaited_once_with(t1["id"], user_id="u1")

    async def test_service_set_last_done_date(self):
        """Test calling set_last_done_date service."""
        t1 = self.storage.data.create_task({"title": "Mow Lawn"})
        call = MagicMock()
        call.data = {"task_id": t1["id"], "date": "2026-09-25"}

        handler = registered_services.get(SERVICE_SET_LAST_DONE_DATE)
        self.assertIsNotNone(handler)
        await handler(call)
        self.storage.async_set_last_done_date.assert_awaited_once_with(t1["id"], "2026-09-25")

    async def test_service_pause_and_resume_task(self):
        """Test calling pause_task and resume_task services."""
        t1 = self.storage.data.create_task({"title": "Water Plants"})
        call = MagicMock()
        call.data = {"task_id": t1["id"]}

        pause_handler = registered_services.get(SERVICE_PAUSE_TASK)
        self.assertIsNotNone(pause_handler)
        await pause_handler(call)
        self.storage.async_pause_task.assert_awaited_once_with(t1["id"])

        resume_handler = registered_services.get(SERVICE_RESUME_TASK)
        self.assertIsNotNone(resume_handler)
        await resume_handler(call)
        self.storage.async_resume_task.assert_awaited_once_with(t1["id"])
