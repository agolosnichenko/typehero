from typer.engine.keystroke import Keystroke, KeystrokeKind
from typer.engine.metrics import compute_metrics
from typer.engine.session import TypingSession


def _char(c: str, t: float) -> Keystroke:
    return Keystroke(kind=KeystrokeKind.CHAR, char=c, timestamp=t)


def _type(target: str, chars: list[tuple[str, float]]) -> TypingSession:
    s = TypingSession(target=target)
    for c, t in chars:
        s.apply(_char(c, t))
    return s


def test_perfect_run_has_full_accuracy():
    # 5 correct chars over 60s => 1 word per minute.
    s = _type("abcde", [("a", 0.0), ("b", 15.0), ("c", 30.0), ("d", 45.0), ("e", 60.0)])
    m = compute_metrics(s)
    assert m.errors == 0
    assert m.accuracy == 1.0
    assert m.elapsed_seconds == 60.0
    assert m.net_wpm == 1.0
    assert m.raw_wpm == 1.0


def test_error_lowers_accuracy_and_net_wpm():
    s = _type("abcde", [("a", 0.0), ("X", 15.0), ("c", 30.0), ("d", 45.0), ("e", 60.0)])
    m = compute_metrics(s)
    assert m.errors == 1
    assert m.error_rate == 1 / 5
    assert m.accuracy == 4 / 5
    assert m.net_wpm == (4 / 5) / 1.0  # 4 correct chars / 5 / 1 minute
    assert m.raw_wpm == 1.0


def test_empty_session_is_zero_not_crash():
    s = TypingSession(target="abc")
    m = compute_metrics(s)
    assert m.errors == 0
    assert m.error_rate == 0.0
    assert m.accuracy == 1.0
    assert m.net_wpm == 0.0
    assert m.elapsed_seconds == 0.0


from hypothesis import given
from hypothesis import strategies as st


@given(st.lists(st.sampled_from("ab"), min_size=1, max_size=20))
def test_accuracy_always_between_zero_and_one(typed: list[str]):
    target = "a" * len(typed)
    session = _type(target, [(c, float(i)) for i, c in enumerate(typed)])
    m = compute_metrics(session)
    assert 0.0 <= m.accuracy <= 1.0
    assert 0.0 <= m.error_rate <= 1.0
