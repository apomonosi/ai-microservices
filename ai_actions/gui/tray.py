"""A system-tray "busy" indicator, shown for the duration of a service
call so a KDE-shortcut-triggered run isn't silently invisible while the
model endpoint is thinking.

Best-effort only: this must never become a new reason ai-actions needs a
display or PySide6 installed. If PySide6 isn't available, or there's no
system tray to show an icon in (headless/SSH sessions, CI, GNOME's
default Wayland session), BusyIndicator quietly does nothing.

The icon is deliberately held up for a minimum real duration (see
_REGISTER_SECONDS/_MIN_VISIBLE_SECONDS below) rather than shown and
hidden the instant the call starts/finishes - confirmed directly that
without this, a fast local model can complete before the desktop shell
has even registered the tray icon, so nothing is ever seen at all.

Known residual limitation: if DISPLAY/WAYLAND_DISPLAY is set but stale -
pointing at an X/Wayland session that's no longer there, e.g. a
disconnected SSH X11-forwarding session - Qt's platform-plugin failure is
a hard process abort at the C++ level, not a catchable Python exception,
so this can still crash the run. That risk already existed for GUI mode
(the review dialog) and `picker` before this module; it's not caught here
because there is no reliable way to check "is DISPLAY actually live"
without risking the same abort. A genuinely absent display (no env var
set at all - the common headless case: cron, plain SSH, most CI) is what
_display_might_exist() actually guards against, and does so completely.
"""

from __future__ import annotations

import os
import sys
import time

# How long to keep pumping the Qt event loop right after `.show()`, before
# letting the blocking model call start. A single `processEvents()` call
# only drains whatever's *already* queued - it doesn't wait for the
# desktop shell's D-Bus round trip that actually registers a brand-new
# StatusNotifierItem, which is asynchronous and can take a moment. Without
# this, a fast local model can finish (and hide the icon again) before
# Plasma ever gets to paint it - confirmed directly against a real KDE
# Plasma session: a one-shot processEvents() showed nothing, holding the
# icon up with a real event loop for a couple of seconds did.
_REGISTER_SECONDS = 0.3

# Minimum total time the icon stays up, enforced in __exit__. The whole
# point is a human being able to notice it; a sub-100ms flash defeats
# that even once registration has completed.
_MIN_VISIBLE_SECONDS = 0.6


def _pump(app, seconds: float) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)


def _display_might_exist() -> bool:
    """True if there's some real reason to expect a Qt platform plugin
    can actually load: a display env var is set (X11/Wayland), or
    QT_QPA_PLATFORM is explicitly set (trust it, including "offscreen" -
    proven safe to construct a QApplication under, see below).

    Without this check, `QApplication(...)` on Linux defaults to trying
    the "xcb" plugin, which - confirmed directly - hard-aborts the whole
    process (SIGABRT, not a catchable Python exception) when there's no
    X server to connect to. A true headless run (SSH, cron, CI with
    nothing set) must never reach that call at all.
    """
    return bool(
        os.environ.get("DISPLAY")
        or os.environ.get("WAYLAND_DISPLAY")
        or os.environ.get("QT_QPA_PLATFORM")
    )


class BusyIndicator:
    """`with BusyIndicator("..."):` shows a tray icon with the given
    tooltip for the lifetime of the block, and hides it afterward -
    including when the block raises. Never raises itself.
    """

    def __init__(self, tooltip: str):
        self._tooltip = tooltip
        self._icon = None
        self._app = None
        self._shown_at = None

    def __enter__(self) -> "BusyIndicator":
        # Broad except by design: this is a cosmetic nicety layered over
        # run_service(), not a requirement - any failure here (missing
        # PySide6, no usable Qt platform plugin, no tray) must degrade to
        # doing nothing rather than taking the real command down with it.
        if not _display_might_exist():
            return self
        try:
            from PySide6.QtGui import QIcon
            from PySide6.QtWidgets import QApplication, QSystemTrayIcon

            # QSystemTrayIcon.isSystemTrayAvailable() needs a QApplication
            # to already exist - calling it first crashes (segfault,
            # confirmed directly: a real Qt/PySide6 quirk, not
            # theoretical), so the instance is created before it's asked.
            app = QApplication.instance() or QApplication(sys.argv[:1])
            if not QSystemTrayIcon.isSystemTrayAvailable():
                return self

            icon = QSystemTrayIcon(QIcon.fromTheme("system-run"))
            icon.setToolTip(self._tooltip)
            icon.show()
            self._shown_at = time.monotonic()
            _pump(app, _REGISTER_SECONDS)
            self._app, self._icon = app, icon
        except Exception:
            self._app, self._icon = None, None
        return self

    def __exit__(self, *exc_info) -> bool:
        try:
            if self._icon is not None:
                elapsed = time.monotonic() - self._shown_at
                remaining = _MIN_VISIBLE_SECONDS - elapsed
                if remaining > 0:
                    _pump(self._app, remaining)
                self._icon.hide()
                self._app.processEvents()
        except Exception:
            pass
        return False
