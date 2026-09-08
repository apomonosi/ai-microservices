"""End-to-end CLI tests, run as real subprocesses (`python3 -m ai_actions
...`) rather than in-process.

Deliberately subprocess-based rather than calling ai_actions.cli.main()
directly: core.py/manage.py resolve their default services_dir/
models_file from module-level constants that are frozen at import time
from AI_ACTIONS_SERVICES_DIR/AI_ACTIONS_MODELS_FILE, so an in-process
test would need those env vars set *before* ai_actions.core is first
imported anywhere in the test session — fragile and order-dependent. A
subprocess re-imports cleanly every time, which is also a more faithful
test of what a user actually runs.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from tests.helpers import write_service_file

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_cli(args, services_dir, models_file, input=None):
    env = {
        **os.environ,
        "AI_ACTIONS_SERVICES_DIR": str(services_dir),
        "AI_ACTIONS_MODELS_FILE": str(models_file),
    }
    return subprocess.run(
        [sys.executable, "-m", "ai_actions", *args],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        input=input,
        timeout=30,
    )


# --- list / service list -----------------------------------------------------------


def test_list_and_service_list_are_equivalent(services_dir, models_file):
    write_service_file(services_dir, "alpha", category="writing")
    write_service_file(services_dir, "beta", category="coding")

    result_list = run_cli(["list"], services_dir, models_file)
    result_service_list = run_cli(["service", "list"], services_dir, models_file)

    assert result_list.returncode == 0
    assert result_list.stdout == result_service_list.stdout
    assert "alpha" in result_list.stdout
    assert "beta" in result_list.stdout


def test_list_filters_by_category(services_dir, models_file):
    write_service_file(services_dir, "alpha", category="writing")
    write_service_file(services_dir, "beta", category="coding")

    result = run_cli(["list", "--category", "writing"], services_dir, models_file)

    assert "alpha" in result.stdout
    assert "beta" not in result.stdout


def test_list_filters_by_query(services_dir, models_file):
    write_service_file(services_dir, "alpha", name="Alpha Thing")
    write_service_file(services_dir, "beta", name="Beta Thing")

    result = run_cli(["list", "--query", "alpha"], services_dir, models_file)

    assert "alpha" in result.stdout
    assert "beta" not in result.stdout


# --- service show/search/categories -----------------------------------------------------------


def test_service_show(services_dir, models_file):
    write_service_file(services_dir, "alpha", prompt="Be helpful.")

    result = run_cli(["service", "show", "alpha"], services_dir, models_file)

    assert result.returncode == 0
    assert "id:                  alpha" in result.stdout
    assert "Be helpful." in result.stdout


def test_service_show_nonexistent(services_dir, models_file):
    result = run_cli(["service", "show", "nope"], services_dir, models_file)
    assert result.returncode == 1
    assert "Unknown service" in result.stderr


def test_service_search_matches_prompt_text(services_dir, models_file):
    write_service_file(services_dir, "alpha", prompt="A very distinctive phrase.")
    write_service_file(services_dir, "beta", prompt="Something else entirely.")

    result = run_cli(["service", "search", "distinctive"], services_dir, models_file)

    assert "alpha" in result.stdout
    assert "beta" not in result.stdout


def test_service_categories_counts(services_dir, models_file):
    write_service_file(services_dir, "alpha", category="writing")
    write_service_file(services_dir, "beta", category="writing")
    write_service_file(services_dir, "gamma", category="coding")

    result = run_cli(["service", "categories"], services_dir, models_file)

    assert f"{'writing':20s} {2:3d}" in result.stdout
    assert f"{'coding':20s} {1:3d}" in result.stdout


# --- service validate -----------------------------------------------------------


def test_service_validate_all_ok(services_dir, models_file):
    write_service_file(services_dir, "alpha")
    result = run_cli(["service", "validate"], services_dir, models_file)
    assert result.returncode == 0
    assert "All services OK" in result.stdout


def test_service_validate_reports_problems(services_dir, models_file):
    write_service_file(services_dir, "alpha", model="unknown-model")
    result = run_cli(["service", "validate"], services_dir, models_file)
    assert result.returncode == 1
    assert "unknown model" in result.stderr


# --- run -----------------------------------------------------------


def test_run_with_text_and_no_gui(services_dir, stub_models_file):
    write_service_file(services_dir, "echo-test")
    result = run_cli(["run", "echo-test", "--text", "hello", "--no-gui"], services_dir, stub_models_file)
    assert result.returncode == 0
    assert "ECHO[test-model]: olleh" in result.stdout


def test_run_unknown_service(services_dir, stub_models_file):
    result = run_cli(["run", "nope", "--text", "hi", "--no-gui"], services_dir, stub_models_file)
    assert result.returncode == 1
    assert "Unknown service" in result.stderr


def test_run_empty_text_is_an_error(services_dir, stub_models_file):
    write_service_file(services_dir, "echo-test")
    result = run_cli(["run", "echo-test", "--text", "   ", "--no-gui"], services_dir, stub_models_file)
    assert result.returncode == 1
    assert "empty" in result.stderr


def test_run_file_input(tmp_path, services_dir, stub_models_file):
    write_service_file(services_dir, "echo-test")
    input_file = tmp_path / "input.txt"
    input_file.write_text("from a file")

    result = run_cli(["run", "echo-test", "--file", str(input_file), "--no-gui"], services_dir, stub_models_file)

    assert result.returncode == 0
    assert "ECHO[test-model]:" in result.stdout


def test_run_stdin_input(services_dir, stub_models_file):
    write_service_file(services_dir, "echo-test")

    result = run_cli(
        ["run", "echo-test", "--stdin", "--no-gui"], services_dir, stub_models_file, input="from stdin"
    )

    assert result.returncode == 0
    assert "ECHO[test-model]:" in result.stdout


def test_run_output_file(tmp_path, services_dir, stub_models_file):
    write_service_file(services_dir, "echo-test")
    output_file = tmp_path / "output.txt"

    result = run_cli(
        ["run", "echo-test", "--text", "hi", "--no-gui", "--output", str(output_file)],
        services_dir,
        stub_models_file,
    )

    assert result.returncode == 0
    assert output_file.exists()
    assert "ECHO[test-model]:" in output_file.read_text()


def test_text_and_file_are_mutually_exclusive(tmp_path, services_dir, stub_models_file):
    write_service_file(services_dir, "echo-test")
    f = tmp_path / "x.txt"
    f.write_text("x")

    result = run_cli(
        ["run", "echo-test", "--text", "a", "--file", str(f), "--no-gui"], services_dir, stub_models_file
    )

    assert result.returncode == 2
    assert "not allowed with argument" in result.stderr


# --- service create/set/duplicate/delete wiring -----------------------------------------------------------


def test_service_create_and_delete_end_to_end(services_dir, models_file):
    create_result = run_cli(
        ["service", "create", "new-svc", "--prompt", "Be helpful.", "--no-edit"], services_dir, models_file
    )
    assert create_result.returncode == 0
    assert (services_dir / "new-svc.yaml").exists()

    delete_result = run_cli(["service", "delete", "new-svc", "--yes"], services_dir, models_file)
    assert delete_result.returncode == 0
    assert not (services_dir / "new-svc.yaml").exists()


def test_service_duplicate_end_to_end(services_dir, models_file):
    write_service_file(services_dir, "source", name="Source")

    result = run_cli(
        ["service", "duplicate", "source", "clone", "--name", "Clone", "--no-edit"], services_dir, models_file
    )

    assert result.returncode == 0
    assert (services_dir / "clone.yaml").exists()


def test_service_set_end_to_end(services_dir, models_file):
    write_service_file(services_dir, "svc", category="old")

    result = run_cli(["service", "set", "svc", "--category", "new"], services_dir, models_file)

    assert result.returncode == 0
    content = (services_dir / "svc.yaml").read_text()
    assert "category: new" in content
