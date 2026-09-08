from __future__ import annotations

import pytest

from ai_actions.core import load_service
from ai_actions.manage import (
    ManageError,
    create_service,
    delete_service,
    duplicate_service,
    get_service_path,
    set_field,
    validate_id,
)


# --- validate_id -----------------------------------------------------------


def test_validate_id_accepts_slug():
    validate_id("my-service-2")  # must not raise


@pytest.mark.parametrize(
    "bad_id",
    ["../etc/passwd", "../../escape", "has spaces", "Upper", "trailing-", "-leading", "with_underscore", ""],
)
def test_validate_id_rejects_unsafe_or_malformed(bad_id):
    with pytest.raises(ManageError):
        validate_id(bad_id)


# --- create_service -----------------------------------------------------------


def test_create_service_happy_path(services_dir):
    path = create_service(
        "my-svc",
        name="My Svc",
        category="testing",
        model="local",
        review="diff",
        prompt="Do the thing.",
        services_dir=services_dir,
    )
    assert path == services_dir / "my-svc.yaml"
    service = load_service("my-svc", services_dir)
    assert service.name == "My Svc"
    assert service.review == "diff"
    assert service.clipboard_on_accept == "replace"  # default for review=diff
    assert "Do the thing." in service.system_prompt


def test_create_service_default_clipboard_mode_for_text_review(services_dir):
    create_service("my-svc", review="text", services_dir=services_dir)
    assert load_service("my-svc", services_dir).clipboard_on_accept == "none"


def test_create_service_default_name_is_title_cased_id(services_dir):
    create_service("my-cool-svc", services_dir=services_dir)
    assert load_service("my-cool-svc", services_dir).name == "My Cool Svc"


def test_create_service_rejects_duplicate_id(services_dir):
    create_service("dup", services_dir=services_dir)
    with pytest.raises(ManageError, match="already exists"):
        create_service("dup", services_dir=services_dir)


def test_create_service_rejects_bad_id(services_dir):
    with pytest.raises(ManageError):
        create_service("../escape", services_dir=services_dir)


def test_create_service_rejects_invalid_review(services_dir):
    with pytest.raises(ManageError, match="invalid review type"):
        create_service("my-svc", review="bogus", services_dir=services_dir)


def test_create_service_rejects_invalid_clipboard_mode(services_dir):
    with pytest.raises(ManageError, match="invalid clipboard_on_accept"):
        create_service("my-svc", clipboard_on_accept="bogus", services_dir=services_dir)


def test_create_service_quotes_special_characters_in_name(services_dir):
    # Regression test for the "unquoted # starts a YAML comment" bug that
    # silently truncated a service's name in production.
    create_service("hashy", name="Reviewer #2", services_dir=services_dir)
    assert load_service("hashy", services_dir).name == "Reviewer #2"


def test_create_service_placeholder_prompt_when_none_given(services_dir):
    create_service("my-svc", services_dir=services_dir)
    service = load_service("my-svc", services_dir)
    assert "TODO" in service.system_prompt


# --- set_field -----------------------------------------------------------


def test_set_field_updates_only_the_target_line(services_dir):
    create_service("my-svc", category="old-cat", services_dir=services_dir)
    before = (services_dir / "my-svc.yaml").read_text()

    set_field("my-svc", "category", "new-cat", services_dir=services_dir)

    after = (services_dir / "my-svc.yaml").read_text()
    assert load_service("my-svc", services_dir).category == "new-cat"
    before_other_lines = [line for line in before.splitlines() if not line.startswith("category:")]
    after_other_lines = [line for line in after.splitlines() if not line.startswith("category:")]
    assert before_other_lines == after_other_lines


def test_set_field_quotes_special_characters(services_dir):
    create_service("my-svc", services_dir=services_dir)
    set_field("my-svc", "name", "Weird #Name", services_dir=services_dir)
    assert load_service("my-svc", services_dir).name == "Weird #Name"


def test_set_field_rejects_disallowed_field(services_dir):
    create_service("my-svc", services_dir=services_dir)
    with pytest.raises(ManageError, match="cannot set"):
        set_field("my-svc", "system_prompt", "x", services_dir=services_dir)


def test_set_field_rejects_invalid_review_value(services_dir):
    create_service("my-svc", services_dir=services_dir)
    with pytest.raises(ManageError, match="invalid review type"):
        set_field("my-svc", "review", "bogus", services_dir=services_dir)


def test_set_field_rejects_invalid_clipboard_mode(services_dir):
    create_service("my-svc", services_dir=services_dir)
    with pytest.raises(ManageError, match="invalid clipboard_on_accept"):
        set_field("my-svc", "clipboard_on_accept", "bogus", services_dir=services_dir)


def test_set_field_nonexistent_service(services_dir):
    with pytest.raises(ManageError, match="does not exist"):
        set_field("nope", "category", "x", services_dir=services_dir)


# --- duplicate_service -----------------------------------------------------------


def test_duplicate_service_updates_id_and_name(services_dir):
    create_service("source", name="Source Name", services_dir=services_dir)

    duplicate_service("source", "clone", name="Clone Name", services_dir=services_dir)

    clone = load_service("clone", services_dir)
    assert clone.id == "clone"
    assert clone.name == "Clone Name"
    source = load_service("source", services_dir)
    assert source.id == "source"  # original untouched


def test_duplicate_service_keeps_name_if_not_given(services_dir):
    create_service("source", name="Source Name", services_dir=services_dir)
    duplicate_service("source", "clone", services_dir=services_dir)
    assert load_service("clone", services_dir).name == "Source Name"


def test_duplicate_service_rejects_existing_new_id(services_dir):
    create_service("source", services_dir=services_dir)
    create_service("clone", services_dir=services_dir)
    with pytest.raises(ManageError, match="already exists"):
        duplicate_service("source", "clone", services_dir=services_dir)


def test_duplicate_service_rejects_missing_source(services_dir):
    with pytest.raises(ManageError, match="does not exist"):
        duplicate_service("nope", "clone", services_dir=services_dir)


def test_duplicate_service_rejects_bad_new_id(services_dir):
    create_service("source", services_dir=services_dir)
    with pytest.raises(ManageError):
        duplicate_service("source", "../escape", services_dir=services_dir)


# --- delete_service -----------------------------------------------------------


def test_delete_service_removes_file(services_dir):
    create_service("gone-soon", services_dir=services_dir)
    path = delete_service("gone-soon", services_dir=services_dir)
    assert not path.exists()


def test_delete_service_nonexistent(services_dir):
    with pytest.raises(ManageError, match="does not exist"):
        delete_service("nope", services_dir=services_dir)


# --- get_service_path -----------------------------------------------------------


def test_get_service_path(services_dir):
    assert get_service_path("foo", services_dir) == services_dir / "foo.yaml"
