import random

import pytest

from typehero.domain.generators import CourseResources, lesson_target, render_stage
from typehero.domain.lesson import Lesson, LessonType, PassCriteria


def _rng() -> random.Random:
    return random.Random(0)


def _lesson(stages: list[object]) -> Lesson:
    return Lesson(
        id="en-01",
        title={"en": "L"},
        type=LessonType.KEYS,
        stages=stages,
        criteria=PassCriteria(max_error_rate=0.1, min_wpm=None),
        reward_xp=10,
    )


def test_render_literal_stage_returned_as_is():
    assert render_stage("fff jjj", wordlist=[], corpora={}, rng=_rng()) == "fff jjj"


def test_render_wordlist_respects_keys_and_count():
    words = ["ask", "all", "type", "word", "dad"]  # only ask/all/dad use a,s,d,k,l
    out = render_stage(
        {"source": "wordlist", "count": 3, "keys": "askdl"},
        wordlist=words,
        corpora={},
        rng=_rng(),
    )
    chosen = out.split()
    assert len(chosen) == 3
    assert all(set(w) <= set("askdl") for w in chosen)


def test_render_wordlist_is_deterministic_under_same_seed():
    words = ["ask", "all", "dad", "lass", "salad", "flask"]
    stage = {"source": "wordlist", "count": 4, "keys": "asdfklg"}
    a = render_stage(stage, wordlist=words, corpora={}, rng=random.Random(7))
    b = render_stage(stage, wordlist=words, corpora={}, rng=random.Random(7))
    assert a == b


def test_render_wordlist_with_replacement_when_pool_too_small():
    out = render_stage(
        {"source": "wordlist", "count": 5, "keys": "ad"},
        wordlist=["dad", "add", "type"],  # only dad/add fit
        corpora={},
        rng=_rng(),
    )
    assert len(out.split()) == 5


def test_render_wordlist_empty_pool_raises():
    with pytest.raises(ValueError, match="keys"):
        render_stage(
            {"source": "wordlist", "count": 2, "keys": "z"},
            wordlist=["dad", "ask"],
            corpora={},
            rng=_rng(),
        )


def test_render_corpus_accumulates_whole_sentences_to_length():
    text = "Alpha beta. Gamma delta epsilon. Zeta eta theta iota."
    out = render_stage(
        {"source": "corpus", "file": "p.txt", "length": 20},
        wordlist=[],
        corpora={"p.txt": text},
        rng=random.Random(0),
    )
    assert len(out) >= 20
    # Every emitted token is a whole word from the source (no mid-word cut).
    source_words = set(text.replace(".", "").split())
    assert all(w.strip(".") in source_words for w in out.split())


def test_render_corpus_emits_only_whole_sentences():
    text = "Alpha beta. Gamma delta epsilon. Zeta eta theta iota."
    out = render_stage(
        {"source": "corpus", "file": "p.txt", "length": 20},
        wordlist=[],
        corpora={"p.txt": text},
        rng=random.Random(0),
    )
    sentences = ["Alpha beta.", "Gamma delta epsilon.", "Zeta eta theta iota."]
    candidates = {
        " ".join(sentences[(start + k) % len(sentences)] for k in range(n))
        for start in range(len(sentences))
        for n in range(1, len(sentences) + 1)
    }
    assert out in candidates


def test_render_corpus_unknown_file_raises():
    with pytest.raises(ValueError, match="unknown file"):
        render_stage(
            {"source": "corpus", "file": "missing.txt", "length": 10},
            wordlist=[],
            corpora={},
            rng=_rng(),
        )


def test_render_unknown_source_raises():
    with pytest.raises(ValueError, match="unknown stage source"):
        render_stage({"source": "nope"}, wordlist=[], corpora={}, rng=_rng())


def test_lesson_target_joins_stages_with_space():
    resources = CourseResources(wordlist=["dad", "ask", "all"], corpora={})
    target = lesson_target(
        _lesson(["fff jjj", {"source": "wordlist", "count": 2, "keys": "askdl"}]),
        resources=resources,
        rng=_rng(),
    )
    assert target.startswith("fff jjj ")
    assert len(target.split()) == 4
