import os

from kivy.app import App
from kivy.event import EventDispatcher
from kivy.properties import BoundedNumericProperty, ListProperty
from kivy.uix.screenmanager import ScreenManagerException

from .state import State
from .utils import console_log


def reload(manager=None) -> None:
    """
    Reloads the current screen by briefly setting the manager's ``current``
    screen to an empty string. If ``manager`` is not provided, the running app's
    root widget is used.
    """
    manager = manager or App.get_running_app().root
    try:
        manager.current = ""
    except ScreenManagerException:
        pass


class History(EventDispatcher):
    """
    This class exposes useful methods and properties that let you navigate
    back and forth through the screen manager, and manipulate the contents
    of the history stack.

    A ``History`` must be created with the :class:`ScreenManager` it tracks::

        history = History(manager)

    The current screen is recorded immediately and the manager's ``current``
    property is bound automatically so screen changes are registered.
    """

    __events__ = ("on_popstate",)

    loading = False
    stack = ListProperty()
    index = BoundedNumericProperty(0, min=0)

    def __init__(self, manager, **kwargs):
        """
        :param manager: the :class:`~kivy.uix.screenmanager.ScreenManager`
            whose navigation should be tracked.
        """
        super().__init__(**kwargs)
        self.manager = manager
        self.stack.append(State(manager.current))
        manager.bind(current=self.on_state)

    @property
    def length(self) -> int:
        """
        Returns an Integer representing the number of elements in the history,
        including the currently loaded screen.
        """
        return len(self.stack)

    @property
    def state(self) -> State:
        """
        Returns an any value representing the state at the top of the history
        stack.
        """
        return self.stack[self.index]

    def back(self) -> None:
        """
        This method goes to the previous screen in session history, equivalent
        to history.go(-1).

        Calling this method to go back beyond the first screen in the session
        history has no effect and doesn't raise an exception.
        """
        self.go(-1)

    def forward(self) -> None:
        """
        This method goes to the next screen in session history, the equivalent
        to history.go(1).

        Calling this method to go forward beyond the most recent screen in the
        session history has no effect and doesn't raise an exception.
        """
        self.go(1)

    def go(self, delta: int = 0) -> None:
        """
        The position in the history to which you want to move, relative to the
        current screen. A negative value moves backwards, a positive value moves
        forwards. So, for example, history.go(2) moves forward two screens and
        history.go(-2) moves back two screens. If no value is passed or if delta
        equals 0, it has the same result as calling reload().

        If you specify an out-of-bounds value (for instance, specifying -1 when
        there are no previous screen in the session history), this method silently
        has no effect.
        """
        self.loading = True

        if not delta:
            reload(self.manager)
        else:
            try:
                self.index += delta
                self.manager.current = str(self.state)
            except ValueError:
                pass
            else:
                self.dispatch("on_popstate", self.state)
        self.loading = False

    def push_state(self, name: str, **kwargs) -> None:
        """
        Pushes the given data onto the session history stack with the specified
        data, drops any forward entries and navigates to the new screen.
        """
        self.loading = True
        self.stack = self.stack[0 : self.index + 1]
        self.stack.append(State(name, **kwargs))
        self.index = self.length - 1
        self.manager.current = name
        self.loading = False

    def replace_state(self, name: str = None, **kwargs) -> None:
        """
        Replaces the current entry with a new state built from ``name`` (optional)
        and ``kwargs``. The previous state is discarded, not merged.
        """
        current_name = self.state.state["name"]
        new_name = name if name is not None else current_name
        self.stack[self.index] = State(new_name, **kwargs)

    def on_state(self, instance, value):
        """
        Registers a screen change in the history stack. It is bound automatically
        to the manager's ``current`` property when the ``History`` is created.
        """
        if not self.loading:
            self.stack = self.stack[0 : self.index + 1]
            self.stack.insert(self.index + 1, State(value))
            self.index += 1

    def on_index(self, instance, value):
        """
        Log the current state of the stack.
        """
        if int(os.environ.get("HISTORY_LOG", "0")):
            console_log(self.stack, value)

    def on_stack(self, instance, value):
        """
        Change the maximum value allowed for the index property.
        """
        prop = self.property
        prop("index").set_max(self, self.length - 1)

    def on_popstate(self, state):
        """
        Event fired after navigating back/forward (like the JavaScript
        ``popstate`` event); ``state`` is the entry being navigated to.
        """
