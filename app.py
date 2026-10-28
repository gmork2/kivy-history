#!/usr/bin/env python
"""Standalone entry point for the kivy-history sample reader.

Used by the packaging workflows (PyInstaller / python-for-android) to launch
the demo application. For development you can also run it directly with::

    python app.py
"""

from kivy_history.sample import main

if __name__ == "__main__":
    main()
