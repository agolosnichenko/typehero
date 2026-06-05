from typehero.tui.widgets.live_stats import LiveStats


def test_render_zero_state():
    rendered = str(LiveStats().render_text())
    assert "0 WPM" in rendered
    assert "0" in rendered  # error count


def test_render_rounds_wpm_and_shows_errors():
    widget = LiveStats()
    widget.update_stats(net_wpm=41.7, errors=3)
    rendered = str(widget.render_text())
    assert "42 WPM" in rendered  # rounded
    assert "3" in rendered
