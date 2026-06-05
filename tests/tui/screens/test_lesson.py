import random
from datetime import date

from typehero.domain.course import Course
from typehero.domain.generators import CourseResources
from typehero.domain.ids import CourseId
from typehero.domain.lesson import Lesson, LessonType, PassCriteria
from typehero.domain.progress import Progress
from typehero.localization import Translator
from typehero.tui.app import TypeHeroApp
from typehero.tui.keyboard_layout import QWERTY
from typehero.tui.screens.benchmark import BenchmarkScreen
from typehero.tui.screens.lesson import LessonScreen
from typehero.tui.screens.menu import MenuScreen
from typehero.tui.screens.results import ResultsScreen
from typehero.tui.state import AppState
from typehero.tui.widgets.finger_map import FingerMap


def _lesson(min_wpm: float | None = None) -> Lesson:
    return Lesson(
        id="en-01",
        title={"en": "Home row"},
        type=LessonType.KEYS,
        stages=["fj"],
        criteria=PassCriteria(max_error_rate=0.1, min_wpm=min_wpm),
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
        id=CourseId("en"),
        layout="qwerty",
        title={"en": "English"},
        benchmark_text="fj",
        lessons=[_lesson()],
    )
    state = AppState(
        courses={CourseId("en"): course},
        achievements=[],
        translator=Translator(tables={"en": {}}),
        progress=Progress(),
        profile_file=tmp_path / "profile.json",
        today=date(2026, 6, 4),
        clock=_Clock(),
        resources={CourseId("en"): CourseResources(wordlist=(), corpora={})},
        rng=random.Random(0),
    )
    return TypeHeroApp(state)


async def test_finishing_a_lesson_awards_xp_saves_and_shows_results(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await app.push_screen(LessonScreen(course_id=CourseId("en"), lesson=_lesson()))
        await pilot.pause()
        await pilot.press("f", "j")
        await pilot.pause()
        assert isinstance(app.screen, ResultsScreen)
        assert app.state.progress.total_xp == 300  # 100 base * 1.5 accuracy * 2.0 first-clear
        assert app.state.progress.completed_lessons == ["en-01"]
        assert (tmp_path / "profile.json").exists()  # saved


async def test_failing_a_lesson_awards_no_xp_but_still_saves_and_counts_streak(tmp_path):
    # The slow _Clock makes "fj" finish well under min_wpm, so the attempt
    # is accurate but too slow: a failed clear — the most common real outcome.
    failing = _lesson(min_wpm=120.0)
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await app.push_screen(LessonScreen(course_id=CourseId("en"), lesson=failing))
        await pilot.pause()
        await pilot.press("f", "j")
        await pilot.pause()
        assert isinstance(app.screen, ResultsScreen)
        assert app.state.progress.total_xp == 0
        assert app.state.progress.completed_lessons == []
        assert app.state.progress.current_streak == 1  # any finished attempt counts
        assert (tmp_path / "profile.json").exists()  # saved even on a fail


async def test_escape_abandons_the_lesson_back_to_menu(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await app.push_screen(LessonScreen(course_id=CourseId("en"), lesson=_lesson()))
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, MenuScreen)
        assert app.state.progress.total_xp == 0  # nothing awarded on abandon


async def test_completing_last_lesson_then_continue_runs_final_benchmark(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await app.push_screen(LessonScreen(course_id=CourseId("en"), lesson=_lesson()))
        await pilot.pause()
        await pilot.press("f", "j")
        await pilot.pause()
        assert isinstance(app.screen, ResultsScreen)
        await pilot.press("enter")  # Continue
        await pilot.pause()
        assert isinstance(app.screen, BenchmarkScreen)


async def test_lesson_shows_finger_map_highlighting_first_char(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await app.push_screen(LessonScreen(course_id=CourseId("en"), lesson=_lesson()))
        await pilot.pause()
        finger_map = app.screen.query_one(FingerMap)
        first = QWERTY.lookup("f")  # the lesson target is "fj"
        assert finger_map.highlight_state.key == first
        await pilot.press("f")
        await pilot.pause()
        assert finger_map.highlight_state.key == QWERTY.lookup("j")
