# ai-microservices

A personal, YAML-driven engine for running small AI actions (proofread,
translate, summarize, review, ...) against an OpenAI-compatible endpoint,
triggered by a KDE global shortcut, a searchable picker, or the command
line. Services are data, not code — adding one means adding a YAML file.

**Full documentation**: `docs/` (built with MkDocs). Browse it locally:

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

Once this repo is public, the built docs will also live at
<https://apomonosi.github.io/ai-microservices/>.

## Quickstart

```bash
pipx install -e .
ai-actions list
ai-actions run proofread          # clipboard -> service -> review -> clipboard
ai-actions picker                 # search/pick a service interactively
```

`python3 -m ai_actions ...` also works identically, with no install at all.
See `docs/install.md` for the KDE global shortcut setup and full install
details.

## Develop

```bash
pip install -r requirements-dev.txt
pytest
```

CI (`.github/workflows/tests.yml`, `.github/workflows/docs.yml`) runs the
test suite and validates the docs build on every push and pull request.
