# Service manifest

Every service is one file, `services/<id>.yaml`. This is the actual
schema `ai_actions.core.load_service()` reads — not a separate
description of it, so it can't drift.

```yaml
id: proofread
name: Proofread
category: writing
model: local

description: >
  Correct spelling, grammar and punctuation while preserving the
  author's wording and style.

prompt:
  system: |
    You are a proofreader.
    Correct spelling, grammar and punctuation errors only.
    Preserve the author's wording, tone, language and formatting.
    Output only the corrected text.

review: diff
clipboard_on_accept: replace
```

## Fields

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Must match the filename (`<id>.yaml`) — `service validate` checks this. |
| `name` | yes | Display name, shown in `list`/`picker`/the review dialog title. |
| `category` | yes | Free-text grouping, used by `list --category` and the picker's icon lookup. Run `service categories` to see what's already in use before inventing a new one. |
| `model` | yes | A profile name from `models.yaml` (see [Model profiles](models.md)). `service validate` flags a reference that doesn't resolve. |
| `prompt.system` | yes | The system prompt sent with every request. This is the entire behavior of the service — see below for what makes one good. |
| `description` | no | One line, shown in `list`/`show`/the generated [service catalog](../services/index.md). |
| `review` | no (default `text`) | `diff` — word-level diff view, Accept/Reject. `text` — read-only view, manual Copy button. Anything else fails `validate`. |
| `clipboard_on_accept` | no (default `none`) | `replace` — Accept writes the result to the clipboard. `none` — it doesn't (still copyable manually in `review: text` mode). Anything else fails `validate`. |
| `verify` | no (default none) | `crossref` — resolve each input line against Crossref before the model call (see below). Anything else fails `validate`. |
| `corpus` | no (default none) | A corpus id under `corpora/` to search before the model call (see below). `service validate` flags a corpus that doesn't exist. |

## Choosing `review`/`clipboard_on_accept`

Use `review: diff` + `clipboard_on_accept: replace` when the output is a
**revision of the input** you'd plausibly want to paste back over it
(proofread, style rewrites, tone fixes) — comparable length and shape to
the input.

Use `review: text` + `clipboard_on_accept: none` for anything that
**produces something new** rather than revising the input — a summary, a
review, extracted action items, generated questions. A diff between a
full paper and a 150-word abstract of it isn't meaningful; showing the
result plainly with a manual Copy button is.

## Writing a good prompt

The services in this repo follow a few conventions worth keeping:

- State the role in one line ("You are a proofreader.").
- Give concrete, checkable instructions rather than vague ones ("Correct
  spelling, grammar and punctuation errors only" rather than "improve the
  writing").
- Say explicitly what *not* to do when it matters ("Do not add or remove
  serial commas", "Do not overstate the findings beyond what the text
  supports").
- End generative/rewrite prompts with `Output only the result` — the
  engine sends the model's reply as-is; without this it tends to add
  preamble ("Here's the corrected text:").
- For anything with a real-world consequence (statistical/methodology
  advice, disclosures), say plainly that it's advisory and doesn't replace
  a qualified human.

## Model reference resolution

`model: local` looks up `local:` in `models.yaml`. `service show <id>`
resolves and displays this for you; `service validate` flags it if the
name doesn't exist.

## `verify: crossref`

Set this when the service needs to check pasted references against a
real bibliographic database rather than relying on the model's own
(unreliable) recollection of what exists. Before the model is called,
`ai_actions.verify.resolve_references()` treats the input as **one
reference per line**, looks each one up against
[Crossref](https://api.crossref.org)'s public `works` API, and appends a
`CROSSREF LOOKUP RESULTS` block to the input the model sees — the
model's job is to reason over that block, not to invent metadata itself.
A per-line lookup failure (no network, no match, an ambiguous result)
never aborts the run; it just shows up as `lookup_failed`/`no_match` for
that one line, and the prompt should tell the model how to talk about
that (see `services/reference-check.yaml` for the pattern: a miss is
"could not verify," never "is fake").

This is the one case in the whole engine where running a service means
something other than the pasted text reaching only your configured model
endpoint — each reference line is also sent to Crossref's public API.
`service show <id>` prints a `verify:` line as a heads-up before you run
one.

An optional `AI_ACTIONS_CONTACT_EMAIL` environment variable gets sent to
Crossref as a courtesy identifier (their "polite pool," for more reliable
service) — see [Install](../install.md).

## `corpus: <id>`

Set this when the service should answer from a specific set of documents
(a course's own material, a policy document, a department's knowledge
base) rather than from the model's own memory. Before the model is
called, `ai_actions.corpus.search_corpus()` ranks that corpus's chunks
against the input (the user's question) with BM25 lexical search and
prepends the top matches as a `RETRIEVED CONTEXT` block — the prompt's
job is to answer from that block, and to say plainly when it doesn't
contain the answer, never to fall back on general knowledge. See
[Corpora](corpora.md) for the full picture: what a corpus actually is, why
lexical search rather than embeddings, and how to build your own. Unlike
`verify`, this never touches the network — `service show <id>` prints a
`corpus:` line either way, so it's clear which kind of external access
(if any) a given service involves.
