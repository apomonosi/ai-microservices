# Pipelines

`run`/`picker` accept input from a file or stdin, and can write the result
to a file, in addition to the default clipboard-based flow — so a service
composes into an ordinary shell pipeline rather than only working
interactively.

## Input sources

`--text`/`--file`/`--stdin` are mutually exclusive; with none given, the
clipboard is read (the default, interactive behavior).

```bash
ai-actions run proofread --file draft.txt --no-gui
cat draft.txt | ai-actions run proofread --stdin --no-gui
```

!!! note "Why `--stdin` is explicit, not auto-detected"
    Some tools auto-detect piped input via `isatty()`. This one doesn't:
    a KDE global shortcut likely invokes the process with a non-tty stdin
    (e.g. attached to `/dev/null`) even when nothing is actually piped in.
    Auto-detection would silently break the clipboard-shortcut flow by
    reading empty stdin instead of falling back to the clipboard.
    `--stdin` is an explicit opt-in instead — the shortcut-driven path is
    never at risk.

## Output

```bash
ai-actions run proofread --text "..." --no-gui --output corrected.txt
```

`--output` writes the result to a file, in addition to printing it to
stdout (so `ai-actions run ... --no-gui | next-command` still works
unchanged).

## Review still applies

With the GUI review dialog (the default — omit `--no-gui`), `--output` is
gated by it exactly like the clipboard is: the file is written only if you
Accept, not on Reject. `--no-gui` skips the dialog for unattended/scripted
use, and in that mode `--output` writes unconditionally — matching how
`--replace-clipboard` already behaved before pipelines existed.

## A full example

```bash
cat manuscript.txt \
  | ai-actions run structure-review --stdin --no-gui \
  | tee review.txt
```

Or picking the service interactively but still working with files:

```bash
ai-actions picker --file manuscript.txt --output review.txt
```
