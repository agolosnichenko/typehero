# Typer Core (Plan 1 of 3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the pure-logic core of the Typer touch-typing trainer — typing engine, metrics, domain model, gamification, localization, content loading, and persistence — fully tested and runnable headlessly (no terminal).

**Architecture:** One-directional dependency flow `gamification → domain → engine`, with `persistence` and `content_loader` as edge adapters. All logic is decoupled from the TUI (Plan 2) and from wall-clock time (timestamps are injected). A thin headless runner ties the engine and domain together so the whole "type → measure → evaluate" loop is testable with plain pytest.

**Tech Stack:** Python 3.13, `uv` (venv + deps), `ruff` (lint/format), `ty` (types), `pytest` + `hypothesis` (tests), `PyYAML` (content), stdlib `json` (persistence).

---

## File Structure

| Path | Responsibility |
| --- | --- |
| `pyproject.toml` | Project metadata, deps, tool config (ruff/ty/pytest) |
| `src/typer/engine/keystroke.py` | `Keystroke`, `KeystrokeKind` value types |
| `src/typer/engine/session.py` | `TypingSession`, `CharState` — applies keystrokes to state |
| `src/typer/engine/metrics.py` | `SessionMetrics`, `compute_metrics` |
| `src/typer/domain/lesson.py` | `Lesson`, `PassCriteria`, `LessonResult`, `evaluate` |
| `src/typer/domain/course.py` | `Course`, `is_unlocked` |
| `src/typer/domain/progress.py` | `Progress`, `BenchmarkSnapshot` |
| `src/typer/gamification/xp.py` | XP bonuses, `earned_xp`, `player_level` |
| `src/typer/gamification/streaks.py` | `update_streak` (calendar-day logic) |
| `src/typer/gamification/achievements.py` | `Achievement`, `check`, `newly_unlocked` |
| `src/typer/localization.py` | `pick_locale` (content), `Translator.t` (UI strings) |
| `src/typer/content_loader.py` | Parse course/achievement/i18n YAML → domain objects |
| `src/typer/persistence/store.py` | Atomic JSON save/load of `Progress`, corrupt recovery |
| `src/typer/play.py` | Headless runner: keystrokes → metrics → lesson result |
| `tests/**` | Mirrors `src/typer/**` |

---

## Task 1: Project scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/typer/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/test_smoke.py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "typer"
version = "0.1.0"
description = "Console touch-typing trainer with gamification"
requires-python = ">=3.13"
dependencies = ["pyyaml>=6.0.2"]

[dependency-groups]
dev = ["pytest>=8.3.4", "hypothesis>=6.125.0"]

[build-system]
requires = ["uv_build>=0.5.0"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-root = "src"
module-name = "typer"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.ty.rules]
```

- [ ] **Step 2: Create package markers**

Create `src/typer/__init__.py` with a single line:

```python
"""Typer — console touch-typing trainer."""
```

Create empty `tests/__init__.py` (zero bytes).

- [ ] **Step 3: Write the smoke test**

Create `tests/test_smoke.py`:

```python
import typer


def test_package_imports():
    assert typer.__doc__ is not None
```

- [ ] **Step 4: Sync env and run the smoke test**

Run: `uv sync && uv run pytest tests/test_smoke.py -v`
Expected: PASS (1 passed).

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/typer/__init__.py tests/__init__.py tests/test_smoke.py uv.lock
git commit -m "chore: scaffold typer project with uv and pytest"
```

---

## Task 2: Keystroke value types

**Files:**
- Create: `src/typer/engine/__init__.py` (empty)
- Create: `src/typer/engine/keystroke.py`
- Create: `tests/engine/__init__.py` (empty)
- Create: `tests/engine/test_keystroke.py`

- [ ] **Step 1: Write the failing test**

Create `tests/engine/test_keystroke.py`:

```python
from typer.engine.keystroke import Keystroke, KeystrokeKind


def test_char_keystroke_holds_char_and_timestamp():
    ks = Keystroke(kind=KeystrokeKind.CHAR, char="a", timestamp=1.5)
    assert ks.kind is KeystrokeKind.CHAR
    assert ks.char == "a"
    assert ks.timestamp == 1.5


def test_backspace_keystroke_has_no_char():
    ks = Keystroke(kind=KeystrokeKind.BACKSPACE, char=None, timestamp=2.0)
    assert ks.kind is KeystrokeKind.BACKSPACE
    assert ks.char is None


def test_keystroke_is_frozen():
    import dataclasses

    ks = Keystroke(kind=KeystrokeKind.CHAR, char="x", timestamp=0.0)
    with __import__("pytest").raises(dataclasses.FrozenInstanceError):
        ks.char = "y"  # type: ignore[misc]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/engine/test_keystroke.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'typer.engine'`.

- [ ] **Step 3: Write minimal implementation**

Create empty `src/typer/engine/__init__.py` and `tests/engine/__init__.py`.

Create `src/typer/engine/keystroke.py`:

```python
"""Keystroke value types — the engine's only input."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class KeystrokeKind(Enum):
    """Kind of a single keypress the engine understands."""

    CHAR = "char"
    BACKSPACE = "backspace"


@dataclass(frozen=True)
class Keystroke:
    """A single keypress with an injected timestamp (seconds).

    `char` is the typed character for `CHAR` keystrokes and `None` for
    `BACKSPACE`. `timestamp` is supplied by the caller so the engine stays
    deterministic and testable.
    """

    kind: KeystrokeKind
    char: str | None
    timestamp: float
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/engine/test_keystroke.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add src/typer/engine/__init__.py src/typer/engine/keystroke.py tests/engine/__init__.py tests/engine/test_keystroke.py
git commit -m "feat: add Keystroke value types"
```

---

## Task 3: TypingSession — character handling

**Files:**
- Create: `src/typer/engine/session.py`
- Create: `tests/engine/test_session.py`

- [ ] **Step 1: Write the failing test**

Create `tests/engine/test_session.py`:

```python
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
    s = TypingSession(target="й")
    assert len(s.target) == 1
    assert s.target == "й"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/engine/test_session.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'typer.engine.session'`.

- [ ] **Step 3: Write minimal implementation**

Create `src/typer/engine/session.py`:

