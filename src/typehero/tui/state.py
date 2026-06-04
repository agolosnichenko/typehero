"""Bootstraps and holds the app's loaded content and mutable profile."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from typehero.content_loader import ContentError, load_achievements, load_course, load_i18n
from typehero.domain.course import Course
from typehero.domain.progress import Progress
from typehero.gamification.achievements import Achievement
from typehero.localization import Translator
from typehero.persistence.store import load_progress, save_progress


@dataclass
class AppState:
    """Everything a running app needs: content, the profile, and injected time."""

    courses: dict[str, Course]
    achievements: list[Achievement]
    translator: Translator
    progress: Progress
    profile_file: Path
    today: date
    clock: Callable[[], float]
    active_course_id: str = "en"
    startup_notices: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.active_course_id not in self.courses:
            raise ContentError(
                f"active_course_id {self.active_course_id!r} has no matching course "
                f"(loaded: {sorted(self.courses)})"
            )

    def save(self) -> None:
        """Persist the current profile atomically."""
        save_progress(self.profile_file, self.progress)


def load_app_state(
    content_root: Path,
    profile_file: Path,
    today: date,
    clock: Callable[[], float],
) -> AppState:
    """Load all courses, achievements, translations, and the saved profile."""
    courses_dir = content_root / "courses"
    courses = {
        course.id: course
        for course in (load_course(path) for path in sorted(courses_dir.glob("*.yaml")))
    }
    if not courses:
        raise ContentError(f"No course files found in {courses_dir}")
    notices: list[str] = []
    progress = load_progress(
        profile_file,
        on_corrupt=lambda backup: notices.append(
            f"Your saved profile was unreadable and has been reset. "
            f"The old file is kept at {backup}."
        ),
    )
    return AppState(
        courses=courses,
        achievements=load_achievements(content_root / "achievements.yaml"),
        translator=load_i18n(content_root / "i18n"),
        progress=progress,
        profile_file=profile_file,
        today=today,
        clock=clock,
        startup_notices=notices,
    )
