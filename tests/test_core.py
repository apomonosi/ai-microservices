from __future__ import annotations

import requests

from ai_actions.core import (
    ConfigError,
    EngineError,
    ModelProfile,
    Service,
    list_services,
    load_models,
    load_service,
    run_service,
    validate_services,
)
from tests.helpers import write_service_file

import pytest


# --- load_service --------------------------------------------------------


def test_load_service_happy_path(services_dir):
    write_service_file(services_dir, "greet", prompt="Say hello.")
    service = load_service("greet", services_dir)
    assert service.id == "greet"
    assert service.model == "local"
    assert service.review == "text"
    assert "Say hello." in service.system_prompt


def test_load_service_missing_file(services_dir):
    with pytest.raises(ConfigError, match="Unknown service"):
        load_service("nope", services_dir)


def test_load_service_invalid_yaml(services_dir):
    (services_dir / "broken.yaml").write_text("not: valid: yaml: [")
    with pytest.raises(ConfigError, match="invalid YAML"):
        load_service("broken", services_dir)


def test_load_service_non_mapping_top_level(services_dir):
    (services_dir / "listy.yaml").write_text("[1, 2, 3]")
    with pytest.raises(ConfigError, match="expected a YAML mapping"):
        load_service("listy", services_dir)


def test_load_service_missing_required_field(services_dir):
    (services_dir / "incomplete.yaml").write_text("name: Incomplete\ncategory: testing\n")
    with pytest.raises(ConfigError, match="missing required field"):
        load_service("incomplete", services_dir)


# --- load_models -----------------------------------------------------------


def test_load_models_happy_path(models_file):
    models = load_models(models_file)
    assert "local" in models
    assert models["local"].model == "test-model"


