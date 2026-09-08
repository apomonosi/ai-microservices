# ai-actions

A personal, YAML-driven engine for running small AI actions — proofread,
translate, summarize, review, and dozens more — against an OpenAI-compatible
endpoint, triggered by a KDE global shortcut, a searchable picker, or the
command line.

The core idea: **services are data, not code**. Each one is a short YAML
file (a name, a category, a model, a system prompt, and how its result
should be reviewed) loaded by a single generic engine. Adding a new
capability means adding a YAML file, not writing a new program.

## Quickstart

```bash
pipx install -e .
ai-actions list
ai-actions run proofread          # clipboard -> service -> review -> clipboard
ai-actions picker                 # search/pick a service interactively
```

See [Install](install.md) for the KDE shortcut setup, and the
[CLI reference](guide/cli.md) for everything the command can do.

## Where to go next

- [Install](install.md) — getting `ai-actions` on your PATH and wired to a KDE shortcut.
- [CLI reference](guide/cli.md) — `run`, `picker`, `list`, `service ...`.
- [Service manifest](guide/service-manifest.md) — the YAML schema behind every service.
- [Creating services](guide/creating-services.md) — `service create`/`edit`/`set`/`duplicate`.
- [Pipelines](guide/pipelines.md) — composing services into shell pipelines.
- [Model profiles](guide/models.md) — `models.yaml` and how services reference it.
- [Service catalog](services/index.md) — every service currently defined, browsable.
- [Architecture](architecture.md) — how the engine is put together.
- [Roadmap](roadmap.md) — project history and what's next.
