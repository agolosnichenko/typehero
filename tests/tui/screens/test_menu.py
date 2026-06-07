import time
from datetime import date

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, ListView, Static
from textual.widgets._footer import FooterKey

from typehero import __version__
from typehero.paths import content_dir
from typehero.tui.app import build_app
from typehero.tui.screens.achievements import AchievementsScreen
from typehero.tui.screens.base import _FOOTER_I18N, AppScreen
from typehero.tui.screens.baseline_prompt import BaselinePrompt
from typehero.tui.screens.benchmark import BenchmarkScreen
from typehero.tui.screens.lesson import LessonScreen
from typehero.tui.screens.menu import MenuRow, MenuScreen
from typehero.tui.screens.progress import ProgressScreen
from typehero.tui.screens.results import ResultsScreen
from typehero.tui.screens.settings import SettingsScreen

# AppScreen subclasses that render a `Footer`; their binding descriptions must
# all be translatable. BaselinePrompt is excluded: it is a modal with no footer.
_FOOTER_SCREENS = (
    MenuScreen,
    BenchmarkScreen,
    AchievementsScreen,
    ProgressScreen,
    SettingsScreen,
    LessonScreen,
    ResultsScreen,
)


def _binding_descriptions(screen_cls):
    for binding in screen_cls.BINDINGS:
        yield binding.description if isinstance(binding, Binding) else binding[2]


def _app(tmp_path, completed=None):
    app = build_app(
        content_root=content_dir(),
        profile_file=tmp_path / "profile.json",
        today=date(2026, 6, 4),
        clock=time.monotonic,
    )
    if completed:
        app.state.progress.completed_lessons.extend(completed)
    return app


async def test_menu_rows_reflect_lock_state(tmp_path):
    app = _app(tmp_path)
    async with app.run_test():
        rows = app.screen.lesson_rows()
        assert isinstance(rows[0], MenuRow)
        assert rows[0].unlocked is True  # first lesson always unlocked
        assert rows[1].unlocked is False  # locked until en-01 done


async def test_completing_first_unlocks_second(tmp_path):
    app = _app(tmp_path, completed=["en-01-home-fj"])
    async with app.run_test():
        rows = app.screen.lesson_rows()
        assert rows[0].completed is True
        assert rows[1].unlocked is True


