# Master plan

Yes. I think this is a **much better framing** than thinking of the 145 items as 145 applications.

What you are really describing is a **KDE-native, clipboard-oriented AI action platform**: a small resident desktop service with global shortcuts, a polished action picker, configurable LLM backends, and a library of narrowly defined AI operations.

I looked specifically at the current KDE/Qt stack, including Plasma/KF6 global shortcuts, clipboard handling, Klipper's D-Bus interface, Kirigami, KDE configuration and D-Bus facilities, and the relevant language/tooling options. My conclusion is quite strong:

> **Build the production version in C++ + Qt 6 + KDE Frameworks 6, with QML/Kirigami for the polished UI.**
>
> Keep the AI services themselves as declarative/configurable service definitions, not hard-coded GUI code.
>
> Use a small CLI executable as the public automation interface, while the resident GUI process handles shortcuts, clipboard, service selection, configuration and jobs.

That gives you something that could start as a personal KDE utility and eventually become a genuinely impressive university desktop AI platform.

---

# 1. The concept I'd build

I'd give the architecture a name along the lines of:

# **KDE AI Actions**

or perhaps:

# **Academic AI Actions**

The basic interaction becomes:

### Shortcut 1 — Quick Action

You copy text.

Press:

> **Meta + Alt + P**

and the predefined action runs:

```text
Clipboard
   ↓
Proofreader
   ↓
LLM endpoint
   ↓
Diff / result
   ↓
Accept
   ↓
Clipboard
```

No application window needs to be open.

---

### Shortcut 2 — Action Picker

Copy something.

Press:

> **Meta + Alt + A**

and a beautiful KDE-style launcher appears:

```text
┌─────────────────────────────────────────────────────────────┐
│  AI Actions                                          Esc    │
│                                                             │
│  🔎 Search actions...                                       │
│                                                             │
│  ✍ Writing                                                  │
│    Proofread                                  Ctrl+1        │
│    Improve academic style                                   │
│    Make concise                                             │
│                                                             │
│  📚 Research                                                │
│    Check references                                         │
│    Check citations                                          │
│    Review research question                                 │
│                                                             │
│  🌍 Language                                                │
│    Translate to Danish                                      │
│    Translate to English                                    │
│                                                             │
│  💻 Code                                                    │
│    Explain code                                             │
│    Review code                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Type:

> `citation`

and immediately get:

```text
📚 Verify citation
📚 Check citation support
📚 Find missing citations
📚 Format citations
```

Then Enter.

---

# 2. The really important architectural decision

I would **not** implement the 145 services as 145 C++ classes.

Instead:

```text
                 AI Actions Application
                         │
          ┌──────────────┼──────────────┐
          │              │              │
      Clipboard       UI/UX         Shortcuts
          │              │              │
          └──────────────┼──────────────┘
                         │
                  Action Engine
                         │
              ┌──────────┴──────────┐
              │                     │
       Service Registry        Job Manager
              │                     │
              ↓                     ↓
        service definition       LLM client
              │                     │
              ↓                     ↓
       prompt/configuration     endpoint/model
                                      │
                                      ↓
                               local / cloud LLM
```

The services should mostly be **data**.

For example:

```yaml
id: proofread
name: Proofread
category: writing
description: Correct spelling, grammar and punctuation.
input: text
output: text

model:
  endpoint: local-gemma
  temperature: 0.1
  thinking: false

prompt:
  system: |
    You are a proofreader...
    
review:
  type: diff

clipboard:
  output: replace
```

Then:

```yaml
id: translate-da
name: Translate to Danish
category: language
description: Translate the clipboard text to Danish.
input: text
output: text

model:
  endpoint: local-translator
  temperature: 0.1

prompt:
  system: |
    You are a translator.
    Translate to Danish.
    Output only the translation.

review:
  type: diff

clipboard:
  output: replace
```

The **same engine** handles both.

That's the key to scaling from 3 services to 145.

---

# 3. And some services need richer definitions

Your insight about different endpoints is exactly right.

A proofreader might need:

```yaml
model: local-small
```

while:

> Research methodology reviewer

might use:

```yaml
model: local-large
```

and:

> Citation verifier

might require:

```yaml
model: cloud-reasoning
tools:
  - crossref
  - openalex
```

So I'd make the service model something like:

```text
Service
 ├── identity
 ├── category
 ├── description
 ├── input requirements
 ├── output type
 ├── prompt
 ├── model profile
 ├── tools
 ├── processing pipeline
 ├── review mode
 ├── clipboard policy
 └── UI configuration
```

This makes the service catalog effectively **a programmable AI workflow language**.

---

# 4. There should actually be three layers

I would separate:

## Layer A — Action

What the user asks for.

Example:

> Proofread

## Layer B — Pipeline

How it happens.

```text
clipboard
 → LLM
 → diff
 → user approval
 → clipboard
```

## Layer C — Model profile

Where/how the intelligence runs.

```text
local-gemma
endpoint=http://127.0.0.1:8081
temperature=0.1
thinking=false
```

That means you can change the model without changing the service.

---

# 5. Model profiles

I'd make these first-class configuration objects.

For example:

```yaml
models:

  local-fast:
    type: openai-compatible
    url: http://127.0.0.1:8081/v1
    model: gemma
    timeout: 120

  local-reasoning:
    type: openai-compatible
    url: http://127.0.0.1:8082/v1
    model: qwen-reasoning
    timeout: 600

  university-cloud:
    type: openai-compatible
    url: https://...
    model: ...
    authentication: ...
```

Then:

```yaml
service:
  id: proofread
  model: local-fast
```

versus:

```yaml
service:
  id: paper-review
  model: local-reasoning
```

versus:

```yaml
service:
  id: citation-check
  model: university-cloud
  tools:
    - crossref
    - openalex
