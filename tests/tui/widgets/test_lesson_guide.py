from typehero.tui.widgets.lesson_guide import _PRINCIPLE_MARKER, LessonGuide


def test_render_shows_tip_and_principle():
    rendered = str(
        LessonGuide(
            tip="о and а sit under the middle fingers", principle="Accuracy first"
        ).render_text()
    )
    assert "о and а sit under the middle fingers" in rendered
    assert "Accuracy first" in rendered


def test_render_principle_only_when_no_tip():
    rendered = str(LessonGuide(tip=None, principle="Accuracy first").render_text())
    assert "Accuracy first" in rendered


def test_render_omits_principle_marker_when_principle_is_empty():
    rendered = str(LessonGuide(tip="Stay on home row", principle="").render_text())
    assert "Stay on home row" in rendered
    assert _PRINCIPLE_MARKER not in rendered
