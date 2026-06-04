from datetime import date

from typehero.domain.course import Course
from typehero.domain.progress import Progress
from typehero.localization import Translator
from typehero.tui.app import TypeHeroApp
from typehero.tui.screens.benchmark import BenchmarkScreen
from typehero.tui.state import AppState


class _Clock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        self.t += 1.0
        return self.t


def _course() -> Course:
    return Course(
        id="en", layout="qwerty", title={"en": "English"}, benchmark_text="fj", lessons=[]
    )


def _app(tmp_path) -> TypeHeroApp:
    state = AppState(
        courses={"en": _course()},
        achievements=[],
        translator=Translator(tables={"en": {}}),
        progress=Progress(),
        profile_file=tmp_path / "profile.json",
        today=date(2026, 6, 4),
        clock=_Clock(),
    )
    return TypeHeroApp(state)


async def test_benchmark_records_snapshot_without_xp_or_streak(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await app.push_screen(BenchmarkScreen(course_id="en"))
        await pilot.pause()
        await pilot.press("f", "j")
        await pilot.pause()
        progress = app.state.progress
        assert len(progress.benchmarks["en"]) == 1
        snap = progress.benchmarks["en"][0]
        assert snap.date == "2026-06-04"
        assert progress.total_xp == 0  # no XP
        assert progress.current_streak == 0  # streak untouched
        assert (tmp_path / "profile.json").exists()
