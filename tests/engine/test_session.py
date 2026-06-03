from typer.engine.keystroke import Keystroke, KeystrokeKind
from typer.engine.session import CharState, TypingSession


def _char(c: str, t: float = 0.0) -> Keystroke:
    return Keystroke(kind=KeystrokeKind.CHAR, char=c, timestamp=t)


def test_new_session_is_all_pending():
    s = TypingSession(target="ab")
    assert s.char_states == [CharState.PENDING, CharState.PENDING]
    assert s.cursor == 0
    assert not s.is_complete


def test_correct_char_advances_cursor_and_marks_correct():
    s = TypingSession(target="ab")
    s.apply(_char("a"))
    assert s.char_states[0] is CharState.CORRECT
    assert s.cursor == 1
    assert s.error_count == 0


def test_wrong_char_marks_error_and_counts_it():
    s = TypingSession(target="ab")
    s.apply(_char("x"))
    assert s.char_states[0] is CharState.ERROR
    assert s.cursor == 1
    assert s.error_count == 1


def test_typing_past_end_is_ignored():
    s = TypingSession(target="a")
    s.apply(_char("a"))
    s.apply(_char("b"))
    assert s.is_complete
    assert s.cursor == 1
    assert len([k for k in s.keystrokes if k.kind is KeystrokeKind.CHAR]) == 2
    assert s.char_keystroke_count == 1  # second char ignored for metrics


def test_target_is_nfc_normalized():
    # "й" as base "и" + combining breve must normalize to a single code point.
    s = TypingSession(target="й")
    assert len(s.target) == 1
    assert s.target == "й"


def _bs(t: float = 0.0) -> Keystroke:
    return Keystroke(kind=KeystrokeKind.BACKSPACE, char=None, timestamp=t)


def test_backspace_moves_cursor_back_and_resets_state():
    s = TypingSession(target="ab")
    s.apply(_char("a"))
    s.apply(_bs())
    assert s.cursor == 0
    assert s.char_states[0] is CharState.PENDING


def test_backspace_at_start_is_ignored():
    s = TypingSession(target="ab")
    s.apply(_bs())
    assert s.cursor == 0
    assert s.char_states == [CharState.PENDING, CharState.PENDING]


def test_corrected_error_still_counts_as_error():
    s = TypingSession(target="ab")
    s.apply(_char("x"))  # wrong
    s.apply(_bs())       # fix
    s.apply(_char("a"))  # correct retype
    assert s.error_count == 1
    assert s.char_states[0] is CharState.CORRECT
