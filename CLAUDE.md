# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`typer` is a console touch-typing trainer with gamification (think "Соло на клавиатуре"): a course of linearly-unlocked lessons, each gated on typing speed and error rate, with XP, levels, achievements, streaks, and combos. The design spec lives in `docs/superpowers/specs/` (gitignored — internal planning, not shipped).

The current branch implements the **core engine + domain + gamification + persistence** only. The `tui/` (Textual) and `content/` (YAML course data) layers from the spec **do not exist yet** — do not assume them.

## Commands

```bash
uv sync                         # install deps + dev group into .venv
uv run pytest                   # run all tests (-q is configured by default)
uv run pytest tests/engine/test_session.py        # one file
uv run pytest tests/engine/test_session.py::test_name   # one test
uv run pytest -k "streak"       # tests matching a keyword
uv run ruff check               # lint (E, F, I, UP, B, SIM)
uv run ruff format              # format (100-char lines)
uv run ty check                 # static type check
```

Property-based tests use `hypothesis`; its database is in `.hypothesis/`.

## Architecture

Dependencies flow one direction: **adapters → gamification → domain → engine**. Inner layers (`engine`, `domain`) never import outer ones, know nothing about the terminal, and take time as injected data — so the whole core is deterministic and unit-testable without a TUI.

- **`engine/`** — pure typing logic, no I/O, no wall-clock.
  - `keystroke.py` — `Keystroke(kind, char, timestamp)`. Timestamps are *supplied by the caller*, never read from a clock. `__post_init__` enforces the char/backspace invariant.
  - `session.py` — `TypingSession` mutates state as keystrokes are applied. Counts every error keystroke (even ones later backspaced) so accuracy can't be gamed; normalizes target to Unicode NFC; tracks combo.
  - `metrics.py` — derives `SessionMetrics` (WPM via 5-chars-per-word convention, accuracy, combo). Elapsed time = first→last char keystroke; sessions under 2 keystrokes report 0.
- **`domain/`** — `Lesson` + `PassCriteria` (`evaluate` requires BOTH accuracy and speed), `Course` (`is_unlocked` = first lesson or predecessor completed), `Progress` (the full saved profile).
- **`gamification/`** — `xp.py` (quality/first-clear multipliers, `base*level^1.5` level curve), `achievements.py` (declarative `metric op value` engine over an allowlisted set of operators), `streaks.py` (calendar-day, `today` injected), `context.py` (builds the flat metric dict achievements are checked against).
- **`persistence/store.py`** — atomic JSON profile save (temp file + `os.replace`); a corrupt profile is **backed up, not deleted**, and replaced with a fresh one.
- **`content_loader.py`** — parses course/achievement YAML into domain objects; fails fast with `ContentError` naming the file and missing key.
- **`localization.py`** — two independent axes: typing language (course property) vs. UI language (profile setting). Missing translations log a warning and fall back to English, then to any available value.
- **`play.py`** — `run_lesson()`: the headless boundary the future TUI will call. Wires engine + domain so the full attempt loop is testable end-to-end.

## Conventions specific to this codebase

- **Inject time and other ambient state** — pass `timestamp` / `today` as arguments; never call a clock inside `engine`/`domain`/`gamification`. Tests rely on this.
- **Count errors at keystroke time**, including corrected ones — this is deliberate (see `TypingSession` docstring), don't "fix" it to count only final-state errors.
- **Fail fast with context** — loaders raise errors naming the file/key; data corruption is preserved (backed up), never silently dropped.
- Frozen dataclasses for value types; mutable dataclass only for `TypingSession` and `Progress` (the things that genuinely change).
- Tests mirror `src/typer/` package structure under `tests/`.

See the user's global standards (in `~/.claude/CLAUDE.md`) for the broader tooling and style rules this project follows (uv/ruff/ty, 100-line functions, absolute imports, no relative paths).
