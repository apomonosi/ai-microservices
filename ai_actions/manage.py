"""Mutating operations on the service library: create, duplicate, delete,
and single-field updates. Read-only inspection (list/show/search/
validate) lives in core.py; this module is specifically the write side.

set_field()/duplicate_service() edit the YAML file as text (targeted
line replacement) rather than round-tripping it through
yaml.safe_load()/yaml.safe_dump() — a full round-trip would reformat
the hand-crafted `prompt: system: |` block (reflowing lines, changing
quote style) since PyYAML's dumper doesn't reproduce the original
formatting. Regenerating only the single line for the field being
changed leaves everything else byte-for-byte untouched.
"""

from __future__ import annotations

import os
import re
import shlex
import subprocess
from pathlib import Path

import yaml

from .core import SERVICES_DIR, _VALID_CLIPBOARD_MODES, _VALID_REVIEW_TYPES, _service_path

_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_SETTABLE_FIELDS = ("name", "category", "model", "review", "clipboard_on_accept")
PLACEHOLDER_PROMPT = "TODO: write the system prompt for this service."


class ManageError(RuntimeError):
    """A service create/edit/set/duplicate/delete operation could not be completed."""


def validate_id(service_id: str) -> None:
    """Reject anything that isn't a plain slug — in particular, this
    blocks path separators/`..` from ever reaching a filesystem path
    built from user input.
    """
    if not _ID_RE.match(service_id):
        raise ManageError(
            f"invalid service id '{service_id}': use lowercase letters, digits and hyphens only, "
            "e.g. 'my-new-service'"
        )


def get_service_path(service_id: str, services_dir: Path = SERVICES_DIR) -> Path:
    return _service_path(service_id, services_dir)


def _yaml_scalar(value: str) -> str:
    """Render `value` the way it should appear after `key: `, letting
    PyYAML decide whether it needs quoting (it will quote a value
    containing e.g. an unescaped ' #', which is exactly the bug class
    that motivated this helper rather than hand-rolling the quoting
    rules again).

    Dumped via a throwaway single-key mapping rather than
    `yaml.safe_dump(value)` directly: dumping a bare scalar as its own
    document appends a `...` end-of-document marker, which would corrupt
    the line it's embedded into.
    """
    dumped = yaml.safe_dump({"v": value}, default_flow_style=False, allow_unicode=True).strip()
    return dumped[len("v: ") :]


def _default_clipboard_mode(review: str) -> str:
    return "replace" if review == "diff" else "none"


def build_manifest_text(
    *,
    service_id: str,
    name: str,
    category: str,
    model: str,
    review: str,
    clipboard_on_accept: str,
    description: str,
    prompt: str,
) -> str:
    prompt_lines = prompt.splitlines() if prompt.strip() else [PLACEHOLDER_PROMPT]
    description = description.strip() or "TODO: one-line description."

    lines = [
        f"id: {_yaml_scalar(service_id)}",
        f"name: {_yaml_scalar(name)}",
        f"category: {_yaml_scalar(category)}",
        f"model: {_yaml_scalar(model)}",
        "",
        "description: >",
        f"  {description}",
        "",
        "prompt:",
        "  system: |",
    ]
    lines.extend(f"    {line}" if line else "" for line in prompt_lines)
    lines += ["", f"review: {review}", f"clipboard_on_accept: {clipboard_on_accept}", ""]
    return "\n".join(lines)


def create_service(
    service_id: str,
    *,
    name: str | None = None,
    category: str = "general",
    model: str = "local",
    review: str = "text",
    clipboard_on_accept: str | None = None,
    description: str = "",
    prompt: str = "",
    services_dir: Path = SERVICES_DIR,
) -> Path:
    validate_id(service_id)
    if review not in _VALID_REVIEW_TYPES:
        raise ManageError(f"invalid review type '{review}' (expected one of {_VALID_REVIEW_TYPES})")
    clipboard_on_accept = clipboard_on_accept or _default_clipboard_mode(review)
    if clipboard_on_accept not in _VALID_CLIPBOARD_MODES:
        raise ManageError(
            f"invalid clipboard_on_accept '{clipboard_on_accept}' (expected one of {_VALID_CLIPBOARD_MODES})"
        )

    path = _service_path(service_id, services_dir)
    if path.exists():
        raise ManageError(f"service '{service_id}' already exists ({path})")

    text = build_manifest_text(
        service_id=service_id,
        name=name or service_id.replace("-", " ").title(),
        category=category,
        model=model,
        review=review,
        clipboard_on_accept=clipboard_on_accept,
        description=description,
        prompt=prompt,
    )
    path.write_text(text)
    return path


def duplicate_service(
    source_id: str,
    new_id: str,
    *,
    name: str | None = None,
    services_dir: Path = SERVICES_DIR,
) -> Path:
    validate_id(new_id)
    src_path = _service_path(source_id, services_dir)
    if not src_path.exists():
        raise ManageError(f"source service '{source_id}' does not exist ({src_path})")
    new_path = _service_path(new_id, services_dir)
    if new_path.exists():
        raise ManageError(f"service '{new_id}' already exists ({new_path})")

    text = src_path.read_text()
    text, n = re.subn(r"(?m)^id:.*$", f"id: {_yaml_scalar(new_id)}", text, count=1)
    if n == 0:
        raise ManageError(f"'{src_path}' has no top-level 'id:' field to update")
    if name is not None:
        text = re.sub(r"(?m)^name:.*$", f"name: {_yaml_scalar(name)}", text, count=1)
    new_path.write_text(text)
    return new_path


def delete_service(service_id: str, *, services_dir: Path = SERVICES_DIR) -> Path:
    path = _service_path(service_id, services_dir)
    if not path.exists():
        raise ManageError(f"service '{service_id}' does not exist ({path})")
    path.unlink()
    return path


def set_field(service_id: str, field: str, value: str, *, services_dir: Path = SERVICES_DIR) -> Path:
    if field not in _SETTABLE_FIELDS:
        raise ManageError(f"cannot set '{field}' this way (allowed: {_SETTABLE_FIELDS}); use `service edit` instead")
    if field == "review" and value not in _VALID_REVIEW_TYPES:
        raise ManageError(f"invalid review type '{value}' (expected one of {_VALID_REVIEW_TYPES})")
    if field == "clipboard_on_accept" and value not in _VALID_CLIPBOARD_MODES:
        raise ManageError(f"invalid clipboard_on_accept '{value}' (expected one of {_VALID_CLIPBOARD_MODES})")

    path = _service_path(service_id, services_dir)
    if not path.exists():
        raise ManageError(f"service '{service_id}' does not exist ({path})")

    text = path.read_text()
    new_text, n = re.subn(rf"(?m)^{re.escape(field)}:.*$", f"{field}: {_yaml_scalar(value)}", text, count=1)
    if n == 0:
        raise ManageError(f"'{field}:' not found as a top-level key in {path}")
    path.write_text(new_text)
    return path


def open_editor(path: Path) -> int:
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
    if not editor:
        raise ManageError(f"no $VISUAL or $EDITOR set; edit the file directly: {path}")
    # $EDITOR/$VISUAL can be a command with arguments (e.g. "code --wait"),
    # not just a bare program name — split it the way a shell would.
    command = shlex.split(editor) + [str(path)]
    try:
        return subprocess.call(command)
    except OSError as exc:
        raise ManageError(f"could not run editor {command!r}: {exc}") from exc