```

---

# 6. I strongly recommend an OpenAI-compatible client abstraction

Your current llama-server already exposes:

```text
/v1/chat/completions
```

That's excellent.

Don't make the application "a llama-server application."

Make it:

> **an OpenAI-compatible AI endpoint client**

Then the backend interface becomes something like:

```cpp
class LlmClient {
public:
    virtual LlmResponse complete(
        const LlmRequest& request
    ) = 0;
};
```

And implementations can eventually include:

```text
OpenAICompatibleClient
LocalLlamaClient
CloudClient
UniversityInferenceClient
MockClient
```

The UI doesn't care.

---

# 7. Why C++ is my recommendation

I considered the realistic candidates as:

| Language | KDE integration | UI    | Deployment | Performance | Verdict                 |
| -------- | --------------- | ----- | ---------- | ----------- | ----------------------- |
| **C++**  | ⭐⭐⭐⭐⭐           | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐⭐       | **Best**                |
| Rust     | ⭐⭐⭐             | ⭐⭐⭐⭐  | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐⭐       | Excellent second choice |
| Python   | ⭐⭐⭐⭐            | ⭐⭐⭐⭐  | ⭐⭐         | ⭐⭐⭐         | Excellent prototype     |
| Go       | ⭐⭐              | ⭐⭐    | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐⭐       | Not ideal here          |

KDE's current development stack is fundamentally Qt 6 + KDE Frameworks 6 + CMake, and KDE's own documentation uses C++ throughout its primary application-development path. ([Developer][1])

The big advantage isn't raw speed.

It's this:

> **You get native access to the KDE ecosystem.**

You can use:

* Qt 6
* KDE Frameworks 6
* KGlobalAccel
* KConfig
* KDBusService
* KStatusNotifierItem
* KDE notifications
* KDE application metadata
* KDE settings
* D-Bus
* Kirigami
* Breeze styling

without fighting language bindings.

---

# 8. Rust is interesting—but I'd make it second choice

Rust would be excellent for the **AI/networking/core engine**.

But your application is unusually KDE-specific.

You aren't merely making:

> a desktop GUI.

You're making:

> a **Plasma-integrated KDE application**.

That's where C++ has a significant advantage.

There are Rust/Qt integration technologies, but you would introduce another layer of bindings and interoperability precisely in the areas where you want the fewest surprises.

I'd therefore consider:

```text
C++ / Qt / KF6
       ↓
application
```

rather than:

```text
Rust
  ↓
Qt binding
  ↓
KDE binding
  ↓
QML
```

For a university project where maintainability matters, I'd keep the dependency stack boring.

---

# 9. Go is the one I'd reject

Go is fantastic for:

* backend services
* network services
* CLIs
* agents
* daemons

But it doesn't have the same natural relationship with KDE/Qt.

Your application is fundamentally:

> KDE desktop integration + GUI + global shortcuts + clipboard + D-Bus + system tray.

That's exactly where C++/Qt wins.

Go could make a very nice:

```text
AI backend daemon
```

but that's not the difficult part of your project.

---

# 10. Python is actually excellent for Phase 0

There's one qualification.

**Don't throw away your Python prototype.**

PySide6 is the official Qt Python binding and gives you access to Qt 6 APIs. KDE also documents PySide6/Kirigami development. ([Qt Documentation][2])

So I'd potentially do:

### Phase 0

```text
Python + PySide6
```

to rapidly prototype:

* action picker
* service definitions
* diff viewer
* endpoint configuration
* result handling

Then:

### Phase 1

Move the mature application to:

```text
C++ + Qt6 + KF6 + QML/Kirigami
```

However, Qt's Python deployment story is more involved than simply shipping a native KDE binary; Qt documents several freezing/deployment mechanisms, including `pyside6-deploy`. ([Qt Documentation][3])

For a personal tool, Python is fine.

For a university-distributed KDE application:

> **C++ wins.**

---

# 11. UI technology: Qt Widgets or QML/Kirigami?

I'd use **both, but primarily QML/Kirigami for the new UI.**

KDE describes Kirigami as a QML-based responsive UI framework, while the business logic should live in another language. ([Developer][4])

That's almost exactly your architecture.

### C++

Business logic:

```text
ClipboardManager
ShortcutManager
ServiceRegistry
ModelManager
JobManager
ReviewEngine
Configuration
D-Bus
```

### QML/Kirigami

Presentation:

```text
ActionPicker
ResultWindow
DiffView
ProgressView
Settings
ServiceEditor
ModelEditor
```

---

# 12. Why I prefer QML for the action picker

Your central interaction is not a conventional application window.

It's more like:

> KRunner + Spotlight + command palette + AI action launcher.

QML is extremely good for this.

You want:

* smooth filtering
* keyboard navigation
* animated selection
* category icons
* compact dialogs
* responsive layout
* search-as-you-type
* result previews

Kirigami is explicitly designed around reusable Qt Quick components and adaptive layouts. ([Developer][4])

---

# 13. But don't make the diff viewer in QML unnecessarily complicated

Your current PyQt diff viewer is actually conceptually good.

I'd retain the architecture:

```text
Original                 Corrected

The study show           The study shows
      ↑                       ↑
     RED                    GREEN
```

But make it considerably more polished.

Something like:

```text
┌─────────────────────────────────────────────────────────────┐
│ Proofread                                      3 changes    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ The results [show] a significant effect.                    │
│              ────                                            │
│              shows                                            │
│                                                             │
│ The [researchers has] demonstrated...                        │
│          ─────────────                                       │
│          researchers have                                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ 3 changes                                                   │
│                                                             │
│ [Reject]                         [Accept & Copy]             │
└─────────────────────────────────────────────────────────────┘
```

And ideally:

* `Enter` → accept
* `Esc` → reject
* `Ctrl+C` → copy selected result
* `Ctrl+Z` → undo
* clickable individual changes
* "accept all"
* "reject all"

---

# 14. Don't call it a "diff box"

I'd conceptualize the output as a **Result Inspector**.

Because eventually different services produce different result types.

### Proofreader

```text
Diff
```

### Translator

```text
Original | Translation
```

### Citation checker

```text
Claim
Citation
Evidence
Verdict
```

### Paper reviewer

```text
Finding
Severity
Evidence
Recommendation
```

### Literature screener

```text
Paper
Include / Exclude / Maybe
Reason
```

So:

```text
Service
   ↓
Result type
   ↓
Result renderer
```

This is another major architectural abstraction.

---

# 15. Result types

I'd define perhaps:

```text
PlainTextResult
MarkdownResult
DiffResult
TableResult
ListResult
StructuredReviewResult
CitationResult
ErrorResult
```

Then your UI knows how to render them.

For example:

```yaml
review:
  type: diff
```

versus:

```yaml
review:
  type: structured
  schema: citation-check
