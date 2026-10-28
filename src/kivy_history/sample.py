#!/usr/bin/env python
"""
Interactive guide to the kivy-history API.

This example is an "ebook reader" that documents the kivy-history API and
compares it with the JavaScript History API. The reader itself uses
``History`` for navigation, so the ‹ › buttons in the header exercise exactly
the methods documented on these pages.

Run with::

    kivy-history
"""

import os

from kivy.app import App
from kivy.core.text import LabelBase
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.properties import NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from kivy_history import History

# ---------------------------------------------------------------------------
# "Sepia" palette inspired by ebook readers.
# ---------------------------------------------------------------------------
PAPER = "#F6F0E1"  # general background (sepia paper)
CARD = "#FCF8EE"  # cards and cells
RULE = "#E3D8C0"  # hairlines and borders
INK = "#3A3228"  # main text
MUTED = "#8A7E6B"  # secondary text
ACCENT = "#9C6B3F"  # titles, links and accents
ACCENT_DARK = "#6E4A2A"  # dark accent (table headers, buttons)
CHROME = "#2C2822"  # top bar and code blocks
CHROME_TEXT = "#F3EADA"  # text on the dark chrome

CHAPTERS = {
    "cover": "Cover",
    "toc": "Contents",
    "intro": "Introduction",
    "install": "Installation",
    "usage": "Basic usage",
    "api": "API reference",
    "compare": "JavaScript comparison",
    "events": "Events & scroll",
    "credits": "Credits",
}

TOC = [
    ("intro", "Introduction", "What kivy-history is and why it resembles the History API."),
    ("install", "Installation", "uv, pip and a three-line quick start."),
    ("usage", "Basic usage", "Create the history, navigate, push_state and replace_state."),
    ("api", "API reference", "Properties, methods and events, one by one."),
    ("compare", "JavaScript comparison", "The differences with the browser's History API."),
    ("events", "Events & scroll", "on_popstate, scroll_restoration and console logging."),
    ("credits", "Credits", "Credits and license."),
]


class Progress(Widget):
    """Thin progress bar used in the footer."""

    value = NumericProperty(0)


class Reader(BoxLayout):
    """Root container of the reader (header + ScreenManager + footer)."""


def _first(*paths):
    for path in paths:
        if path and os.path.isfile(path):
            return path
    return None


def _register_fonts():
    """Register serif and mono fonts (with a fallback to Kivy's fonts)."""
    from kivy import kivy_data_dir

    roboto = os.path.join(kivy_data_dir, "fonts", "Roboto-Regular.ttf")
    roboto_bold = os.path.join(kivy_data_dir, "fonts", "Roboto-Bold.ttf")
    roboto_italic = os.path.join(kivy_data_dir, "fonts", "Roboto-Italic.ttf")
    roboto_mono = os.path.join(kivy_data_dir, "fonts", "RobotoMono-Regular.ttf")
    dejavu_sans = os.path.join(kivy_data_dir, "fonts", "DejaVuSans.ttf")

    serif = _first(
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "C:/Windows/Fonts/times.ttf",
        roboto,
    )
    serif_bold = _first(
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "C:/Windows/Fonts/timesbd.ttf",
        roboto_bold,
    )
    serif_italic = _first(
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        "C:/Windows/Fonts/timesi.ttf",
        roboto_italic,
    )
    mono = _first(
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "C:/Windows/Fonts/cour.ttf",
        roboto_mono,
    )
    icons = _first(
        dejavu_sans,
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        roboto,
    )

    if serif:
        LabelBase.register("Serif", serif, serif_italic, serif_bold, None)
    if mono:
        LabelBase.register("Mono", mono)
    if icons:
        LabelBase.register("Icons", icons)


def _rgba(hex_color, alpha=1.0):
    hex_color = hex_color.lstrip("#")
    return (
        int(hex_color[0:2], 16) / 255.0,
        int(hex_color[2:4], 16) / 255.0,
        int(hex_color[4:6], 16) / 255.0,
        alpha,
    )


