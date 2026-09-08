# Creating services

Growing the library is the normal way this project grows — no engine
changes needed, just another YAML file. This walks through the actual
workflow.

## From scratch

```bash
ai-actions service create summarize-slides \
  --category "course-material" \
  --review text \
  --description "Summarize lecture slide text into a study guide." \
  --prompt-file /tmp/my-prompt.txt
```

This scaffolds `services/summarize-slides.yaml` with the given fields, then
opens it in `$EDITOR`/`$VISUAL` so you can refine the prompt (pass
`--no-edit` to skip that and fill it in later). `--clipboard-on-accept`
defaults sensibly from `--review` if you don't set it (see [the manifest
field reference](service-manifest.md)). Right after creating it, the
command re-runs `validate` on the new service and reports any problem —
a missing field, a bad `--review` value — immediately, not the next time
you happen to run it.

If you'd rather write the prompt inline for something short:

```bash
ai-actions service create quick-check --review text \
  --prompt "Check the input for obvious spelling errors only. List them."
```

## From an existing service

Many services are natural variants of each other (a translator for a
different language, a reviewer for a different document type). Cloning is
usually faster than starting over:

```bash
ai-actions service duplicate translate-da translate-en --name "Translate to English"
```

Copies `translate-da.yaml` to `translate-en.yaml`, updates the internal
`id:` and `name:` fields, and opens it in `$EDITOR` so you can change the
one or two lines that actually differ (in this case, the target language
in the prompt).

## Adjusting a field without opening an editor

For a quick, scriptable change to one of the simple fields (not the
prompt itself, which is multi-line prose):

```bash
ai-actions service set my-service --category writing --model local-reasoning
```

This is a targeted line replacement — it touches only the lines you name,
leaving the hand-formatted `prompt: system: |` block completely untouched.

## Checking your work

```bash
ai-actions service validate my-service   # just this one
ai-actions service validate               # the whole library
```

Checks: the `model` resolves in `models.yaml`, `review`/
`clipboard_on_accept` are valid values, the prompt isn't empty, and the
internal `id:` matches the filename. A single broken file never takes
down `list`/`picker` for everything else — it's skipped with a warning —
but `validate` is how you find out *why*.

## Removing one

```bash
ai-actions service delete my-service      # asks for confirmation
ai-actions service delete my-service --yes  # skips it
```

The file is git-tracked, so this is trivially recoverable from history if
you change your mind.
