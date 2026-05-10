"""Tests for attacker command dispatch."""

import unittest
from unittest.mock import MagicMock

from brutus.attacker.terminal.command.command import dispatch


class FakeWindow:
    def __init__(self):
        self.output = []
        self.Output = MagicMock()
        self.Output.addItem.side_effect = self.output.append
        self.Output.clear = MagicMock()
        self.Input = MagicMock()

    def hide(self):
        pass


class TestDispatch(unittest.TestCase):
    def setUp(self):
        self.window = FakeWindow()
        self.ctx = {"connections": {}, "ip": "1.2.3.4", "version": "TEST", "locator": None}

    def test_echo_command(self):
        dispatch("echo hello world", self.window, self.ctx)
        self.assertIn("hello world", self.window.output)

    def test_echo_empty(self):
        dispatch("echo ", self.window, self.ctx)
        self.assertIn("", self.window.output)

    def test_ip_command(self):
        dispatch("ip", self.window, self.ctx)
        self.assertTrue(any("1.2.3.4" in str(o) for o in self.window.output))

    def test_show_header_clears_and_prints(self):
        dispatch("clear", self.window, self.ctx)
        self.window.Output.clear.assert_called()

    def test_show_clients_no_connections(self):
        dispatch("show_clients", self.window, self.ctx)
        self.assertTrue(any("No connected" in str(o) for o in self.window.output))

    def test_show_clients_alias_sc(self):
        dispatch("sc", self.window, self.ctx)
        self.assertTrue(any("No connected" in str(o) for o in self.window.output))

    def test_unknown_returns_false(self):
        handled = dispatch("xyzzy_unknown", self.window, self.ctx)
        self.assertFalse(handled)

    def test_known_returns_true(self):
        handled = dispatch("ip", self.window, self.ctx)
        self.assertTrue(handled)

    def test_at_notation_missing_client(self):
        dispatch("99@ls", self.window, self.ctx)
        self.assertTrue(any("ERROR" in str(o).upper() for o in self.window.output))