def _with_bg(widget, color, radius=10):
    """Draw a rounded background behind ``widget`` that follows its size."""
    if isinstance(color, str):
        color = _rgba(color)
    with widget.canvas.before:
        Color(rgba=color)
        rect = RoundedRectangle(
            pos=widget.pos,
            size=widget.size,
            radius=[dp(radius), dp(radius), dp(radius), dp(radius)],
        )

    def _update(inst, *_):
        rect.pos = inst.pos
        rect.size = inst.size

    widget.bind(pos=_update, size=_update)
    return widget


def _auto_height(label):
    """Make a Label adjust its height to its text (with line wrapping)."""
    label.size_hint_y = None
    label.bind(width=lambda w, _: setattr(w, "text_size", (w.width, None)))
    label.bind(texture_size=lambda w, ts: setattr(w, "height", ts[1] if ts else 0))
    return label


def _label(
    text,
    *,
    size=16,
    color=INK,
    font="Serif",
    bold=False,
    italic=False,
    justify=True,
    line_height=1.5,
):
    if isinstance(color, str):
        color = _rgba(color)
    lbl = Label(
        text=text,
        markup=True,
        font_name=font,
        font_size=sp(size),
        color=color,
        bold=bold,
        italic=italic,
        halign="justify" if justify else "left",
        valign="top",
        line_height=line_height,
    )
    return _auto_height(lbl)


def _note(text):
    box = BoxLayout(size_hint_y=None, padding=(dp(14), dp(12)), size_hint_x=1)
    box.bind(minimum_height=box.setter("height"))
    _with_bg(box, "#EFE6D0", radius=8)
    box.add_widget(_label(text, size=14, color=INK, justify=False))
    return box


def _code(text, caption=None):
    box = BoxLayout(
        orientation="vertical",
        size_hint_y=None,
        padding=(dp(14), dp(12)),
        spacing=dp(8),
        size_hint_x=1,
    )
    box.bind(minimum_height=box.setter("height"))
    _with_bg(box, CHROME, radius=10)
    if caption:
        cap = Label(
            text=caption,
            markup=True,
            font_name="Serif",
            font_size=sp(12),
            color=_rgba("#C9BFA8"),
            halign="left",
            valign="middle",
        )
        box.add_widget(_auto_height(cap))
    code = Label(
        text=text,
        markup=False,
        font_name="Mono",
        font_size=sp(13),
        color=_rgba(CHROME_TEXT),
        halign="left",
        valign="top",
    )
    box.add_widget(_auto_height(code))
    return box


def _list(items):
    box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6), size_hint_x=1)
    box.bind(minimum_height=box.setter("height"))
    for item in items:
        row = BoxLayout(size_hint_y=None, spacing=dp(10), size_hint_x=1)
        row.bind(minimum_height=row.setter("height"))
        bullet = _label("•", size=16, color=ACCENT, justify=False)
        bullet.size_hint_x = None
        bullet.width = dp(16)
        bullet.text_size = (dp(16), None)
        row.add_widget(bullet)
        row.add_widget(_label(item))
        box.add_widget(row)
    return box


def _cell(text, header=False, mono=True):
    box = BoxLayout(size_hint_y=None, padding=(dp(10), dp(8)), size_hint_x=1)
    box.bind(minimum_height=box.setter("height"))
    _with_bg(box, ACCENT_DARK if header else CARD, radius=6)
    lbl = Label(
        text=text,
        markup=True,
        font_name="Mono" if mono else "Serif",
        font_size=sp(13),
        color=_rgba(CHROME_TEXT if header else INK),
        bold=header,
        halign="left",
        valign="middle",
    )
    box.add_widget(_auto_height(lbl))
    return box


def _table(headers, rows):
    grid = GridLayout(cols=len(headers), spacing=dp(2), size_hint_y=None, size_hint_x=1)
    grid.bind(minimum_height=grid.setter("height"))
    for head in headers:
        grid.add_widget(_cell(head, header=True))
    for row in rows:
        for cell_text in row:
            grid.add_widget(_cell(cell_text))
    return grid


