from textual.app import App, ComposeResult

from typehero.engine.keystroke import KeystrokeKind
from typehero.tui.widgets.typing_view import TypingView


class _Clock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        self.t += 1.0
        return self.t


class _Host(App):
    def __init__(self, target: str) -> None:
        super().__init__()
        self._target = target
        self.finished: TypingView.Finished | None = None

    def compose(self) -> ComposeResult:
        yield TypingView(self._target, clock=_Clock())

    def on_typing_view_finished(self, event: TypingView.Finished) -> None:
        self.finished = event


async def test_typing_all_correct_chars_finishes_with_keystrokes():
    app = _Host("fj")
    async with app.run_test() as pilot:
        await pilot.press("f", "j")
        assert app.finished is not None
        chars = [k for k in app.finished.keystrokes if k.kind is KeystrokeKind.CHAR]
        assert [k.char for k in chars] == ["f", "j"]


async def test_backspace_lets_you_correct_then_finish():
    app = _Host("fj")
    async with app.run_test() as pilot:
        await pilot.press("x", "backspace", "f", "j")
        assert app.finished is not None
        view = app.query_one(TypingView)
        assert view.session.error_count == 1  # the wrong 'x' is still counted
