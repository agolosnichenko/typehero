"""Bootstraps and holds the app's loaded content and mutable profile."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import cast

from typehero.content_loader import (
    ContentError,
    load_achievements,
    load_corpus,
    load_course,
    load_i18n,
    load_wordlist,
)
from typehero.domain.course import Course
from typehero.domain.generators import CourseResources
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
    resources: dict[str, CourseResources] = field(default_factory=dict)
    rng: random.Random = field(default_factory=random.Random)
    startup_notices: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.progress.active_course_id not in self.courses:
            raise ContentError(
                f"active_course_id {self.progress.active_course_id!r} has no matching course "
                f"(loaded: {sorted(self.courses)})"
            )

    @property
    def active_course_id(self) -> str:
        """The course the player is currently training on (persisted)."""
        return self.progress.active_course_id

    def save(self) -> None:
        """Persist the current profile atomically."""
        save_progress(self.profile_file, self.progress)


def _course_resources(content_root: Path, course: Course) -> CourseResources:
    """Load only the resources the course actually cites.

    The wordlist is read only when a lesson uses a wordlist stage, and only
    the corpus files referenced by lessons are loaded. A course of literal
    stages needs no resource files at all.
    """
    stages = [
        cast("dict[str, object]", stage)
        for lesson in course.lessons
        for stage in lesson.stages
        if isinstance(stage, dict)
    ]
    needs_wordlist = any(stage.get("source") == "wordlist" for stage in stages)
    wordlist = (
        tuple(load_wordlist(content_root / "wordlists" / f"{course.id}.txt"))
        if needs_wordlist
        else ()
    )
    files = sorted({str(stage["file"]) for stage in stages if stage.get("source") == "corpus"})
    corpora = {name: load_corpus(content_root / "corpora" / name) for name in files}
    return CourseResources(wordlist=wordlist, corpora=corpora)


def load_app_state(
    content_root: Path,
    profile_file: Path,
    today: date,
    clock: Callable[[], float],
    rng: random.Random,
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
    if progress.active_course_id not in courses:
        default_course = sorted(courses)[0]
        notices.append(
            f"Course {progress.active_course_id!r} from your profile is unavailable; "
            f"switched to {default_course!r}."
        )
        progress.active_course_id = default_course
    return AppState(
        courses=courses,
        achievements=load_achievements(content_root / "achievements.yaml"),
        translator=load_i18n(content_root / "i18n"),
        progress=progress,
        profile_file=profile_file,
        today=today,
        clock=clock,
        rng=rng,
        resources={
            course.id: _course_resources(content_root, course) for course in courses.values()
        },
        startup_notices=notices,
    )