def _chip(text, color=ACCENT, bg=CARD):
    lbl = Label(
        text=text,
        markup=True,
        font_name="Serif",
        bold=True,
        font_size=sp(11),
        color=_rgba(color),
        halign="center",
        valign="middle",
        size_hint=(None, None),
        size=(0, dp(24)),
    )
    _with_bg(lbl, bg, radius=12)

    def _fit(w, ts):
        w.size = (ts[0] + dp(16), dp(24))

    lbl.bind(texture_size=_fit)
    return lbl


def _api_entry(tag, sig, desc):
    card = BoxLayout(
        orientation="vertical",
        size_hint_y=None,
        spacing=dp(8),
        padding=(dp(14), dp(12)),
        size_hint_x=1,
    )
    card.bind(minimum_height=card.setter("height"))
    _with_bg(card, CARD, radius=10)

    header = BoxLayout(size_hint_y=None, spacing=dp(8), size_hint_x=1)
    header.bind(minimum_height=header.setter("height"))
    header.add_widget(_chip(tag))
    sig_label = Label(
        text=sig,
        markup=False,
        font_name="Mono",
        font_size=sp(14),
        color=_rgba(ACCENT_DARK),
        halign="left",
        valign="middle",
    )
    header.add_widget(_auto_height(sig_label))
    card.add_widget(header)

    if desc:
        card.add_widget(_label(desc, size=14, color=MUTED, justify=False))
    return card


def _chapter(title, subtitle):
    box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4), size_hint_x=1)
    box.bind(minimum_height=box.setter("height"))
    box.add_widget(_label(title, size=30, bold=True, justify=False, line_height=1.15))
    if subtitle:
        box.add_widget(_label(subtitle, size=15, color=ACCENT, italic=True, justify=False))
    rule = Widget(size_hint_y=None, height=dp(1), size_hint_x=1)
    _with_bg(rule, RULE, radius=0)
    box.add_widget(rule)
    return box


def _build_block(block):
    kind = block["kind"]
    if kind == "p":
        return _label(block["text"], size=block.get("size", 16))
    if kind == "lead":
        return _label(block["text"], size=19, line_height=1.6)
    if kind == "note":
        return _note(block["text"])
    if kind == "code":
        return _code(block["text"], block.get("caption"))
    if kind == "list":
        return _list(block["items"])
    if kind == "table":
        return _table(block["headers"], block["rows"])
    if kind == "api_entry":
        return _api_entry(block["tag"], block["sig"], block["desc"])
    if kind == "space":
        return Widget(size_hint_y=None, height=dp(block.get("height", 8)))
    return None


def _page(chapter, subtitle, blocks):
    content = BoxLayout(orientation="vertical", spacing=dp(16), size_hint_y=None)
    content.bind(minimum_height=content.setter("height"))
    content.add_widget(_chapter(chapter, subtitle))
    for block in blocks:
        content.add_widget(_build_block(block))

    scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))
    scroll.add_widget(content)

    outer = BoxLayout(orientation="vertical", padding=(dp(28), dp(18), dp(28), dp(24)))
    outer.add_widget(scroll)
    return outer


def _make_screen(name, chapter, subtitle, blocks):
    screen = Screen(name=name)
    screen.add_widget(_page(chapter, subtitle, blocks))
    return screen


class TocRow(ButtonBehavior, BoxLayout):
    def __init__(self, number, title, desc, target, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            padding=(dp(16), dp(12)),
            spacing=dp(2),
            size_hint_x=1,
            **kwargs,
        )
        self.target = target
        self.bind(minimum_height=self.setter("height"))
        _with_bg(self, CARD, radius=10)
        self.add_widget(_label(f"[b]{number}.[/b]  {title}", size=16, justify=False))
        if desc:
            self.add_widget(_label(desc, size=13, color=MUTED, justify=False))

    def on_press(self):
        App.get_running_app().root.ids.sm.current = self.target


