from __future__ import annotations

import pytest

from ai_actions.corpus import CorpusError, list_corpora, load_corpus_chunks, search_corpus


def _write(path, text):
    path.write_text(text)


# --- chunking --------------------------------------------------------------


def test_load_corpus_chunks_splits_on_blank_lines(corpora_dir):
    course = corpora_dir / "course"
    course.mkdir()
    _write(course / "syllabus.txt", "First paragraph here.\n\nSecond paragraph here.\n\nThird one.")

    chunks = load_corpus_chunks("course", corpora_dir)

    assert [c.text for c in chunks] == ["First paragraph here.", "Second paragraph here.", "Third one."]
    assert all(c.source == "syllabus.txt" for c in chunks)
    assert [c.index for c in chunks] == [0, 1, 2]


def test_load_corpus_chunks_splits_long_paragraph(corpora_dir):
    course = corpora_dir / "course"
    course.mkdir()
    long_paragraph = " ".join(f"word{i}" for i in range(450))
    _write(course / "notes.txt", long_paragraph)

    chunks = load_corpus_chunks("course", corpora_dir)

    assert len(chunks) == 3  # 450 words / 200-word chunks -> 3 pieces
    assert sum(len(c.text.split()) for c in chunks) == 450


def test_load_corpus_chunks_multiple_files(corpora_dir):
    course = corpora_dir / "course"
    course.mkdir()
    _write(course / "a.txt", "Content of file A.")
    _write(course / "b.txt", "Content of file B.")

    chunks = load_corpus_chunks("course", corpora_dir)

    assert {c.source for c in chunks} == {"a.txt", "b.txt"}


def test_load_corpus_chunks_skips_unreadable_file(corpora_dir):
    course = corpora_dir / "course"
    course.mkdir()
    _write(course / "good.txt", "Readable content.")
    (course / "binary.dat").write_bytes(b"\xff\xfe\x00\x01not-utf8\xfa")

    chunks = load_corpus_chunks("course", corpora_dir)

    assert all(c.source != "binary.dat" for c in chunks)
    assert any(c.source == "good.txt" for c in chunks)


def test_load_corpus_chunks_missing_directory(corpora_dir):
    with pytest.raises(CorpusError, match="Unknown corpus"):
        load_corpus_chunks("does-not-exist", corpora_dir)


def test_load_corpus_chunks_empty_directory(corpora_dir):
    (corpora_dir / "empty").mkdir()
    with pytest.raises(CorpusError, match="no readable text"):
        load_corpus_chunks("empty", corpora_dir)


# --- search_corpus (BM25) ---------------------------------------------------


def test_search_corpus_ranks_relevant_chunk_first(corpora_dir):
    course = corpora_dir / "course"
    course.mkdir()
    _write(
        course / "policy.txt",
        "Late submissions lose ten percent per day.\n\n"
        "The course meets on Tuesdays and Thursdays at noon.\n\n"
        "Office hours are Wednesday afternoons in room 204.",
    )

    results = search_corpus("course", "what is the late submission penalty", top_k=1, corpora_dir=corpora_dir)

    assert len(results) == 1
    assert "Late submissions" in results[0].text


def test_search_corpus_top_k_limits_results(corpora_dir):
    course = corpora_dir / "course"
    course.mkdir()
    _write(course / "doc.txt", "\n\n".join(f"Paragraph number {i} about topic {i}." for i in range(10)))

    results = search_corpus("course", "topic 5", top_k=3, corpora_dir=corpora_dir)

    assert len(results) == 3


def test_search_corpus_no_query_terms_falls_back_to_order(corpora_dir):
    course = corpora_dir / "course"
    course.mkdir()
    _write(course / "doc.txt", "First.\n\nSecond.")

    results = search_corpus("course", "!!!", top_k=5, corpora_dir=corpora_dir)

    assert len(results) == 2


# --- list_corpora ------------------------------------------------------------


def test_list_corpora_finds_flat_and_namespaced(corpora_dir):
    (corpora_dir / "hr-policy").mkdir()
    _write(corpora_dir / "hr-policy" / "doc.txt", "content")
    (corpora_dir / "examples" / "course").mkdir(parents=True)
    _write(corpora_dir / "examples" / "course" / "doc.txt", "content")

    ids = list_corpora(corpora_dir)

    assert ids == ["examples/course", "hr-policy"]


def test_list_corpora_ignores_empty_directories(corpora_dir):
    (corpora_dir / "empty-dir").mkdir()

    assert list_corpora(corpora_dir) == []


def test_list_corpora_missing_root_returns_empty(tmp_path):
    assert list_corpora(tmp_path / "nonexistent") == []
