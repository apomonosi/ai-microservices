# Roadmap

## Context

The original brainstorm in `ai-microservices.plan.md` proposed a C++/Qt6/KDE
Frameworks 6 desktop application (KGlobalAccel, KDBusService, Kirigami/QML,
CMake) as the production architecture for turning the 145 services in
`ai-microservices.tables.md` into a KDE-native AI action platform.

After reflection, that plan is oversized for the actual goal:

- **Audience**: personal tool, single user (KDE-only is fine).
- **Skill base**: some C++, no Qt/KF6 experience yet.
- **Time budget**: a few hours a week, indefinitely.
- **What "professional-looking UI" actually requires**: Qt's own rendering
  and Breeze theming — not the C++ language. **PySide6** (Qt for Python)
  gives the identical Qt6 widget/QML stack, including Kirigami components
  if wanted later, with no CMake, no KF6 C++ bindings, and no compiled
  binary. The C++ rewrite only pays for itself when *distributing* to many
  users outside your own machine — which is explicitly not the goal here.

This roadmap replaces the C++/Kirigami plan with a **Python + PySide6 +
YAML** architecture that reaches the same MVP (global shortcut → clipboard
→ service → review → clipboard, plus a picker for multiple services) at a
fraction of the engineering cost, while keeping the same core idea that
made the original plan sound: **services are data, not code.**

The existing bash-script workflow keeps running unchanged until each phase
below has a working replacement — nothing gets switched over until it's
proven.

## Stack

| Concern | Choice | Why |
|---|---|---|
| Language | Python 3 | Already used for the review box |
| UI toolkit | PySide6 (Qt for Python) | Real Qt6 widgets, Breeze-themed automatically on KDE |
| Service/model config | YAML (`PyYAML`) | Services and model endpoints are declarative data, not code |
| HTTP | `requests` or `httpx` | Talks to the OpenAI-compatible llama-server endpoint |
| Clipboard | `wl-clipboard` (Wayland) / `xclip` (X11) via subprocess | See Phase 1 note — `QClipboard` proved unreliable here in practice |
| Global shortcuts | KDE System Settings → Shortcuts → custom command | No shortcut-registration code needed |
| Packaging | venv + a thin launcher script | No CMake, no compiled binary |

Deliberately **not** used (unless a real need shows up later): CMake/ECM,
KGlobalAccel, KDBusService, KConfig, a resident daemon, D-Bus APIs for
other apps, Klipper integration, a tool registry, an evaluation harness.
All of these solve problems that only exist at institutional scale or with
many concurrent users.

## Phases

### Phase 0 — Formalize existing services ✅ Done
Write `services/*.yaml` for the 3 existing services (proofread,
translate-da, code-assist) and one `models.yaml` for the llama-server
endpoint(s). Pure configuration; the bash script is untouched and keeps
working.

```yaml
# services/proofread.yaml
id: proofread
name: Proofread
category: writing
model: local-fast
prompt:
  system: |
    You are a proofreader. Correct spelling, grammar and punctuation only.
    Preserve the author's wording, tone and formatting.
    Output only the corrected text.
review: diff
clipboard_on_accept: replace
```

```yaml
# models.yaml
local-fast:
  type: openai-compatible
  url: http://127.0.0.1:8081/v1
  model: gemma
  timeout: 120
```

**Deliverable**: service/model definitions exist as data; nothing runtime
changes yet.

### Phase 1 — Python engine core ✅ Done
`ai_actions/core.py`: load YAML, build the chat-completion request, POST
to the endpoint, return the result text.
`ai_actions/cli.py`: `python -m ai_actions run <service-id>` reads the
clipboard, calls the core, prints/returns the result.

**What actually happened with the clipboard**: `QClipboard` was tried first
per this plan, but proved unreliable in practice — reading immediately
after constructing `QGuiApplication` races the Wayland compositor's async
clipboard-offer handshake, with no event loop running yet to let it settle,
and consistently returned empty text (confirmed directly against Qt on the
target machine). Switched to `wl-paste`/`wl-copy` (Wayland) and `xclip`
(X11) via subprocess instead — what the original bash script already used
successfully, and `wl-copy` self-daemonizes to keep serving the clipboard,
which is cleaner than the manual delay this plan anticipated needing.
`ai_actions/clipboard.py` still has room to revisit `QClipboard` once a
persistent Qt event loop exists (Phase 5), if ever needed.

**Deliverable**: the CLI functionally replaces the bash script for all 3
services.

### Phase 2 — Result Inspector (PySide6) ✅ Done
Port the existing review box into a `QDialog`: color-coded diff view,
Accept/Reject buttons, Enter/Esc keyboard handling. Wire it to the clipboard
on accept.

**Deliverable**: `Meta+Alt+P` (KDE custom shortcut) → `ai-actions run
proofread` → polished review popup → clipboard.

### Phase 3 — Action picker ✅ Done (MVP milestone reached)
`ai-actions picker`: a `QDialog` with a `QLineEdit` search filter over a
`QListWidget` (service name + category icon via `QIcon.fromTheme`), arrow-key
navigation, Enter to run.

