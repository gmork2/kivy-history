def test_initial_state_is_recorded_immediately(history):
    assert history.length == 1
    assert history.index == 0
    assert str(history.state) == "s1"
    assert [str(s) for s in history.stack] == ["s1"]


def test_on_state_registers_screen_change(history, screen_manager):
    screen_manager.current = "s2"

    assert history.length == 2
    assert history.index == 1
    assert str(history.state) == "s2"
    assert [str(s) for s in history.stack] == ["s1", "s2"]


def test_back(history, screen_manager):
    screen_manager.current = "s2"

    history.back()

    assert history.index == 0
    assert str(history.state) == "s1"
    assert screen_manager.current == "s1"


def test_forward(history, screen_manager):
    screen_manager.current = "s2"
    history.back()

    history.forward()

    assert history.index == 1
    assert str(history.state) == "s2"
    assert screen_manager.current == "s2"


def test_go_with_negative_delta(history, screen_manager):
    screen_manager.current = "s2"
    screen_manager.current = "s3"

    history.go(-2)

    assert history.index == 0
    assert str(history.state) == "s1"
    assert screen_manager.current == "s1"


def test_back_beyond_first_screen_has_no_effect(history, screen_manager):
    screen_manager.current = "s2"
    history.back()

    history.back()  # already at the first screen

    assert history.index == 0
    assert str(history.state) == "s1"
    assert screen_manager.current == "s1"


def test_forward_beyond_last_screen_has_no_effect(history, screen_manager):
    screen_manager.current = "s2"

    history.forward()  # already at the most recent screen

    assert history.index == 1
    assert str(history.state) == "s2"


def test_push_state_navigates_and_makes_entry_current(history, screen_manager):
    history.push_state("s4")

    assert history.length == 2
    assert history.index == 1
    assert str(history.state) == "s4"
    assert screen_manager.current == "s4"
    assert [str(s) for s in history.stack] == ["s1", "s4"]


def test_push_state_drops_forward_entries(history, screen_manager):
    screen_manager.current = "s2"
    history.back()  # back to s1, the forward entry s2 remains

    history.push_state("s4")

    assert [str(s) for s in history.stack] == ["s1", "s4"]
    assert history.index == 1
    assert screen_manager.current == "s4"


def test_replace_state_replaces_entire_entry(history):
    history.replace_state(title="hello", id=42)

    assert history.state.state == {"name": "s1", "title": "hello", "id": 42}


def test_replace_state_keeps_name_when_omitted(history):
    history.replace_state(title="hello")

    assert str(history.state) == "s1"
    assert history.state.state == {"name": "s1", "title": "hello"}


def test_replace_state_changes_name(history):
    history.replace_state(name="sX")

    assert str(history.state) == "sX"
    assert history.state.state == {"name": "sX"}


def test_go_dispatches_popstate(history, screen_manager):
    screen_manager.current = "s2"
    popped = []
    history.bind(on_popstate=lambda *args: popped.append(args))

    history.back()

    assert len(popped) == 1
    assert str(popped[0][-1]) == "s1"


def test_state_property_returns_current_entry(history, screen_manager):
    screen_manager.current = "s2"

    assert str(history.state) == "s2"