def _toc_page():
    content = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None)
    content.bind(minimum_height=content.setter("height"))
    content.add_widget(_chapter("Contents", "Tap a chapter to read it; use ‹ › to go back."))
    for number, (name, title, desc) in enumerate(TOC, start=1):
        content.add_widget(TocRow(number, title, desc, name))

    scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))
    scroll.add_widget(content)

    outer = BoxLayout(orientation="vertical", padding=(dp(28), dp(18), dp(28), dp(24)))
    outer.add_widget(scroll)
    screen = Screen(name="toc")
    screen.add_widget(outer)
    return screen


INTRO_BLOCKS = [
    {
        "kind": "lead",
        "text": "kivy-history is a Kivy helper inspired by the JavaScript History API. It turns your ScreenManager into a full navigation history: go forward, go back and manipulate the stack of screens.",
    },
    {
        "kind": "p",
        "text": "In the browser, the [b]history[/b] object remembers the documents visited in a session. Here, each screen of the [b]ScreenManager[/b] plays the role of a document: its “URL” is the screen name.",
    },
    {"kind": "p", "text": "With kivy-history you can:"},
    {
        "kind": "list",
        "items": [
            "Navigate with [b]back()[/b], [b]forward()[/b] and [b]go(delta)[/b].",
            "Add and replace entries with [b]push_state()[/b] and [b]replace_state()[/b].",
            "Inspect [b]state[/b], [b]stack[/b], [b]index[/b] and [b]length[/b].",
            "Listen to the [b]on_popstate[/b] event after navigating.",
            "Restore [b]ScrollView[/b] positions with [b]scroll_restoration[/b].",
        ],
    },
    {
        "kind": "note",
        "text": "[b]No visual dependency:[/b] it only needs a ScreenManager. It works with any transition and requires no widgets of its own.",
    },
    {"kind": "space", "height": 8},
]

INSTALL_BLOCKS = [
    {
        "kind": "lead",
        "text": "Install the package with uv or pip and create the history in three lines.",
    },
    {"kind": "p", "text": "With [b]uv[/b] (recommended):", "size": 15},
    {"kind": "code", "caption": "terminal", "text": "uv add kivy-history"},
    {"kind": "p", "text": "With [b]pip[/b]:", "size": 15},
    {"kind": "code", "caption": "terminal", "text": "pip install kivy-history"},
    {"kind": "p", "text": "Quick start:", "size": 15},
    {
        "kind": "code",
        "caption": "app.py",
        "text": """from kivy.app import App
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

MyApp().run()""",
    },
]

USAGE_BLOCKS = [
    {
        "kind": "lead",
        "text": "History(manager) records the current screen synchronously and binds to the ScreenManager's current property. The stack is never empty.",
    },
    {"kind": "p", "text": "Create the history:", "size": 15},
    {"kind": "code", "caption": "python", "text": "manager.history = History(manager)"},
    {"kind": "p", "text": "Navigate:", "size": 15},
    {
        "kind": "code",
        "caption": "python",
        "text": "manager.history.back()     # go(-1)\nmanager.history.forward()  # go(1)\nmanager.history.go(-2)     # two screens back\nmanager.history.go()       # reload (go(0))",
    },
    {"kind": "p", "text": "Manipulate the stack:", "size": 15},
    {
        "kind": "code",
        "caption": "python",
        "text": 'manager.history.push_state("settings", foo="bar")\nmanager.history.replace_state(name="settings", foo="baz")',
    },
    {
        "kind": "note",
        "text": "[b]push_state[/b] navigates to the given screen and drops any forward entries (like a new navigation). [b]replace_state[/b] replaces the current entry entirely, without merging.",
    },
    {"kind": "space", "height": 8},
]