```python
"""Typing session state — applies keystrokes to a target string."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from enum import Enum

from typer.engine.keystroke import Keystroke, KeystrokeKind


class CharState(Enum):
    """Per-character display/correctness state."""

    PENDING = "pending"
    CORRECT = "correct"
    ERROR = "error"


@dataclass
class TypingSession:
    """Mutable state of one typing attempt.

    Counts every error keystroke (including ones later fixed with backspace)
    so accuracy cannot be gamed by corrections. `char_keystroke_count` excludes
    keystrokes typed past the end of the target.
    """

    target: str
    cursor: int = 0
    char_states: list[CharState] = field(default_factory=list)
    keystrokes: list[Keystroke] = field(default_factory=list)
    error_count: int = 0
    char_keystroke_count: int = 0
    max_combo: int = 0
    _combo: int = 0

    def __post_init__(self) -> None:
        self.target = unicodedata.normalize("NFC", self.target)
        if not self.char_states:
            self.char_states = [CharState.PENDING] * len(self.target)

    @property
    def is_complete(self) -> bool:
        return self.cursor >= len(self.target)

    def apply(self, ks: Keystroke) -> None:
        """Apply one keystroke, mutating session state."""
        self.keystrokes.append(ks)
        if ks.kind is KeystrokeKind.BACKSPACE:
            self._apply_backspace()
            return
        if self.is_complete:
            return
        self.char_keystroke_count += 1
        expected = self.target[self.cursor]
        if ks.char == expected:
            self.char_states[self.cursor] = CharState.CORRECT
            self._combo += 1
            self.max_combo = max(self.max_combo, self._combo)
        else:
            self.char_states[self.cursor] = CharState.ERROR
            self.error_count += 1
            self._combo = 0
        self.cursor += 1

    def _apply_backspace(self) -> None:
        if self.cursor > 0:
            self.cursor -= 1
            self.char_states[self.cursor] = CharState.PENDING
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/engine/test_session.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add src/typer/engine/session.py tests/engine/test_session.py
git commit -m "feat: add TypingSession character handling with NFC normalization"
```

---

## Task 4: TypingSession — backspace behaviour

**Files:**
- Modify: `tests/engine/test_session.py` (append tests)

(No production change expected — backspace is already implemented in Task 3. This task locks the behaviour with edge tests.)

- [ ] **Step 1: Write the failing/edge tests**

Append to `tests/engine/test_session.py`:

```python
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
```

- [ ] **Step 2: Run tests**

Run: `uv run pytest tests/engine/test_session.py -v`
Expected: PASS (8 passed). If `test_corrected_error_still_counts_as_error` fails, the error counter is being decremented on backspace — it must not be.

- [ ] **Step 3: Commit**

```bash
git add tests/engine/test_session.py
git commit -m "test: lock backspace and corrected-error behaviour"
```

---

## Task 5: Combo tracking

**Files:**
- Modify: `tests/engine/test_session.py` (append tests)

(Combo is implemented in Task 3; this task verifies it.)

- [ ] **Step 1: Write the tests**

Append to `tests/engine/test_session.py`:

```python
def test_combo_grows_on_consecutive_correct():
    s = TypingSession(target="abc")
    for c in "abc":
        s.apply(_char(c))
    assert s.max_combo == 3


def test_error_resets_combo():
    s = TypingSession(target="abcd")
    s.apply(_char("a"))
    s.apply(_char("b"))
    s.apply(_char("X"))  # wrong -> combo resets
    s.apply(_char("d"))
    assert s.max_combo == 2
```

- [ ] **Step 2: Run tests**

Run: `uv run pytest tests/engine/test_session.py -v`
Expected: PASS (10 passed).

- [ ] **Step 3: Commit**

```bash
git add tests/engine/test_session.py
git commit -m "test: verify combo tracking resets on error"
```

---

## Task 6: Session metrics

**Files:**
- Create: `src/typer/engine/metrics.py`
- Create: `tests/engine/test_metrics.py`

- [ ] **Step 1: Write the failing test**

Create `tests/engine/test_metrics.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/engine/test_metrics.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'typer.engine.metrics'`.

- [ ] **Step 3: Write minimal implementation**

Create `src/typer/engine/metrics.py`:

```python
"""Derived metrics for a typing session.

WPM uses the industry-standard 5-characters-per-word convention so results are
comparable across lessons and with external typing tests. Elapsed time runs
from the first to the last character keystroke.
"""

from __future__ import annotations

from dataclasses import dataclass

from typer.engine.keystroke import KeystrokeKind
from typer.engine.session import CharState, TypingSession

_CHARS_PER_WORD = 5


@dataclass(frozen=True)
class SessionMetrics:
    """Immutable snapshot of one session's performance."""

    errors: int
    error_rate: float
    accuracy: float
    net_wpm: float
    raw_wpm: float
    elapsed_seconds: float
    max_combo: int


def compute_metrics(session: TypingSession) -> SessionMetrics:
    """Compute metrics from a (possibly incomplete) session."""
    char_keys = [k for k in session.keystrokes if k.kind is KeystrokeKind.CHAR]
    total = session.char_keystroke_count
    errors = session.error_count
    error_rate = errors / total if total else 0.0
    accuracy = 1.0 - error_rate
    correct_chars = sum(1 for st in session.char_states if st is CharState.CORRECT)

    elapsed = char_keys[-1].timestamp - char_keys[0].timestamp if len(char_keys) >= 2 else 0.0
    minutes = elapsed / 60.0
    net_wpm = (correct_chars / _CHARS_PER_WORD) / minutes if minutes > 0 else 0.0
    raw_wpm = (total / _CHARS_PER_WORD) / minutes if minutes > 0 else 0.0

    return SessionMetrics(
        errors=errors,
        error_rate=error_rate,
        accuracy=accuracy,
        net_wpm=net_wpm,
        raw_wpm=raw_wpm,
        elapsed_seconds=elapsed,
        max_combo=session.max_combo,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/engine/test_metrics.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Add a property test for the accuracy invariant**

Append to `tests/engine/test_metrics.py`:

```python
from hypothesis import given
from hypothesis import strategies as st


