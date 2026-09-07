"""The Action Picker: Meta+Alt+A -> a filterable list of services -> Enter
runs the selected one, per ../../ROADMAP.md Phase 3.

Plain Qt Widgets for now (see ROADMAP.md Phase 3.5 for an optional later
upgrade to Kirigami/QML for a more animated look).
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout

from ..core import Service

_CATEGORY_ICONS = {
    "writing": "accessories-text-editor",
    "language": "preferences-desktop-locale",
    "coding": "text-x-script",
}
_DEFAULT_ICON = "system-run"


class ActionPicker(QDialog):
    def __init__(self, services: list[Service], parent=None):
        super().__init__(parent)
        self._services = sorted(services, key=lambda s: s.name)
        self.selected_service: Service | None = None

        self.setWindowTitle("AI Actions")
        self.resize(420, 360)

        layout = QVBoxLayout(self)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search actions…")
        self._search.installEventFilter(self)
        layout.addWidget(self._search)

        self._list = QListWidget()
        self._list.itemActivated.connect(self._activate_item)
        layout.addWidget(self._list, 1)

        self._populate("")
        self._search.textChanged.connect(self._populate)
        self._search.setFocus()

    def _populate(self, query: str) -> None:
        self._list.clear()
        query = query.strip().lower()
        for service in self._services:
            haystack = f"{service.name} {service.id} {service.category} {service.description}".lower()
            if query and query not in haystack:
                continue
            icon_name = _CATEGORY_ICONS.get(service.category, _DEFAULT_ICON)
            item = QListWidgetItem(QIcon.fromTheme(icon_name), f"{service.name}  ·  {service.category}")
            item.setData(Qt.ItemDataRole.UserRole, service)
            self._list.addItem(item)
        if self._list.count():
            self._list.setCurrentRow(0)

    def _activate_item(self, item: QListWidgetItem) -> None:
        self.selected_service = item.data(Qt.ItemDataRole.UserRole)
        self.accept()

    def _move_selection(self, delta: int) -> None:
        count = self._list.count()
        if count == 0:
            return
        row = self._list.currentRow()
        row = (row + delta) % count if row != -1 else 0
        self._list.setCurrentRow(row)

    def eventFilter(self, obj, event) -> bool:
        if obj is self._search and event.type() == event.Type.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_Down:
                self._move_selection(1)
                return True
            if key == Qt.Key.Key_Up:
                self._move_selection(-1)
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                item = self._list.currentItem()
                if item is not None:
                    self._activate_item(item)
                return True
        return super().eventFilter(obj, event)