def test_load_models_missing_file(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_models(tmp_path / "does-not-exist.yaml")


def test_load_models_invalid_yaml(tmp_path):
    path = tmp_path / "models.yaml"
    path.write_text("not: valid: [")
    with pytest.raises(ConfigError, match="invalid YAML"):
        load_models(path)


def test_load_models_non_mapping_top_level(tmp_path):
    path = tmp_path / "models.yaml"
    path.write_text("[1, 2, 3]")
    with pytest.raises(ConfigError, match="expected a YAML mapping"):
        load_models(path)


def test_load_models_missing_required_field(tmp_path):
    path = tmp_path / "models.yaml"
    path.write_text("local:\n  model: test-model\n")  # no url
    with pytest.raises(ConfigError, match="missing required field"):
        load_models(path)


def test_load_models_extra_body(tmp_path):
    path = tmp_path / "models.yaml"
    path.write_text(
        "local:\n"
        "  url: http://example.test/v1\n"
        "  model: test-model\n"
        "  extra_body:\n"
        "    chat_template_kwargs:\n"
        "      enable_thinking: false\n"
    )
    models = load_models(path)
    assert models["local"].extra_body == {"chat_template_kwargs": {"enable_thinking": False}}


def test_load_models_extra_body_defaults_to_none(models_file):
    models = load_models(models_file)
    assert models["local"].extra_body is None


# --- list_services -----------------------------------------------------------


def test_list_services_skips_broken_file_with_warning(services_dir, capsys):
    write_service_file(services_dir, "good")
    (services_dir / "broken.yaml").write_text("not: valid: yaml: [")
    services = list_services(services_dir)
    assert [s.id for s in services] == ["good"]
    assert "warning: skipping 'broken.yaml'" in capsys.readouterr().err


def test_list_services_empty_dir(services_dir):
    assert list_services(services_dir) == []


# --- validate_services -----------------------------------------------------------


def test_validate_services_all_ok(services_dir, models_file):
    write_service_file(services_dir, "good")
    assert validate_services(services_dir, models_file) == []


def test_validate_services_unknown_model(services_dir, models_file):
    write_service_file(services_dir, "bad-model", model="does-not-exist")
    problems = validate_services(services_dir, models_file)
    assert any("unknown model" in p for p in problems)


def test_validate_services_invalid_review(services_dir, models_file):
    write_service_file(services_dir, "bad-review", review="bogus")
    problems = validate_services(services_dir, models_file)
    assert any("invalid review type" in p for p in problems)


def test_validate_services_invalid_clipboard_mode(services_dir, models_file):
    write_service_file(services_dir, "bad-clip", clipboard_on_accept="bogus")
    problems = validate_services(services_dir, models_file)
    assert any("invalid clipboard_on_accept" in p for p in problems)


def test_validate_services_empty_prompt(services_dir, models_file):
    write_service_file(services_dir, "empty-prompt", prompt=" ")
    problems = validate_services(services_dir, models_file)
    assert any("empty prompt.system" in p for p in problems)


def test_validate_services_invalid_verify(services_dir, models_file):
    write_service_file(services_dir, "bad-verify", verify="openalex")
    problems = validate_services(services_dir, models_file)
    assert any("invalid verify" in p for p in problems)


def test_validate_services_valid_verify_ok(services_dir, models_file):
    write_service_file(services_dir, "good-verify", verify="crossref")
    assert validate_services(services_dir, models_file) == []


def test_validate_services_unknown_corpus(services_dir, models_file, corpora_dir, monkeypatch):
    monkeypatch.setattr("ai_actions.corpus.CORPORA_DIR", corpora_dir)
    write_service_file(services_dir, "bad-corpus", corpus="does-not-exist")
    problems = validate_services(services_dir, models_file)
    assert any("unknown corpus" in p for p in problems)


def test_validate_services_valid_corpus_ok(services_dir, models_file, corpora_dir, monkeypatch):
    monkeypatch.setattr("ai_actions.corpus.CORPORA_DIR", corpora_dir)
    (corpora_dir / "mycorpus").mkdir()
    (corpora_dir / "mycorpus" / "doc.txt").write_text("hello")
    write_service_file(services_dir, "good-corpus", corpus="mycorpus")
    assert validate_services(services_dir, models_file) == []


def test_validate_services_id_filename_mismatch(services_dir, models_file):
    write_service_file(services_dir, "outer-name", internal_id="inner-name")
    problems = validate_services(services_dir, models_file)
    assert any("does not match filename" in p for p in problems)


def test_validate_services_broken_models_file_reported(services_dir, tmp_path):
    write_service_file(services_dir, "good")
    bad_models = tmp_path / "models.yaml"
    bad_models.write_text("not: valid: [")
    problems = validate_services(services_dir, bad_models)
    assert any("invalid YAML" in p for p in problems)


def test_validate_services_only_id_nonexistent(services_dir, models_file):
    problems = validate_services(services_dir, models_file, only_id="nope")
    assert len(problems) == 1
    assert "no such service" in problems[0]


def test_validate_services_only_id_scopes_to_one_service(services_dir, models_file):
    write_service_file(services_dir, "good")
    write_service_file(services_dir, "bad-review", review="bogus")
    assert validate_services(services_dir, models_file, only_id="good") == []
    assert validate_services(services_dir, models_file, only_id="bad-review") != []


# --- run_service -----------------------------------------------------------


def _service(**overrides) -> Service:
    fields = dict(
        id="test",
        name="Test",
        category="testing",
        model="local",
        system_prompt="Say hi.",
        review="text",
        clipboard_on_accept="none",
    )
    fields.update(overrides)
    return Service(**fields)


def test_run_service_with_verify_crossref_splices_lookup_results(monkeypatch):
    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["json"] = json

        class Resp:
            def raise_for_status(self):
                pass

            def json(self):
                return {"choices": [{"message": {"content": "checked"}}]}

        return Resp()

    monkeypatch.setattr("ai_actions.core.requests.post", fake_post)
    monkeypatch.setattr(
        "ai_actions.verify.resolve_references", lambda text: "Input: ref one\nStatus: matched"
    )
    models = {"local": ModelProfile(name="local", url="http://example.test/v1", model="m")}

    result = run_service(_service(verify="crossref"), "ref one", models=models)

    assert result == "checked"
    user_message = captured["json"]["messages"][1]["content"]
    assert "ref one" in user_message
    assert "CROSSREF LOOKUP RESULTS" in user_message
    assert "Status: matched" in user_message


def test_run_service_without_verify_does_not_touch_lookup(monkeypatch):
    def boom(text):
        raise AssertionError("resolve_references should not be called")

    monkeypatch.setattr("ai_actions.verify.resolve_references", boom)

    def fake_post(url, json, headers, timeout):
        class Resp:
            def raise_for_status(self):
                pass

            def json(self):
                return {"choices": [{"message": {"content": "ok"}}]}

        return Resp()

    monkeypatch.setattr("ai_actions.core.requests.post", fake_post)
    models = {"local": ModelProfile(name="local", url="http://example.test/v1", model="m")}

    result = run_service(_service(), "hello", models=models)

    assert result == "ok"


def test_run_service_with_corpus_splices_retrieved_context(monkeypatch):
    from ai_actions.corpus import Chunk

    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["json"] = json

        class Resp:
            def raise_for_status(self):
                pass

            def json(self):
                return {"choices": [{"message": {"content": "answered"}}]}

        return Resp()

    monkeypatch.setattr("ai_actions.core.requests.post", fake_post)
    monkeypatch.setattr(
        "ai_actions.corpus.search_corpus",
        lambda corpus_id, query, **kw: [Chunk(source="syllabus.txt", index=0, text="Class meets on Tuesdays.")],
    )
    models = {"local": ModelProfile(name="local", url="http://example.test/v1", model="m")}

    result = run_service(_service(corpus="course"), "When does the class meet?", models=models)

    assert result == "answered"
    user_message = captured["json"]["messages"][1]["content"]
    assert "RETRIEVED CONTEXT" in user_message
    assert "Class meets on Tuesdays." in user_message
    assert "When does the class meet?" in user_message


def test_run_service_merges_extra_body_into_request(monkeypatch):
    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["json"] = json

        class Resp:
            def raise_for_status(self):
                pass

            def json(self):
                return {"choices": [{"message": {"content": "ok"}}]}

        return Resp()

    monkeypatch.setattr("ai_actions.core.requests.post", fake_post)
    models = {
        "local": ModelProfile(
            name="local",
            url="http://example.test/v1",
            model="m",
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
    }

    run_service(_service(), "hello", models=models)

    assert captured["json"]["chat_template_kwargs"] == {"enable_thinking": False}


def test_run_service_extra_body_cannot_override_model_or_messages(monkeypatch):
    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["json"] = json

        class Resp:
            def raise_for_status(self):
                pass

            def json(self):
                return {"choices": [{"message": {"content": "ok"}}]}

        return Resp()

    monkeypatch.setattr("ai_actions.core.requests.post", fake_post)
    models = {
        "local": ModelProfile(
            name="local",
            url="http://example.test/v1",
            model="m",
            extra_body={"model": "sneaky-override", "messages": "sneaky"},
        )
    }

    run_service(_service(), "hello", models=models)

    assert captured["json"]["model"] == "m"
    assert captured["json"]["messages"][1]["content"] == "hello"


def test_run_service_with_missing_corpus_raises_config_error(monkeypatch):
    from ai_actions.corpus import CorpusError

    def boom(corpus_id, query, **kw):
        raise CorpusError(f"Unknown corpus '{corpus_id}'")

    monkeypatch.setattr("ai_actions.corpus.search_corpus", boom)
    models = {"local": ModelProfile(name="local", url="http://example.test/v1", model="m")}

    with pytest.raises(ConfigError, match="Unknown corpus"):
        run_service(_service(corpus="nope"), "a question", models=models)


def test_run_service_without_corpus_does_not_touch_retrieval(monkeypatch):
    def boom(*args, **kwargs):
        raise AssertionError("search_corpus should not be called")

    monkeypatch.setattr("ai_actions.corpus.search_corpus", boom)

    def fake_post(url, json, headers, timeout):
        class Resp:
            def raise_for_status(self):
                pass

            def json(self):
                return {"choices": [{"message": {"content": "ok"}}]}

        return Resp()

    monkeypatch.setattr("ai_actions.core.requests.post", fake_post)
    models = {"local": ModelProfile(name="local", url="http://example.test/v1", model="m")}

    result = run_service(_service(), "hello", models=models)

    assert result == "ok"


def test_run_service_success(monkeypatch):
    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json

        class Resp:
            def raise_for_status(self):
                pass

            def json(self):
                return {"choices": [{"message": {"content": "hi back"}}]}

        return Resp()

    monkeypatch.setattr("ai_actions.core.requests.post", fake_post)
    models = {"local": ModelProfile(name="local", url="http://example.test/v1", model="m")}

    result = run_service(_service(), "hello", models=models)

    assert result == "hi back"
    assert captured["url"] == "http://example.test/v1/chat/completions"
    assert captured["json"]["messages"][0] == {"role": "system", "content": "Say hi."}
    assert captured["json"]["messages"][1] == {"role": "user", "content": "hello"}


def test_run_service_unknown_model():
    with pytest.raises(ConfigError, match="unknown model"):
        run_service(_service(model="nope"), "hi", models={})


def test_run_service_network_error(monkeypatch):
    def fake_post(*args, **kwargs):
        raise requests.ConnectionError("boom")

    monkeypatch.setattr("ai_actions.core.requests.post", fake_post)
    models = {"local": ModelProfile(name="local", url="http://x/v1", model="m")}

    with pytest.raises(EngineError, match="failed"):
        run_service(_service(), "hi", models=models)


def test_run_service_bad_response_shape(monkeypatch):
    class Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"unexpected": True}

    monkeypatch.setattr("ai_actions.core.requests.post", lambda *a, **kw: Resp())
    models = {"local": ModelProfile(name="local", url="http://x/v1", model="m")}

    with pytest.raises(EngineError, match="Unexpected response shape"):
        run_service(_service(), "hi", models=models)
