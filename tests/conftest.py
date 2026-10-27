"""Shared pytest fixtures for the kivy_history test suite.

Kivy needs a window to create widgets. Run the suite under a display server:
a desktop session locally, or ``xvfb-run -a`` in headless/CI environments.
"""

import os

os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("KIVY_LOG_MODE", "PYTHON")

import pytest
from kivy.clock import Clock
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager

from kivy_history import History


@pytest.fixture
def screen_manager():
    """A ScreenManager with a few named screens and no visual transition."""
    manager = ScreenManager()
    manager.transition = NoTransition()
    for name in ("s1", "s2", "s3", "s4"):
        manager.add_widget(Screen(name=name))
    manager.current = "s1"
    return manager


@pytest.fixture
def history(screen_manager):
    """A History instance tracking the ScreenManager."""
    return History(screen_manager)


@pytest.fixture(autouse=True)
def _flush_clock():
    """Flush pending Clock events (e.g. NoTransition animations) after a test."""
    yield
    Clock.tick()