```

---

# 16. This also solves your "145 services" problem

Imagine service definitions:

```text
services/
    writing/
        proofread.yaml
        academic-style.yaml
        concise.yaml

    language/
        translate-da.yaml
        translate-en.yaml

    references/
        reference-check.yaml
        citation-check.yaml

    research/
        methodology-review.yaml
        paper-review.yaml
        research-question.yaml

    thesis/
        thesis-audit.yaml
        viva.yaml
```

You don't need to modify C++ when you add:

> "Make this paragraph more concise."

You add a YAML definition.

That's enormously important.

---

# 17. CLI architecture

I would actually create **one executable**.

Something like:

```bash
ai-actions
```

with:

```bash
ai-actions proofread
ai-actions translate-da
ai-actions citation-check
ai-actions review-paper
ai-actions --picker
ai-actions --quick
```

Or:

```bash
ai-actions run proofread
ai-actions run translate-da
ai-actions list
ai-actions config
ai-actions picker
```

The CLI becomes a first-class interface.

---

# 18. Use Qt's own command-line machinery first

For a KDE application, Qt's `QCommandLineParser` is already part of the natural KDE application stack; KDE's own application examples use it. ([Developer][5])

You don't actually need a third-party CLI parser unless you want particularly sophisticated subcommand handling.

If you do want one, **CLI11** is a mature C++11+ parser, header-only and currently actively maintained. ([GitHub][6])

My preference:

### GUI application

**QCommandLineParser**

### Standalone developer CLI with many subcommands

**CLI11**

But I would probably start with Qt's parser.

---

# 19. Global shortcuts: definitely use KGlobalAccel

This part of your concept is very well aligned with KDE.

KGlobalAccel provides configurable global accelerators that work even when the application's window doesn't have focus. ([KDE API Reference][7])

So you can have:

```text
Meta+Alt+P
```

→ default action

and:

```text
Meta+Alt+A
```

→ action picker.

And importantly, these should be registered as actual KDE global actions rather than relying on some custom X11 key-grabbing mechanism.

---

# 20. The application should be a resident process

This is an important change from your current shell script.

Don't launch the program from scratch for every shortcut.

Instead:

```text
                    Plasma session
                         │
                         ↓
                 ai-actions daemon
                    / resident
                         │
       ┌─────────────────┼─────────────────┐
       ↓                 ↓                 ↓
 Global shortcuts    System tray       D-Bus API
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ↓
                   Action engine
```

Then the shortcut response is immediate.

No startup latency.

---

# 21. System tray integration

I'd give it a small status icon.

KDE provides `KStatusNotifierItem` specifically for Status Notifier/desktop tray integration, with KDE's current KF6 API. ([KDE API Reference][8])

Tray menu:

```text
AI Actions

● Ready

Quick action
    Proofread

Choose action...

Recent
    Proofread
    Translate to Danish
    Code review

──────────────

Settings
Keyboard shortcuts
Models
Services

Quit
```

---

# 22. Clipboard: use QClipboard, not wl-paste

This is an important improvement over your current implementation.

Qt already provides `QClipboard` for accessing the system clipboard, including text, MIME data, images and the X11 selection where supported. ([Qt Documentation][9])

So the core should use:

```cpp
QGuiApplication::clipboard()
```

rather than:

```text
wl-paste
xclip
```

That makes the application more portable and removes shell-process overhead.

Qt's clipboard abstraction is also appropriate for Wayland and X11; the selection API is naturally conditional because the global mouse selection is an X11-style facility. ([Qt Documentation][9])

---

# 23. What about Klipper?

Here's the subtle part.

You **don't need Klipper to access the current clipboard**.

Use:

```text
QClipboard
```

for:

> current clipboard contents.

Klipper becomes useful when you want:

> **clipboard history**

or explicit interaction with KDE's clipboard manager.

The current Klipper source registers:

```text
org.kde.klipper
/klipper
```

on the session D-Bus and exposes clipboard-related methods/signals. ([GitHub][10])

For example, current KDE/Plasma material shows methods including:

```text
getClipboardContents
setClipboardContents
getClipboardHistoryItem
getClipboardHistoryMenu
clearClipboardContents
clearClipboardHistory
```

and the D-Bus interface is:

```text
org.kde.klipper.klipper
```

([Debian Sources][11])

So you can optionally have:

```text
Current clipboard
      ↓
QClipboard
```

and:

```text
Clipboard history
      ↓
Klipper D-Bus
```

---

# 24. That gives you an interesting future feature

Imagine:

### AI Actions → History

```text
Recent clipboard

1. Original paragraph
   → Proofread

2. Python code
   → Explain code

3. Danish paragraph
   → Translate English

4. Citation
   → Verify citation
```

The user could select **any previous Klipper item** and run an AI action on it.

That would be extremely powerful.

But I'd make this **Phase 2**, not part of the initial MVP.

---

# 25. D-Bus should be part of your architecture

KDE has `KDBusService`, which makes registering an application on D-Bus straightforward and supports unique application instances and activation. ([KDE API Reference][12])

I'd expose your own service:

```text
org.university.AIActions
```

perhaps:

```text
/org/university/AIActions
```

with methods conceptually like:

```text
RunAction("proofread")
RunAction("translate-da")
OpenPicker()
GetServices()
GetStatus()
```

Now other programs can invoke your AI services.

That's where this becomes **platform infrastructure**.

---

# 26. Imagine Dolphin integration

Right-click a file:

```text
Open with
...
AI Actions
    Summarize document
    Translate document
    Proofread document
    Extract references
    Review paper
```

Dolphin could invoke your D-Bus/CLI interface.

---

# 27. Imagine Kate integration

Select code:

```text
AI Actions
    Explain code
    Review code
    Optimize code
    Translate comments
```

Again:

```text
Kate
 ↓
AI Actions D-Bus/CLI
 ↓
service
```

No special AI implementation inside Kate.

---

# 28. Imagine LibreOffice

Select text:

```text
Ctrl+C
Meta+Alt+A
→ Proofread
```

Result:

```text
Accept & Copy
```

Paste back.

That is the beauty of the clipboard architecture.

---

# 29. The universal interaction model

The core UX should therefore be:

```text
                    SELECT SOMETHING
                          │
                          ↓
                       Ctrl+C
                          │
                          ↓
                    AI Actions
                          │
              ┌───────────┴───────────┐
              ↓                       ↓
         Quick Action            Action Picker
              │                       │
              ↓                       ↓
         Known service           Choose service
              │                       │
              └───────────┬───────────┘
                          ↓
                       Execute
                          │
                          ↓
                    Result Inspector
                          │
                  ┌───────┴───────┐
                  ↓               ↓
               Reject           Accept
                                  │
                                  ↓
                              Clipboard
