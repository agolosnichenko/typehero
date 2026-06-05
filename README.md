```
████████╗██╗   ██╗██████╗ ███████╗██╗  ██╗███████╗██████╗  ██████╗
╚══██╔══╝╚██╗ ██╔╝██╔══██╗██╔════╝██║  ██║██╔════╝██╔══██╗██╔═══██╗
   ██║    ╚████╔╝ ██████╔╝█████╗  ███████║█████╗  ██████╔╝██║   ██║
   ██║     ╚██╔╝  ██╔═══╝ ██╔══╝  ██╔══██║██╔══╝  ██╔══██╗██║   ██║
   ██║      ██║   ██║     ███████╗██║  ██║███████╗██║  ██║╚██████╔╝
   ╚═╝      ╚═╝   ╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝
```

<p align="center">
  <a href="https://pypi.org/project/typehero/"><img alt="PyPI" src="https://img.shields.io/pypi/v/typehero?color=2dd4bf&label=pypi"></a>
  <a href="https://pypi.org/project/typehero/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/typehero?color=2dd4bf"></a>
  <a href="./LICENSE"><img alt="License: MIT" src="https://img.shields.io/pypi/l/typehero?color=2dd4bf"></a>
  <a href="https://textual.textualize.io/"><img alt="Built with Textual" src="https://img.shields.io/badge/TUI-Textual-5f5fff"></a>
</p>

<p align="center"><b>A touch-typing trainer that lives in your terminal — a typing course turned into a game you actually want to finish.</b></p>

Work through a course of lessons, one unlocking the next. Each lesson is gated on **speed** and **accuracy**, so you can't sprint past the basics — you earn your way forward. Along the way you rack up **XP**, climb **levels**, chase **achievements**, keep a daily **streak** alive, and build **combos** for every key you hit without a typo.

The trainer ships with full **English and Russian** courses. Your typing language and your menu language are independent — practise Russian text with an English interface, or the other way round.

## Quick start

You'll need **Python 3.13+**. The fastest way in — no install, no cleanup:

```bash
uvx typehero
```

That downloads and runs the latest version in a throwaway environment. ([uv](https://docs.astral.sh/uv/) is a tiny, fast Python tool runner — `brew install uv` or see their site.)

Want it to stick around as a real command on your `PATH`?

```bash
uv tool install typehero    # or: pipx install typehero
typehero                    # then just type this anytime
```

Prefer plain pip into an existing environment? `pip install typehero` works too — everything it needs (the courses, the interface) comes bundled in.

## How to play

1. **Pick a lesson.** The menu is your dashboard: completed lessons are marked, locked ones are greyed out until you clear the one before.
2. **Take the benchmark (optional but recommended).** Before your first lesson, typehero offers a short speed test so it knows where you're starting from. Press **`b`** anytime to retake it.
3. **Type the text in front of you.** Live stats show your speed, accuracy, and current combo as you go. Pasting is blocked — this is about your fingers, not your clipboard.
4. **Beat the bar.** Clear a lesson by hitting both its target speed **and** its accuracy threshold. Miss either one and you can retry as many times as you like.
5. **Watch the numbers climb.** Every clear awards XP (more for clean, fast, first-time runs), pushes your level, and may unlock an achievement.

### Keys on the menu

| Key | What it does                                   |
| --- | ---------------------------------------------- |
| `b` | Take or retake the speed **b**enchmark         |
| `p` | View your **p**rogress — level, XP, stats      |
| `a` | Browse **a**chievements, locked and unlocked   |
| `s` | **S**ettings — switch course or menu language  |
| `q` | **Q**uit                                       |

## What you're chasing

- **20 achievements** across four themes — speed milestones (40 → 100 WPM), accuracy (95% → flawless), combos (25 → 100 keys in a row), and streaks (3 → 30 days).
- **Levels & XP** on a rising curve, so each level takes a little more than the last.
- **Daily streaks** that count calendar days — show up every day to keep the chain.
- **Combos** that build with every correct key and reset the moment you slip.

## Your save file

Your profile lives as a small JSON file under `$XDG_CONFIG_HOME` (or your platform's default config folder). It's yours — back it up, move it between machines, peek inside. If it ever gets corrupted, typehero backs up the broken copy rather than throwing it away, then starts you a fresh one.

## License

[MIT](./LICENSE). Free to use, free to fork.

---

<sub>Curious how it's built, or want to contribute? The architecture, conventions, and development workflow are documented in <a href="./CLAUDE.md">CLAUDE.md</a>.</sub>
