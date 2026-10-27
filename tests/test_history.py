def test_initial_state(history):
    assert history.lenght == 1
    assert history.index == 0
    assert str(history.state) == "s1"
    assert [str(s) for s in history.stack] == ["s1"]


def test_on_state_registers_screen_change(history, running_app):
    running_app.root.current = "s2"

    assert history.lenght == 2
    assert history.index == 1
    assert str(history.state) == "s2"
    assert [str(s) for s in history.stack] == ["s1", "s2"]


def test_back(history, running_app):
    running_app.root.current = "s2"

    history.back()

    assert history.index == 0
    assert str(history.state) == "s1"
    assert running_app.root.current == "s1"


def test_forward(history, running_app):
    running_app.root.current = "s2"
    history.back()

    history.forward()

    assert history.index == 1
    assert str(history.state) == "s2"
    assert running_app.root.current == "s2"


def test_go_with_negative_delta(history, running_app):
    running_app.root.current = "s2"
    running_app.root.current = "s3"

    history.go(-2)

    assert history.index == 0
    assert str(history.state) == "s1"
    assert running_app.root.current == "s1"


def test_back_beyond_first_screen_has_no_effect(history, running_app):
    running_app.root.current = "s2"
    history.back()

    history.back()  # already at the first screen

    assert history.index == 0
    assert str(history.state) == "s1"
    assert running_app.root.current == "s1"


def test_forward_beyond_last_screen_has_no_effect(history, running_app):
    running_app.root.current = "s2"

    history.forward()  # already at the most recent screen

    assert history.index == 1
    assert str(history.state) == "s2"


def test_push_state(history):
    history.push_state("s4")

    assert history.lenght == 2
    assert [str(s) for s in history.stack] == ["s1", "s4"]


def test_replace_state_updates_current_entry(history):
    history.replace_state(name="sX")

    assert str(history.state) == "sX"
    assert [str(s) for s in history.stack] == ["sX"]


def test_state_property_returns_current_entry(history, running_app):
    running_app.root.current = "s2"

    assert str(history.state) == "s2"
