import unittest
from unittest.mock import MagicMock
from aifr.cli import CliArgs

from aifr.cli import resolve_agent_config

class TestAgentRouting(unittest.TestCase):
    def setUp(self):
        self.defaults = {
            "default_provider": "default_prov",
            "default_model": "default_mod",
            "default_system_prompt": "default_sys"
        }
        self.custom_agents = {
            "full_agent": {
                "provider": "custom_prov",
                "model": "custom_mod",
                "system_prompt": "custom_sys"
            },
            "partial_agent": {
                "provider": "partial_prov"
            }
        }

    def test_no_agent(self):
        """Should return defaults if no agent specified."""
        p, m, s = resolve_agent_config(None, self.custom_agents, **self.defaults)
        self.assertEqual(p, "default_prov")
        self.assertEqual(m, "default_mod")
        self.assertEqual(s, "default_sys")

    def test_unknown_agent(self):
        """Should warn and return defaults if agent unknown."""
        # We could mock stderr to verify warning, but return values check is enough for logic
        p, m, s = resolve_agent_config("unknown", self.custom_agents, **self.defaults)
        self.assertEqual(p, "default_prov")

    def test_full_agent(self):
        """Should override all values."""
        p, m, s = resolve_agent_config("full_agent", self.custom_agents, **self.defaults)
        self.assertEqual(p, "custom_prov")
        self.assertEqual(m, "custom_mod")
        self.assertEqual(s, "custom_sys")

    def test_partial_agent(self):
        """Should override only specified values."""
        p, m, s = resolve_agent_config("partial_agent", self.custom_agents, **self.defaults)
        self.assertEqual(p, "partial_prov")     # Overridden
        self.assertEqual(m, "default_mod")      # Default preserved
        self.assertEqual(s, "default_sys")      # Default preserved

if __name__ == "__main__":
    unittest.main()
