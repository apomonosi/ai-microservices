# Do you need the cloud for this?

Short answer: for almost everything this project does, no.

If you've used a cloud AI chat product, it's easy to assume that's the
only way to get AI help — that you need an account, a subscription, and
an internet connection every time. For the kind of task this project
targets (fix this abstract's grammar, check these numbers, turn these
slides into a study guide), that assumption is wrong, and it's worth
spelling out plainly why, because the "install a local model" step in
[Install](install.md) can look intimidating if you don't already know
this.

## What "a small model" actually means

A large cloud AI service runs a model with hundreds of billions of
parameters, on racks of specialized hardware, because it's built to
handle absolutely anything you might ask it — write a novel, debug
unfamiliar code, hold a wide-ranging conversation.

A **small model** is the same basic technology at a much smaller size —
typically 4 to 14 billion parameters — distributed as a file a few
gigabytes in size (this project's own `models.yaml` example uses one
called `gemma-4-E4B-it-UD-Q5_K_XL.gguf` — the `.gguf` part just means
it's been compressed, or "quantized," to run efficiently on ordinary
hardware). It runs entirely on your own computer: no account, no
internet connection needed once it's downloaded, no data sent anywhere.

## Is your computer capable enough? Probably.

You very likely already own hardware that can run one of these
comfortably:

- **A laptop from the last two or three years.** Even without a
  dedicated graphics card, 16GB or more of memory is usually enough to
  run a small model at a readable pace — a few seconds per response
  rather than instant, but entirely usable for checking a paragraph or
  summarizing a page.
- **A desktop with a mid-range gaming GPU** (8GB of video memory or
  more). This is where it gets fast — often faster than waiting on a
  cloud service's queue.
- **A shared department or lab workstation.** If one exists, it's
  probably already overpowered for this — one workstation can serve an
  entire small team, each person pointing their own `models.yaml` at it
  over the network (see [Model profiles](guide/models.md)).

If none of that describes your situation, cloud or a shared institutional
endpoint is a perfectly reasonable model profile too — `models.yaml`
doesn't care where the endpoint lives, see below.

## But is it actually good enough?

This is the part that's easy to doubt, because "small" sounds like a
compromise. For the mundane, checkable tasks this project's
[catalog](catalog.md) is built from, it isn't. Every one of the 61
services already in `services/*.yaml` is configured to run on the
`local` profile in the example above, and the reason is in [Design
principles](philosophy.md): checking whether a citation supports a
claim, whether two numbers agree, or whether a rubric covers its stated
objectives is exactly the kind of task where a small model is reliable —
and if it does miss something, you notice, because you're reading the
same manuscript it just read. The cases that genuinely need a much
larger model — broad, open-ended literary judgement rather than a
checkable fact — are the minority [Design principles](philosophy.md)
also describes, and nothing stops you from pointing just those specific
services at a cloud endpoint instead, service by service.

## The exception: three services that do talk to the network

Everything above is true of every service except three:
[`reference-check`](services/reference-check.md),
[`doi-resolve`](services/doi-resolve.md), and
[`suspicious-reference-detect`](services/suspicious-reference-detect.md).
Checking whether a citation is real isn't something any model, local or
cloud, can do from its own training — it has to look the reference up
against an actual bibliographic database. These three send each pasted
reference line (not the rest of your document) to
[Crossref](https://api.crossref.org)'s free public API to do that lookup,
in addition to your local model. `ai-actions service show <id>` prints a
`verify:` line as a heads-up before you run one — see [Service
manifest](guide/service-manifest.md#verify-crossref) for exactly what
gets sent. Every other service in the catalog never leaves your machine.

Worth being precise about one thing that might look similar but isn't:
[`course-qa`](services/course-qa.md), [`policy-qa`](services/policy-qa.md),
and [`department-knowledge-assistant`](services/department-knowledge-assistant.md)
also pull in outside material — your course notes, a policy document — but
that material lives in a plain folder on your own disk (`corpora/`, see
[Corpora](guide/corpora.md)) and is searched locally. Nothing about them
talks to a network. `service show <id>` still prints a line either way
(`corpus:` for these, `verify:` for the Crossref three) so you never have
to guess which kind of service you're looking at.

## Getting a model running, without a computer-science degree

This project just needs *something* that speaks the OpenAI chat-completion
API on a URL — it doesn't care how that URL came to exist. Two realistic
starting points:

**If you don't want to touch a terminal:** install
[LM Studio](https://lmstudio.ai) (Windows/Mac/Linux, plain installer, no
command line). Inside it, search for a small model (a 4B–8B Gemma or Qwen
model is a solid default), download it, then turn on its **Local
Server** feature — it'll show you a URL, typically
`http://localhost:1234/v1`. That's what goes in `models.yaml`.

**If you're comfortable with a terminal:** [llama.cpp](https://github.com/ggml-org/llama.cpp)'s
`llama-server` does the same job from the command line and is what the
`models.yaml` example on this page assumes — it listens on port `8080`
by default (the example uses `8081`; either is fine, just match whatever
port it prints on startup).

Either way, the result is a URL — plug it into `models.yaml` as shown in
[Model profiles](guide/models.md), and every service in the
[catalog](catalog.md) starts working against it. See
[Install](install.md) for the rest of the setup.