API_BLOCKS = [
    {
        "kind": "lead",
        "text": "The API mirrors the JavaScript History API. These are the properties, methods and events exposed by History.",
    },
    {
        "kind": "api_entry",
        "tag": "property",
        "sig": "length -> int",
        "desc": "Number of entries in the history, including the current screen.",
    },
    {
        "kind": "api_entry",
        "tag": "property",
        "sig": "state -> State",
        "desc": "Entry at the current position of the stack (the active “document”).",
    },
    {
        "kind": "api_entry",
        "tag": "property",
        "sig": "index -> int",
        "desc": "Current position within the stack (starts at 0).",
    },
    {
        "kind": "api_entry",
        "tag": "property",
        "sig": "stack -> list[State]",
        "desc": "The full stack of history entries.",
    },
    {
        "kind": "api_entry",
        "tag": "property",
        "sig": "scroll_restoration -> 'auto' | 'manual'",
        "desc": "How scroll positions are restored when navigating.",
    },
    {
        "kind": "api_entry",
        "tag": "method",
        "sig": "back()",
        "desc": "Go to the previous screen; equivalent to go(-1).",
    },
    {
        "kind": "api_entry",
        "tag": "method",
        "sig": "forward()",
        "desc": "Go to the next screen; equivalent to go(1).",
    },
    {
        "kind": "api_entry",
        "tag": "method",
        "sig": "go(delta=0)",
        "desc": "Move delta screens; go(0) reloads the screen.",
    },
    {
        "kind": "api_entry",
        "tag": "method",
        "sig": "push_state(name, **kwargs)",
        "desc": "Add an entry, navigate to it and drop any forward entries.",
    },
    {
        "kind": "api_entry",
        "tag": "method",
        "sig": "replace_state(name=None, **kwargs)",
        "desc": "Replace the current entry; can change the screen name.",
    },
    {
        "kind": "api_entry",
        "tag": "method",
        "sig": "restore_scroll(screen=None)",
        "desc": "Restore the saved scroll positions of a screen.",
    },
    {
        "kind": "api_entry",
        "tag": "method",
        "sig": "reload(manager=None)",
        "desc": "Reload the current screen (module-level helper).",
    },
    {
        "kind": "api_entry",
        "tag": "event",
        "sig": "on_popstate(state)",
        "desc": "Fired after back()/forward()/go() and receives the target State.",
    },
    {"kind": "space", "height": 8},
]

COMPARE_BLOCKS = [
    {
        "kind": "lead",
        "text": "kivy-history maps the concepts of the History API onto Kivy. The table shows the term-by-term correspondence.",
    },
    {
        "kind": "table",
        "headers": ["JavaScript History API", "kivy-history"],
        "rows": [
            ["history.length", "history.length"],
            ["history.state", "history.state"],
            ["history.scrollRestoration", "history.scroll_restoration"],
            ["back() / forward() / go(delta)", "back() / forward() / go(delta)"],
            ["pushState(state, title, url)", "push_state(name, **kwargs)"],
            ["replaceState(state, title, url)", "replace_state(name=None, **kwargs)"],
            ["popstate event (event.state)", "on_popstate event (receives the state)"],
        ],
    },
    {"kind": "p", "text": "Kivy particularities:", "size": 15},
    {
        "kind": "list",
        "items": [
            "The “URL” is the [b]screen name[/b] of the ScreenManager.",
            "[b]push_state[/b] navigates to the screen and drops whatever is ahead.",
            "[b]replace_state[/b] replaces the current entry [b]entirely[/b] (no merge) and can change the name.",
            "History requires the ScreenManager it tracks: [b]History(manager)[/b].",
            "The event is called [b]on_popstate[/b] and receives the target State directly.",
        ],
    },
    {"kind": "space", "height": 8},
]

EVENTS_BLOCKS = [
    {
        "kind": "lead",
        "text": "After navigating with back()/forward()/go(), History fires the on_popstate event with the target State. It also manages scroll restoration.",
    },
    {"kind": "p", "text": "Listen to the event:", "size": 15},
    {
        "kind": "code",
        "caption": "python",
        "text": 'def on_popstate(self, state):\n    print("navigated to:", state)\n\nhistory.bind(on_popstate=my_callback)',
    },
    {"kind": "p", "text": "Scroll restoration:", "size": 15},
    {
        "kind": "code",
        "caption": "python",
        "text": 'history.scroll_restoration = "manual"   # or "auto"',
    },
    {
        "kind": "p",
        "text": "In [b]auto[/b] mode, History remembers the position of every ScrollView and restores it when you come back. In [b]manual[/b] mode, you control restoration with [b]restore_scroll()[/b].",
    },
    {
        "kind": "note",
        "text": "With the [b]HISTORY_LOG=1[/b] environment variable, the stack is printed to the console on every change.",
    },
    {"kind": "space", "height": 8},
]

