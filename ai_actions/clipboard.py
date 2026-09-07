"""System clipboard access via Qt's QClipboard.

PySide6 is imported lazily inside these functions so that the rest of the
engine (config loading, the HTTP call, `ai-actions list`, `--text` input)
works without PySide6 installed or a display available — useful for
testing over SSH or in a headless environment. A real desktop session is
only needed once you actually read/write the clipboard.
"""

from __future__ import annotations

import sys
import time


def _app():
    from PySide6.QtGui import QGuiApplication

    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication(sys.argv[:1])
    return app


def read_text() -> str:
    from PySide6.QtGui import QClipboard

    app = _app()
    return app.clipboard().text(QClipboard.Mode.Clipboard)


def write_text(text: str, settle_seconds: float = 0.3) -> None:
    """Write text to the system clipboard.

    On X11/Wayland the clipboard content is served by the writing process
    itself; a paste can fail if that process exits before the pasting
    application requests the content. Processing events plus a short delay
    before returning gives it time to do so. If this proves flaky in
    practice, running a clipboard manager (e.g. Klipper) that grabs the
    content immediately is the usual fix.
    """
    from PySide6.QtGui import QClipboard

    app = _app()
    app.clipboard().setText(text, QClipboard.Mode.Clipboard)
    app.processEvents()
    time.sleep(settle_seconds)
