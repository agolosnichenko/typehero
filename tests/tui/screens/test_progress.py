import time
from datetime import date

from textual.widgets import Sparkline, Static

from typehero.domain.progress import BenchmarkSnapshot
from typehero.paths import content_dir
from typehero.tui.app import build_app
from typehero.tui.screens.progress import ProgressScreen


def _app(tmp_path):
    app = build_app(
        content_root=content_dir(),
        profile_file=tmp_path / "profile.json",
        today=date(2026, 6, 4),
        clock=time.monotonic,
    )
    app.state.progress.add_benchmark("en", BenchmarkSnapshot("2026-06-01", 20.0, 0.92, 8))
    app.state.progress.add_benchmark("en", BenchmarkSnapshot("2026-06-04", 40.0, 0.97, 2))
    return app


def _app_one_snapshot(tmp_path):
    app = build_app(
        content_root=content_dir(),
        profile_file=tmp_path / "profile.json",
        today=date(2026, 6, 4),
        clock=time.monotonic,
    )
    app.state.progress.add_benchmark("en", BenchmarkSnapshot("2026-06-04", 38.0, 0.97, 2))
    return app


async def test_progress_series_extracts_speed_and_accuracy(tmp_path):
    app = _app(tmp_path)
    async with app.run_test():
        screen = ProgressScreen(course_id="en")
        await app.push_screen(screen)
        assert screen.speed_series() == [20.0, 40.0]
        assert screen.accuracy_series() == [92.0, 97.0]


async def test_progress_history_rows_lists_each_snapshot(tmp_path):
    app = _app(tmp_path)
    async with app.run_test():
        screen = ProgressScreen(course_id="en")
        await app.push_screen(screen)
        rows = screen.history_rows()
        assert len(rows) == 3  # header + two snapshots
        assert "WPM" in rows[0] and "acc" in rows[0]
        assert rows[1].split() == ["2026-06-01", "20", "92%", "8", "interim"]
        assert rows[2].split() == ["2026-06-04", "40", "97%", "2", "interim"]


async def test_progress_history_rows_empty_when_no_benchmarks(tmp_path):
    app = build_app(
        content_root=content_dir(),
        profile_file=tmp_path / "profile.json",
        today=date(2026, 6, 4),
        clock=time.monotonic,
    )
    async with app.run_test():
        screen = ProgressScreen(course_id="en")
        await app.push_screen(screen)
        assert screen.history_rows() == []


async def test_progress_widgets_fit_inside_terminal(tmp_path):
    app = _app(tmp_path)  # two snapshots → sparklines are rendered
    async with app.run_test(size=(100, 30)) as pilot:
        screen = ProgressScreen(course_id="en")
        await app.push_screen(screen)
        await pilot.pause()
        assert len(screen.query(Sparkline)) == 2  # the widgets that used to overflow
        width = app.size.width
        for widget in screen.query("Sparkline, Static, Label"):
            region = widget.region
            assert region.right <= width, f"{widget} overflows: {region!r} > {width}"


async def test_progress_hides_sparklines_with_single_snapshot(tmp_path):
    app = _app_one_snapshot(tmp_path)
    async with app.run_test() as pilot:
        screen = ProgressScreen(course_id="en")
        await app.push_screen(screen)
        await pilot.pause()
        assert len(screen.query(Sparkline)) == 0
        assert len(screen.query(Static)) >= 1  # the history table still renders


async def test_progress_series_empty_when_no_benchmarks(tmp_path):
    app = build_app(
        content_root=content_dir(),
        profile_file=tmp_path / "profile.json",
        today=date(2026, 6, 4),
        clock=time.monotonic,
    )
    async with app.run_test():
        screen = ProgressScreen(course_id="en")
        await app.push_screen(screen)
        assert screen.speed_series() == []
