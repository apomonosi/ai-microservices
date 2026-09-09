"""mkdocs-gen-files script: builds docs/services/* from the actual service
manifests, using the same loader the CLI itself uses (ai_actions.core), so
these pages can never drift from what `ai-actions service list/show`
actually does — there's no second YAML parser to keep in sync.

Pages are generated virtually (mkdocs_gen_files.open), not written to disk
under docs/ — nothing here should be committed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import mkdocs_gen_files

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ai_actions.core import ConfigError, list_services, load_models  # noqa: E402

services = sorted(list_services(), key=lambda s: (s.category, s.id))

try:
    models = load_models()
except ConfigError:
    models = {}

# --- catalog index, grouped by category -----------------------------------------------------------

index_lines = [
    "# Service catalog",
    "",
    f"{len(services)} services, generated from `services/*.yaml` — always in sync with "
    "`ai-actions list`/`service show`.",
]

current_category = None
for service in services:
    if service.category != current_category:
        current_category = service.category
        index_lines += ["", f"## {current_category}", "", "| Service | Review | Description |", "|---|---|---|"]
    description = service.description or "*(no description)*"
    index_lines.append(f"| [{service.name}]({service.id}.md) (`{service.id}`) | {service.review} | {description} |")

with mkdocs_gen_files.open("services/index.md", "w") as f:
    f.write("\n".join(index_lines) + "\n")

# --- one page per service, mirroring `ai-actions service show` -----------------------------------------------------------

for service in services:
    profile = models.get(service.model)
    model_line = (
        f"`{service.model}` → `{profile.model}` @ `{profile.url}`"
        if profile is not None
        else f"`{service.model}` (not found in models.yaml)"
    )

    lines = [
        f"# {service.name}",
        "",
        f"| | |",
        f"|---|---|",
        f"| **id** | `{service.id}` |",
        f"| **category** | {service.category} |",
        f"| **model** | {model_line} |",
        f"| **review** | {service.review} |",
        f"| **clipboard on accept** | {service.clipboard_on_accept} |",
    ]
    if service.verify:
        lines.append(f"| **verify** | `{service.verify}` (sends input lines to an external API) |")
    if service.corpus:
        lines.append(f"| **corpus** | `{service.corpus}` (local retrieval only, see [Corpora](../guide/corpora.md)) |")
    if service.description:
        lines += ["", service.description]
    lines += ["", "## Prompt", "", "```", service.system_prompt.rstrip(), "```"]
    lines += ["", f"Run it: `ai-actions run {service.id}`"]

    with mkdocs_gen_files.open(f"services/{service.id}.md", "w") as f:
        f.write("\n".join(lines) + "\n")
