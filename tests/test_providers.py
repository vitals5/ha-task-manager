"""Unit tests for Task Manager provider adapters."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock

# Mock homeassistant module hierarchy
def mock_slugify(val):
    import re
    return re.sub(r"[^a-zA-Z0-9_]+", "_", str(val).lower()).strip("_")

ha_mock = MagicMock()
ha_mock.callback = lambda func: func
core_mock = MagicMock()
core_mock.callback = lambda func: func

dt_mock = MagicMock()
dt_mock.DEFAULT_TIME_ZONE = timezone.utc
dt_mock.now.return_value = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)

util_mock = sys.modules.get("homeassistant.util") or MagicMock()
util_mock.dt = dt_mock
util_mock.slugify = mock_slugify

sys.modules["homeassistant"] = ha_mock
sys.modules["homeassistant.core"] = core_mock
sys.modules["homeassistant.helpers"] = ha_mock
sys.modules["homeassistant.helpers.entity_registry"] = MagicMock()
sys.modules["homeassistant.util"] = util_mock
sys.modules["homeassistant.util.dt"] = dt_mock

project_root = Path(__file__).parent.parent

providers_spec = importlib.util.spec_from_file_location(
    "custom_components.task_manager.providers",
    project_root / "custom_components" / "task_manager" / "providers.py",
)
providers_mod = importlib.util.module_from_spec(providers_spec)
providers_spec.loader.exec_module(providers_mod)

detect_provider_type = providers_mod.detect_provider_type
async_get_available_todo_entities = providers_mod.async_get_available_todo_entities


class TestTaskManagerProviders(unittest.TestCase):
    """Test suite for provider detection and adapters."""

    def test_detect_provider_type_known_domains(self):
        """Test detecting known provider domains from entity registry."""
        hass = MagicMock()
        entity_entry = MagicMock()
        entity_entry.name = "My Google Chores"
        entity_entry.config_entry_id = "cfg_123"

        config_entry = MagicMock()
        config_entry.domain = "google_tasks"

        hass.config_entries.async_get_entry.return_value = config_entry

        er_mock = MagicMock()
        er_mock.async_get.return_value = entity_entry
        providers_mod.er.async_get.return_value = er_mock

        result = detect_provider_type(hass, "todo.my_google_chores")
        self.assertEqual(result["provider_type"], "google_tasks")
        self.assertEqual(result["name"], "My Google Chores")
        self.assertEqual(result["provider_name"], "Google Tasks")
        self.assertEqual(result["icon"], "mdi:google")

    def test_detect_provider_type_fallback(self):
        """Test fallback when entity is not in entity registry."""
        hass = MagicMock()
        er_mock = MagicMock()
        er_mock.async_get.return_value = None
        providers_mod.er.async_get.return_value = er_mock
        hass.states.get.return_value = None

        result = detect_provider_type(hass, "todo.custom_list")
        self.assertEqual(result["provider_type"], "generic")
        self.assertEqual(result["name"], "todo.custom_list")
        self.assertEqual(result["provider_name"], "External To-do")

    def test_get_available_todo_entities_excludes_internal(self):
        """Test available todo entities listing filters out task_manager entities."""
        hass = MagicMock()

        state1 = MagicMock(entity_id="todo.task_manager_shared")
        state2 = MagicMock(entity_id="todo.task_manager_user_1")
        state3 = MagicMock(entity_id="todo.household_shopping")
        state3.attributes = {"friendly_name": "Household Shopping"}

        hass.states.async_all.return_value = [state1, state2, state3]

        er_mock = MagicMock()
        er_mock.entities = {}
        providers_mod.er.async_get.return_value = er_mock

        available = async_get_available_todo_entities(hass)
        entity_ids = [e["entity_id"] for e in available]

        self.assertNotIn("todo.task_manager_shared", entity_ids)
        self.assertNotIn("todo.task_manager_user_1", entity_ids)
        self.assertIn("todo.household_shopping", entity_ids)


if __name__ == "__main__":
    unittest.main()
