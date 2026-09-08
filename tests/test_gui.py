"""GUI widget tests. Skipped entirely if PySide6 isn't installed.

Runs with QT_QPA_PLATFORM=offscreen (set in conftest.py) so no real
display is needed — these construct real Qt widgets and simulate
button clicks, they just never show a window.
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox  # noqa: E402

from ai_actions.core import Service  # noqa: E402
from ai_actions.gui.picker import ActionPicker  # noqa: E402
from ai_actions.gui.result_inspector import ResultInspector  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def _service(**overrides) -> Service:
    fields = dict(
        id="test",
        name="Test Service",
        category="testing",
        model="local",
        system_prompt="...",
        review="text",
        clipboard_on_accept="none",
    )
    fields.update(overrides)
    return Service(**fields)


# --- ResultInspector -----------------------------------------------------------


def test_result_inspector_diff_mode_accept(qapp):
    service = _service(review="diff", clipboard_on_accept="replace")
    dialog = ResultInspector(service, "old text", "new text")
    buttons = dialog.findChild(QDialogButtonBox)
    accept_btn = next(b for b in buttons.buttons() if "Accept" in b.text())

    accept_btn.click()

    assert dialog.result() == QDialog.DialogCode.Accepted


def test_result_inspector_diff_mode_reject(qapp):
    service = _service(review="diff", clipboard_on_accept="replace")
    dialog = ResultInspector(service, "old text", "new text")
    buttons = dialog.findChild(QDialogButtonBox)
    reject_btn = next(b for b in buttons.buttons() if "Reject" in b.text())

    reject_btn.click()

    assert dialog.result() == QDialog.DialogCode.Rejected


def test_result_inspector_text_mode_copy_button_writes_clipboard(qapp, monkeypatch):
    calls = []
    monkeypatch.setattr("ai_actions.gui.result_inspector.clipboard.write_text", lambda text: calls.append(text))
    service = _service(review="text")
    dialog = ResultInspector(service, "irrelevant", "the result")
    buttons = dialog.findChild(QDialogButtonBox)
    copy_btn = next(b for b in buttons.buttons() if b.text() == "Copy")

    copy_btn.click()

    assert calls == ["the result"]


def test_result_inspector_text_mode_close_button_rejects(qapp):
    service = _service(review="text")
    dialog = ResultInspector(service, "irrelevant", "the result")
    buttons = dialog.findChild(QDialogButtonBox)
    close_btn = next(b for b in buttons.buttons() if b.text() == "Close")

    close_btn.click()

    assert dialog.result() == QDialog.DialogCode.Rejected


# --- ActionPicker -----------------------------------------------------------


def test_action_picker_lists_all_services_initially(qapp):
    services = [_service(id="alpha", name="Alpha"), _service(id="beta", name="Beta")]
    picker = ActionPicker(services)
    assert picker._list.count() == 2


def test_action_picker_filters_by_query(qapp):
    services = [
        _service(id="alpha", name="Alpha Service", category="writing"),
        _service(id="beta", name="Beta Service", category="coding"),
    ]
    picker = ActionPicker(services)

    picker._search.setText("beta")

    assert picker._list.count() == 1
    assert "Beta" in picker._list.item(0).text()


def test_action_picker_filter_with_no_matches(qapp):
    services = [_service(id="alpha", name="Alpha")]
    picker = ActionPicker(services)

    picker._search.setText("zzz-no-match")

    assert picker._list.count() == 0


def test_action_picker_activation_selects_and_accepts(qapp):
    services = [_service(id="alpha", name="Alpha"), _service(id="beta", name="Beta")]
    picker = ActionPicker(services)
    item = picker._list.item(0)

    picker._activate_item(item)

    assert picker.selected_service is not None
    assert picker.selected_service.id in ("alpha", "beta")
    assert picker.result() == QDialog.DialogCode.Accepted


def test_action_picker_keyboard_navigation_wraps_around(qapp):
    services = [_service(id="a"), _service(id="b"), _service(id="c")]
    picker = ActionPicker(services)
    picker._list.setCurrentRow(2)

    picker._move_selection(1)

    assert picker._list.currentRow() == 0
