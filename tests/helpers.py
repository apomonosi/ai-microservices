"""Shared helpers for writing minimal-but-valid test fixtures to disk.

Kept as plain functions (not fixtures) so both conftest.py and test
modules can build arbitrarily-named/shaped files per test, rather than
being limited to one fixed fixture shape.
"""

from __future__ import annotations

from pathlib import Path


def write_models_file(path: Path, **profiles) -> Path:
    """Write a models.yaml. With no profiles given, writes a single
    'local' profile pointing at an unroutable address — fine for tests
    that never actually call run_service over real HTTP.
    """
    if not profiles:
        profiles = {"local": {"url": "http://127.0.0.1:1", "model": "test-model", "timeout": 5}}
    lines: list[str] = []
    for name, cfg in profiles.items():
        lines.append(f"{name}:")
        lines.append("  type: openai-compatible")
        lines.append(f"  url: {cfg['url']}")
        lines.append(f"  model: {cfg['model']}")
        for key in ("temperature", "timeout", "api_key"):
            if key in cfg:
                lines.append(f"  {key}: {cfg[key]}")
        lines.append("")
    path.write_text("\n".join(lines))
    return path


def write_service_file(
    services_dir: Path,
    service_id: str,
    *,
    name: str | None = None,
    category: str = "testing",
    model: str = "local",
    review: str = "text",
    clipboard_on_accept: str = "none",
    prompt: str = "You are a test assistant.\nRespond briefly.",
    internal_id: str | None = None,
) -> Path:
    """Write a minimal-but-valid service manifest.

    `internal_id` lets a test deliberately create an id/filename
    mismatch (the file is still named `<service_id>.yaml`, but its
    `id:` field says `internal_id`).
    """
    lines = [
        f"id: {internal_id if internal_id is not None else service_id}",
        f"name: {name or service_id.title()}",
        f"category: {category}",
        f"model: {model}",
        "",
        "prompt:",
        "  system: |",
    ]
    lines.extend(f"    {line}" for line in prompt.splitlines())
    lines += ["", f"review: {review}", f"clipboard_on_accept: {clipboard_on_accept}", ""]
    path = services_dir / f"{service_id}.yaml"
    path.write_text("\n".join(lines))
    return path
