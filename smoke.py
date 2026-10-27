"""Smoke test for the Kivy-independent parts of ``kivy_history``.

This script intentionally does not import Kivy, so it can run on Python versions
for which Kivy does not publish wheels yet (currently 3.14 and 3.15). It only
exercises ``kivy_history.version`` and ``kivy_history.state``.
"""

import sys

import kivy_history
from kivy_history import state, version


def main() -> int:
    # Importing the package must not require Kivy.
    assert isinstance(kivy_history.__version__, str)
    assert kivy_history.__version__ == version.__version__

    # ``State`` is pure Python and must work without Kivy.
    entry = state.State("home", id=42)
    assert entry.state == {"name": "home", "id": 42}
    entry.update(id=43, title="hello")
    assert entry.state == {"name": "home", "id": 43, "title": "hello"}
    assert repr(entry) == "home"

    print(f"smoke OK: kivy_history {kivy_history.__version__} on Python {sys.version.split()[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
