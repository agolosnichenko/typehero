import time
from datetime import date

from typehero.paths import content_dir
from typehero.tui.app import build_app
from typehero.tui.screens.achievements import AchievementRow, AchievementsScreen


async def test_rows_reflect_unlocked_state(tmp_path):
    app = build_app(
        content_root=content_dir(),
        profile_file=tmp_path / "profile.json",
        today=date(2026, 6, 4),
        clock=time.monotonic,
    )
    app.state.progress.unlocked_achievements.append("flawless")
    async with app.run_test():
        screen = AchievementsScreen()
        await app.push_screen(screen)
        rows = screen.achievement_rows()
        by_id = {row.id: row for row in rows}
        assert isinstance(by_id["flawless"], AchievementRow)
        assert by_id["flawless"].unlocked is True
        assert by_id["speed-demon"].unlocked is False
        assert by_id["flawless"].title  # localized, non-empty
