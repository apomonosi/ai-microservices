# Model profiles

`models.yaml` at the repo root defines the named endpoints that service
manifests reference by `model: <name>`.

```yaml
local:
  type: openai-compatible
  url: http://127.0.0.1:8081/v1
  model: gemma-4-E4B-it-UD-Q5_K_XL.gguf
  temperature: 0.1
  timeout: 120

external-reasoning:
  type: openai-compatible
  url: http://your-endpoint-host/v1
  model: some-larger-model.gguf
  temperature: 0.1
  timeout: 300
  # api_key: ...          # uncomment if the endpoint requires auth
  extra_body:
    chat_template_kwargs:
      enable_thinking: false      # e.g. Qwen3: skip its thinking pass for faster single-shot replies
```

## Fields

| Field | Required | Meaning |
|---|---|---|
| `url` | yes | Base URL of an OpenAI-compatible endpoint. `/chat/completions` is appended automatically. |
| `model` | yes | The model name passed in the request body — whatever your server expects (e.g. the `.gguf` file it was started with). |
| `temperature` | no (default `0.2`) | |
| `timeout` | no (default `120`) | Seconds. Give a slower/larger model more headroom. |
| `api_key` | no | Sent as `Authorization: Bearer <key>` if set. |
| `extra_body` | no | Arbitrary extra fields merged into the request body sent to this profile's endpoint — for server-specific options outside the standard OpenAI chat-completions shape (e.g. vLLM/SGLang's `chat_template_kwargs`, used to turn off Qwen3's `enable_thinking` reasoning pass so a quick rewrite doesn't pay for a reasoning trace it doesn't need). Passed through as-is; `model`/`temperature`/`messages` always win if a key collides. |
| `type` | — | Currently informational only — every profile is treated as OpenAI-compatible regardless of this value. |

## Multiple profiles

Nothing stops you from defining several — a fast local model for simple
rewrites, a larger/slower one for anything needing more reasoning — and
pointing different services at whichever fits:

```bash
ai-actions service set methodology-review --model external-reasoning
```

`ai-actions service show <id>` displays the resolved profile (name, model,
URL) for whichever service you're looking at, and `service validate`
flags a `model:` value that doesn't match any profile here.
