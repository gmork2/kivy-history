# kivy-history

[![CI](https://github.com/gmork2/kivy-history/actions/workflows/ci.yml/badge.svg)](https://github.com/gmork2/kivy-history/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/kivy-history.svg)](https://pypi.org/project/kivy-history/)
[![Python versions](https://img.shields.io/pypi/pyversions/kivy-history.svg)](https://pypi.org/project/kivy-history/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)

**kivy-history** is a [Kivy](https://kivy.org) helper inspired by the
[JavaScript History API](https://developer.mozilla.org/en-US/docs/Web/API/History).
It lets you navigate back and forth through a `ScreenManager` and manipulate the
contents of its history stack.

![](image.png)

## Screenshots

<table>
  <tr>
    <td align="center"><img src="shots/cover.png" width="160" alt="Cover"><br><sub>Cover</sub></td>
    <td align="center"><img src="shots/toc.png" width="160" alt="Contents"><br><sub>Contents</sub></td>
    <td align="center"><img src="shots/intro.png" width="160" alt="Introduction"><br><sub>Introduction</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="shots/api.png" width="160" alt="API reference"><br><sub>API reference</sub></td>
    <td align="center"><img src="shots/compare.png" width="160" alt="JavaScript comparison"><br><sub>JavaScript comparison</sub></td>
    <td align="center"><img src="shots/events.png" width="160" alt="Events and scroll"><br><sub>Events and scroll</sub></td>
  </tr>
</table>

## Features

- Navigate with `back()`, `forward()` and `go(delta)`.
- Push and replace states with `push_state()` and `replace_state()`.
- Inspect the current `state`, the `stack`, the `index` and the number of
  entries (`length`).
- Listen to the `on_popstate` event fired after `back()`/`forward()`/`go()`.
- Restore `ScrollView` positions on navigation (`scroll_restoration`).
- Optional logging of the stack (`HISTORY_LOG=1`).
- No visual dependency beyond a Kivy `ScreenManager` (works with any
  transition).

## Installation

### With `uv` (recommended)

```bash
uv add kivy-history
```

### With `pip`

```bash
pip install kivy-history
```

## Quick start

```python
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy_history import History


class MyApp(App):
    def build(self):
        manager = ScreenManager()
        manager.add_widget(Screen(name="home"))
        manager.add_widget(Screen(name="settings"))
        manager.current = "home"

        manager.history = History(manager)
        return manager


MyApp().run()
```

Then use `manager.history.back()`, `manager.history.forward()`,
`manager.history.go(-1)`, `manager.history.push_state("screen_name")` or
`manager.history.replace_state(name="screen_name")`.

See [`src/kivy_history/sample.py`](src/kivy_history/sample.py) for a complete
demo. You can also run it after installing the package:

```bash
kivy-history
```

## Standalone binaries

On every `v*` tag (and on manual dispatch), a GitHub Actions workflow
([`.github/workflows/release-binaries.yml`](.github/workflows/release-binaries.yml))
builds unsigned, self-contained binaries of the sample reader for two
platforms:

| Platform | Artifact |
|---|---|
| Windows | `kivy-history-sample.exe` |
| Linux x86_64 | `kivy-history-sample-x86_64.AppImage` |

They are attached to the GitHub Release of the tag (and are also available as
workflow artifacts on manual runs). Note that they are **not code-signed**, so
Windows SmartScreen will show a warning.

To build them locally:

```bash
python -m pip install . pyinstaller

# Windows .exe
pyinstaller --onefile --windowed --icon assets/icon.ico --name kivy-history-sample app.py

# Linux AppImage
pyinstaller --onefile --windowed --name kivy-history-sample app.py
./tools/package_appimage.sh
```

## Migration from the previous `History()` API

`History` now requires the `ScreenManager` it tracks (a breaking change from
the previous no-argument constructor):

```python
# Before
history = History()
manager.bind(current=history.on_state)

# Now
history = History(manager)
```

What changed:

- The current screen is recorded **synchronously** when `History(manager)` is
  created, so the history stack is never empty.
- The manager's `current` property is bound automatically; the manual
  `manager.bind(current=history.on_state)` is no longer needed (and would
  register each change twice).
- `History` no longer depends on `App.get_running_app()`; it only needs the
  `ScreenManager`.

## API alignment with the JavaScript History API

The API mirrors the
[JavaScript History API](https://developer.mozilla.org/en-US/docs/Web/API/History):

| JavaScript | kivy-history |
|---|---|
| `history.length` | `history.length` |
| `history.state` | `history.state` |
| `history.scrollRestoration` | `history.scroll_restoration` |
| `back()` / `forward()` / `go(delta)` | `back()` / `forward()` / `go(delta)` |
| `pushState(state, title, url)` | `push_state(name, **kwargs)` |
| `replaceState(state, title, url)` | `replace_state(name=None, **kwargs)` |
| `popstate` event (`event.state`) | `on_popstate` event (receives the target `state`) |

Kivy particularities:

- The "URL" is the `ScreenManager` screen name, so `push_state(name, ...)`
  navigates to that screen and drops any forward entries (like a new navigation).
- `replace_state` replaces the current entry **entirely** (no merge) and can
  optionally change the screen name via `name`.

## Development

This project uses [uv](https://docs.astral.sh/uv/) as the package manager while
remaining fully compatible with `pip` (standard PEP 517/621 `pyproject.toml`).

```bash
# Create the environment and install the project in editable mode + dev tools
uv sync --extra dev

# Run the test suite (headless)
uv run pytest

# In a headless environment such as CI, run under a virtual framebuffer:
xvfb-run -a uv run pytest

# Lint and format checks
uv run ruff check .
uv run ruff format --check .

# Build sdist + wheel
uv build
```

> **Nota sobre tests headless:** Kivy necesita una ventana con contexto OpenGL,
> por lo que `SDL_VIDEODRIVER=dummy` (el driver *dummy* de SDL2) **no** sirve
> para ejecutar la suite en GitHub Actions: no expone OpenGL y el proceso
> termina con `exit code 102`. Por eso el CI ejecuta los tests bajo
> [Xvfb](https://en.wikipedia.org/wiki/Xvfb) con renderizado por software de
> Mesa (`libgl1-mesa-dri`, llvmpipe).

With `pip`, install in editable mode with the dev extras:

```bash
pip install -e ".[dev]"
```

## Continuous integration

GitHub Actions runs the lint, test and build steps on every push and pull
request (Python 3.9–3.13) on `ubuntu-24.04` (pinned because newer runner images
no longer ship the prebuilt Python 3.9 toolchain). Python 3.14 and 3.15 run a
Kivy-free smoke test (Kivy has no wheels for them yet). See
[`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Releasing / deploying to PyPI

Publishing to [PyPI](https://pypi.org/project/kivy-history/) is automated with
GitHub Actions using PyPI *trusted publishing* (OpenID Connect) — no tokens are
stored in the repository.

1. Bump the version in
   [`src/kivy_history/version.py`](src/kivy_history/version.py).
2. Commit and push.
3. Create and push an annotated tag:

   ```bash
   git tag -a v2.1.2 -m "Release v2.1.2"
   git push origin v2.1.2
   ```

Pushing a `v*` tag triggers
[`.github/workflows/publish.yml`](.github/workflows/publish.yml), which builds
the package and publishes it to PyPI.

> **One-time setup:** in PyPI, configure the repository
> `gmork2/kivy-history` as a *trusted publisher*
> (Project → Publishing → Add a new trusted publisher) with the workflow name
> `publish.yml`.

## License

[GPL-3.0](LICENSE)