CREDITS_BLOCKS = [
    {
        "kind": "lead",
        "text": "This reader uses kivy-history itself to navigate: the ‹ › buttons in the header call history.back() and history.forward(), and the bottom bar shows state, index and length live.",
    },
    {
        "kind": "p",
        "text": "kivy-history is free software released under the GPL-3.0 license. More information in the project repository.",
    },
    {
        "kind": "code",
        "caption": "reference",
        "text": "https://github.com/gmork2/kivy-history\npip install kivy-history",
    },
    {"kind": "p", "text": "— The End —", "size": 18},
    {"kind": "space", "height": 8},
]


KV = """
#:import sp kivy.metrics.sp
#:import dp kivy.metrics.dp

<Progress>:
    canvas.before:
        Color:
            rgba: 0.89, 0.85, 0.75, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [3, 3, 3, 3]
    canvas:
        Color:
            rgba: 0.61, 0.42, 0.25, 1
        RoundedRectangle:
            pos: self.pos
            size: (self.width * self.value, self.height) if self.value > 0 else (0, 0)
            radius: [3, 3, 3, 3]

<IconButton@Button>:
    size_hint: None, None
    size: dp(42), dp(42)
    font_name: 'Icons'
    font_size: sp(22)
    color: 1, 1, 1, 0.92
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    canvas.before:
        Color:
            rgba: (0.6, 0.52, 0.4, 0.9) if self.state == 'down' else (1, 1, 1, 0.14)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(21)]

<PrimaryButton@Button>:
    size_hint_y: None
    height: dp(50)
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    font_name: 'Serif'
    font_size: sp(17)
    bold: True
    color: 1, 1, 1, 1
    canvas.before:
        Color:
            rgba: (0.43, 0.29, 0.16, 1) if self.state == 'down' else (0.61, 0.42, 0.25, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(25)]

<Reader>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0.965, 0.941, 0.882, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        size_hint_y: None
        height: dp(60)
        padding: dp(10), dp(9)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: 0.173, 0.157, 0.133, 1
            Rectangle:
                pos: self.pos
                size: self.size

        IconButton:
            text: '‹'
            on_press: app.root.history.back()
        IconButton:
            text: '›'
            on_press: app.root.history.forward()

        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 1
            Label:
                text: 'kivy-history · API guide'
                font_name: 'Serif'
                font_size: sp(11)
                color: 0.95, 0.92, 0.85, 0.75
                halign: 'left'
                valign: 'bottom'
                text_size: self.size
            Label:
                id: chapter_label
                text: 'Cover'
                font_name: 'Serif'
                bold: True
                font_size: sp(17)
                color: 0.95, 0.92, 0.85, 1
                halign: 'left'
                valign: 'top'
                text_size: self.size

        IconButton:
            text: '☰'
            on_press: app.root.history.push_state('toc')

    ScreenManager:
        id: sm

        Screen:
            name: 'cover'
            BoxLayout:
                orientation: 'vertical'
                padding: dp(44), dp(32)
                spacing: dp(6)
                canvas.before:
                    Color:
                        rgba: 0.965, 0.941, 0.882, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                Widget:
                Label:
                    text: 'KIVY · HISTORY'
                    font_name: 'Serif'
                    bold: True
                    font_size: sp(15)
                    color: 0.61, 0.42, 0.25, 1
                    halign: 'center'
                    size_hint_y: None
                    height: dp(24)
                Label:
                    text: 'kivy-history'
                    font_name: 'Serif'
                    bold: True
                    font_size: sp(48)
                    color: 0.23, 0.2, 0.16, 1
                    halign: 'center'
                    size_hint_y: None
                    height: dp(72)
                Label:
                    text: 'The JavaScript History API, in Kivy'
                    font_name: 'Serif'
                    italic: True
                    font_size: sp(19)
                    color: 0.54, 0.49, 0.42, 1
                    halign: 'center'
                    size_hint_y: None
                    height: dp(34)
                Widget:
                    size_hint_y: None
                    height: dp(10)
                BoxLayout:
                    size_hint_y: None
                    height: dp(1)
                    size_hint_x: None
                    width: dp(220)
                    pos_hint: {'center_x': .5}
                    canvas:
                        Color:
                            rgba: 0.61, 0.42, 0.25, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                Widget:
                    size_hint_y: None
                    height: dp(10)
                Label:
                    text: 'A pocket guide · v2.1.2'
                    font_name: 'Serif'
                    font_size: sp(14)
                    color: 0.54, 0.49, 0.42, 1
                    halign: 'center'
                    size_hint_y: None
                    height: dp(24)
                Widget:
                PrimaryButton:
                    text: 'Start reading'
                    size_hint_x: None
                    width: dp(260)
                    pos_hint: {'center_x': .5}
                    on_press: app.root.ids.sm.current = 'toc'
                Widget:

    BoxLayout:
        size_hint_y: None
        height: dp(44)
        padding: dp(14), dp(6)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: 0.89, 0.85, 0.75, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            id: status_state
            text: 'state · toc'
            markup: True
            font_name: 'Serif'
            font_size: sp(13)
            color: 0.42, 0.37, 0.3, 1
            halign: 'left'
            valign: 'middle'
            size_hint_x: None
            width: dp(210)
            text_size: self.size

        Progress:
            id: progress
            size_hint_y: None
            height: dp(6)
            pos_hint: {'center_y': .5}

        Label:
            id: status_index
            text: 'index 0 · length 1'
            font_name: 'Serif'
            font_size: sp(13)
            color: 0.42, 0.37, 0.3, 1
            halign: 'right'
            valign: 'middle'
            size_hint_x: None
            width: dp(210)
            text_size: self.size
"""


