# Install

## Get the command on your PATH

```bash
pipx install -e .
```

`pipx` installs `ai-actions` in its own isolated environment while still
putting it on PATH globally — the right choice here, since a KDE global
shortcut invokes the command outside of any shell that would normally
activate a venv for you.

A plain venv works too, if you're wiring the shortcut to an absolute path
or otherwise ensuring it's reachable:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

Either way this is an **editable** install on purpose: `services/*.yaml`
and `models.yaml` live in this checkout and are meant to be hand-edited
(via `ai-actions service create`/`edit`/`set`/`duplicate`) — an editable
install keeps the command pointed at this real checkout instead of a frozen
copy that a normal install would produce.

`python3 -m ai_actions ...` also works identically, with no install at all.

## Configure your model endpoint

Edit `models.yaml` to point at your OpenAI-compatible endpoint (e.g. a
local `llama-server`):

```yaml
local:
  type: openai-compatible
  url: http://127.0.0.1:8081/v1
  model: your-model-name
  temperature: 0.1
  timeout: 120
```

Every service references a profile here by name (`model: local`). See
[Model profiles](guide/models.md) for the full field list.

## Clipboard tooling

On Wayland, `ai-actions` shells out to `wl-clipboard` (`wl-paste`/`wl-copy`);
on X11, to `xclip`. Install whichever matches your session if it isn't
already present:

```bash
sudo dnf install wl-clipboard    # or xclip, on X11 — adjust for your distro
```

## Wire up a KDE global shortcut

`ai-actions` doesn't register its own global shortcuts — KDE already has a
perfectly good mechanism for running an arbitrary command on a key combo,
so there's no reason to duplicate it.

1. **System Settings → Shortcuts → Custom Shortcuts**
2. Add a new **Global Shortcut → Command/URL**
3. Set the command to, for example:
   ```
   ai-actions run proofread
   ```
4. Assign a key combination (e.g. `Meta+Alt+P`).
5. Repeat for the picker, bound to a different key (e.g. `Meta+Alt+A`):
   ```
   ai-actions picker
   ```

Copy some text, press your shortcut, review the result — done.