```

That is **very elegant**.

---

# 30. One shortcut should not necessarily replace the clipboard immediately

I would change one thing in your current workflow.

For safe services:

> proofreader

you can offer:

```text
Accept & Copy
```

For dangerous/interpretive services:

> paper reviewer

don't automatically overwrite anything.

Instead:

```text
Result ready

[Copy result]
[Copy as Markdown]
[Save]
[Close]
```

And for verification services:

> citation checker

there may not even be a meaningful clipboard replacement.

So the action definition needs:

```yaml
output:
  mode: replace-clipboard
```

or:

```yaml
output:
  mode: inspect
```

or:

```yaml
output:
  mode: copy
```

or:

```yaml
output:
  mode: file
```

---

# 31. Think in terms of input/output contracts

This becomes critical as the service catalog grows.

### Simple

```text
text → text
```

### Review

```text
text → diff
```

### Verification

```text
text → structured findings
```

### Research

```text
document → structured report
```

### Coding

```text
code → annotated code/review
```

### Literature

```text
papers → classification
```

The service registry should specify this.

---

# 32. The service definition could look like this

Something like:

```yaml
id: citation-support
name: Check Citation Support
category: Research Integrity

description: >
  Determine whether the cited source actually supports
  the claim.

input:
  type: text
  source: clipboard

model:
  profile: research-reasoning

prompt:
  system: |
    You are a scholarly citation verification assistant...

tools:
  - scholarly-search
  - crossref

output:
  type: structured
  renderer: citation-review

clipboard:
  mode: inspect
```

That's already starting to look like a **domain-specific AI service manifest**.

---

# 33. And I'd give every service a risk classification

This is particularly important in a university.

```yaml
risk: low
```

for:

> spelling correction.

But:

```yaml
risk: high
```

for:

> research methodology assessment.

Then the UI can behave accordingly.

### Low risk

```text
Result ready
[Accept & Copy]
```

### Medium

```text
AI suggestion ready
[Review]
```

### High

```text
AI analysis

This output is advisory and should be
reviewed by a qualified researcher.

[Open report]
```

---

# 34. Also classify services by privacy

For example:

```yaml
privacy:
  classification: confidential
  allowed_models:
    - local
```

Then the application could **refuse to send confidential material to a cloud endpoint**.

This becomes very powerful in a university.

For example:

> unpublished manuscript

could be tagged:

```text
CONFIDENTIAL
```

and only models configured as:

```text
local / university-private
```

are selectable.

---

# 35. This is where your local LLM infrastructure becomes genuinely useful

Your model isn't just:

> "another AI."

It becomes the **private inference tier**.

For example:

```text
                    AI Actions
                        │
             ┌──────────┴───────────┐
             │                      │
         PRIVATE                 PUBLIC
             │                      │
        Local LLM             Cloud endpoint
             │                      │
   confidential research       public text
   thesis drafts               public literature
   internal policy             expensive reasoning
   unpublished papers
```

The service registry decides which is permissible.

---

# 36. Model selection should be automatic

The user shouldn't have to think:

> "Which model should proofreader use?"

They should see:

```text
Proofread
✓ Fast local model
```

While:

```text
Research Preflight
● Research reasoning model
● Literature retrieval
● Citation verification
```

The model profile is an implementation detail.

---

# 37. But Settings should expose it

Advanced users should be able to go:

```text
Settings
 ├── General
 ├── Shortcuts
 ├── Models
 │    ├── Local Fast
 │    ├── Local Reasoning
 │    └── University Cloud
 ├── Services
 ├── Privacy
 └── Advanced
```

For each model:

```text
Name:             Local Fast
Provider:         OpenAI-compatible
Endpoint:         http://127.0.0.1:8081/v1
Model:            gemma
Temperature:      0.1
Thinking:         Disabled
Timeout:          120 s

[Test Connection]
```

---

# 38. Configuration: use KConfig

This is another place where native KDE pays off.

KDE's KConfig/KConfigWidgets stack provides configuration facilities and standard KDE configuration dialogs. ([Developer][13])

So don't invent:

```text
~/.ai-actions/config.json
```

unless there's a reason.

Use KDE conventions.

Something like:

```text
~/.config/ai-actionsrc
```

for user settings.

Service definitions could live separately:

```text
~/.local/share/ai-actions/services/
```

or a system installation could provide:

```text
/usr/share/ai-actions/services/
```

with user overrides.

---

# 39. Built-in vs user services

I'd support three layers:

```text
System services
      ↓
University services
      ↓
User services
```

For example:

### System

```text
Proofread
Translate
Summarize
Explain code
```

### University

```text
University paper pre-review
University citation policy
University thesis audit
```

### User

```text
My Danish proofreading
My grant reviewer
My coding style
```

This could eventually be extremely powerful.

---

# 40. The action picker becomes the heart of the application

I would invest heavily here.

Think:

> **KRunner meets Raycast meets KDE's own design language.**

Search:

```text
┌──────────────────────────────────────────────────────┐
│ 🔍  citation_                                        │
├──────────────────────────────────────────────────────┤
│ 📚 Verify citation                                   │
│ 📚 Check citation support                            │
│ 📚 Find missing citations                            │
│ 📚 Format citation                                   │
└──────────────────────────────────────────────────────┘
```

Keyboard:

```text
↑ ↓     navigate
Enter   execute
Esc     close
Tab     categories
```

No mouse required.

---

# 41. Use Kirigami dialogs carefully

KDE's Human Interface Guidelines specifically caution against overusing modal dialogs; they recommend dialogs primarily for immediate decisions or progress that blocks continuation, and recommend menu/dialog components for choosing actions. ([Developer][14])

So I wouldn't make the picker a clunky modal form.

I'd make it:

> a compact **command palette**.

The result inspector can then be a separate window/dialog when necessary.

---

# 42. Result windows should remember context

Suppose you run:

> Proofread

The result window should say:

```text
Proofread

3 changes

Original:
...

Corrected:
...

Model:
Local Fast

Service:
Proofread

[Reject]  [Accept & Copy]
```

For a more complex service:

```text
Citation Review

