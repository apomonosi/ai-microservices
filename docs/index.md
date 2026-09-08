# ai-actions

Most of what you actually want from AI on a given afternoon is mundane.
Fix the grammar in this abstract. Check that the numbers in Table 3 match
the text. Turn these slides into a study guide. Explain this regulation in
plain language. None of that needs a trillion-parameter model in a
hyperscale data center — it needs a model that's good enough, running on
the machine already in front of you.

**ai-actions** is what that looks like as a tool instead of an argument.
It's a personal, YAML-driven engine for running small, single-purpose AI
actions against an OpenAI-compatible endpoint — local by default — wired
to a KDE global shortcut, a searchable picker, or the command line.

If your reaction to "local model" is "I don't have the hardware for
that" — you probably do. See [Do you need the cloud?](local-models.md)
for what "capable enough" actually means in practice, and how to get a
model running without any AI or programming background.

## What a service actually is

An action here is not an app. It's:

- **one prompt** — a plain-text system prompt, version-controlled in a
  `services/*.yaml` file, alongside its input/output shape and how its
  result should be reviewed;
- **one model** — chosen per service in `models.yaml`, and swappable
  without touching the prompt;
- **no state** — a service doesn't remember you between runs and doesn't
  need an account, because it's a function call, not a chat.

That makes it closer to a Unix filter than a copilot. Every one of the
[58 services in the catalog](services/index.md) runs like this, whether
it's triggered by a shortcut or by a pipe:

```bash
cat manuscript.md | ai-actions run proofread --stdin --no-gui | tee proofread.md
```

Text in, text out, reviewable at every step — see [Pipelines](guide/pipelines.md)
for the full `--file`/`--stdin`/`--output` story.

## Why this shape keeps paying off

- **Cheap to build.** The prompt *is* the service; the engine is generic.
  Adding a capability means adding a YAML file — see
  [Creating services](guide/creating-services.md).
- **Cheap to evaluate.** A single-purpose prompt has a single-purpose test:
  does *this* transform hold up on a handful of real examples? Nobody has
  to evaluate "the assistant."
- **Cheap to trust.** Every prompt in [the catalog](services/index.md) is a
  file you can read in ten seconds. Nothing leaves the machine unless a
  service's model profile says otherwise.
- **Cheap to replace.** A better model for a task is a one-line edit to
  `models.yaml` — see [Model profiles](guide/models.md).

It also matches what the underlying [service catalog](catalog.md) actually
looks like once you total it up: most of it is **checking**, not
generating — structure, methodology, statistics, citations, terminology,
numbers that should but don't match — and checking is exactly the task
class where a small local model is strongest and a wrong answer costs
almost nothing to catch. See [Design principles](philosophy.md) for the
architecture pattern (LLM + retrieval + deterministic validation) behind
that, and why the mundane, verifiable tasks were built first on purpose.

## Get started

```bash
pipx install -e .
ai-actions list
ai-actions run proofread          # clipboard -> service -> review -> clipboard
ai-actions picker                 # search/pick a service interactively
```

See [Install](install.md) for the KDE shortcut, and [Examples](examples.md)
for worked walkthroughs beyond the clipboard case — pipelines, scripted
review-free runs, and building a new service end to end.

## Where to go next

- [Do you need the cloud?](local-models.md) — why a small local model is enough, and whether your hardware can run one.
- [Install](install.md) — getting `ai-actions` on your PATH and wired to a KDE shortcut.
- [Examples](examples.md) — concrete walkthroughs: pipelines, batch runs, building a service.
- [CLI reference](guide/cli.md) — `run`, `picker`, `list`, `service ...`.
- [Service manifest](guide/service-manifest.md) — the YAML schema behind every service.
- [Creating services](guide/creating-services.md) — `service create`/`edit`/`set`/`duplicate`.
- [Pipelines](guide/pipelines.md) — composing services into shell pipelines.
- [Model profiles](guide/models.md) — `models.yaml` and how services reference it.
- [Service catalog](services/index.md) — every service currently defined, browsable.
- [Full catalog](catalog.md) — the 145-entry backlog this was built from, and what's still open.
- [Design principles](philosophy.md) — the architecture pattern and priorities behind the catalog.
- [Architecture](architecture.md) — how the engine is put together.
- [Roadmap](roadmap.md) — project history and what's next.
