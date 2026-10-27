"""Scroll restoration behavior, mirroring ``history.scrollRestoration``."""

from enum import Enum, unique


@unique
class ScrollRestoration(str, Enum):
    """How scroll positions are restored on back/forward navigation.

    ``auto`` restores the scroll position automatically; ``manual`` leaves it to
    the developer (e.g. via
    :meth:`~kivy_history.history.History.restore_scroll`).
    """

    auto = "auto"
    manual = "manual"
