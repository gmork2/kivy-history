import kivy_history.utils as utils
from kivy_history.state import State


def test_console_log_marks_current_index(monkeypatch):
    messages = []
    monkeypatch.setattr(utils.Logger, "info", lambda msg: messages.append(msg))

    stack = [State("home"), State("settings"), State("detail")]
    utils.console_log(stack, index=1)

    assert messages == ["History: Stack is {'home > [settings] > detail'}"]


def test_console_log_single_state(monkeypatch):
    messages = []
    monkeypatch.setattr(utils.Logger, "info", lambda msg: messages.append(msg))

    utils.console_log([State("home")], index=0)

    assert messages == ["History: Stack is {'[home]'}"]
