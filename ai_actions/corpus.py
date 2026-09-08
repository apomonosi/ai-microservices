"""Local retrieval layer: BM25 lexical search over a directory of plain-
text documents, for services that declare `corpus: <corpus_id>`.

Deliberately lexical, not embedding-based - no embedding model, no vector
database, no new dependency, just Python's stdlib. See
docs/architecture.md for why. Nothing here is cached: a corpus is read
and re-chunked fresh on every search, the same convention
services/*.yaml and models.yaml already follow.
"""

from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPORA_DIR = Path(os.environ.get("AI_ACTIONS_CORPORA_DIR", REPO_ROOT / "corpora"))

_WORD_RE = re.compile(r"[a-z0-9]+")
_MAX_CHUNK_WORDS = 200


class CorpusError(RuntimeError):
    """Missing corpus directory, or one with no readable text in it."""


@dataclass
class Chunk:
    source: str  # filename the chunk came from
    index: int  # chunk number within that file
    text: str


def _tokenize(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


def _chunk_document(text: str) -> list[str]:
    """Split on blank lines (paragraphs); further split any paragraph
    over _MAX_CHUNK_WORDS so no chunk is too large to usefully quote in a
    prompt.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    for paragraph in paragraphs:
        words = paragraph.split()
        if len(words) <= _MAX_CHUNK_WORDS:
            chunks.append(paragraph)
        else:
            for i in range(0, len(words), _MAX_CHUNK_WORDS):
                chunks.append(" ".join(words[i : i + _MAX_CHUNK_WORDS]))
    return chunks


def list_corpora(corpora_dir: Path = CORPORA_DIR) -> list[str]:
    """Every corpus id found under corpora_dir: any directory containing
    at least one regular file, given as its path relative to corpora_dir
    (so both a flat corpus and a namespaced one like 'examples/course'
    are found the same way).
    """
    if not corpora_dir.is_dir():
        return []
    found: list[str] = []
    for dirpath, _dirnames, filenames in os.walk(corpora_dir):
        if any((Path(dirpath) / name).is_file() for name in filenames):
            rel = Path(dirpath).relative_to(corpora_dir)
            found.append("." if str(rel) == "." else str(rel).replace(os.sep, "/"))
    return sorted(f for f in found if f != ".")


def load_corpus_chunks(corpus_id: str, corpora_dir: Path = CORPORA_DIR) -> list[Chunk]:
    corpus_dir = corpora_dir / corpus_id
    if not corpus_dir.is_dir():
        raise CorpusError(f"Unknown corpus '{corpus_id}' (expected directory {corpus_dir})")

    chunks: list[Chunk] = []
    for path in sorted(corpus_dir.glob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        for i, chunk_text in enumerate(_chunk_document(text)):
            chunks.append(Chunk(source=path.name, index=i, text=chunk_text))

    if not chunks:
        raise CorpusError(f"Corpus '{corpus_id}' has no readable text files in {corpus_dir}")
    return chunks


def _bm25_scores(query_terms: list[str], tokenized_chunks: list[list[str]]) -> list[float]:
    k1, b = 1.5, 0.75
    n_docs = len(tokenized_chunks)
    doc_lens = [len(tokens) for tokens in tokenized_chunks]
    avg_len = (sum(doc_lens) / n_docs) if n_docs else 0.0

    doc_freq: dict[str, int] = {}
    for tokens in tokenized_chunks:
        for term in set(tokens):
            doc_freq[term] = doc_freq.get(term, 0) + 1

    scores = [0.0] * n_docs
    for i, tokens in enumerate(tokenized_chunks):
        term_freq: dict[str, int] = {}
        for term in tokens:
            term_freq[term] = term_freq.get(term, 0) + 1
        score = 0.0
        for term in query_terms:
            freq = term_freq.get(term)
            if not freq:
                continue
            n_qi = doc_freq.get(term, 0)
            idf = math.log((n_docs - n_qi + 0.5) / (n_qi + 0.5) + 1)
            denom = freq + k1 * (1 - b + b * doc_lens[i] / avg_len) if avg_len else freq
            score += idf * (freq * (k1 + 1)) / denom
        scores[i] = score
    return scores


def search_corpus(corpus_id: str, query: str, top_k: int = 5, corpora_dir: Path = CORPORA_DIR) -> list[Chunk]:
    """Rank corpus_id's chunks against query with BM25 and return the
    top_k. Falls back to the corpus's own order if the query has no
    recognizable words, or every chunk scores zero (no term overlap at
    all) - always returns something rather than nothing.
    """
    chunks = load_corpus_chunks(corpus_id, corpora_dir)
    query_terms = _tokenize(query)
    if not query_terms:
        return chunks[:top_k]

    tokenized_chunks = [_tokenize(chunk.text) for chunk in chunks]
    scores = _bm25_scores(query_terms, tokenized_chunks)
    ranked = sorted(zip(scores, chunks), key=lambda pair: pair[0], reverse=True)
    top = [chunk for score, chunk in ranked if score > 0][:top_k]
    return top if top else chunks[:top_k]
