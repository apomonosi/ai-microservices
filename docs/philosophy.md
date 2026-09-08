# Design principles

These are the working rules the [catalog](catalog.md) actually gets built
against — not aspirations, decisions that show up directly in what's
already there and what still isn't.

## Automate the mechanical, augment the judgement

Fixing grammar, flagging an inconsistent number, checking that a rubric
covers its stated learning objectives — these are mechanical. A model
either gets them right or the mismatch is visible and cheap to check.
Deciding whether a thesis makes a genuine contribution, or whether a study
design is sound, is not mechanical — it's the researcher's judgement to
make, and a service's job there is to sharpen the question, not answer it.

That's why [`research-question-critic`](services/research-question-critic.md)
returns *what's unclear about this question* rather than a better question,
why [`hypothesis-review`](services/hypothesis-review.md) checks
falsifiability rather than proposing a hypothesis, and why nothing in the
catalog is titled "grade this" or "decide this" — see
[`student-feedback-generate`](services/student-feedback-generate.md) for the
concrete version of that line: formative feedback, not a grade.

## The pattern behind a service that checks something

Most of the catalog's still-open, highest-value entries (the reference and
citation checkers, rows 11–20) share one shape, and it's worth stating
explicitly because it's the reason those specific entries haven't been
built yet — the engine only does the last two steps so far:

```text
input → resolve against a source of truth → LLM reasons over that → structured output → human
```

A reference checker should never ask a model whether a citation is real —
models don't know that, they pattern-match. It asks the model to compare
the citation against a resolved DOI record. The model's job is reasoning
over *verified* material, not recalling facts. Every already-built service
skips the middle step because its input is fully self-contained — a
manuscript's own text is enough to check its own terminology or its own
internal numbers — which is exactly why those were cheap to build first,
and why the [full catalog](catalog.md#what-the-still-open-entries-share)'s
verification and retrieval layers are the two biggest blocks of remaining
work.

## What decides what gets built next

Not "what can a model do" — a genuinely useful rule of thumb, applied
informally every time a new entry moves from the catalog into
`services/*.yaml`:

| Question | Why it matters |
|---|---|
| How often does someone actually hit this? | Volume is where the time saved adds up. |
| Is a wrong answer cheap or expensive to catch? | Decides whether it belongs in this engine at all — see [Roadmap](roadmap.md#growing-the-service-library) for what's explicitly out of scope. |
| Can the input alone answer it, or does it need retrieval/state? | Self-contained input is a same-afternoon YAML file; anything else is its own project. |
| Is a generic chat assistant already good enough for this? | If yes, a dedicated service isn't worth the maintenance. |

That last row is the practical filter behind [Roadmap](roadmap.md)'s "in
scope" rules: single pasted-text input, one system prompt, no external
tools, not redundant with an existing service. Everything currently in
`services/*.yaml` passed all four; everything still marked "not started" in
the [catalog](catalog.md) failed at least one — usually the third.
