# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`typehero` is a console touch-typing trainer with gamification (think "Соло на клавиатуре"): a course of linearly-unlocked lessons, each gated on typing speed and error rate, with XP, levels, achievements, streaks, and combos. The design spec lives in `docs/superpowers/specs/` (gitignored — internal planning, not shipped).

The current branch implements the **core engine + domain + gamification + persistence + a Textual TUI**. Course/achievement/i18n YAML lives under `src/typehero/content/` and ships inside the wheel. Generator stages (`wordlist`/`corpus`) from the spec are **not built yet** — `stage_text` only accepts literal string stages.

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
uv run typehero                 # launch the TUI (also `python -m typehero`)
```

Property-based tests use `hypothesis`; its database is in `.hypothesis/`.

## Architecture

Dependencies flow one direction: **tui → gamification → domain → engine**. Inner layers (`engine`, `domain`, `gamification`) never import outer ones, know nothing about the terminal, and take time as injected data — so the whole core is deterministic and unit-testable without a TUI.

- **`engine/`** — pure typing logic, no I/O, no wall-clock.
  - `keystroke.py` — `Keystroke(kind, char, timestamp)`. Timestamps are *supplied by the caller*, never read from a clock. `__post_init__` enforces the char/backspace invariant.
  - `session.py` — `TypingSession` mutates state as keystrokes are applied. Counts every error keystroke (even ones later backspaced) so accuracy can't be gamed; normalizes target to Unicode NFC; tracks combo.
  - `metrics.py` — derives `SessionMetrics` (WPM via 5-chars-per-word convention, accuracy, combo). Elapsed time = first→last char keystroke; sessions under 2 keystrokes report 0.
- **`domain/`** — `Lesson` (`type` is a `LessonType` enum, not a free string) + `PassCriteria` (`evaluate` requires BOTH accuracy and speed; `min_wpm` is `None` or strictly positive), `LessonResult` (`passed` is a computed property over `met_accuracy`/`met_speed`), `Course` (`is_unlocked` = first lesson or predecessor completed), `Progress` (the full saved profile), `benchmark.py` (`snapshot_from_metrics`).
- **`gamification/`** — `xp.py` (quality/first-clear multipliers, `base*level^1.5` level curve), `achievements.py` (declarative `metric op value` engine over an allowlisted set of operators), `streaks.py` (calendar-day, `today` injected), `context.py` (builds the flat metric dict achievements are checked against).
- **`persistence/store.py`** — atomic JSON profile save (temp file + `os.replace`); a corrupt profile is **backed up, not deleted**, and replaced with a fresh one.
- **`content_loader.py`** — parses course/achievement YAML into domain objects; fails fast with `ContentError` naming the file and the missing/invalid key (unknown `LessonType`, non-numeric achievement value, etc.).
- **`localization.py`** — two independent axes: typing language (course property) vs. UI language (profile setting). Missing translations log a warning and fall back to English, then to any available value.
- **`paths.py`** — `content_dir()` resolves the bundled `content/` via `importlib.resources` (overridable with `TYPEHERO_CONTENT_DIR`); `profile_path()` honours `XDG_CONFIG_HOME`.
- **`play.py`** — `run_lesson()`: the headless boundary the TUI calls. Wires engine + domain so the full attempt loop is testable end-to-end.
- **`tui/`** — Textual layer. `app.py` (`TypeHeroApp`, `build_app`, and `main()` which converts a startup `ContentError`/`OSError` into a clean stderr message + exit 1), `state.py` (`AppState`: loaded content + mutable profile + injected `clock`/`today`; fails fast if no course loads), and `screens/` (each extends `AppScreen` for typed `app_state` access and `save_profile`, and exposes a pure, unit-tested view-model method). `widgets/typing_view.py` captures live keystrokes (paste blocked) and posts a `Finished` message carrying both the keystrokes and the applied session.

## Conventions specific to this codebase

- **Inject time and other ambient state** — pass `timestamp` / `today` as arguments; never call a clock inside `engine`/`domain`/`gamification`. Tests rely on this.
- **Count errors at keystroke time**, including corrected ones — this is deliberate (see `TypingSession` docstring), don't "fix" it to count only final-state errors.
- **Fail fast with context** — loaders raise errors naming the file/key; data corruption is preserved (backed up), never silently dropped.
- **Surface failures to the user, not just the log** — under Textual, stderr is captured, so `logging` alone is invisible to the player. User-relevant events go to a toast: save failures via `AppScreen.save_profile`, a reset of a corrupt profile via `AppState.startup_notices` shown on mount. The inner layer stays decoupled (`load_progress` takes an `on_corrupt` callback rather than importing the TUI).
- Frozen dataclasses for value types; mutable dataclass only for `TypingSession`, `Progress`, and `AppState` (the things that genuinely change).
- Tests mirror `src/typehero/` package structure under `tests/`; TUI screens are tested through their pure view-model methods plus a Textual `Pilot` integration test, with `clock`/`today` injected.

See the user's global standards (in `~/.claude/CLAUDE.md`) for the broader tooling and style rules this project follows (uv/ruff/ty, 100-line functions, absolute imports, no relative paths).