4 claims examined
2 supported
1 partially supported
1 unsupported

...
```

---

# 43. Don't send gigantic clipboard content blindly

The engine should have an input policy.

```yaml
input:
  type: text
  max_characters: 50000
  truncation: reject
```

For larger material:

```text
Clipboard contains 180,000 characters.

This service requires document processing.

[Open as document]
[Cancel]
```

This prevents accidental enormous requests.

---

# 44. Add content-type detection

This is another very useful feature.

Clipboard may contain:

```text
plain text
HTML
rich text
image
URL
file list
code
```

The application can infer:

```text
Looks like Python code.
```

and the picker can prioritize:

```text
Explain code
Review code
Find bugs
Document code
```

If it looks like academic prose:

```text
Proofread
Academic style
Citation check
Summarize
```

This doesn't need to be an LLM.

Use heuristics first.

---

# 45. Eventually: contextual action ranking

You could have:

```text
AI Actions

Recommended

✍ Proofread
🌍 Translate to Danish
📝 Make concise

All actions...
```

based on:

* detected content type
* clipboard length
* language
* previous actions
* current application

But I would **not** build this initially.

---

# 46. A key architectural separation

I'd make the actual AI call asynchronous.

Never:

```text
UI → blocking curl
```

Instead:

```text
UI
 ↓
JobManager
 ↓
Network request
 ↓
streaming response
 ↓
UI update
```

That allows:

* cancellation
* timeout
* progress
* streaming
* multiple jobs
* retry
* error handling

---

# 47. Streaming should be supported from the beginning

Your current script waits for:

```text
curl
 ↓
entire response
```

For simple proofreading that's fine.

For:

> paper review

it becomes unpleasant.

Instead:

```text
Analyzing...

██████████░░░░░░

Findings
1. ...
2. ...
```

If the backend supports streaming, the client should expose it.

---

# 48. Job lifecycle

I would explicitly model:

```text
Queued
   ↓
Running
   ↓
Streaming
   ↓
Completed
   │
   ├── Accepted
   ├── Rejected
   └── Cancelled
```

and:

```text
Running
   ↓
Timeout
   ↓
Retry / Failed
```

This makes the system much more robust.

---

# 49. Notifications

Don't make every result steal focus.

For a quick action:

```text
✓ Proofreading complete
3 changes found
```

Use KDE's notification infrastructure.

For the tray/status item, `KStatusNotifierItem` also provides notification-related facilities, though KDE recommends KNotify where appropriate. ([KDE API Reference][8])

---

# 50. Proposed process architecture

I'd actually use **two processes** eventually.

### `ai-actions`

Resident GUI/controller.

```text
shortcuts
clipboard
UI
D-Bus
service registry
```

### `ai-actions-cli`

Thin CLI.

```text
stdin
clipboard
files
stdout
exit codes
```

Both talk to:

### `ai-actions-core`

Shared library.

```text
service engine
LLM client
configuration
result types
pipelines
```

So:

```text
                   ai-actions-core
                  /       |       \
                 /        |        \
                ↓         ↓         ↓
        ai-actions    ai-actions    D-Bus
            GUI           CLI       clients
```

This is a very clean architecture.

---

# 51. Why the CLI matters

You could then do:

```bash
echo "This are a test." | ai-actions run proofread
```

and get:

```text
This is a test.
```

Or:

```bash
cat paper.txt | ai-actions run paper-review
```

Or:

```bash
ai-actions run translate-da < input.txt > output.txt
```

Now the AI platform becomes useful from:

* shell
* scripts
* Kate
* Dolphin
* cron
* other applications
* university workflows

---

# 52. CLI11 vs QCommandLineParser

For the GUI executable, I'd use:

> **QCommandLineParser**

because you're already in Qt/KDE.

For a more elaborate standalone CLI:

> **CLI11**

is a very good choice; it is mature, header-only and BSD-3-Clause licensed. ([GitHub][6])

But I wouldn't introduce CLI11 merely because it looks fashionable.

Keep dependencies minimal.

---

# 53. Proposed repository structure

I'd structure the project roughly like:

```text
ai-actions/
│
├── CMakeLists.txt
├── README.md
├── LICENSE
│
├── src/
│   ├── core/
│   │   ├── service/
│   │   ├── pipeline/
│   │   ├── llm/
│   │   ├── result/
│   │   ├── job/
│   │   └── config/
│   │
│   ├── desktop/
│   │   ├── clipboard/
│   │   ├── shortcuts/
│   │   ├── dbus/
│   │   ├── tray/
│   │   └── notifications/
│   │
│   ├── gui/
│   │   ├── picker/
│   │   ├── result/
│   │   ├── settings/
│   │   └── qml/
│   │
│   └── cli/
│
├── services/
│   ├── writing/
│   ├── language/
│   ├── coding/
│   ├── research/
│   ├── references/
│   └── teaching/
│
├── models/
│   └── profiles.yaml
│
├── tests/
│
├── icons/
│
├── packaging/
│
└── docs/
```

---

# 54. The first service manifest

Your existing proofreader could become:

```yaml
id: proofread
name: Proofread
category: Writing
icon: tools-check-spelling

description: >
  Correct spelling, grammar and punctuation
  while preserving the author's wording and style.

input:
  type: text
  source: clipboard

model:
  profile: local-fast

prompt:
  system: |
    You are a proofreader.
    Correct spelling, grammar and punctuation errors only.
    Preserve the author's wording, tone, language and formatting.
    Keep the original spelling variant.
    Do not convert British and American spelling.
    Do not add or remove serial commas.
    Insert words that are clearly missing when required
    for grammatical correctness.
    Output only the corrected text.

output:
  type: diff

clipboard:
  on_accept: replace
```

Your current shell script essentially becomes the **first implementation of this manifest**.

That's a very good migration path.

---

# 55. Then the translator is trivial

```yaml
id: translate-da
name: Translate to Danish
category: Language
icon: languages

input:
  type: text
  source: clipboard

model:
  profile: local-translator

prompt:
  system: |
    You are a professional translator.
    Translate the input into Danish.
    Preserve formatting and meaning.
    Output only the translation.

output:
  type: diff

clipboard:
  on_accept: replace
```

No new C++ service implementation.

---

# 56. A citation checker is where the architecture becomes interesting

```yaml
id: citation-check
name: Check Citation
category: Research Integrity