@given(st.lists(st.sampled_from("ab"), min_size=1, max_size=20))
def test_accuracy_always_between_zero_and_one(typed: list[str]):
    target = "a" * len(typed)
    session = _type(target, [(c, float(i)) for i, c in enumerate(typed)])
    m = compute_metrics(session)
    assert 0.0 <= m.accuracy <= 1.0
    assert 0.0 <= m.error_rate <= 1.0
```

- [ ] **Step 6: Run all metric tests**

Run: `uv run pytest tests/engine/test_metrics.py -v`
Expected: PASS (4 passed).

- [ ] **Step 7: Commit**

```bash
git add src/typer/engine/metrics.py tests/engine/test_metrics.py
git commit -m "feat: add session metrics with WPM/accuracy and property test"
```

---

## Task 7: Pass criteria and evaluation

**Files:**
- Create: `src/typer/domain/__init__.py` (empty)
- Create: `src/typer/domain/lesson.py`
- Create: `tests/domain/__init__.py` (empty)
- Create: `tests/domain/test_lesson.py`

- [ ] **Step 1: Write the failing test**

Create `tests/domain/test_lesson.py`:

```python
from typer.domain.lesson import Lesson, PassCriteria, evaluate
from typer.engine.metrics import SessionMetrics


def _metrics(error_rate: float, net_wpm: float) -> SessionMetrics:
    return SessionMetrics(
        errors=0,
        error_rate=error_rate,
        accuracy=1 - error_rate,
        net_wpm=net_wpm,
        raw_wpm=net_wpm,
        elapsed_seconds=60.0,
        max_combo=0,
    )


def test_passes_when_both_criteria_met():
    crit = PassCriteria(max_error_rate=0.05, min_wpm=25.0)
    result = evaluate(crit, _metrics(error_rate=0.04, net_wpm=30.0))
    assert result.passed
    assert result.met_accuracy
    assert result.met_speed


def test_fails_when_too_many_errors():
    crit = PassCriteria(max_error_rate=0.05, min_wpm=25.0)
    result = evaluate(crit, _metrics(error_rate=0.06, net_wpm=30.0))
    assert not result.passed
    assert not result.met_accuracy
    assert result.met_speed


def test_fails_when_too_slow():
    crit = PassCriteria(max_error_rate=0.05, min_wpm=25.0)
    result = evaluate(crit, _metrics(error_rate=0.0, net_wpm=20.0))
    assert not result.passed
    assert result.met_accuracy
    assert not result.met_speed


def test_speed_optional_when_min_wpm_none():
    crit = PassCriteria(max_error_rate=0.08, min_wpm=None)
    result = evaluate(crit, _metrics(error_rate=0.07, net_wpm=1.0))
    assert result.passed
    assert result.met_speed


def test_boundary_error_rate_exactly_at_threshold_passes():
    crit = PassCriteria(max_error_rate=0.05, min_wpm=None)
    result = evaluate(crit, _metrics(error_rate=0.05, net_wpm=99.0))
    assert result.met_accuracy


def test_lesson_holds_criteria_and_reward():
    lesson = Lesson(
        id="en-01",
        title={"en": "Home row"},
        type="keys",
        stages=["fff jjj"],
        criteria=PassCriteria(max_error_rate=0.08, min_wpm=None),
        reward_xp=50,
    )
    assert lesson.criteria.max_error_rate == 0.08
    assert lesson.reward_xp == 50
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/domain/test_lesson.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'typer.domain'`.

- [ ] **Step 3: Write minimal implementation**

Create empty `src/typer/domain/__init__.py` and `tests/domain/__init__.py`.

Create `src/typer/domain/lesson.py`:

```python
"""Lesson definition and pass/fail evaluation."""

from __future__ import annotations

from dataclasses import dataclass

from typer.engine.metrics import SessionMetrics


@dataclass(frozen=True)
class PassCriteria:
    """Thresholds a session must meet to clear a lesson.

    `max_error_rate` is a fraction of error keystrokes and is always required.
    `min_wpm` is optional (`None` on early lessons where speed is not gated).
    """

    max_error_rate: float
    min_wpm: float | None = None


@dataclass(frozen=True)
class LessonResult:
    """Outcome of evaluating one session against a lesson's criteria."""

    passed: bool
    met_accuracy: bool
    met_speed: bool


@dataclass(frozen=True)
class Lesson:
    """A single ordered exercise in a course."""

    id: str
    title: dict[str, str]
    type: str
    stages: list[object]
    criteria: PassCriteria
    reward_xp: int