async def test_resuming_menu_refreshes_lock_state(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        lessons = app.screen.query_one("#lessons", ListView)
        assert lessons.children[1].disabled is True  # second locked on first render

        app.state.progress.mark_completed("en-01-home-fj")
        await pilot.press("p")  # push ProgressScreen
        await pilot.pause()
        await pilot.press("escape")  # pop back → ScreenResume on the menu
        await pilot.pause()

        lessons = app.screen.query_one("#lessons", ListView)
        assert lessons.children[1].disabled is False  # now unlocked after resume


def _highlighted_rows(app):
    lessons = app.screen.query_one("#lessons", ListView)
    return [child for child in lessons.children if child.has_class("-highlight")]


async def test_selection_highlight_visible_at_startup(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        assert len(_highlighted_rows(app)) == 1  # the selected lesson is shown


async def test_selection_highlight_survives_resume(tmp_path):
    app = _app(tmp_path, completed=["en-01-home-fj"])
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("p")  # leave the menu...
        await pilot.pause()
        await pilot.press("escape")  # ...and return → on_screen_resume rebuilds
        await pilot.pause()
        assert len(_highlighted_rows(app)) == 1  # selection still visible after rebuild


async def test_dashboard_tagline_shows_version_and_cleared_count(tmp_path):
    app = _app(tmp_path)
    async with app.run_test():
        tagline = app.screen.dashboard_tagline()
        assert f"v{__version__}" in tagline
        assert "0/" in tagline  # nothing cleared yet


async def test_dashboard_tagline_updates_after_clearing_a_lesson(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        app.state.progress.mark_completed("en-01-home-fj")
        await pilot.press("p")  # leave the menu, then return → ScreenResume
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        rendered = app.screen.query_one("#tagline", Static).render()
        assert "1/" in str(rendered)


async def test_menu_bindings_open_each_screen(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("b")
        assert isinstance(app.screen, BenchmarkScreen)
        await pilot.press("escape")
        await pilot.press("p")
        assert isinstance(app.screen, ProgressScreen)
        await pilot.press("escape")
        await pilot.press("a")
        assert isinstance(app.screen, AchievementsScreen)


async def test_selecting_first_lesson_prompts_for_baseline(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("enter")  # select the highlighted first lesson
        await pilot.pause()
        assert isinstance(app.screen, BaselinePrompt)


async def test_baseline_prompt_yes_opens_benchmark(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("y")
        await pilot.pause()
        assert isinstance(app.screen, BenchmarkScreen)


def _footer_labels(app):
    return [key.description for key in app.screen.query(FooterKey)]


async def test_tagline_localized_to_ui_locale(tmp_path):
    app = _app(tmp_path)
    app.state.progress.ui_locale = "ru"
    async with app.run_test():
        tagline = app.screen.dashboard_tagline()
        assert "пройдено уроков" in tagline
        assert f"v{__version__}" in tagline
        assert "0/" in tagline


async def test_footer_localized_to_ui_locale(tmp_path):
    app = _app(tmp_path)
    app.state.progress.ui_locale = "ru"
    async with app.run_test() as pilot:
        await pilot.pause()
        labels = _footer_labels(app)
        assert "Бенчмарк" in labels  # binding description
        assert "палитра" in labels  # app-level command palette binding
        assert "Benchmark" not in labels


async def test_switching_ui_language_relocalizes_menu_footer(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        assert "Benchmark" in _footer_labels(app)

        app.state.progress.ui_locale = "ru"
        await pilot.press("p")  # leave the menu...
        await pilot.pause()
        await pilot.press("escape")  # ...and return → on_screen_resume refreshes
        await pilot.pause()

        assert "Бенчмарк" in _footer_labels(app)


async def test_baseline_prompt_buttons_localized(tmp_path):
    from textual.widgets import Button

    app = _app(tmp_path)
    app.state.progress.ui_locale = "ru"
    async with app.run_test() as pilot:
        await pilot.press("enter")  # select first lesson → baseline prompt
        await pilot.pause()
        labels = [str(button.label) for button in app.screen.query(Button)]
        assert "Да" in labels
        assert "Пропустить" in labels


async def test_menu_s_opens_settings(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("s")
        assert isinstance(app.screen, SettingsScreen)


async def test_baseline_prompt_skip_records_and_opens_lesson(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("s")
        await pilot.pause()
        assert isinstance(app.screen, LessonScreen)
        assert app.state.progress.skipped_baselines == ["en"]


def test_footer_i18n_covers_every_screen_binding():
    """Drift guard: a footer binding without an i18n key silently renders English
    under a non-en locale. Fails if a screen adds or renames a binding, or if
    Textual renames its built-in command-palette description."""
    described = {desc for cls in _FOOTER_SCREENS for desc in _binding_descriptions(cls)}
    described.add("palette")  # Textual's built-in command-palette binding
    missing = described - set(_FOOTER_I18N)
    assert not missing, f"footer bindings missing an i18n key: {missing}"


class _UnmappedBindingScreen(AppScreen):
    BINDINGS = [("z", "noop", "Frobnicate")]

    def compose(self) -> ComposeResult:
        yield Footer()

    def action_noop(self) -> None:
        pass


async def test_footer_passes_through_unmapped_binding(tmp_path):
    app = _app(tmp_path)
    app.state.progress.ui_locale = "ru"
    async with app.run_test() as pilot:
        await app.push_screen(_UnmappedBindingScreen())
        await pilot.pause()
        descriptions = [a.binding.description for a in app.screen.active_bindings.values()]
        assert "Frobnicate" in descriptions  # unmapped → passed through unchanged


async def test_resume_with_no_prior_selection_defaults_to_first_row(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        app.screen.query_one("#lessons", ListView).index = None  # clear any selection
        await pilot.press("p")  # leave the menu...
        await pilot.pause()
        await pilot.press("escape")  # ...and return → on_screen_resume rebuilds
        await pilot.pause()
        lessons = app.screen.query_one("#lessons", ListView)
        assert lessons.index == 0  # a missing selection defaults to the first lesson
        assert len(_highlighted_rows(app)) == 1
