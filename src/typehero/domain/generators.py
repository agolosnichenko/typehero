"""Stage text generation: literal, wordlist, and corpus sources.

Pure — takes pre-loaded word/corpus data and an injected RNG so the engine
stays deterministic under test. Filesystem reads live in content_loader/state.
"""

from __future__ import annotations

import random
import re
from collections.abc import Mapping
from dataclasses import dataclass

from typehero.domain.lesson import Lesson

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


@dataclass(frozen=True)
class CourseResources:
    """Pre-loaded generation inputs for one course."""

    wordlist: list[str]
    corpora: dict[str, str]


def _render_wordlist(stage: dict[str, object], *, wordlist: list[str], rng: random.Random) -> str:
    count = int(str(stage["count"]))
    keys = set(str(stage["keys"]))
    pool = [word for word in wordlist if set(word) <= keys]
    if not pool:
        raise ValueError(f"wordlist stage has no words within keys {sorted(keys)!r}")
    if count <= len(pool):
        chosen = rng.sample(pool, count)
    else:
        chosen = [rng.choice(pool) for _ in range(count)]
    return " ".join(chosen)


def _render_corpus(
    stage: dict[str, object], *, corpora: Mapping[str, str], rng: random.Random
) -> str:
    file = str(stage["file"])
    length = int(str(stage["length"]))
    if file not in corpora:
        raise ValueError(f"corpus stage references unknown file {file!r}")
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(corpora[file]) if s.strip()]
    if not sentences:
        raise ValueError(f"corpus file {file!r} has no sentences")
    start = rng.randrange(len(sentences))
    chosen: list[str] = []
    total = 0
    index = start
    while total < length and len(chosen) < len(sentences):
        sentence = sentences[index % len(sentences)]
        chosen.append(sentence)
        total += len(sentence) + 1
        index += 1
    return " ".join(chosen)


def render_stage(
    stage: object,
    *,
    wordlist: list[str],
    corpora: Mapping[str, str],
    rng: random.Random,
) -> str:
    """Render one stage to typed text.

    A `str` stage is returned verbatim. A `{source: ...}` dict is dispatched to
    the wordlist or corpus generator.

    Raises:
        ValueError: on a malformed stage or unknown source.
    """
    if isinstance(stage, str):
        return stage
    if not isinstance(stage, dict) or "source" not in stage:
        raise ValueError(f"stage must be a string or a {{source: ...}} dict, got {stage!r}")
    source = stage["source"]
    if source == "wordlist":
        return _render_wordlist(stage, wordlist=wordlist, rng=rng)
    if source == "corpus":
        return _render_corpus(stage, corpora=corpora, rng=rng)
    raise ValueError(f"unknown stage source {source!r}; expected 'wordlist' or 'corpus'")


def lesson_target(lesson: Lesson, *, resources: CourseResources, rng: random.Random) -> str:
    """The full text the player types: every stage rendered and joined by spaces."""
    return " ".join(
        render_stage(stage, wordlist=resources.wordlist, corpora=resources.corpora, rng=rng)
        for stage in lesson.stages
    )