input:
  type: text
  source: clipboard

model:
  profile: research-reasoning

tools:
  - crossref
  - openalex

pipeline:
  - extract-citations
  - resolve-references
  - retrieve-metadata
  - evaluate-support
  - produce-findings

output:
  type: structured
  renderer: citation-review
```

Now you have a genuine **AI workflow engine** rather than a prompt launcher.

---

# 57. Don't make everything a prompt

This is perhaps my strongest architectural recommendation.

Some services should be:

```text
LLM only
```

Some:

```text
LLM + deterministic processing
```

Some:

```text
LLM + retrieval
```

Some:

```text
LLM + external APIs
```

Some:

```text
LLM + local tools
```

For example:

### Proofreader

```text
LLM
```

### Reference checker

```text
LLM
+
Crossref
+
OpenAlex
```

### Research preflight

```text
LLM
+
document parser
+
citation checker
+
numerical consistency
+
journal rules
```

That is why `pipeline` should be a first-class concept.

---

# 58. The service engine should eventually support tools

Something like:

```text
ToolRegistry

crossref
openalex
pubmed
doi
filesystem
pdf-extractor
git
python
r
```

Then a service can declare:

```yaml
tools:
  - crossref
```

rather than hard-coding API calls into the service.

---

# 59. But don't make it an autonomous agent framework

I would resist the temptation.

You don't need:

> "Agent that can do anything."

You want:

> **small, deterministic, inspectable workflows.**

This is particularly appropriate for a university.

A service should say exactly:

```text
I take clipboard text.
I send it to model X.
I query Crossref.
I return this structured result.
```

That is much easier to trust and evaluate.

---

# 60. Evaluation needs to be a first-class part of the project

This is another area where the project could become academically interesting.

Every service should eventually have:

```text
service
 ↓
test corpus
 ↓
expected properties
 ↓
evaluation
 ↓
quality score
```

For proofreader:

```text
100 known examples
```

For translator:

```text
parallel corpus
```

For citation checker:

```text
verified citation/claim pairs
```

For paper reviewer:

```text
expert reviewer judgments
```

Then you can say:

> "Version 1.4 improved citation-support detection from 82% to 89%."

That is vastly better than:

> "The AI seems pretty good."

---

# 61. Build a service test harness

I'd add:

```bash
ai-actions test proofread
ai-actions test citation-check
ai-actions benchmark paper-review
```

Output:

```text
Proofread benchmark
────────────────────

Cases:          250
Passed:         239
Failed:          11

Precision:      96.2%
Recall:         93.8%

Regression:     PASS
```

That would be fantastic for a university project.

---

# 62. The first development phases I'd use

## Phase 0 — Preserve what already works

**Goal:** don't rewrite your successful prototype prematurely.

Keep:

```text
bash
 ↓
llama-server
 ↓
Python diff viewer
```

But formalize the service definition.

### Deliverable

```text
proofread.yaml
translate-da.yaml
```

---

# 63. Phase 1 — C++ shell

Build:

```text
ai-actions
```

with:

* Qt 6
* KF6
* CMake
* QClipboard
* KGlobalAccel
* KStatusNotifierItem
* KConfig
* QNetworkAccessManager
* QCommandLineParser

No fancy UI yet.

Implement:

```bash
ai-actions run proofread
```

and:

```text
global shortcut → proofread
```

---

# 64. Phase 2 — Resident application

Implement:

```text
ai-actions
```

as a persistent Plasma application.

Features:

* startup
* global shortcut
* clipboard
* model endpoint
* notifications
* tray icon

At this point:

> **Your current shell script is obsolete.**

But functionality remains the same.

---

# 65. Phase 3 — Action picker

This is where the project becomes visually impressive.

Build:

```text
Meta+Alt+A
```

→ Kirigami action picker.

Features:

* search
* categories
* icons
* keyboard navigation
* recently used
* favorites
* descriptions

---

# 66. Phase 4 — Result Inspector

Replace the Python dialog with a native KDE result interface.

Start with:

```text
DiffResult
```

Then add:

```text
TextResult
StructuredResult
TableResult
```

---

# 67. Phase 5 — Model profiles

Add:

```text
Settings → Models
```

with:

* endpoint
* model
* temperature
* thinking
* timeout
* authentication
* privacy classification

---

# 68. Phase 6 — Service catalog

Convert the first ~10 services into manifests.

I'd start with:

```text
proofread
translate-da
translate-en
summarize
rewrite-academic
make-concise
explain-code
review-code
citation-check
reference-check
```

---

# 69. Phase 7 — D-Bus API

Expose:

```text
RunAction
OpenPicker
GetServices
```

Now other KDE applications can integrate with it.

---

# 70. Phase 8 — Klipper integration

Only now.

Add:

```text
Use current clipboard
Use Klipper history
```

Potential UI:

```text
Input

● Current clipboard
○ Clipboard history
○ File
○ Selection
```

This turns Klipper into an optional input source rather than a dependency.

---

# 71. Phase 9 — Rich research services

Then implement:

```text
Reference Checker
Citation Checker
Citation–Claim Checker
Research Question Reviewer
Paper Pre-Reviewer
Thesis Auditor
```

These will stress the architecture and tell you whether your service abstraction is actually good.

---

# 72. Phase 10 — University service packs

Then introduce:

```text
University Academic Pack
```

with services such as:

```text
University policy checker
Thesis requirements checker
Research integrity preflight
Grant proposal reviewer
University citation conventions
```

This is where the project becomes institutionally interesting.

---

# 73. I would keep the 145-service catalog outside the binary

This is important.

Don't compile:

```cpp
if (service == "proofread") ...
else if (service == "translate") ...
else if ...
```

Instead:

```text
service registry
        ↓
manifest
        ↓
generic engine
```

The binary becomes relatively stable.

The service catalog can evolve weekly.

---

# 74. And support service packs

For example:

```text
ai-actions-core
ai-actions-academic
ai-actions-university-x
ai-actions-computer-science
```

A department could install its own service pack.

---

# 75. One especially powerful feature: favorites

The picker could show:

```text
Favorites

