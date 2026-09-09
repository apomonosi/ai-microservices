from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from ai_actions.gui.tray import BusyIndicator, _display_might_exist
from tests.helpers import write_service_file

pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtWidgets import QSystemTrayIcon  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_busy_indicator_shows_and_hides_when_tray_available(monkeypatch):
    calls = []

    monkeypatch.setattr(QSystemTrayIcon, "isSystemTrayAvailable", staticmethod(lambda: True))
    monkeypatch.setattr(QSystemTrayIcon, "show", lambda self: calls.append("show"))
    monkeypatch.setattr(QSystemTrayIcon, "hide", lambda self: calls.append("hide"))
    monkeypatch.setattr(QSystemTrayIcon, "setToolTip", lambda self, text: None)

    with BusyIndicator("running thing…"):
        calls.append("inside")

    assert calls == ["show", "inside", "hide"]


def test_busy_indicator_noop_when_tray_unavailable(monkeypatch):
    calls = []

    monkeypatch.setattr(QSystemTrayIcon, "isSystemTrayAvailable", staticmethod(lambda: False))
    monkeypatch.setattr(QSystemTrayIcon, "show", lambda self: calls.append("show"))
    monkeypatch.setattr(QSystemTrayIcon, "hide", lambda self: calls.append("hide"))

    with BusyIndicator("running thing…"):
        calls.append("inside")

    assert calls == ["inside"]


def test_busy_indicator_hides_icon_and_reraises_on_exception(monkeypatch):
    calls = []

    monkeypatch.setattr(QSystemTrayIcon, "isSystemTrayAvailable", staticmethod(lambda: True))
    monkeypatch.setattr(QSystemTrayIcon, "show", lambda self: calls.append("show"))
    monkeypatch.setattr(QSystemTrayIcon, "hide", lambda self: calls.append("hide"))
    monkeypatch.setattr(QSystemTrayIcon, "setToolTip", lambda self, text: None)

    with pytest.raises(ValueError, match="boom"):
        with BusyIndicator("running thing…"):
            calls.append("inside")
            raise ValueError("boom")

    assert calls == ["show", "inside", "hide"]


def test_busy_indicator_noop_when_pyside6_missing(monkeypatch):
    real_import = __import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("PySide6"):
            raise ImportError("no PySide6 for this test")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with BusyIndicator("running thing…") as indicator:
        assert indicator._icon is None


# --- _display_might_exist ---------------------------------------------------


def test_display_might_exist_false_when_nothing_set(monkeypatch):
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.delenv("QT_QPA_PLATFORM", raising=False)

    assert _display_might_exist() is False


@pytest.mark.parametrize("var", ["DISPLAY", "WAYLAND_DISPLAY", "QT_QPA_PLATFORM"])
def test_display_might_exist_true_when_any_var_set(monkeypatch, var):
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.delenv("QT_QPA_PLATFORM", raising=False)
    monkeypatch.setenv(var, "something")

    assert _display_might_exist() is True


# --- regression: a real, fully headless `ai-actions run --no-gui` ----------
# This is the exact scenario that used to hard-abort (SIGABRT) the whole
# process: BusyIndicator used to construct a QApplication unconditionally,
# and Qt's default "xcb" platform plugin aborts the process (not a
# catchable Python exception) when there's no X server at all. Run as a
# real subprocess with DISPLAY/WAYLAND_DISPLAY/QT_QPA_PLATFORM all
# removed - conftest.py's QT_QPA_PLATFORM=offscreen default would
# otherwise mask exactly this regression.


def test_run_no_gui_survives_with_no_display_at_all(services_dir, stub_models_file):
    write_service_file(services_dir, "echo-test")
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in ("DISPLAY", "WAYLAND_DISPLAY", "QT_QPA_PLATFORM")
    }
    env["AI_ACTIONS_SERVICES_DIR"] = str(services_dir)
    env["AI_ACTIONS_MODELS_FILE"] = str(stub_models_file)

    result = subprocess.run(
        [sys.executable, "-m", "ai_actions", "run", "echo-test", "--text", "hello", "--no-gui"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "ECHO[test-model]: olleh" in result.stdout