def evaluate(criteria: PassCriteria, metrics: SessionMetrics) -> LessonResult:
    """A lesson is cleared only when BOTH accuracy and speed criteria hold."""
    met_accuracy = metrics.error_rate <= criteria.max_error_rate
    met_speed = criteria.min_wpm is None or metrics.net_wpm >= criteria.min_wpm
    return LessonResult(
        passed=met_accuracy and met_speed,
        met_accuracy=met_accuracy,
        met_speed=met_speed,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/domain/test_lesson.py -v`
Expected: PASS (6 passed).

- [ ] **Step 5: Commit**

```bash
git add src/typer/domain/__init__.py src/typer/domain/lesson.py tests/domain/__init__.py tests/domain/test_lesson.py
git commit -m "feat: add Lesson and pass-criteria evaluation"
```

---

## Task 8: Course and unlock logic

**Files:**
- Create: `src/typer/domain/course.py`
- Create: `tests/domain/test_course.py`

- [ ] **Step 1: Write the failing test**

Create `tests/domain/test_course.py`:

```python
import pytest

from typer.domain.course import Course, is_unlocked
from typer.domain.lesson import Lesson, PassCriteria


def _lesson(lesson_id: str) -> Lesson:
    return Lesson(
        id=lesson_id,
        title={"en": lesson_id},
        type="keys",
        stages=["x"],
        criteria=PassCriteria(max_error_rate=0.1, min_wpm=None),
        reward_xp=10,
    )


def _course() -> Course:
    return Course(
        id="en",
        layout="qwerty",
        title={"en": "English"},
        benchmark_text="the quick brown fox",
        lessons=[_lesson("l1"), _lesson("l2"), _lesson("l3")],
    )


def test_first_lesson_always_unlocked():
    assert is_unlocked(_course(), "l1", completed_ids=set())


def test_second_lesson_locked_until_first_completed():
    course = _course()
    assert not is_unlocked(course, "l2", completed_ids=set())
    assert is_unlocked(course, "l2", completed_ids={"l1"})


def test_unknown_lesson_id_raises():
    with pytest.raises(KeyError):
        is_unlocked(_course(), "nope", completed_ids=set())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/domain/test_course.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'typer.domain.course'`.

- [ ] **Step 3: Write minimal implementation**

Create `src/typer/domain/course.py`:

```python
"""Course: an ordered list of lessons with linear unlocking."""

from __future__ import annotations

from dataclasses import dataclass

from typer.domain.lesson import Lesson


@dataclass(frozen=True)
class Course:
    """An ordered curriculum for one keyboard layout."""

    id: str
    layout: str
    title: dict[str, str]
    benchmark_text: str
    lessons: list[Lesson]


def is_unlocked(course: Course, lesson_id: str, completed_ids: set[str]) -> bool:
    """A lesson is unlocked if it is first, or its predecessor is completed.

    Raises:
        KeyError: if `lesson_id` is not in the course.
    """
    index = _index_of(course, lesson_id)
    if index == 0:
        return True
    return course.lessons[index - 1].id in completed_ids


def _index_of(course: Course, lesson_id: str) -> int:
    for i, lesson in enumerate(course.lessons):
        if lesson.id == lesson_id:
            return i
    raise KeyError(f"Lesson {lesson_id!r} not found in course {course.id!r}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/domain/test_course.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add src/typer/domain/course.py tests/domain/test_course.py
git commit -m "feat: add Course with linear unlock logic"
```

---

## Task 9: Progress and benchmark snapshots

**Files:**
- Create: `src/typer/domain/progress.py`
- Create: `tests/domain/test_progress.py`

- [ ] **Step 1: Write the failing test**

Create `tests/domain/test_progress.py`:

```python
from typer.domain.progress import BenchmarkSnapshot, Progress


def test_default_progress_is_empty():
    p = Progress()
    assert p.ui_locale == "en"
    assert p.total_xp == 0
    assert p.completed_lessons == []
    assert p.current_streak == 0
    assert p.last_active_date is None
    assert p.unlocked_achievements == []
    assert p.benchmarks == {}


def test_mark_completed_is_idempotent():
    p = Progress()
    p.mark_completed("l1")
    p.mark_completed("l1")
    assert p.completed_lessons == ["l1"]


def test_add_benchmark_appends_per_course():
    p = Progress()
    snap = BenchmarkSnapshot(date="2026-06-04", net_wpm=20.0, accuracy=0.9, errors=3)
    p.add_benchmark("en", snap)
    assert p.benchmarks["en"] == [snap]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/domain/test_progress.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'typer.domain.progress'`.

- [ ] **Step 3: Write minimal implementation**

Create `src/typer/domain/progress.py`:

```python
"""Persistent player progress."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BenchmarkSnapshot:
    """One before/after benchmark measurement."""

    date: str
    net_wpm: float
    accuracy: float
    errors: int


@dataclass
class Progress:
    """All saved state for the single local profile."""

    ui_locale: str = "en"
    total_xp: int = 0
    completed_lessons: list[str] = field(default_factory=list)
    last_active_date: str | None = None
    current_streak: int = 0
    unlocked_achievements: list[str] = field(default_factory=list)
    benchmarks: dict[str, list[BenchmarkSnapshot]] = field(default_factory=dict)

    def mark_completed(self, lesson_id: str) -> None:
        """Record a lesson as cleared (idempotent)."""
        if lesson_id not in self.completed_lessons:
            self.completed_lessons.append(lesson_id)

    def add_benchmark(self, course_id: str, snapshot: BenchmarkSnapshot) -> None:
        """Append a benchmark snapshot for a course."""
        self.benchmarks.setdefault(course_id, []).append(snapshot)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/domain/test_progress.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add src/typer/domain/progress.py tests/domain/test_progress.py
git commit -m "feat: add Progress and benchmark snapshots"
```

---

## Task 10: XP bonuses and player level

**Files:**
- Create: `src/typer/gamification/__init__.py` (empty)
- Create: `src/typer/gamification/xp.py`
- Create: `tests/gamification/__init__.py` (empty)
- Create: `tests/gamification/test_xp.py`

- [ ] **Step 1: Write the failing test**

Create `tests/gamification/test_xp.py`:

```python
from typer.gamification.xp import (
    accuracy_bonus,
    earned_xp,
    player_level,
    speed_bonus,
)


def test_accuracy_bonus_ranges():
    assert accuracy_bonus(0.80) == 1.0   # at or below 0.9 floor
    assert accuracy_bonus(0.90) == 1.0
    assert accuracy_bonus(1.00) == 1.5   # perfect
    assert accuracy_bonus(0.95) == 1.25  # halfway


def test_speed_bonus_requires_meeting_min():
    assert speed_bonus(net_wpm=20.0, min_wpm=25.0) == 1.0   # below min
    assert speed_bonus(net_wpm=25.0, min_wpm=25.0) == 1.0   # exactly min
    assert speed_bonus(net_wpm=37.5, min_wpm=25.0) == 1.3   # 50% over caps at 1.3
    assert speed_bonus(net_wpm=50.0, min_wpm=25.0) == 1.3   # beyond cap stays 1.3


def test_speed_bonus_neutral_when_no_min():
    assert speed_bonus(net_wpm=99.0, min_wpm=None) == 1.0


def test_earned_xp_first_clear_doubles():
    base = 100
    repeat = earned_xp(base, accuracy=0.9, net_wpm=10.0, min_wpm=None, first_clear=False)
    first = earned_xp(base, accuracy=0.9, net_wpm=10.0, min_wpm=None, first_clear=True)
    assert repeat == 100
    assert first == 200


def test_player_level_increases_with_xp():
    assert player_level(0) == 1
    assert player_level(99) == 1
    assert player_level(100) == 2          # first threshold base*1^1.5 = 100
    assert player_level(100 + 282) == 3    # + base*2^1.5 ≈ 282
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/gamification/test_xp.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'typer.gamification'`.

- [ ] **Step 3: Write minimal implementation**

Create empty `src/typer/gamification/__init__.py` and `tests/gamification/__init__.py`.

Create `src/typer/gamification/xp.py`:

```python
"""XP rewards and player-level curve.

Bonuses reward quality (accuracy, speed) and first clears, steering players
toward progressing through the course rather than grinding easy lessons.
"""

from __future__ import annotations

_ACCURACY_FLOOR = 0.9
_ACCURACY_MAX_BONUS = 0.5
_SPEED_CAP_RATIO = 0.5
_SPEED_MAX_BONUS = 0.3
_FIRST_CLEAR_MULTIPLIER = 2.0
_LEVEL_BASE = 100
_LEVEL_EXPONENT = 1.5


def accuracy_bonus(accuracy: float) -> float:
    """1.0 at/below 90% accuracy, scaling linearly to 1.5 at 100%."""
    if accuracy >= 1.0:
        return 1.0 + _ACCURACY_MAX_BONUS
    if accuracy <= _ACCURACY_FLOOR:
        return 1.0
    span = (accuracy - _ACCURACY_FLOOR) / (1.0 - _ACCURACY_FLOOR)
    return 1.0 + span * _ACCURACY_MAX_BONUS


def speed_bonus(net_wpm: float, min_wpm: float | None) -> float:
    """1.0 until `min_wpm` is met, scaling to 1.3 at 50% over the requirement."""
    if not min_wpm or net_wpm < min_wpm:
        return 1.0
    over = (net_wpm - min_wpm) / min_wpm
    span = min(over, _SPEED_CAP_RATIO) / _SPEED_CAP_RATIO
    return 1.0 + span * _SPEED_MAX_BONUS


def earned_xp(
    base: int,
    accuracy: float,
    net_wpm: float,
    min_wpm: float | None,
    first_clear: bool,
) -> int:
    """Total XP for a session, rounded to the nearest integer."""
    multiplier = accuracy_bonus(accuracy) * speed_bonus(net_wpm, min_wpm)
    if first_clear:
        multiplier *= _FIRST_CLEAR_MULTIPLIER
    return round(base * multiplier)


def player_level(total_xp: int, base: int = _LEVEL_BASE) -> int:
    """Player level from cumulative XP using a `base * level^1.5` curve."""
    level = 1
    spent = 0
    while True:
        needed = int(base * level**_LEVEL_EXPONENT)
        if total_xp < spent + needed:
            return level
        spent += needed
        level += 1
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/gamification/test_xp.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add src/typer/gamification/__init__.py src/typer/gamification/xp.py tests/gamification/__init__.py tests/gamification/test_xp.py
git commit -m "feat: add XP bonuses and player-level curve"
```

---

## Task 11: Streak logic

**Files:**
- Create: `src/typer/gamification/streaks.py`
- Create: `tests/gamification/test_streaks.py`

- [ ] **Step 1: Write the failing test**

Create `tests/gamification/test_streaks.py`:

```python
from datetime import date

from typer.gamification.streaks import update_streak


def test_first_ever_activity_starts_streak_at_one():
    streak, last = update_streak(current_streak=0, last_active=None, today=date(2026, 6, 4))
    assert streak == 1
    assert last == "2026-06-04"


def test_same_day_does_not_change_streak():
    streak, last = update_streak(
        current_streak=3, last_active="2026-06-04", today=date(2026, 6, 4)
    )
    assert streak == 3
    assert last == "2026-06-04"


def test_consecutive_day_increments_streak():
    streak, last = update_streak(
        current_streak=3, last_active="2026-06-04", today=date(2026, 6, 5)
    )
    assert streak == 4
    assert last == "2026-06-05"


def test_gap_resets_streak_to_one():
    streak, last = update_streak(
        current_streak=9, last_active="2026-06-04", today=date(2026, 6, 7)
    )
    assert streak == 1
    assert last == "2026-06-07"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/gamification/test_streaks.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'typer.gamification.streaks'`.

- [ ] **Step 3: Write minimal implementation**

Create `src/typer/gamification/streaks.py`:

```python
"""Calendar-day streak tracking. `today` is injected for determinism."""

from __future__ import annotations

from datetime import date


def update_streak(
    current_streak: int,
    last_active: str | None,
    today: date,
) -> tuple[int, str]:
    """Return the updated `(streak, last_active_iso)` for activity on `today`.

    Same day: unchanged. Next day: +1. Any larger gap: reset to 1.
    """
    today_iso = today.isoformat()
    if last_active is None:
        return 1, today_iso
    delta = (today - date.fromisoformat(last_active)).days
    if delta == 0:
        return current_streak, last_active
    if delta == 1:
        return current_streak + 1, today_iso
    return 1, today_iso
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/gamification/test_streaks.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add src/typer/gamification/streaks.py tests/gamification/test_streaks.py
git commit -m "feat: add calendar-day streak logic"
```

---

## Task 12: Achievements engine

**Files:**
- Create: `src/typer/gamification/achievements.py`
- Create: `tests/gamification/test_achievements.py`

- [ ] **Step 1: Write the failing test**

Create `tests/gamification/test_achievements.py`:

```python
from typer.gamification.achievements import Achievement, check, newly_unlocked


def _ach(ach_id: str, metric: str, op: str, value: float) -> Achievement:
    return Achievement(
        id=ach_id,
        title={"en": ach_id},
        desc={"en": ach_id},
        metric=metric,
        op=op,
        value=value,
    )


def test_check_equality_condition():
    flawless = _ach("flawless", "errors", "==", 0)
    assert check(flawless, {"errors": 0})
    assert not check(flawless, {"errors": 1})


def test_check_gte_condition():
    speed = _ach("speed", "net_wpm", ">=", 80)
    assert check(speed, {"net_wpm": 80})
    assert check(speed, {"net_wpm": 95})
    assert not check(speed, {"net_wpm": 79})


def test_missing_metric_is_not_unlocked():
    speed = _ach("speed", "net_wpm", ">=", 80)
    assert not check(speed, {"errors": 0})


def test_newly_unlocked_excludes_already_owned():
    flawless = _ach("flawless", "errors", "==", 0)
    speed = _ach("speed", "net_wpm", ">=", 80)
    achievements = [flawless, speed]
    context = {"errors": 0, "net_wpm": 90}
    result = newly_unlocked(achievements, context, already_unlocked={"flawless"})
    assert result == ["speed"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/gamification/test_achievements.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'typer.gamification.achievements'`.

- [ ] **Step 3: Write minimal implementation**

Create `src/typer/gamification/achievements.py`:

```python
"""Declarative achievement engine.

Each achievement is a `metric op value` condition checked against a context
dict built from session metrics and player progress.
"""

from __future__ import annotations

import operator
from collections.abc import Callable, Mapping
from dataclasses import dataclass

_OPS: dict[str, Callable[[float, float], bool]] = {
    "==": operator.eq,
    ">=": operator.ge,
    ">": operator.gt,
    "<=": operator.le,
    "<": operator.lt,
}


@dataclass(frozen=True)
class Achievement:
    """A single unlockable badge defined by a numeric condition."""

    id: str
    title: dict[str, str]
    desc: dict[str, str]
    metric: str
    op: str
    value: float


def check(achievement: Achievement, context: Mapping[str, float]) -> bool:
    """True if the achievement's condition holds for `context`.

    Raises:
        KeyError: if the achievement uses an unsupported operator.
    """
    if achievement.metric not in context:
        return False
    compare = _OPS[achievement.op]
    return compare(context[achievement.metric], achievement.value)


def newly_unlocked(
    achievements: list[Achievement],
    context: Mapping[str, float],
    already_unlocked: set[str],
) -> list[str]:
    """IDs of achievements whose condition now holds and weren't owned before."""
    return [
        a.id
        for a in achievements
        if a.id not in already_unlocked and check(a, context)
    ]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/gamification/test_achievements.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add src/typer/gamification/achievements.py tests/gamification/test_achievements.py
git commit -m "feat: add declarative achievements engine"
```

---

## Task 13: Localization

**Files:**
- Create: `src/typer/localization.py`
- Create: `tests/test_localization.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_localization.py`:

```python
import logging

from typer.localization import Translator, pick_locale


def test_pick_locale_returns_requested():
    field = {"ru": "Привет", "en": "Hello"}
    assert pick_locale(field, "ru") == "Привет"


def test_pick_locale_falls_back_to_english(caplog):
    field = {"en": "Hello"}
    with caplog.at_level(logging.WARNING):
        assert pick_locale(field, "ru") == "Hello"
    assert "ru" in caplog.text


def test_pick_locale_falls_back_to_any_when_no_english():
    field = {"de": "Hallo"}
    assert pick_locale(field, "ru") == "Hallo"


def test_translator_resolves_key():
    t = Translator(tables={"en": {"menu.start": "Start"}, "ru": {"menu.start": "Старт"}})
    assert t.t("menu.start", "ru") == "Старт"


def test_translator_missing_key_falls_back_to_english():
    t = Translator(tables={"en": {"menu.start": "Start"}, "ru": {}})
    assert t.t("menu.start", "ru") == "Start"


def test_translator_missing_everywhere_returns_key():
    t = Translator(tables={"en": {}})
    assert t.t("menu.unknown", "ru") == "menu.unknown"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_localization.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'typer.localization'`.

- [ ] **Step 3: Write minimal implementation**

Create `src/typer/localization.py`:

```python
"""Localization for content fields and UI strings.

Two axes, intentionally separate: typing language is a course property;
interface language is a profile setting. Missing translations fall back to
English with a logged warning rather than crashing.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

_FALLBACK = "en"
_logger = logging.getLogger(__name__)


def pick_locale(field: dict[str, str], locale: str, fallback: str = _FALLBACK) -> str:
    """Resolve a localized content field, falling back to English then any value."""
    if locale in field:
        return field[locale]
    _logger.warning("Missing %r translation; falling back to %r", locale, fallback)
    if fallback in field:
        return field[fallback]
    return next(iter(field.values()))


@dataclass(frozen=True)
class Translator:
    """Resolves UI string keys per locale with English fallback."""

    tables: dict[str, dict[str, str]]

    def t(self, key: str, locale: str) -> str:
        """Translate `key` for `locale`; fall back to English, then the key itself."""
        table = self.tables.get(locale, {})
        if key in table:
            return table[key]
        english = self.tables.get(_FALLBACK, {})
        if key in english:
            _logger.warning("Missing %r UI string for %r; using English", key, locale)
            return english[key]
        _logger.warning("Missing UI string %r entirely; using key", key)
        return key
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_localization.py -v`
Expected: PASS (6 passed).

- [ ] **Step 5: Commit**

```bash
git add src/typer/localization.py tests/test_localization.py
git commit -m "feat: add content and UI localization with English fallback"
```

---

## Task 14: Content loader

**Files:**
- Create: `src/typer/content_loader.py`
- Create: `tests/test_content_loader.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_content_loader.py`:

```python
import pytest

from typer.content_loader import ContentError, load_achievements, load_course

_COURSE_YAML = """
course:
  id: en
  layout: qwerty
  title:
    en: "Touch typing"
  benchmark_text: "the quick brown fox"
  lessons:
    - id: en-01
      title:
        en: "Home row"
      type: keys
      stages:
        - "fff jjj"
      pass:
        max_error_rate: 0.08
        min_wpm: null
      reward_xp: 50
    - id: en-02
      title:
        en: "Words"
      type: words
      stages:
        - { source: wordlist, count: 40 }
      pass:
        max_error_rate: 0.05
        min_wpm: 25
      reward_xp: 120
"""

_ACH_YAML = """
achievements:
  - id: flawless
    title:
      en: "Flawless"
    desc:
      en: "Zero typos"
    condition: { metric: errors, op: "==", value: 0 }
"""


def _write(tmp_path, name: str, text: str):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_load_course_parses_lessons(tmp_path):
    path = _write(tmp_path, "en.yaml", _COURSE_YAML)
    course = load_course(path)
    assert course.id == "en"
    assert course.benchmark_text == "the quick brown fox"
    assert [lesson.id for lesson in course.lessons] == ["en-01", "en-02"]
    assert course.lessons[0].criteria.max_error_rate == 0.08
    assert course.lessons[0].criteria.min_wpm is None
    assert course.lessons[1].criteria.min_wpm == 25


def test_load_achievements_parses_condition(tmp_path):
    path = _write(tmp_path, "achievements.yaml", _ACH_YAML)
    achievements = load_achievements(path)
    assert achievements[0].id == "flawless"
    assert achievements[0].metric == "errors"
    assert achievements[0].op == "=="
    assert achievements[0].value == 0


def test_malformed_course_raises_content_error(tmp_path):
    path = _write(tmp_path, "bad.yaml", "course:\n  id: en\n")  # missing lessons
    with pytest.raises(ContentError) as exc:
        load_course(path)
    assert "bad.yaml" in str(exc.value)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_content_loader.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'typer.content_loader'`.

- [ ] **Step 3: Write minimal implementation**

Create `src/typer/content_loader.py`:

```python
"""Parse YAML content (courses, achievements) into domain objects.

Fails fast with a `ContentError` naming the file when data is malformed,
rather than silently skipping content.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from typer.domain.course import Course
from typer.domain.lesson import Lesson, PassCriteria
from typer.gamification.achievements import Achievement


class ContentError(Exception):
    """Raised when a content file is missing required structure."""


def _load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ContentError(f"Cannot read content file {path}: {exc}") from exc


def _require(data: dict[str, Any], key: str, path: Path) -> Any:
    if not isinstance(data, dict) or key not in data:
        raise ContentError(f"{path}: missing required key {key!r}")
    return data[key]


def load_course(path: Path) -> Course:
    """Parse a course YAML file into a `Course`."""
    root = _require(_load_yaml(path), "course", path)
    lessons = [_parse_lesson(raw, path) for raw in _require(root, "lessons", path)]
    return Course(
        id=_require(root, "id", path),
        layout=_require(root, "layout", path),
        title=_require(root, "title", path),
        benchmark_text=_require(root, "benchmark_text", path),
        lessons=lessons,
    )


def _parse_lesson(raw: dict[str, Any], path: Path) -> Lesson:
    criteria_raw = _require(raw, "pass", path)
    return Lesson(
        id=_require(raw, "id", path),
        title=_require(raw, "title", path),
        type=_require(raw, "type", path),
        stages=_require(raw, "stages", path),
        criteria=PassCriteria(
            max_error_rate=_require(criteria_raw, "max_error_rate", path),
            min_wpm=criteria_raw.get("min_wpm"),
        ),
        reward_xp=_require(raw, "reward_xp", path),
    )


def load_achievements(path: Path) -> list[Achievement]:
    """Parse an achievements YAML file into `Achievement` objects."""
    items = _require(_load_yaml(path), "achievements", path)
    return [_parse_achievement(raw, path) for raw in items]


def _parse_achievement(raw: dict[str, Any], path: Path) -> Achievement:
    condition = _require(raw, "condition", path)
    return Achievement(
        id=_require(raw, "id", path),
        title=_require(raw, "title", path),
        desc=_require(raw, "desc", path),
        metric=_require(condition, "metric", path),
        op=_require(condition, "op", path),
        value=_require(condition, "value", path),
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_content_loader.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add src/typer/content_loader.py tests/test_content_loader.py
git commit -m "feat: add YAML content loader for courses and achievements"
```

---

## Task 15: Persistence with atomic write and corrupt recovery

**Files:**
- Create: `src/typer/persistence/__init__.py` (empty)
- Create: `src/typer/persistence/store.py`
- Create: `tests/persistence/__init__.py` (empty)
- Create: `tests/persistence/test_store.py`

- [ ] **Step 1: Write the failing test**

Create `tests/persistence/test_store.py`:

```python
from typer.domain.progress import BenchmarkSnapshot, Progress
from typer.persistence.store import load_progress, save_progress


def test_round_trip_preserves_progress(tmp_path):
    path = tmp_path / "profile.json"
    original = Progress(ui_locale="ru", total_xp=350, current_streak=4)
    original.mark_completed("en-01")
    original.add_benchmark("en", BenchmarkSnapshot("2026-06-04", 22.0, 0.95, 2))

    save_progress(path, original)
    loaded = load_progress(path)

    assert loaded.ui_locale == "ru"
    assert loaded.total_xp == 350
    assert loaded.current_streak == 4
    assert loaded.completed_lessons == ["en-01"]
    assert loaded.benchmarks["en"][0] == BenchmarkSnapshot("2026-06-04", 22.0, 0.95, 2)


def test_missing_file_returns_default_progress(tmp_path):
    loaded = load_progress(tmp_path / "nope.json")
    assert loaded == Progress()


def test_corrupt_file_is_backed_up_and_reset(tmp_path):
    path = tmp_path / "profile.json"
    path.write_text("{not valid json", encoding="utf-8")

    loaded = load_progress(path)

    assert loaded == Progress()
    backups = list(tmp_path.glob("profile.json.corrupt-*"))
    assert len(backups) == 1


def test_save_is_atomic_no_temp_left_behind(tmp_path):
    path = tmp_path / "profile.json"
    save_progress(path, Progress(total_xp=10))
    leftovers = [p for p in tmp_path.iterdir() if p.name != "profile.json"]
    assert leftovers == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/persistence/test_store.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'typer.persistence'`.

- [ ] **Step 3: Write minimal implementation**

Create empty `src/typer/persistence/__init__.py` and `tests/persistence/__init__.py`.

Create `src/typer/persistence/store.py`:

```python
"""Atomic JSON persistence for the single local profile.

Writes go through a temp file + `os.replace` so an interrupted save never
leaves a half-written profile. A corrupt profile is backed up (not deleted)
and replaced with a fresh one, so progress is never silently lost.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import asdict
from pathlib import Path

from typer.domain.progress import BenchmarkSnapshot, Progress

_logger = logging.getLogger(__name__)


def save_progress(path: Path, progress: Progress) -> None:
    """Atomically write `progress` to `path` as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(asdict(progress), ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def load_progress(path: Path) -> Progress:
    """Load progress from `path`, returning a default on missing/corrupt files."""
    if not path.exists():
        return Progress()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return _from_dict(data)
    except (json.JSONDecodeError, TypeError, KeyError) as exc:
        _logger.warning("Corrupt profile at %s (%s); backing up and resetting", path, exc)
        _backup_corrupt(path)
        return Progress()


def _from_dict(data: dict) -> Progress:
    benchmarks = {
        course_id: [BenchmarkSnapshot(**snap) for snap in snaps]
        for course_id, snaps in data.get("benchmarks", {}).items()
    }
    return Progress(
        ui_locale=data["ui_locale"],
        total_xp=data["total_xp"],
        completed_lessons=list(data["completed_lessons"]),
        last_active_date=data["last_active_date"],
        current_streak=data["current_streak"],
        unlocked_achievements=list(data["unlocked_achievements"]),
        benchmarks=benchmarks,
    )


def _backup_corrupt(path: Path) -> None:
    backup = path.with_name(f"{path.name}.corrupt-{int(time.time())}")
    path.replace(backup)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/persistence/test_store.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add src/typer/persistence/__init__.py src/typer/persistence/store.py tests/persistence/__init__.py tests/persistence/test_store.py
git commit -m "feat: add atomic profile persistence with corrupt recovery"
```

---

## Task 16: Headless play runner

**Files:**
- Create: `src/typer/play.py`
- Create: `tests/test_play.py`

This ties the engine and domain together: feed a target + keystrokes, get back metrics and a lesson result. It is the seam the TUI (Plan 2) will call, and proves the whole core works without a terminal.

- [ ] **Step 1: Write the failing test**

Create `tests/test_play.py`:

```python
from typer.domain.lesson import Lesson, PassCriteria
from typer.engine.keystroke import Keystroke, KeystrokeKind
from typer.play import run_lesson


def _chars(text: str) -> list[Keystroke]:
    return [
        Keystroke(kind=KeystrokeKind.CHAR, char=c, timestamp=float(i))
        for i, c in enumerate(text)
    ]


def _lesson(min_wpm: float | None) -> Lesson:
    return Lesson(
        id="en-01",
        title={"en": "Home row"},
        type="keys",
        stages=["fj"],
        criteria=PassCriteria(max_error_rate=0.1, min_wpm=min_wpm),
        reward_xp=50,
    )


def test_run_lesson_returns_metrics_and_result():
    outcome = run_lesson(target="fj", lesson=_lesson(min_wpm=None), keystrokes=_chars("fj"))
    assert outcome.metrics.errors == 0
    assert outcome.result.passed


def test_run_lesson_flags_failure_on_errors():
    outcome = run_lesson(target="fj", lesson=_lesson(min_wpm=None), keystrokes=_chars("xj"))
    assert outcome.metrics.errors == 1
    assert not outcome.result.passed  # 1/2 = 50% error rate > 10%


def test_run_lesson_speed_gate_fails_when_too_slow():
    # Two chars one second apart => very low WPM, below a 25 wpm gate.
    slow = [
        Keystroke(kind=KeystrokeKind.CHAR, char="f", timestamp=0.0),
        Keystroke(kind=KeystrokeKind.CHAR, char="j", timestamp=60.0),
    ]
    outcome = run_lesson(target="fj", lesson=_lesson(min_wpm=25.0), keystrokes=slow)
    assert outcome.metrics.errors == 0
    assert not outcome.result.passed
    assert not outcome.result.met_speed
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_play.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'typer.play'`.

- [ ] **Step 3: Write minimal implementation**

Create `src/typer/play.py`:

```python
"""Headless runner that drives one typing attempt end to end.

This is the boundary the TUI calls: it owns no terminal logic, only the
engine + domain wiring, so the full loop is unit-testable.
"""

from __future__ import annotations

from dataclasses import dataclass

from typer.domain.lesson import Lesson, LessonResult, evaluate
from typer.engine.keystroke import Keystroke
from typer.engine.metrics import SessionMetrics, compute_metrics
from typer.engine.session import TypingSession


@dataclass(frozen=True)
class LessonOutcome:
    """Metrics plus pass/fail for one completed attempt."""

    metrics: SessionMetrics
    result: LessonResult


def run_lesson(target: str, lesson: Lesson, keystrokes: list[Keystroke]) -> LessonOutcome:
    """Replay `keystrokes` against `target` and evaluate against `lesson`."""
    session = TypingSession(target=target)
    for keystroke in keystrokes:
        session.apply(keystroke)
    metrics = compute_metrics(session)
    result = evaluate(lesson.criteria, metrics)
    return LessonOutcome(metrics=metrics, result=result)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_play.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Run the full suite and linters**

Run: `uv run pytest && uv run ruff check . && uv run ruff format --check .`
Expected: all tests pass; ruff reports no issues.

- [ ] **Step 6: Commit**

```bash
git add src/typer/play.py tests/test_play.py
git commit -m "feat: add headless lesson runner wiring engine and domain"
```

---

## Definition of Done (Plan 1)

- `uv run pytest` is green across all modules.
- `uv run ruff check .` and `uv run ruff format --check .` are clean.
- The full loop "keystrokes → metrics → lesson result" runs headlessly via
  `run_lesson` with no terminal involved.
- XP, streaks, achievements, localization, content loading, and persistence are
  each unit-tested including edge/error paths (empty input, exact thresholds,
  streak gaps, missing translations, corrupt profile).

## Deferred to later plans

- **Plan 2 (TUI):** Textual app, screens (menu/lesson/results/progress/
  achievements), `TypingView` widget, paste/Esc handling, sparkline charts,
  wiring `run_lesson` to live keystrokes, applying XP/streak/achievement updates
  to `Progress` and saving via `persistence`.
- **Plan 3 (Content & balance):** ru/en course YAML, wordlists/corpora,
  achievement set, benchmark wiring (baseline/intermediate/final sessions),
  tuning of XP and level-curve coefficients.

## Notes on items intentionally NOT in Plan 1

- **Benchmark session orchestration** (when to offer baseline/final) is UI flow —
  it belongs in Plan 2. Plan 1 already provides the data type
  (`BenchmarkSnapshot`) and storage (`Progress.add_benchmark`).
- **Stage generators** (`wordlist`/`corpus`) parse into `Lesson.stages` as raw
  specs here; turning them into concrete practice text is Plan 3 content work.
