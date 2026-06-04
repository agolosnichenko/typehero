# typehero

A console touch-typing trainer with gamification — think "Соло на клавиатуре" in your
terminal. Work through a course of linearly-unlocked lessons, each gated on typing speed
and error rate, and earn XP, levels, achievements, streaks, and combos along the way.

The trainer ships with full English and Russian courses; the typing language (a course
property) and the UI language (a profile setting) are independent.

## Install & run

The project is managed with [uv](https://docs.astral.sh/uv/).

```bash
uv sync            # create .venv and install runtime + dev dependencies
uv run typehero    # launch the TUI (equivalent to `python -m typehero`)
```

Your profile is stored as JSON under `$XDG_CONFIG_HOME` (falling back to the platform
default). A corrupt profile is backed up rather than deleted, then replaced with a fresh
one.

## Development

```bash
uv run pytest                  # run all tests (-q is configured by default)
uv run pytest -k streak        # tests matching a keyword
uv run ruff check              # lint (E, F, I, UP, B, SIM)
uv run ruff format             # format (100-char lines)
uv run ty check                # static type check
```

Property-based tests use [hypothesis](https://hypothesis.readthedocs.io/); its database
lives in `.hypothesis/`.

## Architecture

Dependencies flow one direction: **tui → gamification → domain → engine**. The inner
layers never import outer ones, know nothing about the terminal, and take time as injected
data — so the whole core is deterministic and unit-testable without a TUI.

| Layer            | Responsibility                                                                 |
| ---------------- | ------------------------------------------------------------------------------ |
| `engine/`        | Pure typing logic — keystrokes, session state, derived metrics. No I/O, no clock. |
| `domain/`        | Lessons, pass criteria, results, course unlocking, saved progress, generators. |
| `gamification/`  | XP curve, declarative achievements, calendar-day streaks, combo tracking.      |
| `persistence/`   | Atomic JSON profile save (temp file + `os.replace`).                           |
| `tui/`           | The [Textual](https://textual.textualize.io/) layer — app, screens, widgets.   |

A key convention: **time and other ambient state are injected** (`timestamp`, `today`),
never read from a clock inside the core. See [CLAUDE.md](./CLAUDE.md) for the full set of
codebase conventions.

Course, achievement, and i18n YAML lives under `src/typehero/content/` and ships inside
the wheel.

## Releases

This repository uses [Conventional Commits](https://www.conventionalcommits.org/) and
automated releases:

- **CI** (`.github/workflows/ci.yml`) runs `ruff check`, `ruff format --check`,
  `ty check`, and `pytest` on every pull request and on pushes to `main`.
- **release-please** (`.github/workflows/release-please.yml`) reads `feat:` / `fix:`
  commits on `main`, opens a release pull request that bumps the version in
  `pyproject.toml` and updates `CHANGELOG.md`, and tags a GitHub Release when that pull
  request is merged.
- **Publish** (`.github/workflows/publish.yml`) runs when a GitHub Release is published,
  builds the wheel and sdist with `uv build`, and uploads them to PyPI via Trusted
  Publishing (OIDC) — no API token is stored. The job runs in the `pypi` environment.
- **Dependabot** (`.github/dependabot.yml`) proposes weekly, grouped minor/patch updates
  for Python dependencies (`uv`) and GitHub Actions, with a 7-day cooldown. Major bumps
  are not opened automatically.

Commit type → changelog section: `feat` (Features), `fix` (Bug Fixes), `perf`
(Performance), `refactor` (Refactoring), `docs` (Documentation).