**Deliverable**: `Meta+Alt+A` → picker → same engine, same review box, for
all services defined so far. **This is the MVP milestone** — it proves the
whole architecture (shortcut → picker → service → review → clipboard) end
to end.

### Phase 3.5 — Optional: Kirigami/QML picker — not started
Only if the Widgets picker doesn't feel polished enough. Nothing so far has
suggested it's needed. PySide6 can load Kirigami QML components via
`QQmlApplicationEngine` (`org.kde.kirigami`, already present as part of the
KDE runtime) — no C++, no KF6 bindings. Low-risk: touches only the picker
window, not the engine or review box.

### Phase 4 — Polish — not started
QSS styling pass if wanted; Breeze icons throughout; optional
`QSystemTrayIcon`; background-completion notifications via `notify-send` or
D-Bus instead of a focus-stealing popup. Still optional — no real friction
reported yet.

### Phase 5 — Optional: background daemon — not started
Only if per-invocation Python/Qt startup latency (~200-400ms) actually
becomes noticeable next to LLM response times (1s+). A small `pydbus`
session-bus service or Unix socket lets the shortcut talk to an
already-running process instead of a fresh interpreter each time. No signal
yet that this is worth doing.

## Beyond the original roadmap

The MVP (Phase 3) was the last thing this roadmap originally planned for.
Since then, real usage surfaced needs the original plan didn't anticipate,
and they've been built:

- **Pipeline I/O**: `run`/`picker` accept `--file`/`--stdin` input and
  `--output` (in addition to clipboard/`--text`), so services compose into
  shell pipelines, e.g. `cat draft.txt | ai-actions run proofread --stdin
  --no-gui -o out.txt`. `--output` is gated by the review dialog exactly
  like the clipboard is — nothing bypasses review by default.
- **Service library management** (`ai-actions service ...`): `list`,
  `show`, `search`, `categories`, `validate` (read-only), and `create`,
  `edit`, `set`, `duplicate`, `delete` (mutating) — a full CRUD surface over
  `services/*.yaml`, so managing dozens of services doesn't mean hand-editing
  YAML and hoping nothing's broken. `validate` checks model references,
  `review`/`clipboard_on_accept` values, non-empty prompts, and id/filename
  consistency; `list_services()` skips a broken file with a warning instead
  of crashing the whole picker.
- **Automated test suite**: `tests/` (pytest, 100+ tests) covers the engine,
  clipboard I/O, service management, the CLI end-to-end, and the GUI
  widgets. Run with `pytest` after `pip install -r requirements-dev.txt`.
- **CI**: `.github/workflows/tests.yml` runs the full suite (GUI tests
  included, via a headless Qt platform) on every push and pull request.
- **Installable CLI**: `pyproject.toml` registers `ai-actions` as a real
  console-script entry point (`pipx install -e .` or `pip install -e .`),
  so the command is just `ai-actions run proofread` — no more `python3 -m
  ai_actions`, though that still works identically. Deliberately an
  *editable* install, not a real one: `services/*.yaml`/`models.yaml` are
  hand-edited data that live in this checkout, not files a normal install
  would bundle into site-packages, so the installed command needs to keep
  pointing back at the real checkout.

## Growing the service library

Growing the catalog is just adding YAML files — no engine changes needed.
Pull from `ai-microservices.tables.md` opportunistically; it's a backlog,
not a deliverable, and there's no fixed target count. As of this writing the
library has 51 services, added in two batches using a consistent rule for
what qualifies as "just a YAML file" versus a separate mini-project:

**In scope** (single pasted-text input, one system prompt, no external
tools/APIs/RAG, no images, no multi-document input, not redundant with an
existing service): the bulk of the writing/reference/literature/paper-review/
thesis/research-design/teaching/communication services already added.

**Deliberately out of scope for now** — each is a separate mini-project,
not a quick addition:

- Anything needing real verification against an external registry
  (Crossref/OpenAlex/DOI resolution) — reference/citation *verifiers*, as
  opposed to the citation-completeness/-overuse checkers already built,
  which work purely on the pasted text's own internal consistency.
- Anything needing a persistent corpus or RAG (Course Q&A, Policy Q&A,
  department/lab knowledge assistants, equipment manuals).
- Anything needing image input (alt-text generation, chart explanation) —
  the engine is text-only.
- Multi-turn/conversational services (Viva Simulator, Socratic Tutor) — the
  engine is single-shot request/response.
- Genuinely multi-document inputs that can't reasonably be combined into
  one paste (journal-guideline adapters, reviewer-response checkers).
- The "preflight"/linting pipelines (Research Integrity Preflight, Academic
  Linter, and the various per-domain Preflight rows) — these are explicitly
  multi-check pipelines in the source brainstorm, not a single prompt.
- Close near-duplicates of an already-built service, to keep the picker
  from becoming repetitive — skipped even when technically in scope.

Attempt the harder categories above only once there's an actual reason to
(e.g. a real need for citation verification), not preemptively.