class ReaderApp(App):
    def build(self):
        _register_fonts()
        Builder.load_string(KV)
        root = Reader()
        sm = root.ids.sm

        history = History(sm)
        sm.history = history
        root.history = history

        self._root = root
        self._sm = sm

        sm.add_widget(_toc_page())
        sm.add_widget(
            _make_screen("intro", "Introduction", "A navigation history for Kivy", INTRO_BLOCKS)
        )
        sm.add_widget(
            _make_screen("install", "Installation", "uv or pip, and a quick start", INSTALL_BLOCKS)
        )
        sm.add_widget(
            _make_screen(
                "usage", "Basic usage", "Navigate and manipulate the history", USAGE_BLOCKS
            )
        )
        sm.add_widget(
            _make_screen("api", "API reference", "Properties, methods and events", API_BLOCKS)
        )
        sm.add_widget(
            _make_screen(
                "compare",
                "JavaScript comparison",
                "The differences with the History API",
                COMPARE_BLOCKS,
            )
        )
        sm.add_widget(
            _make_screen(
                "events", "Events & scroll", "on_popstate and scroll_restoration", EVENTS_BLOCKS
            )
        )
        sm.add_widget(_make_screen("credits", "Credits", "Credits and license", CREDITS_BLOCKS))

        history.bind(index=self._refresh, stack=self._refresh)
        sm.bind(current=self._refresh)
        self._refresh()
        return root

    def _refresh(self, *args):
        sm = self._sm
        name = sm.current or "cover"
        self._root.ids.chapter_label.text = CHAPTERS.get(name, name)

        hist = sm.history
        self._root.ids.status_state.text = f"state  [b]{hist.state}[/b]"
        index = int(hist.index)
        length = int(hist.length)
        self._root.ids.status_index.text = f"index {index} · length {length}"
        self._root.ids.progress.value = (index + 1) / length if length else 0.0


def main():
    os.environ["HISTORY_LOG"] = "1"
    ReaderApp().run()


if __name__ == "__main__":
    main()
