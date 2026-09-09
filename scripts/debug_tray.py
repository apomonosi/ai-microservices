"""Manual diagnostic for the system-tray "busy" icon (ai_actions/gui/tray.py).

Not exercised by pytest - this sandbox has no display, so BusyIndicator's
actual on-screen behavior can only be confirmed on a real desktop. Run
this directly on the machine where the tray icon isn't showing up:

    python3 scripts/debug_tray.py

It checks, in order, each thing that could independently make the icon
invisible even though the code runs without error: no display detected,
no system tray available at all, the "system-run" icon resolving to
nothing, or the icon just not being visible long enough to notice. It
also fires a real desktop notification via showMessage() as an
independent check - if that pops up but no tray icon appears, the
problem is specifically about tray visibility (icon theme, or Plasma's
per-app "hidden icons" setting), not the underlying Qt/D-Bus plumbing.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ai_actions.gui.tray import _display_might_exist  # noqa: E402


def main() -> int:
    print("--- environment ---")
    for var in ("DISPLAY", "WAYLAND_DISPLAY", "QT_QPA_PLATFORM", "XDG_SESSION_TYPE", "XDG_CURRENT_DESKTOP"):
        print(f"{var} = {os.environ.get(var)!r}")
    print(f"_display_might_exist() = {_display_might_exist()}")
    if not _display_might_exist():
        print("\nNo display detected by that check - this is why the real `ai-actions run`")
        print("skips the tray entirely. If you ARE on a real desktop session, something")
        print("about how this was launched (e.g. a systemd unit, or a shortcut runner that")
        print("scrubs the environment) isn't passing DISPLAY/WAYLAND_DISPLAY through.")
        return 1

    try:
        from PySide6.QtGui import QIcon
        from PySide6.QtWidgets import QApplication, QSystemTrayIcon
    except ImportError as exc:
        print(f"\nPySide6 not importable: {exc}")
        return 1

    app = QApplication(sys.argv[:1])

    print("\n--- Qt tray availability ---")
    available = QSystemTrayIcon.isSystemTrayAvailable()
    print(f"QSystemTrayIcon.isSystemTrayAvailable() = {available}")
    if not available:
        print("\nQt itself says there's no system tray. On Plasma this usually means the")
        print("System Tray plasmoid isn't running, or org.kde.StatusNotifierWatcher isn't")
        print("registered on the session bus. Check with:")
        print("  qdbus org.kde.StatusNotifierWatcher /StatusNotifierWatcher 2>&1 | head -5")
        return 1

    print("\n--- icon lookup ---")
    icon = QIcon.fromTheme("system-run")
    print(f"QIcon.fromTheme('system-run').isNull() = {icon.isNull()}")
    print(f"available sizes = {icon.availableSizes()}")
    if icon.isNull():
        print("\nThe icon name resolved to nothing in your current icon theme - the tray")
        print("entry may be getting created with a blank/invisible pixmap. Try a name you")
        print("know your theme has (`ls /usr/share/icons/breeze/*/actions/ | grep run`, or")
        print("just swap in something else here) to confirm this is the cause.")

    print("\n--- showing the icon for 20 seconds ---")
    print("Check your tray NOW, including the hidden-icons chevron/arrow if you have one")
    print("(Plasma sometimes auto-hides an app's first-ever tray icon there). A desktop")
    print("notification should also pop up as an independent check.")
    tray_icon = QSystemTrayIcon(icon)
    tray_icon.setToolTip("ai-actions debug_tray.py")
    tray_icon.show()
    tray_icon.showMessage(
        "ai-actions",
        "If you see this notification but no tray icon, the icon/tray-visibility "
        "side is the problem, not the underlying Qt/D-Bus setup.",
        QSystemTrayIcon.MessageIcon.Information,
        8000,
    )

    from PySide6.QtCore import QTimer

    QTimer.singleShot(20_000, app.quit)
    app.exec()

    tray_icon.hide()
    app.processEvents()
    print("\nDone - icon hidden. Report back what you saw (or didn't).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
