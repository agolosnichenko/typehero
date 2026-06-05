from typehero.tui.widgets.lesson_guide import LessonGuide


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
