# Corpora

A **corpus** is what a service declaring `corpus: <id>` in its manifest
searches before asking the model anything — the retrieval half of the
"LLM + retrieval + validation" pattern [Design principles](../philosophy.md)
describes, used by [`course-qa`](../services/course-qa.md),
[`policy-qa`](../services/policy-qa.md), and
[`department-knowledge-assistant`](../services/department-knowledge-assistant.md).

## What it actually is

A corpus is a plain directory of `.txt`/`.md` files under `corpora/`.
That's the whole data model — no database, no ingestion step, no
"build index" command. Drop files in with `cp`, a text editor, or your
own export from wherever the real document lives; `ai-actions` reads
them fresh every time a corpus-backed service runs, the same convention
`services/*.yaml` and `models.yaml` already follow.

```
corpora/
  examples/
    course/
      syllabus.txt
      schedule.txt
  cs101-notes/        # a corpus you create yourself
    lecture-1.txt
```

A corpus id is its path relative to `corpora/` — `examples/course` above,
or just `cs101-notes` for a flat one. `service.yaml`'s `corpus:` field
names one directly.

## Lexical search, not embeddings

Retrieval here is [BM25](https://en.wikipedia.org/wiki/Okapi_BM25) — a
decades-old, well-understood lexical ranking algorithm, implemented in
`ai_actions/corpus.py` with nothing beyond Python's standard library. No
embedding model, no vector database. See [Architecture](../architecture.md)
for why that's the right trade-off at this project's scale: a syllabus or
a policy document is dozens to a few hundred paragraphs, not millions,
and BM25 scores all of them in milliseconds with zero setup. The
trade-off is real and worth knowing: BM25 matches on shared words, not
meaning — a question phrased very differently from the source document
("penalty for handing things in late" vs. a document that only ever says
"late submission") can rank the right paragraph lower than an exact-
wording query would. It's the same "smallest real version first" call
this project already made for [Crossref lookups](service-manifest.md#verify-crossref);
an embedding-based upgrade stays possible later if a real corpus
demonstrates the need.

Every corpus-backed service is fully local — unlike `verify: crossref`,
searching a corpus never leaves your machine. See
[Do you need the cloud?](../local-models.md).

## Chunking

Each document is split into paragraphs (on blank lines); a paragraph
longer than about 200 words is split further so no single chunk is too
large to usefully quote in a prompt. A file that can't be read as text
(binary, wrong encoding) is skipped rather than failing the whole corpus.

## Inspecting a corpus

```bash
ai-actions corpus list                    # every corpus id found, with chunk counts
ai-actions corpus show examples/course    # files, chunk count, word count
```

`ai-actions service show course-qa` also prints a `corpus:` line with the
resolved chunk count, so it's visible up front what's actually backing a
given service.

## Your own corpus stays private by default

`.gitignore` excludes everything under `corpora/` except
`corpora/examples/` — the three small, fictional demo corpora shipped
with this repo. A real corpus (your actual course notes, an HR policy,
department documents) is never committed unless you deliberately
override that, matching this project's own "local or nothing for
anything unpublished" stance from [Roadmap](../roadmap.md).

## Building a service around a new corpus

```bash
mkdir -p corpora/cs101-notes
cp ~/teaching/cs101/*.md corpora/cs101-notes/
ai-actions service duplicate course-qa cs101-qa --no-edit
ai-actions service set cs101-qa --corpus cs101-notes
ai-actions service validate cs101-qa
ai-actions run cs101-qa --text "When is the midterm?"
```

`service duplicate` copies `course-qa`'s already-written prompt (answer
only from context, say plainly when it doesn't know); `service set
--corpus` just repoints which corpus it searches.
