from datetime import date

from typehero.domain.course import Course
from typehero.domain.lesson import Lesson, PassCriteria
from typehero.domain.progress import Progress
from typehero.localization import Translator
from typehero.tui.app import TypeHeroApp
from typehero.tui.screens.lesson import LessonScreen
from typehero.tui.screens.menu import MenuScreen
from typehero.tui.screens.results import ResultsScreen
from typehero.tui.state import AppState


def _lesson() -> Lesson:
    return Lesson(
        id="en-01",
        title={"en": "Home row"},
        type="keys",
        stages=["fj"],
        criteria=PassCriteria(max_error_rate=0.1, min_wpm=None),
        reward_xp=100,
    )


class _Clock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        self.t += 1.0
        return self.t


def _app(tmp_path) -> TypeHeroApp:
    # The menu mounts under every pushed screen, so it needs a real "en" course.
    course = Course(
        id="en", layout="qwerty", title={"en": "English"}, benchmark_text="fj", lessons=[_lesson()]
    )
    state = AppState(
        courses={"en": course},
        achievements=[],
        translator=Translator(tables={"en": {}}),
        progress=Progress(),
        profile_file=tmp_path / "profile.json",
        today=date(2026, 6, 4),
        clock=_Clock(),
    )
    return TypeHeroApp(state)


async def test_finishing_a_lesson_awards_xp_saves_and_shows_results(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await app.push_screen(LessonScreen(course_id="en", lesson=_lesson()))
        await pilot.pause()
        await pilot.press("f", "j")
        await pilot.pause()
        assert isinstance(app.screen, ResultsScreen)
        assert app.state.progress.total_xp == 300  # 100 base * 1.5 accuracy * 2.0 first-clear
        assert app.state.progress.completed_lessons == ["en-01"]
        assert (tmp_path / "profile.json").exists()  # saved


async def test_escape_abandons_the_lesson_back_to_menu(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await app.push_screen(LessonScreen(course_id="en", lesson=_lesson()))
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, MenuScreen)
        assert app.state.progress.total_xp == 0  # nothing awarded on abandon
