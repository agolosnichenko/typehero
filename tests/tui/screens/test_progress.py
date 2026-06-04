import time
from datetime import date

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


async def test_progress_series_extracts_speed_and_accuracy(tmp_path):
    app = _app(tmp_path)
    async with app.run_test():
        screen = ProgressScreen(course_id="en")
        await app.push_screen(screen)
        assert screen.speed_series() == [20.0, 40.0]
        assert screen.accuracy_series() == [92.0, 97.0]


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
