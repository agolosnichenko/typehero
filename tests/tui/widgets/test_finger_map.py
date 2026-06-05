from textual.app import App, ComposeResult

from typehero.tui.keyboard_layout import JCUKEN, QWERTY, Finger, Hand, KeyboardLayout
from typehero.tui.widgets.finger_map import FingerMap


class _Host(App):
    def __init__(self, layout: KeyboardLayout) -> None:
        super().__init__()
        self._layout = layout

    def compose(self) -> ComposeResult:
        yield FingerMap(self._layout)


async def test_highlight_marks_key_and_opposite_shift():
    app = _Host(JCUKEN)
    async with app.run_test():
        widget = app.query_one(FingerMap)
        widget.highlight("Д")
        state = widget.highlight_state
        assert state.key is not None and state.key.finger is Finger.R_RING
        assert state.shift_hand is Hand.LEFT


async def test_highlight_lowercase_has_no_shift():
    app = _Host(JCUKEN)
    async with app.run_test():
        widget = app.query_one(FingerMap)
        widget.highlight("д")
        assert widget.highlight_state.shift_hand is None


async def test_highlight_jcuken_comma_uses_shift():
    # Comma is the shifted char on the R_PINKY key in JCUKEN, so the
    # opposite-hand Shift is LEFT (not right).
    app = _Host(JCUKEN)
    async with app.run_test():
        widget = app.query_one(FingerMap)
        widget.highlight(",")
        assert widget.highlight_state.shift_hand is Hand.LEFT


async def test_highlight_off_map_char_clears_highlight():
    app = _Host(QWERTY)
    async with app.run_test():
        widget = app.query_one(FingerMap)
        widget.highlight("d")
        widget.highlight("1")
        assert widget.highlight_state.key is None
        assert widget.highlight_state.shift_hand is None


async def test_renders_letters_from_the_layout():
    app = _Host(QWERTY)
    async with app.run_test():
        widget = app.query_one(FingerMap)
        widget.highlight("f")
        rendered = str(widget.render())
        assert "f" in rendered and "j" in rendered
        assert "Shift" in rendered


async def test_highlight_space_marks_the_space_key():
    app = _Host(QWERTY)
    async with app.run_test():
        widget = app.query_one(FingerMap)
        widget.highlight(" ")
        assert widget.highlight_state.key is not None
        assert widget.highlight_state.key.finger is Finger.THUMB
        rendered = str(widget.render())
        assert "space" in rendered