★ Proofread
★ Translate → Danish
★ Explain Code
★ Citation Check
★ Summarize
```

And the first shortcut could invoke:

> **favorite #1**

rather than hard-coding "proofread."

Then the user can configure:

```text
Meta+Alt+P → Proofread
```

or:

```text
Meta+Alt+P → Translate to Danish
```

---

# 76. Multiple quick shortcuts

Eventually:

```text
Meta+Alt+P → Primary action
Meta+Alt+T → Translate
Meta+Alt+C → Code
Meta+Alt+R → Research
Meta+Alt+A → Action picker
```

But don't ship all of these initially.

Two is enough:

### Quick Action

and

### Action Picker

Exactly as you proposed.

---

# 77. The default quick action should be configurable

Settings:

```text
Quick action

[ Proofread                    ▼ ]
```

Then:

```text
Shortcut
[ Meta + Alt + P ]
```

This is much better than baking proofreader into the program.

---

# 78. One additional shortcut I'd eventually add

### Repeat last action

```text
Meta+Alt+Shift+A
```

If the previous action was:

> Translate to Danish

then the next selected clipboard text is automatically translated.

That's surprisingly useful.

---

# 79. Another important UX feature: preview before sending

For privacy-sensitive services:

```text
You're about to send:

"This unpublished manuscript..."

to:

University Cloud / Research Model

[Cancel] [Send]
```

For local models:

> no warning necessary.

Could even show:

```text
🔒 Stays on this computer
```

---

# 80. Security model

I would explicitly classify endpoint profiles:

| Profile               | Data                      |
| --------------------- | ------------------------- |
| 🔒 Local              | Can process confidential  |
| 🏛 University private | Institutional data        |
| ☁️ Approved cloud     | Approved material         |
| 🌐 Public cloud       | Public/non-sensitive only |

Then service manifests can specify:

```yaml
privacy:
  minimum: university-private
```

and the engine refuses unsuitable endpoints.

---

# 81. The application should never silently upload clipboard contents

This should be a core principle.

Before the first cloud request, perhaps:

```text
AI Actions wants to send clipboard text to:

University Cloud
```

Then:

> Remember this choice for this service.

This is particularly important for an academic environment.

---

# 82. The application can also make model provenance visible

Every result:

```text
Proofread
────────────────────
Model: Local Gemma
Endpoint: Local
Temperature: 0.1
Time: 1.8 s
```

For research:

```text
Citation Review
────────────────────
Model: Research Reasoning
Sources: Crossref, OpenAlex
Retrieved: 7
```

This makes the service much more transparent.

---

# 83. I'd use KDE's own visual language rather than inventing a theme

KDE already has Breeze and Kirigami components designed for this environment. KDE documents both Qt Widgets and Qt Quick/Kirigami approaches, with the latter aimed at adaptive interfaces. ([Developer][4])

So avoid:

> custom rounded rectangles everywhere.

Use:

* Breeze
* standard controls
* standard icons
* KDE spacing
* KDE keyboard conventions
* Kirigami components

The application should look like it **belongs in Plasma**.

---

# 84. The final architecture I'd target

```text
                           KDE PLASMA
                               │
                 ┌─────────────┼─────────────┐
                 │             │             │
            Global Keys     Clipboard      Klipper
                 │             │             │
                 └─────────────┼─────────────┘
                               ↓
                    ┌─────────────────────┐
                    │    AI ACTIONS       │
                    │     CONTROLLER      │
                    ├─────────────────────┤
                    │ Shortcut Manager    │
                    │ Clipboard Manager   │
                    │ D-Bus Service       │
                    │ Tray                 │
                    │ Notifications       │
                    └──────────┬──────────┘
                               │
                         ACTION ENGINE
                               │
            ┌──────────────────┼──────────────────┐
            ↓                  ↓                  ↓
       Service Registry     Job Manager       Tool Registry
            │                  │                  │
            ↓                  ↓                  ↓
       YAML services       async jobs       Crossref/OpenAlex
                                               PDF parser
                                               etc.
            │
            ↓
       MODEL ROUTER
            │
       ┌────┼───────┐
       ↓    ↓       ↓
     Local  Uni    Cloud
     LLM    LLM    LLM
       │    │       │
       └────┴───────┘
            │
            ↓
       RESULT MODEL
            │
       ┌────┼──────────┐
       ↓    ↓          ↓
     Diff  Text    Structured
       │    │          │
       └────┼──────────┘
            ↓
      RESULT INSPECTOR
            │
      ┌─────┴─────┐
      ↓           ↓
    Reject       Accept
                    │
                    ↓
               Clipboard
```

That is the system I would build.

---

# 85. Recommended technology stack

| Component           | Recommendation                                                  |
| ------------------- | --------------------------------------------------------------- |
| Language            | **C++20**                                                       |
| UI                  | **Qt 6 + QML**                                                  |
| KDE UI components   | **Kirigami**                                                    |
| KDE integration     | **KDE Frameworks 6**                                            |
| Build               | **CMake + ECM**                                                 |
| Configuration       | **KConfig/KConfigXT**                                           |
| Global shortcuts    | **KGlobalAccel**                                                |
| Clipboard           | **QClipboard**                                                  |
| Klipper             | **D-Bus, optional**                                             |
| System tray         | **KStatusNotifierItem**                                         |
| Notifications       | **KNotification / KDE facilities**                              |
| App D-Bus           | **KDBusService + QtDBus**                                       |
| HTTP                | **QNetworkAccessManager**                                       |
| JSON                | **Qt JSON**                                                     |
| CLI                 | **QCommandLineParser** initially                                |
| Advanced CLI        | CLI11 if needed                                                 |
| Service definitions | **YAML**                                                        |
| Local AI            | OpenAI-compatible endpoint                                      |
| Cloud AI            | OpenAI-compatible endpoint                                      |
| Async               | Qt signals/slots + worker architecture                          |
| Testing             | Qt Test + service regression corpus                             |
| Packaging           | KDE-native CMake/CPack initially; later Flatpak/native packages |
| Icons               | Breeze/system icon names                                        |

KDE's own CMake examples already use Qt 6 and KF6 together, with ECM/KDE CMake settings and standard KDE installation facilities. ([Developer][5])

---

# 86. One thing I would *not* do

Don't start by implementing:

> 145 services.

Start by implementing:

> **the machine that can run 145 services.**

Specifically:

### Milestone 1

```text
Clipboard
+
Shortcut
+
Service definition
+
LLM endpoint
+
Result
+
Accept/reject
```

Once that works beautifully, you have the platform.

Everything afterward is essentially:

```text
new service definition
```

or:

```text
new tool
```

---

# 87. The first milestone should be surprisingly small

I would make the first C++ version capable of exactly this:

```text
Meta+Alt+P
      ↓
