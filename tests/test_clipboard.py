from __future__ import annotations

import subprocess

import pytest

from ai_actions import clipboard


# --- _is_wayland -----------------------------------------------------------


def test_is_wayland_via_wayland_display(monkeypatch):
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
    monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)
    assert clipboard._is_wayland() is True


def test_is_wayland_via_session_type(monkeypatch):
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    assert clipboard._is_wayland() is True


def test_is_not_wayland_on_x11(monkeypatch):
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    assert clipboard._is_wayland() is False


# --- read_text ---------------------------------------------------------------


def test_read_text_wayland_success(monkeypatch):
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
    monkeypatch.setattr(clipboard.shutil, "which", lambda binary: f"/usr/bin/{binary}")
    calls = []

    def fake_run(cmd, capture_output, text):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="hello", stderr="")

    monkeypatch.setattr(clipboard.subprocess, "run", fake_run)

    assert clipboard.read_text() == "hello"
    assert calls == [["wl-paste", "--no-newline"]]


def test_read_text_x11_success(monkeypatch):
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    monkeypatch.setattr(clipboard.shutil, "which", lambda binary: f"/usr/bin/{binary}")
    calls = []

    def fake_run(cmd, capture_output, text):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="hello", stderr="")

    monkeypatch.setattr(clipboard.subprocess, "run", fake_run)

    assert clipboard.read_text() == "hello"
    assert calls == [["xclip", "-selection", "clipboard", "-o"]]


def test_read_text_missing_binary_raises(monkeypatch):
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
    monkeypatch.setattr(clipboard.shutil, "which", lambda binary: None)

    with pytest.raises(clipboard.ClipboardError, match="not found on PATH"):
        clipboard.read_text()


def test_read_text_nonzero_exit_returns_empty_not_error(monkeypatch):
    # An empty or non-text clipboard makes wl-paste/xclip exit non-zero;
    # that's "no text available", not a real error.
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
    monkeypatch.setattr(clipboard.shutil, "which", lambda binary: f"/usr/bin/{binary}")
    monkeypatch.setattr(
        clipboard.subprocess,
        "run",
        lambda cmd, capture_output, text: subprocess.CompletedProcess(cmd, 1, stdout="", stderr="no selection"),
    )

    assert clipboard.read_text() == ""


# --- write_text ---------------------------------------------------------------


def test_write_text_x11_success(monkeypatch):
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    monkeypatch.setattr(clipboard.shutil, "which", lambda binary: f"/usr/bin/{binary}")
    calls = []

    def fake_run(cmd, input, text, check, capture_output):
        calls.append((cmd, input))
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(clipboard.subprocess, "run", fake_run)

    clipboard.write_text("hello")

    assert calls == [(["xclip", "-selection", "clipboard"], "hello")]


def test_write_text_wayland_success(monkeypatch):
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
    monkeypatch.setattr(clipboard.shutil, "which", lambda binary: f"/usr/bin/{binary}")
    calls = []

    def fake_run(cmd, input, text, check, capture_output):
        calls.append((cmd, input))
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(clipboard.subprocess, "run", fake_run)

    clipboard.write_text("hello")

    assert calls == [(["wl-copy"], "hello")]


def test_write_text_missing_binary_raises(monkeypatch):
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
    monkeypatch.setattr(clipboard.shutil, "which", lambda binary: None)

    with pytest.raises(clipboard.ClipboardError, match="not found on PATH"):
        clipboard.write_text("hello")


def test_write_text_failure_raises_clipboard_error_not_calledprocesserror(monkeypatch):
    # Regression test: write_text used to let subprocess.CalledProcessError
    # propagate raw on a non-zero exit instead of a clean ClipboardError.
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
    monkeypatch.setattr(clipboard.shutil, "which", lambda binary: f"/usr/bin/{binary}")

    def fake_run(cmd, input, text, check, capture_output):
        raise subprocess.CalledProcessError(1, cmd, stderr="compositor gone")

    monkeypatch.setattr(clipboard.subprocess, "run", fake_run)

    with pytest.raises(clipboard.ClipboardError, match="compositor gone"):
        clipboard.write_text("hello")
