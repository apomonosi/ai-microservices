# Examples

Real workflows, each a variation on the same shape: text in, a service,
text out. See [CLI reference](guide/cli.md) for every flag and
[Pipelines](guide/pipelines.md) for the `--file`/`--stdin`/`--output`
mechanics these build on.

## Proofread a file like a Unix filter

The whole point of `--stdin`/`--no-gui`: a service behaves like `sort` or
`grep`, not like an app you open.

```bash
cat manuscript.md | ai-actions run proofread --stdin --no-gui | tee proofread.md
```

`tee` here is doing its normal job — printing to the terminal *and*
saving to `proofread.md` — nothing about `ai-actions` is special-cased for
it. Drop `--no-gui` and it's the same command with a review step in the
middle: nothing is written until you Accept.

## Chain two checks in one pipeline

Services compose because each one is just text in, text out. Running a
structure check and then softening the tone of what comes back:

```bash
cat manuscript.md \
  | ai-actions run structure-review --stdin --no-gui \
  | ai-actions run reviewer-tone-fix --stdin --no-gui --output review.txt
```

Each stage is independently a full service — you could stop after the
first command and read the raw structural critique, or run
[`structure-review`](services/structure-review.md) alone against ten
different manuscripts in a loop. Nothing about chaining them is a separate
feature.

## Batch-check a folder without reviewing every result

The essay behind this project's [design principles](philosophy.md) puts it
plainly: checking is cheap to run and cheap to be wrong about, so run it
often. `--no-gui` is what makes that practical for a whole folder at once:

```bash
for f in drafts/*.md; do
  ai-actions run numerical-consistency-check --file "$f" --no-gui \
    --output "checked/$(basename "$f")"
done
```

Fifty files checked unattended; you only open the ones with something to
say. Compare that with a chat assistant, where each of those fifty is a
manual copy-paste round trip.

## Build a service and use it the same afternoon

Say proofreading a manuscript keeps missing one specific thing: unexplained
acronyms. Rather than repeating that instruction by hand every time, it
becomes its own service — the "cheap to build" half of [design
principles](philosophy.md) in practice:

```bash
ai-actions service create acronym-check \
  --category writing \
  --review text \
  --description "List every acronym used before it's defined." \
  --prompt "List every acronym in the input that appears before it is spelled out in full. For each, give the acronym, the sentence it first appears in, and nothing else." \
  --no-edit

ai-actions service validate acronym-check
ai-actions run acronym-check --file manuscript.md --no-gui
```

`--no-edit` skips opening `$EDITOR` since the prompt was short enough to
pass inline; for anything longer, drop it and refine the prompt in your
editor before the first real run. See [Creating services](guide/creating-services.md)
for the rest of the lifecycle — duplicating, adjusting fields, deleting.

## Check a bibliography against a real database

Unlike every other service, [`reference-check`](services/reference-check.md)
talks to Crossref's public API as well as your local model — see [Do you
need the cloud?](local-models.md#the-exception-three-services-that-do-talk-to-the-network).
Paste one reference per line, real ones and a fabricated one included:

```bash
ai-actions run reference-check --text "$(cat <<'EOF'
Vaswani et al., Attention is all you need, 2017
Smith and Jones, A Totally Fabricated Study of Nothing in Particular, Journal of Made-Up Results, 2099
EOF
)" --no-gui
```

The first line resolves cleanly against Crossref's records; the second
won't — and the output says so as "could not verify," not "is fake":
Crossref not finding something is evidence of absence at best, never
proof. `service show reference-check` prints a `verify:` line up front so
this is never a surprise. `doi-resolve` and
[`suspicious-reference-detect`](services/suspicious-reference-detect.md)
run the same lookup, framed as a plain metadata report and a
verified/ambiguous/not-found classification respectively.

## Not sure which service you want?

```bash
ai-actions picker --file manuscript.md --output result.txt
```

Search-as-you-type over all [58 services](services/index.md), then the
same review step as `run` — just with the choice of *what* to run made
interactively instead of on the command line.
