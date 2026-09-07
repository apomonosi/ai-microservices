"""Word-level diff rendering for the Result Inspector."""

from __future__ import annotations

import difflib
import html
import re

_TOKEN_RE = re.compile(r"\s+|\S+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text)


def _opcodes(original: str, revised: str):
    return difflib.SequenceMatcher(None, _tokenize(original), _tokenize(revised), autojunk=False).get_opcodes()


def render_word_diff_html(original: str, revised: str) -> str:
    """Return an HTML fragment with an inline word-level diff: deletions
    struck-through in red, insertions underlined in green, unchanged text
    as-is.
    """
    orig_tokens = _tokenize(original)
    new_tokens = _tokenize(revised)
    parts: list[str] = []
    for tag, i1, i2, j1, j2 in _opcodes(original, revised):
        if tag == "equal":
            parts.append(html.escape("".join(orig_tokens[i1:i2])))
            continue
        deleted = html.escape("".join(orig_tokens[i1:i2])) if tag in ("delete", "replace") else ""
        inserted = html.escape("".join(new_tokens[j1:j2])) if tag in ("insert", "replace") else ""
        if deleted.strip():
            parts.append(f'<span style="color:#c0392b; text-decoration:line-through;">{deleted}</span>')
        # A same-spot word replacement has no whitespace token between the
        # old and new word (the surrounding spaces are in the equal runs on
        # either side), so without this they'd render glued together.
        if deleted.strip() and inserted.strip():
            parts.append(" ")
        if inserted.strip():
            parts.append(f'<span style="color:#1e7e34; text-decoration:underline;">{inserted}</span>')
    return "".join(parts).replace("\n", "<br>")


def count_changes(original: str, revised: str) -> int:
    """Rough count of distinct edits (non-equal diff opcodes)."""
    return sum(1 for tag, *_ in _opcodes(original, revised) if tag != "equal")
