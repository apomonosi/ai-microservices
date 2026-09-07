"""The Result Inspector: shows a service's output for review before it's
trusted, per ../../ROADMAP.md Phase 2.

- review == "diff": word-level diff view with Reject / Accept & Copy.
- review == "text" (or anything else): plain read-only view with a manual
  Copy button, since there's no "corrected version" concept to diff against
  and no clipboard_on_accept to trigger.
"""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QTextBrowser, QVBoxLayout

from .. import clipboard
from ..core import Service
from ..diff import count_changes, render_word_diff_html


class ResultInspector(QDialog):
    def __init__(self, service: Service, original_text: str, result_text: str, parent=None):
        super().__init__(parent)
        self.result_text = result_text
        self.setWindowTitle(service.name)
        self.resize(640, 420)

        layout = QVBoxLayout(self)

        if service.review == "diff":
            n = count_changes(original_text, result_text)
            layout.addWidget(QLabel(f"<b>{service.name}</b> — {n} change{'s' if n != 1 else ''}"))

            view = QTextBrowser()
            diff_html = render_word_diff_html(original_text, result_text)
            view.setHtml(f"<div style='font-size:11pt; line-height:150%;'>{diff_html}</div>")
            layout.addWidget(view, 1)

            buttons = QDialogButtonBox()
            reject_btn = buttons.addButton("Reject", QDialogButtonBox.ButtonRole.RejectRole)
            accept_btn = buttons.addButton("Accept && Copy", QDialogButtonBox.ButtonRole.AcceptRole)
            accept_btn.setDefault(True)
            reject_btn.clicked.connect(self.reject)
            accept_btn.clicked.connect(self.accept)
        else:
            layout.addWidget(QLabel(f"<b>{service.name}</b>"))

            view = QTextBrowser()
            view.setPlainText(result_text)
            layout.addWidget(view, 1)

            buttons = QDialogButtonBox()
            copy_btn = buttons.addButton("Copy", QDialogButtonBox.ButtonRole.ActionRole)
            close_btn = buttons.addButton("Close", QDialogButtonBox.ButtonRole.RejectRole)
            close_btn.setDefault(True)
            copy_btn.clicked.connect(lambda: clipboard.write_text(self.result_text))
            close_btn.clicked.connect(self.reject)

        layout.addWidget(buttons)
