# CLI reference

```
usage: ai-actions [-h] {run,picker,list,service} ...
```

Every subcommand also accepts `-h`/`--help` directly (e.g. `ai-actions run
--help`) — this page mirrors that output, not the other way around, so if
they ever disagree, trust the terminal.

## `run` / `picker`: input, output and review

`run <service_id>` and `picker` (which lets you choose the service
interactively first) share the same options:

```
--text TEXT          Use this text instead of reading the clipboard
--file PATH          Read input from this file
--stdin              Read input from stdin (for piping: `cat x | ai-actions run ...`)
--output PATH        Also write the result to this file (for piping onward)
--no-gui             Skip the review dialog; just print/write the result
                      (optionally with --replace-clipboard)
--replace-clipboard  With --no-gui: write the result to the clipboard
                      unreviewed. Ignored otherwise (the review dialog's
                      Accept & Copy controls this instead).
```

`--text`/`--file`/`--stdin` are mutually exclusive; omit all three to read
the clipboard (the default, and what a KDE shortcut normally does).

While the request to the model is in flight, `run`/`picker` show a
system-tray icon (tooltip: which service is running) so a shortcut press
doesn't look like nothing happened — it clears as soon as the result
comes back. This is best-effort: on a desktop with no tray at all (e.g.
GNOME's default session), or with no display (SSH, cron, CI), it's
silently skipped — never a reason a command fails.

By default the result goes through the **Result Inspector** dialog: a diff
view with Accept/Reject for services declared `review: diff`, or a
read-only view with a manual Copy button for `review: text`. Nothing is
written back — to clipboard or to `--output` — unless you accept it there.
`--no-gui` skips the dialog entirely for scripting; `--output` still writes
unconditionally in that mode, and `--replace-clipboard` opts into writing
the clipboard unreviewed too. See [Pipelines](pipelines.md) for worked
examples.

```bash
ai-actions run proofread                                    # clipboard, with review
ai-actions run proofread --text "..." --no-gui               # print only, no clipboard write
cat draft.txt | ai-actions run proofread --stdin --no-gui -o out.txt
ai-actions picker                                            # choose a service, then the above
```

## `list`

Alias for `service list` (below) — kept as a shortcut since it's the most
common lookup.

## `service`: inspect and manage the library

```
usage: ai-actions service [-h]
                          {list,show,search,categories,validate,create,edit,set,duplicate,delete}
                          ...
```

### Read-only

**`list [--category CAT] [--query TEXT]`** — list services, optionally
filtered.

**`show <id>`** — full manifest detail for one service, including the
resolved model endpoint and the complete prompt text.

**`search <query>`** — matches id/name/category/description **and prompt
text** — broader than `list`'s filtering.

**`categories`** — distinct categories in use, with counts.

**`validate [<id>]`** — checks manifests (or just one) for: a `model` that
resolves in `models.yaml`, a valid `review` value (`diff`/`text`), a valid
`clipboard_on_accept` value (`replace`/`none`), a non-empty prompt, and
that the internal `id:` field matches the filename. Run with no argument
to check the whole library.

### Mutating

**`create <id> [--name] [--category] [--model] [--review diff|text] [--clipboard-on-accept replace|none] [--description] [--prompt TEXT | --prompt-file PATH] [--no-edit]`**
— scaffolds a new manifest from the given flags, then opens `$EDITOR`/`$VISUAL`
on it (pass `--no-edit` to skip). `--clipboard-on-accept` defaults to
`replace` for `review: diff` and `none` for `review: text`.

**`edit <id>`** — opens the manifest in `$EDITOR`/`$VISUAL` directly.

**`set <id> [--name] [--category] [--model] [--review diff|text] [--clipboard-on-accept replace|none] [--corpus ID]`**
— updates one or more simple fields without opening an editor (a targeted
line replacement, so the hand-crafted prompt block is never touched).
`--corpus` only works on a service whose manifest already has a `corpus:`
line (see [Corpora](corpora.md)) — it repoints an existing field, it
doesn't add a new one.

**`duplicate <source_id> <new_id> [--name] [--no-edit]`** — clones an
existing service under a new id, a good starting point for a variant.

**`delete <id> [--yes]`** — removes a manifest, with a confirmation prompt
(`--yes` skips it).

Every create/edit/set/duplicate immediately re-runs `validate` on the
affected service and reports any problem found — so a typo shows up right
away, not the next time you happen to run it.
