"""System clipboard access.

Uses the Wayland clipboard CLI tools (wl-clipboard) on Wayland sessions and
xclip on X11.

Qt's QClipboard was tried first (per the original roadmap) but proved
unreliable for a short-lived CLI process on Wayland/KDE Plasma: reading
immediately after constructing QGuiApplication races the compositor's
asynchronous clipboard-offer handshake, and with no event loop running in
a one-shot process, it consistently returned empty text. wl-paste/wl-copy
don't have this problem — they're what the original bash-script prototype
already used successfully — so we use them here instead. wl-copy also
self-daemonizes to keep serving the clipboard, which solves the "process
must stay alive to be pasted from" problem more cleanly than manually
delaying before exit.

QClipboard is expected to become viable from Phase 2 onward, once
ai-actions is a persistent Qt application with its own running event
loop; revisit then if it's worth switching this module over.
"""

from __future__ import annotations

import os
import shutil
import subprocess


class ClipboardError(RuntimeError):
    """The clipboard could not be read or written."""


def _is_wayland() -> bool:
    return bool(os.environ.get("WAYLAND_DISPLAY")) or os.environ.get("XDG_SESSION_TYPE") == "wayland"


def _require(binary: str, package_hint: str) -> str:
    path = shutil.which(binary)
    if path is None:
        raise ClipboardError(f"'{binary}' not found on PATH — install {package_hint}")
    return path


def read_text() -> str:
    if _is_wayland():
        _require("wl-paste", "wl-clipboard")
        result = subprocess.run(["wl-paste", "--no-newline"], capture_output=True, text=True)
    else:
        _require("xclip", "xclip")
        result = subprocess.run(["xclip", "-selection", "clipboard", "-o"], capture_output=True, text=True)
    # A non-text clipboard (or an empty one) makes both tools exit non-zero;
    # treat that as "no text available" rather than an error.
    return result.stdout if result.returncode == 0 else ""


def write_text(text: str) -> None:
    if _is_wayland():
        _require("wl-copy", "wl-clipboard")
        command = ["wl-copy"]
    else:
        _require("xclip", "xclip")
        command = ["xclip", "-selection", "clipboard"]
    try:
        subprocess.run(command, input=text, text=True, check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        raise ClipboardError(f"'{command[0]}' failed" + (f": {stderr}" if stderr else "")) from exc
