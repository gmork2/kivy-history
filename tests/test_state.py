from kivy_history.state import State


def test_init_with_defaults():
    state = State("home")
    assert state.state == {"name": "home"}


def test_init_with_extra_data():
    state = State("detail", id=42, title="Hello")
    assert state.state == {"name": "detail", "id": 42, "title": "Hello"}


def test_update_merges_kwargs():
    state = State("home", id=1)
    state.update(id=2, title="new")
    assert state.state == {"name": "home", "id": 2, "title": "new"}


def test_repr_returns_name():
    state = State("settings")
    assert repr(state) == "settings"
    assert str(state) == "settings"
