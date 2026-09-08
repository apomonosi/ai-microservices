"""Service/model configuration loading and the OpenAI-compatible engine call.

Services and model profiles are plain YAML data (see ../services/*.yaml and
../models.yaml). This module never hard-codes a specific service — adding
a new one is purely a matter of dropping in another YAML file.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

import requests
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SERVICES_DIR = Path(os.environ.get("AI_ACTIONS_SERVICES_DIR", REPO_ROOT / "services"))
MODELS_FILE = Path(os.environ.get("AI_ACTIONS_MODELS_FILE", REPO_ROOT / "models.yaml"))


class ConfigError(RuntimeError):
    """Missing or invalid service/model configuration."""


class EngineError(RuntimeError):
    """The model endpoint could not be reached or returned something unexpected."""


@dataclass
class ModelProfile:
    name: str
    url: str
    model: str
    temperature: float = 0.2
    timeout: float = 120.0
    api_key: str | None = None


@dataclass
class Service:
    id: str
    name: str
    category: str
    model: str
    system_prompt: str
    review: str = "text"
    clipboard_on_accept: str = "none"
    description: str = ""
    verify: str | None = None


def load_models(path: Path = MODELS_FILE) -> dict[str, ModelProfile]:
    if not path.exists():
        raise ConfigError(f"Model profile file not found: {path}")
    try:
        data = yaml.safe_load(path.read_text()) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path}: invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"{path}: expected a YAML mapping at the top level, got {type(data).__name__}")
    profiles: dict[str, ModelProfile] = {}
    for name, cfg in data.items():
        try:
            profiles[name] = ModelProfile(
                name=name,
                url=cfg["url"],
                model=cfg["model"],
                temperature=cfg.get("temperature", 0.2),
                timeout=cfg.get("timeout", 120),
                api_key=cfg.get("api_key"),
            )
        except (KeyError, TypeError) as exc:
            raise ConfigError(f"Model profile '{name}' is missing required field {exc}") from exc
    return profiles


def _service_path(service_id: str, services_dir: Path) -> Path:
    return services_dir / f"{service_id}.yaml"


def load_service(service_id: str, services_dir: Path = SERVICES_DIR) -> Service:
    path = _service_path(service_id, services_dir)
    if not path.exists():
        raise ConfigError(f"Unknown service '{service_id}' (expected {path})")
    try:
        data = yaml.safe_load(path.read_text()) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Service '{service_id}': invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(
            f"Service '{service_id}': expected a YAML mapping at the top level, got {type(data).__name__}"
        )
    try:
        system_prompt = data["prompt"]["system"]
        model = data["model"]
    except (KeyError, TypeError) as exc:
        raise ConfigError(f"Service '{service_id}' is missing required field {exc}") from exc
    return Service(
        id=data.get("id", service_id),
        name=data.get("name", service_id),
        category=data.get("category", ""),
        model=model,
        system_prompt=system_prompt,
        review=data.get("review", "text"),
        clipboard_on_accept=data.get("clipboard_on_accept", "none"),
        description=(data.get("description") or "").strip(),
        verify=data.get("verify"),
    )


def _load_all_services(services_dir: Path) -> tuple[list[tuple[Path, Service]], list[tuple[Path, ConfigError]]]:
    """Load every service, keyed by its actual file path (not by whatever
    its internal `id:` field claims — those can disagree, which is
    exactly one of the things validate_services() checks for).
    """
    loaded: list[tuple[Path, Service]] = []
    errors: list[tuple[Path, ConfigError]] = []
    for path in sorted(services_dir.glob("*.yaml")):
        try:
            loaded.append((path, load_service(path.stem, services_dir)))
        except ConfigError as exc:
            errors.append((path, exc))
    return loaded, errors


def list_services(services_dir: Path = SERVICES_DIR) -> list[Service]:
    """All loadable services. A broken manifest is skipped (with a
    warning) rather than crashing the whole list/picker — use
    validate_services() to see what's broken and why.
    """
    loaded, errors = _load_all_services(services_dir)
    for path, exc in errors:
        print(f"warning: skipping '{path.name}': {exc}", file=sys.stderr)
    return [service for _, service in loaded]


_VALID_REVIEW_TYPES = ("diff", "text")
_VALID_CLIPBOARD_MODES = ("replace", "none")
_VALID_VERIFY_TYPES = ("crossref",)


def validate_services(
    services_dir: Path = SERVICES_DIR,
    models_file: Path = MODELS_FILE,
    only_id: str | None = None,
) -> list[str]:
    """Check service manifest(s) and the model profiles they reference.
    Returns a list of human-readable problems; an empty list means
    everything checks out.
    """
    problems: list[str] = []

    try:
        models = load_models(models_file)
    except ConfigError as exc:
        problems.append(f"models.yaml: {exc}")
        models = {}

    if only_id is not None:
        path = _service_path(only_id, services_dir)
        if not path.exists():
            return [f"{only_id}: no such service (expected {path})"]
        try:
            loaded = [(path, load_service(only_id, services_dir))]
        except ConfigError as exc:
            return [f"{path.name}: {exc}"]
    else:
        loaded, load_errors = _load_all_services(services_dir)
        for path, exc in load_errors:
            problems.append(f"{path.name}: {exc}")

    for path, service in loaded:
        if service.id != path.stem:
            problems.append(f"{path.name}: internal id '{service.id}' does not match filename '{path.stem}'")
        if service.model not in models:
            problems.append(f"{path.name}: references unknown model '{service.model}'")
        if service.review not in _VALID_REVIEW_TYPES:
            problems.append(
                f"{path.name}: invalid review type '{service.review}' (expected one of {_VALID_REVIEW_TYPES})"
            )
        if service.clipboard_on_accept not in _VALID_CLIPBOARD_MODES:
            problems.append(
                f"{path.name}: invalid clipboard_on_accept '{service.clipboard_on_accept}' "
                f"(expected one of {_VALID_CLIPBOARD_MODES})"
            )
        if not service.system_prompt.strip():
            problems.append(f"{path.name}: empty prompt.system")
        if service.verify is not None and service.verify not in _VALID_VERIFY_TYPES:
            problems.append(
                f"{path.name}: invalid verify '{service.verify}' (expected one of {_VALID_VERIFY_TYPES})"
            )

    return problems


def run_service(
    service: Service,
    input_text: str,
    models: dict[str, ModelProfile] | None = None,
) -> str:
    """Send input_text through the service's model profile and return the
    model's reply text.
    """
    models = load_models() if models is None else models
    if service.model not in models:
        raise ConfigError(f"Service '{service.id}' references unknown model '{service.model}'")
    profile = models[service.model]

    user_content = input_text
    if service.verify == "crossref":
        from . import verify  # lazy: only services that use it need it

        resolved = verify.resolve_references(input_text)
        user_content = (
            f"{input_text}\n\n---\nCROSSREF LOOKUP RESULTS (reason over these - a match is not "
            "proof, check the score and details against what's claimed; a miss is not proof of "
            "fabrication, Crossref doesn't index everything):\n"
            f"{resolved}"
        )

    payload = {
        "model": profile.model,
        "temperature": profile.temperature,
        "messages": [
            {"role": "system", "content": service.system_prompt},
            {"role": "user", "content": user_content},
        ],
    }
    headers = {"Content-Type": "application/json"}
    if profile.api_key:
        headers["Authorization"] = f"Bearer {profile.api_key}"

    try:
        response = requests.post(
            f"{profile.url.rstrip('/')}/chat/completions",
            json=payload,
            headers=headers,
            timeout=profile.timeout,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise EngineError(f"Request to model endpoint '{profile.name}' ({profile.url}) failed: {exc}") from exc

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise EngineError(f"Unexpected response shape from '{profile.name}': {data}") from exc
