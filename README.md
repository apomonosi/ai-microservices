# ai-microservices

A personal, YAML-driven engine for running small AI actions (proofread,
translate, summarize, review, ...) against an OpenAI-compatible endpoint,
triggered by a KDE global shortcut or run from the command line. See
`ROADMAP.md` for the project's background and status.

## Install

```bash
pipx install -e .
```

`pipx` installs the `ai-actions` command in its own isolated environment
while still putting it on your PATH globally — the right choice here since
KDE global shortcuts invoke the command outside of any shell that would
normally activate a venv for you.

A plain venv works too if you prefer:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

Either way, this is an **editable** install on purpose: `services/*.yaml`
and `models.yaml` live in this checkout and are meant to be hand-edited
(via `ai-actions service create/edit/set/duplicate`) — an editable install
keeps the command pointed at this real checkout instead of a frozen copy.

## Use

```bash
ai-actions list                        # see available services
ai-actions run proofread                # clipboard -> service -> review -> clipboard
ai-actions picker                       # search/pick a service interactively
cat draft.txt | ai-actions run proofread --stdin --no-gui -o out.txt
```

`python3 -m ai_actions ...` still works identically if you'd rather not
install anything.

## Develop

```bash
pip install -r requirements-dev.txt
pytest
```

CI (`.github/workflows/tests.yml`) runs the same suite on every push and
pull request.
