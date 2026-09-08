"""External reference-verification lookups for services that declare
`verify: crossref` in their manifest.

This is the one place in the engine that talks to a third-party service
rather than only the configured model endpoint - see docs/local-models.md
for the privacy trade-off this implies for the handful of services that
use it. Crossref's public `works` API needs no API key; a per-line lookup
never raises, since one bad or ambiguous reference shouldn't abort the
whole batch (the same "skip what's broken" posture core.list_services()
already applies to a broken manifest file).
"""

from __future__ import annotations

import os

import requests

CROSSREF_WORKS_URL = "https://api.crossref.org/works"
_LOOKUP_TIMEOUT = 10.0


def _crossref_headers() -> dict[str, str]:
    contact = os.environ.get("AI_ACTIONS_CONTACT_EMAIL")
    identity = f"mailto:{contact}" if contact else "no contact configured"
    return {"User-Agent": f"ai-actions/0.1 ({identity}; https://github.com/apomonosi/ai-microservices)"}


def _crossref_params(reference_text: str) -> dict[str, str]:
    params = {"query.bibliographic": reference_text, "rows": "1"}
    contact = os.environ.get("AI_ACTIONS_CONTACT_EMAIL")
    if contact:
        params["mailto"] = contact
    return params


def _lookup_one(reference_text: str) -> dict:
    """Look up one bibliographic reference string. Never raises - a
    network problem or an unexpected response shape becomes a
    'lookup_failed' result instead of propagating.
    """
    try:
        response = requests.get(
            CROSSREF_WORKS_URL,
            params=_crossref_params(reference_text),
            headers=_crossref_headers(),
            timeout=_LOOKUP_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        return {"input": reference_text, "status": "lookup_failed", "error": str(exc)}
    except ValueError as exc:  # response.json() failed to parse
        return {"input": reference_text, "status": "lookup_failed", "error": f"invalid response: {exc}"}

    items = (data.get("message") or {}).get("items") or []
    if not items:
        return {"input": reference_text, "status": "no_match"}

    top = items[0]
    date_parts = (
        (top.get("published") or {}).get("date-parts")
        or (top.get("published-print") or {}).get("date-parts")
        or (top.get("published-online") or {}).get("date-parts")
        or []
    )
    year = date_parts[0][0] if date_parts and date_parts[0] else None
    authors = [
        " ".join(part for part in (author.get("given"), author.get("family")) if part)
        for author in (top.get("author") or [])
    ]

    return {
        "input": reference_text,
        "status": "matched",
        "score": top.get("score"),
        "title": " ".join(top.get("title") or []) or None,
        "authors": authors,
        "year": year,
        "container_title": " ".join(top.get("container-title") or []) or None,
        "doi": top.get("DOI"),
    }


def _format_result(result: dict) -> str:
    lines = [f"Input: {result['input']}"]
    status = result["status"]
    if status == "matched":
        lines.append(f"Status: matched (score {result['score']})")
        lines.append(f"Resolved title: {result['title'] or '(none)'}")
        lines.append(f"Resolved authors: {', '.join(result['authors']) or '(none)'}")
        lines.append(f"Resolved year: {result['year'] or '(none)'}")
        lines.append(f"Resolved journal/container: {result['container_title'] or '(none)'}")
        lines.append(f"DOI: {result['doi'] or '(none)'}")
    elif status == "no_match":
        lines.append("Status: no_match (Crossref returned no candidate - not proof the reference is fake, "
                      "Crossref doesn't index everything)")
    else:
        lines.append(f"Status: lookup_failed ({result.get('error', 'unknown error')})")
    return "\n".join(lines)


def resolve_references(input_text: str) -> str:
    """Resolve each non-blank line of input_text as one bibliographic
    reference against Crossref, and return a formatted block describing
    the outcome for every line - meant to be appended to a service's
    prompt, not shown to the user directly.
    """
    lines = [line.strip() for line in input_text.splitlines() if line.strip()]
    blocks = [_format_result(_lookup_one(line)) for line in lines]
    return "\n\n".join(blocks)
