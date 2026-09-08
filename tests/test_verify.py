from __future__ import annotations

import requests

from ai_actions.verify import resolve_references


class _Resp:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def _crossref_payload(**item_overrides):
    item = {
        "score": 87.5,
        "title": ["Attention Is All You Need"],
        "author": [{"given": "Ashish", "family": "Vaswani"}, {"given": "Noam", "family": "Shazeer"}],
        "container-title": ["Advances in Neural Information Processing Systems"],
        "published": {"date-parts": [[2017]]},
        "DOI": "10.5555/example",
    }
    item.update(item_overrides)
    return {"message": {"items": [item]}}


def test_resolve_references_matched(monkeypatch):
    monkeypatch.setattr("ai_actions.verify.requests.get", lambda *a, **kw: _Resp(_crossref_payload()))

    result = resolve_references("Vaswani et al., Attention is all you need, 2017")

    assert "Status: matched (score 87.5)" in result
    assert "Attention Is All You Need" in result
    assert "Ashish Vaswani" in result
    assert "2017" in result
    assert "10.5555/example" in result


def test_resolve_references_no_match(monkeypatch):
    monkeypatch.setattr(
        "ai_actions.verify.requests.get", lambda *a, **kw: _Resp({"message": {"items": []}})
    )

    result = resolve_references("A totally fabricated reference, Nobody, 2099")

    assert "Status: no_match" in result


def test_resolve_references_network_error(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError("no route to host")

    monkeypatch.setattr("ai_actions.verify.requests.get", fake_get)

    result = resolve_references("Some reference")

    assert "Status: lookup_failed" in result
    assert "no route to host" in result


def test_resolve_references_bad_json(monkeypatch):
    class BadJsonResp:
        def raise_for_status(self):
            pass

        def json(self):
            raise ValueError("not json")

    monkeypatch.setattr("ai_actions.verify.requests.get", lambda *a, **kw: BadJsonResp())

    result = resolve_references("Some reference")

    assert "Status: lookup_failed" in result
    assert "invalid response" in result


def test_resolve_references_multiple_lines_independent(monkeypatch):
    calls = []

    def fake_get(url, params, headers, timeout):
        calls.append(params["query.bibliographic"])
        if "good" in params["query.bibliographic"]:
            return _Resp(_crossref_payload())
        raise requests.Timeout("slow")

    monkeypatch.setattr("ai_actions.verify.requests.get", fake_get)

    result = resolve_references("a good reference\na bad reference")

    assert len(calls) == 2
    assert "Status: matched" in result
    assert "Status: lookup_failed" in result


def test_resolve_references_blank_lines_skipped(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "ai_actions.verify.requests.get",
        lambda *a, **kw: (calls.append(1), _Resp(_crossref_payload()))[1],
    )

    resolve_references("one reference\n\n\n   \nanother reference")

    assert len(calls) == 2


def test_crossref_params_include_mailto_when_configured(monkeypatch):
    monkeypatch.setenv("AI_ACTIONS_CONTACT_EMAIL", "me@example.com")
    from ai_actions.verify import _crossref_params

    params = _crossref_params("some reference")

    assert params["mailto"] == "me@example.com"


def test_crossref_params_omit_mailto_when_not_configured(monkeypatch):
    monkeypatch.delenv("AI_ACTIONS_CONTACT_EMAIL", raising=False)
    from ai_actions.verify import _crossref_params

    params = _crossref_params("some reference")

    assert "mailto" not in params
