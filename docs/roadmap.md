# Roadmap

## Why Python + PySide6, not C++/Qt6/KF6

The original brainstorm (`ai-microservices.plan.md` in the repo root)
proposed a C++/Qt6/KDE Frameworks 6 desktop application — KGlobalAccel,
KDBusService, Kirigami/QML, CMake — as the production architecture for
turning the 145-service brainstorm (now the [full catalog](catalog.md))
into a KDE-native AI action platform.

That's oversized for what this actually is: a personal, single-user tool,
built a few hours a week, by someone with some C++ but no Qt/KF6
experience. The one thing that argument got right — "professional-looking
UI" — turns out to come from Qt's own rendering and Breeze theming, not
from the C++ language. **PySide6** (Qt for Python) gives the identical
Qt6 widget/QML stack at a fraction of the engineering cost. The C++
rewrite only pays for itself when *distributing* to many users outside
your own machine, which was never the goal here.

What survived from that original plan: **services are data, not code** —
the one idea that made it sound in the first place.

## Phase history

The MVP was: global shortcut → clipboard → service → review → clipboard,
plus a picker for choosing between services. All of it shipped:

1. **Formalize existing services** — the 3 original services (proofread,
   translate, code-assist) became `services/*.yaml` + `models.yaml`, no
   runtime change yet.
2. **Python engine core** — `ai_actions/core.py` (load YAML, call the
   endpoint) + a bare CLI.
3. **Result Inspector** — the review dialog (diff view, Accept/Reject),
   wired to the clipboard.
4. **Action picker** — the searchable list; **this was the MVP
   milestone**, proving the full architecture end to end.

One real deviation from the original plan happened in phase 2: `QClipboard`
was tried first, as planned, but proved unreliable on Wayland — reading
immediately after constructing `QGuiApplication` races the compositor's
async clipboard-offer handshake, with no event loop yet running to let it
settle, and consistently returned empty text (confirmed directly against
Qt on the target machine). The fix was `wl-paste`/`wl-copy` (Wayland) and
`xclip` (X11) via subprocess — what the original bash-script prototype
already used successfully, and `wl-copy` self-daemonizes to keep serving
the clipboard, which is cleaner than the manual delay the original plan
anticipated needing.

**Still not started, and explicitly optional** — nothing so far has
surfaced an actual need for any of these:

- A Kirigami/QML picker, if the Widgets one ever stops feeling polished
  enough.
- Visual polish (QSS, a tray icon, background notifications).
- A resident background daemon, if per-invocation Python/Qt startup
  latency (~200–400ms) ever becomes noticeable next to LLM response times
  (1s+).

## Beyond the original plan

Real usage surfaced needs the original plan didn't anticipate:

- **Pipeline I/O** — `--file`/`--stdin` input and `--output`, so services
  compose into shell pipelines. Gated by the review dialog exactly like
  the clipboard is.
- **Service library management** (`ai-actions service ...`) — a full
  CRUD surface (`list`/`show`/`search`/`categories`/`validate`,
  `create`/`edit`/`set`/`duplicate`/`delete`) over `services/*.yaml`, once
  hand-editing dozens of YAML files by hand stopped scaling. Building
  `service search` immediately found a real, previously-silent bug: a
  service's `name:` field containing an unescaped `#` had been truncated
  by YAML's comment parsing since the file was added.
- **A test suite** (pytest) and **CI** (GitHub Actions) — each phase had
  been verified with hand-rolled sandbox scripts up to this point;
  formalizing them means regressions get caught automatically as the
  codebase keeps growing.
- **An installable CLI** — `pyproject.toml` registers `ai-actions` as a
  console-script entry point. Deliberately an *editable* install: see
  [Architecture](architecture.md#design-decisions-worth-knowing).
- **This documentation site** — generated with MkDocs + Material; the
  [service catalog](services/index.md) is generated directly from
  `services/*.yaml` via the same loader the CLI uses, so it can't drift
  from what `ai-actions service show` actually reports.

## Growing the service library

Growing the catalog is adding YAML files — no engine changes needed. Pull
from the [full catalog](catalog.md) opportunistically; it's a backlog, not
a deliverable, and there's no fixed target count.

**In scope**: single pasted-text input, one system prompt, no external
tools/APIs/RAG, no images, no multi-document input, not redundant with an
existing service.

**Deliberately out of scope for now** — each of these is a separate
mini-project, not a quick addition, and should only be attempted once
there's an actual reason to (a real need for citation verification, say),
not preemptively:

- Anything needing real verification against an external registry
  (Crossref/OpenAlex/DOI resolution) — as opposed to the
  citation-completeness/-overuse checkers already built, which work
  purely on the pasted text's own internal consistency.
- Anything needing a persistent corpus or RAG (course/policy Q&A,
  department/lab knowledge assistants, equipment manuals).
- Anything needing image input — the engine is text-only.
- Multi-turn/conversational services — the engine is single-shot
  request/response.
- Genuinely multi-document inputs that can't reasonably be combined into
  one paste.
- The "preflight"/linting pipelines — explicitly multi-check pipelines in
  the source brainstorm, not a single prompt.
- Close near-duplicates of an already-built service, to keep the catalog
  from becoming repetitive.