read clipboard
      ↓
service = proofread
      ↓
local endpoint
      ↓
diff
      ↓
Accept / Cancel
      ↓
clipboard
```

But with **no compromises in architecture**.

Then:

```text
Meta+Alt+A
      ↓
Action Picker
      ↓
Proofread
Translate
Summarize
Explain Code
      ↓
same engine
```

If those two things work, you've proved the central idea.

---

# 88. Then your 145-service table becomes a product roadmap

The status column you asked me to create earlier becomes much more meaningful.

Instead of:

| Service           | Status |
| ----------------- | ------ |
| Proofreader       | ✅      |
| Coder             | ✅      |
| Translator        | ✅      |
| Reference checker | ⬜      |

you'll eventually have:

| Service           | Definition | Pipeline | Model | UI renderer | Evaluation | Status |
| ----------------- | :--------: | :------: | :---: | :---------: | :--------: | :----: |
| Proofreader       |      ✅     |     ✅    |   ✅   |      ✅      |     🔄     |   🔄   |
| Translator        |      ✅     |     ✅    |   ✅   |      ✅      |      ⬜     |   🔄   |
| Reference checker |      ⬜     |     ⬜    |   ⬜   |      ⬜      |      ⬜     |    ⬜   |
| Citation checker  |      ⬜     |     ⬜    |   ⬜   |      ⬜      |      ⬜     |    ⬜   |
| Paper reviewer    |      ⬜     |     ⬜    |   ⬜   |      ⬜      |      ⬜     |    ⬜   |

That gives you a **real engineering roadmap**, rather than simply a feature list.

---

# 89. My recommended project phases at a glance

| Phase  | Focus                      | Main technology    | Outcome                                   |
| ------ | -------------------------- | ------------------ | ----------------------------------------- |
| **0**  | Formalize existing scripts | Bash/Python/YAML   | Existing services described declaratively |
| **1**  | Core engine                | C++/Qt6            | CLI can run services                      |
| **2**  | Plasma resident app        | KF6                | Global shortcut + clipboard               |
| **3**  | Action picker              | QML/Kirigami       | Beautiful service launcher                |
| **4**  | Result inspector           | QML/Kirigami       | Professional review UI                    |
| **5**  | Model profiles             | KConfig            | Multiple local/cloud endpoints            |
| **6**  | Service catalog            | YAML               | 20–50 services                            |
| **7**  | D-Bus                      | KF6/QtDBus         | Other apps can invoke AI                  |
| **8**  | Klipper                    | D-Bus              | Clipboard-history workflows               |
| **9**  | Research tools             | APIs + RAG         | Citation/literature services              |
| **10** | Evaluation                 | Test corpus        | Measurable quality                        |
| **11** | University packs           | Service manifests  | Institutional deployment                  |
| **12** | Packaging                  | KDE/Flatpak/native | Distributable application                 |

---

# 90. The end state is much more interesting than an AI app

I think your original intuition is exactly right.

The end product isn't really:

> **"An application with 145 AI functions."**

It's:

> **A KDE-native AI action layer for the desktop.**

The user learns **one interaction pattern**:

> **Copy → AI Action → Review → Accept**

And that pattern works for:

* proofreading
* translation
* coding
* citation verification
* literature review
* thesis review
* research methodology
* grant review
* teaching
* accessibility
* university policies
* document analysis
* research integrity

That is a very strong product concept.

And the fact that KDE already gives you native global shortcuts through KGlobalAccel, a proper clipboard abstraction through QClipboard, D-Bus integration, status-notifier support, KConfig, and Kirigami means you don't need to build a desktop framework yourself. ([KDE API Reference][7])

**My strongest recommendation:** make **C++/Qt6/KF6 + QML/Kirigami** the production architecture, preserve your current Python implementation as the behavioral prototype, and make the **service manifest + model profile + pipeline + result renderer** the four central abstractions. That is what will allow the system to grow from your three current tools into the 145-service university AI platform without turning into an unmaintainable collection of special cases.

[1]: https://develop.kde.org/products/frameworks/?utm_source=chatgpt.com "KDE Frameworks | Developer"
[2]: https://doc.qt.io/qtforpython-6/?utm_source=chatgpt.com "Qt for Python"
[3]: https://doc.qt.io/qtforpython-6.8/deployment/index.html?utm_source=chatgpt.com "Deployment - Qt for Python"
[4]: https://develop.kde.org/docs/getting-started/kirigami/?utm_source=chatgpt.com "Getting started with Kirigami | Developer"
[5]: https://develop.kde.org/docs/getting-started/kxmlgui/main_window/?utm_source=chatgpt.com "Creating the main window | Developer"
[6]: https://github.com/CLIUtils/CLI11?utm_source=chatgpt.com "GitHub - CLIUtils/CLI11: CLI11 is a command line parser for C++11 and beyond that provides a rich feature set with a simple and intuitive interface. · GitHub"
[7]: https://api.kde.org/kglobalaccel.html?utm_source=chatgpt.com "KGlobalAccel Class | KGlobalAccel"
[8]: https://api.kde.org/kstatusnotifieritem.html?utm_source=chatgpt.com "KStatusNotifierItem Class | KStatusNotifierItem"
[9]: https://doc.qt.io/QT-6/qclipboard.html?utm_source=chatgpt.com "QClipboard Class | Qt GUI | Qt 6.11.1"
[10]: https://github.com/KDE/plasma-workspace/blob/master/klipper/klipper.cpp?utm_source=chatgpt.com "plasma-workspace/klipper/klipper.cpp at master · KDE/plasma-workspace · GitHub"
[11]: https://sources.debian.org/src/plasma-workspace/4%3A5.8.6-2.1%2Bdeb9u1/klipper/klipper.h/?utm_source=chatgpt.com "File: klipper.h | Debian Sources"
[12]: https://api.kde.org/kdbusservice.html?utm_source=chatgpt.com "KDBusService Class | KDBusAddons"
[13]: https://develop.kde.org/docs/features/configuration/?utm_source=chatgpt.com "Configuration | Developer"
[14]: https://develop.kde.org/hig/getting_input/?utm_source=chatgpt.com "Getting input | Developer"

