from __future__ import annotations

import json
import os
import sys
import ctypes
from ctypes import wintypes
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QFontDialog,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QIcon, QPainter, QPen, QPalette

from pathlib import Path

from database.db import SessionLocal
from database.models import ClienteFornecedor, Contrato


class RelatoriosWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        filter_bar = QFrame()
        filter_bar.setStyleSheet(
            "background: #EAF2FF;"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 12px;"
        )
        fb_layout = QHBoxLayout(filter_bar)
        fb_layout.setContentsMargins(10, 8, 10, 8)
        fb_layout.setSpacing(6)

        self.tab_buttons = []
        for label in ["Hoje", "Ultimos 7 dias", "Ultimos 30 dias", "Personalizado"]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setStyleSheet(
                "QPushButton {"
                "background: rgba(255,255,255,0.9);"
                "border: 1px solid rgba(30,136,229,0.2);"
                "border-radius: 10px;"
                "padding: 6px 12px;"
                "color: #0D47A1;"
                "font-weight: 600;"
                "}"
                "QPushButton:checked {"
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
                "stop:0 #64B5F6, stop:1 #1E88E5);"
                "color: #FFFFFF;"
                "border: none;"
                "}"
            )
            btn.clicked.connect(self._on_tab_clicked)
            self.tab_buttons.append(btn)
            fb_layout.addWidget(btn)
        self.tab_buttons[2].setChecked(True)
        fb_layout.addStretch(1)
        main_layout.addWidget(filter_bar)

        cards = QFrame()
        cards.setStyleSheet(
            "background: #F8FBFF;"
            "border: 1px solid rgba(30,136,229,0.18);"
            "border-radius: 14px;"
        )
        cards_layout = QGridLayout(cards)
        cards_layout.setContentsMargins(12, 12, 12, 12)
        cards_layout.setSpacing(10)

        cards_layout.addWidget(self._stat_card("Orcamentos", "12", "Ultimos 30 dias"), 0, 0)
        cards_layout.addWidget(self._stat_card("Contratos", "0", "Total"), 0, 1)
        cards_layout.addWidget(self._stat_card("Clientes", "0", "Cadastrados"), 1, 0)
        cards_layout.addWidget(
            self._list_card("Atividades", ["Orcamentos gerados", "Contratos gerados", "Clientes cadastrados"]),
            1,
            1,
        )
        cards_layout.setRowStretch(0, 1)
        cards_layout.setRowStretch(1, 1)
        cards_layout.setColumnStretch(0, 1)
        cards_layout.setColumnStretch(1, 1)

        main_layout.addWidget(cards, 1)

        planilha_card = QFrame()
        planilha_card.setStyleSheet(
            "background: #FFFFFF;"
            "border: 1px solid rgba(30,136,229,0.18);"
            "border-radius: 14px;"
        )
        planilha_layout = QHBoxLayout(planilha_card)
        planilha_layout.setContentsMargins(12, 12, 12, 12)
        planilha_layout.setSpacing(10)

        planilha_title = QLabel("Planilha")
        planilha_title.setStyleSheet("color: #0D47A1; font-weight: 700;")
        planilha_layout.addWidget(planilha_title)

        planilha_desc = QLabel("Crie tabelas livres com estilos, mesclas e modelos.")
        planilha_desc.setStyleSheet("color: #5c6f91; font-size: 12px;")
        planilha_layout.addWidget(planilha_desc, 1)

        self.planilha_btn = QPushButton("Planilha")
        self.planilha_btn.setStyleSheet(
            "QPushButton {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
            "stop:0 #64B5F6, stop:1 #1E88E5);"
            "color: #FFFFFF;"
            "border: none;"
            "border-radius: 10px;"
            "padding: 6px 14px;"
            "font-weight: 700;"
            "}"
            "QPushButton:hover {"
            "background: #1E88E5;"
            "}"
        )
        planilha_layout.addWidget(self.planilha_btn)
        self.backup_btn = QPushButton("Backup na nuvem")
        self.backup_btn.setStyleSheet(
            "QPushButton {"
            "background: rgba(255,255,255,0.9);"
            "color: #0D47A1;"
            "border: 1px solid rgba(30,136,229,0.2);"
            "border-radius: 10px;"
            "padding: 6px 14px;"
            "font-weight: 700;"
            "}"
            "QPushButton:hover {"
            "background: #D6ECFF;"
            "}"
        )
        planilha_layout.addWidget(self.backup_btn)
        main_layout.addWidget(planilha_card)

        self._planilha_store = self._load_planilha_store()
        self.planilha_btn.clicked.connect(self._open_planilha_dialog)
        self.backup_btn.clicked.connect(self._open_backup_dialog)

        self._bind_cards()
        self.refresh()

    def _on_tab_clicked(self):
        sender = self.sender()
        for btn in self.tab_buttons:
            btn.setChecked(btn is sender)

    def _stat_card(self, title: str, value: str, subtitle: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
            "stop:0 #FFFFFF, stop:1 #EAF2FF);"
            "border: 1px solid rgba(30,136,229,0.18);"
            "border-radius: 12px;"
            "QLabel { border: none; background: transparent; }"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #0D47A1; font-weight: 700; font-size: 13px;")
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet("color: #0D47A1; font-size: 22px; font-weight: 800;")
        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet("color: #5c6f91; font-size: 12px;")
        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)
        layout.addWidget(sub_lbl)
        card._value_label = value_lbl
        card._subtitle_label = sub_lbl
        return card

    def _list_card(self, title: str, items: list[str]) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
            "stop:0 #FFFFFF, stop:1 #EAF2FF);"
            "border: 1px solid rgba(30,136,229,0.18);"
            "border-radius: 12px;"
            "QLabel { border: none; background: transparent; }"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #0D47A1; font-weight: 700; font-size: 13px;")
        layout.addWidget(title_lbl)
        for item in items:
            row = QLabel(f"- {item}")
            row.setStyleSheet("color: #5c6f91; font-size: 12px;")
            layout.addWidget(row)
        layout.addStretch(1)
        card._rows = layout
        return card

    def _bind_cards(self):
        self.card_orcamentos = self.layout().itemAt(1).widget().layout().itemAt(0).widget()
        self.card_contratos = self.layout().itemAt(1).widget().layout().itemAt(1).widget()
        self.card_clientes = self.layout().itemAt(1).widget().layout().itemAt(2).widget()
        self.card_atividades = self.layout().itemAt(1).widget().layout().itemAt(3).widget()

    def refresh(self):
        session = SessionLocal()
        try:
            total_clientes = session.query(ClienteFornecedor).count()
            total_contratos = session.query(Contrato).count()
        finally:
            session.close()

        total_orcamentos = self._count_orcamentos()

        self.card_orcamentos._value_label.setText(str(total_orcamentos))
        self.card_contratos._value_label.setText(str(total_contratos))
        self.card_clientes._value_label.setText(str(total_clientes))

    def _count_orcamentos(self) -> int:
        base = Path("contracts") / "orcamentos"
        if not base.exists():
            return 0
        return len(list(base.glob("*.pdf")))

    def _planilha_path(self) -> Path:
        if getattr(sys, "frozen", False):
            base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
            data_dir = base / "EcoverdeApp"
            data_dir.mkdir(parents=True, exist_ok=True)
            return data_dir / "planilha_gastos.json"
        return Path("planilha_gastos.json")

    def _load_planilha_store(self) -> dict:
        path = self._planilha_path()
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_planilha_store(self):
        path = self._planilha_path()
        path.write_text(json.dumps(self._planilha_store, ensure_ascii=False, indent=2), encoding="utf-8")

    def _open_planilha_dialog(self):
        dlg = PlanilhaDialog(self, self._planilha_store)
        if dlg.exec():
            self._planilha_store = dlg.get_store()
            self._save_planilha_store()

    def _open_backup_dialog(self):
        from ui.backup_dialog import BackupDialog
        dlg = BackupDialog(self)
        dlg.exec()


class TableEditorDelegate(QStyledItemDelegate):
    def __init__(self, border_role: int, parent=None):
        super().__init__(parent)
        self._border_role = border_role

    def paint(self, painter: QPainter, option, index):
        super().paint(painter, option, index)
        color_name = index.data(self._border_role)
        if not color_name:
            return
        color = QColor(color_name)
        if not color.isValid():
            return
        painter.save()
        pen = QPen(color, 1)
        painter.setPen(pen)
        rect = option.rect.adjusted(0, 0, -1, -1)
        painter.drawRect(rect)
        painter.restore()

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if editor is not None:
            palette = editor.palette()
            palette.setColor(QPalette.ColorRole.Text, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
            editor.setPalette(palette)
            editor.setStyleSheet("color: #000000; background: #FFFFFF;")
        return editor


class TableRuler(QWidget):
    def __init__(self, orientation: Qt.Orientation, table: QTableWidget, parent=None):
        super().__init__(parent)
        self._orientation = orientation
        self._table = table
        self._bg = QColor("#EEF3FA")
        self._fg = QColor("#5C6F91")
        self._tick = QColor("#9CB3D6")
        self._dragging = False
        self._drag_index = -1
        self._drag_start_pos = 0
        self._drag_start_size = 0
        if orientation == Qt.Orientation.Horizontal:
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.setFixedHeight(22)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            self.setFixedWidth(28)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self._bg)
        painter.setPen(self._tick)

        if self._orientation == Qt.Orientation.Horizontal:
            self._paint_horizontal(painter)
        else:
            self._paint_vertical(painter)

    def _paint_horizontal(self, painter: QPainter):
        offset = self._table.verticalHeader().width()
        height = self.height()
        viewport_width = self._table.viewport().width()

        painter.setPen(self._tick)
        painter.drawLine(0, height - 1, self.width(), height - 1)

        step_minor = 10
        step_major = 50
        start = -self._table.horizontalScrollBar().value()
        end = start + viewport_width
        x = ((start // step_minor) - 1) * step_minor
        while x <= end + step_minor:
            screen_x = offset + x
            if 0 <= screen_x <= self.width():
                if x % step_major == 0:
                    painter.drawLine(screen_x, height - 14, screen_x, height - 1)
                    painter.setPen(self._fg)
                    painter.drawText(screen_x + 2, 12, str(max(0, x)))
                    painter.setPen(self._tick)
                else:
                    painter.drawLine(screen_x, height - 8, screen_x, height - 1)
            x += step_minor

    def _paint_vertical(self, painter: QPainter):
        offset = self._table.horizontalHeader().height()
        width = self.width()
        viewport_height = self._table.viewport().height()

        painter.setPen(self._tick)
        painter.drawLine(width - 1, 0, width - 1, self.height())

        step_minor = 10
        step_major = 50
        start = -self._table.verticalScrollBar().value()
        end = start + viewport_height
        y = ((start // step_minor) - 1) * step_minor
        while y <= end + step_minor:
            screen_y = offset + y
            if 0 <= screen_y <= self.height():
                if y % step_major == 0:
                    painter.drawLine(width - 14, screen_y, width - 1, screen_y)
                    painter.setPen(self._fg)
                    painter.drawText(2, screen_y - 2, str(max(0, y)))
                    painter.setPen(self._tick)
                else:
                    painter.drawLine(width - 8, screen_y, width - 1, screen_y)
            y += step_minor

    def mouseDoubleClickEvent(self, event):
        if self._orientation == Qt.Orientation.Horizontal:
            logical = self._table.columnAt(int(event.position().x()))
            if logical < 0:
                return
            current = self._table.columnWidth(logical)
            value, ok = QInputDialog.getInt(
                self, "Largura da coluna", "Largura (px):", current, 20, 2000, 1
            )
            if ok:
                self._table.setColumnWidth(logical, value)
        else:
            logical = self._table.rowAt(int(event.position().y()))
            if logical < 0:
                return
            current = self._table.rowHeight(logical)
            value, ok = QInputDialog.getInt(
                self, "Altura da linha", "Altura (px):", current, 16, 800, 1
            )
            if ok:
                self._table.setRowHeight(logical, value)
        self.update()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        if self._orientation == Qt.Orientation.Horizontal:
            logical = self._table.columnAt(int(event.position().x()))
            if logical < 0:
                return
            self._drag_start_size = self._table.columnWidth(logical)
            self._drag_start_pos = int(event.position().x())
        else:
            logical = self._table.rowAt(int(event.position().y()))
            if logical < 0:
                return
            self._drag_start_size = self._table.rowHeight(logical)
            self._drag_start_pos = int(event.position().y())
        self._dragging = True
        self._drag_index = logical

    def mouseMoveEvent(self, event):
        if not self._dragging or self._drag_index < 0:
            return
        if self._orientation == Qt.Orientation.Horizontal:
            delta = int(event.position().x()) - self._drag_start_pos
            new_size = max(20, self._drag_start_size + delta)
            self._table.setColumnWidth(self._drag_index, new_size)
        else:
            delta = int(event.position().y()) - self._drag_start_pos
            new_size = max(16, self._drag_start_size + delta)
            self._table.setRowHeight(self._drag_index, new_size)
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self._dragging = False
        self._drag_index = -1


class FontPickerDialog(QDialog):
    def __init__(self, current: QFont, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fonte")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setMinimumWidth(360)
        self._font = QFont(current)
        self.setStyleSheet(
            "QDialog { background: #F7FAFF; }"
            "QLabel { color: #0D47A1; }"
            "QComboBox { color: #0D47A1; background: #FFFFFF; border: 1px solid rgba(13,71,161,0.25); border-radius: 8px; padding: 4px 8px; }"
            "QComboBox QAbstractItemView { color: #0D47A1; background: #FFFFFF; selection-background-color: #D6ECFF; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        row = QHBoxLayout()
        row.setSpacing(8)

        families = QComboBox()
        family_list = QFontDatabase.families()
        families.addItems(family_list)
        for idx, family in enumerate(family_list):
            families.setItemData(idx, QFont(family), Qt.ItemDataRole.FontRole)
        families.setCurrentText(current.family())
        families.setStyleSheet(
            "QComboBox { color: #0D47A1; background: #FFFFFF; border: 1px solid rgba(13,71,161,0.25); border-radius: 8px; padding: 4px 8px; }"
            "QComboBox QAbstractItemView { color: #0D47A1; background: #FFFFFF; selection-background-color: #D6ECFF; }"
        )
        row.addWidget(families, 2)

        sizes = QComboBox()
        sizes.addItems([str(s) for s in range(6, 73, 1)])
        size_text = str(current.pointSize()) if current.pointSize() > 0 else "10"
        sizes.setCurrentText(size_text)
        sizes.setStyleSheet(
            "QComboBox { color: #0D47A1; background: #FFFFFF; border: 1px solid rgba(13,71,161,0.25); border-radius: 8px; padding: 4px 8px; }"
            "QComboBox QAbstractItemView { color: #0D47A1; background: #FFFFFF; selection-background-color: #D6ECFF; }"
        )
        row.addWidget(sizes, 1)

        layout.addLayout(row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.setStyleSheet(
            "QDialogButtonBox QPushButton {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #64B5F6, stop:1 #1E88E5);"
            "color: #FFFFFF;"
            "border-radius: 8px;"
            "padding: 6px 12px;"
            "}"
        )
        layout.addWidget(buttons)

        def apply_selection():
            family = families.currentText().strip()
            try:
                size = int(sizes.currentText())
            except ValueError:
                size = current.pointSize() if current.pointSize() > 0 else 10
            self._font = QFont(family, size)
            self.accept()

        buttons.accepted.connect(apply_selection)
        buttons.rejected.connect(self.reject)

    def selected_font(self) -> QFont:
        return self._font

    def open_and_exec(self) -> int:
        if self.parent():
            parent_geo = self.parent().geometry()
            center_x = parent_geo.x() + parent_geo.width() // 2
            center_y = parent_geo.y() + parent_geo.height() // 2
            self.move(center_x - self.width() // 2, center_y - self.height() // 2)
        if isinstance(self.parent(), PlanilhaDialog):
            self.parent()._apply_titlebar_for(self)
        self.show()
        self.raise_()
        self.activateWindow()
        return self.exec()


class FontSizeDialog(QDialog):
    def __init__(self, current_size: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tamanho da fonte")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self._size = current_size
        self.setMinimumWidth(280)
        self.setStyleSheet(
            "QDialog { background: #F7FAFF; }"
            "QLabel { color: #0D47A1; font-weight: 700; }"
            "QComboBox { color: #0D47A1; background: #FFFFFF; border: 1px solid rgba(13,71,161,0.25); border-radius: 10px; padding: 6px 10px; }"
            "QComboBox QAbstractItemView { color: #0D47A1; background: #FFFFFF; selection-background-color: #D6ECFF; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        label = QLabel("Tamanho (pt):")
        label.setStyleSheet("color: #0D47A1;")
        card = QFrame()
        card.setStyleSheet(
            "background: #FFFFFF;"
            "border: 1px solid rgba(13,71,161,0.2);"
            "border-radius: 12px;"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(8)
        card_layout.addWidget(label)
        layout.addWidget(card)

        self.size_combo = QComboBox()
        self.size_combo.addItems([str(s) for s in range(6, 73, 1)])
        self.size_combo.setCurrentText(str(current_size))
        self.size_combo.setStyleSheet(
            "QComboBox { color: #0D47A1; background: #FFFFFF; border: 1px solid rgba(13,71,161,0.25); border-radius: 8px; padding: 4px 8px; }"
            "QComboBox QAbstractItemView { color: #0D47A1; background: #FFFFFF; selection-background-color: #D6ECFF; }"
        )
        card_layout.addWidget(self.size_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.setStyleSheet(
            "QDialogButtonBox QPushButton {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #64B5F6, stop:1 #1E88E5);"
            "color: #FFFFFF;"
            "border-radius: 10px;"
            "padding: 7px 14px;"
            "font-weight: 700;"
            "}"
        )
        layout.addWidget(buttons)

        def apply_selection():
            try:
                self._size = int(self.size_combo.currentText())
            except ValueError:
                self._size = current_size
            self.accept()

        buttons.accepted.connect(apply_selection)
        buttons.rejected.connect(self.reject)

    def selected_size(self) -> int:
        return self._size

    def open_and_exec(self) -> int:
        if self.parent():
            parent_geo = self.parent().geometry()
            center_x = parent_geo.x() + parent_geo.width() // 2
            center_y = parent_geo.y() + parent_geo.height() // 2
            self.move(center_x - self.width() // 2, center_y - self.height() // 2)
        if isinstance(self.parent(), PlanilhaDialog):
            self.parent()._apply_titlebar_for(self)
        self.show()
        self.raise_()
        self.activateWindow()
        return self.exec()


class PlanilhaDialog(QDialog):
    def __init__(self, parent: QWidget, store: dict):
        super().__init__(parent)
        self.setWindowTitle("Planilha")
        self.setMinimumSize(880, 560)
        self.setWindowState(self.windowState() | Qt.WindowState.WindowMaximized)
        self.setStyleSheet("background: #F7FAFF;")
        self.setWindowIcon(QIcon(self._resource_path("assets/logo.ico")))
        self._titlebar_applied = False
        self._store = json.loads(json.dumps(store)) if store else {}
        self._role_bg = Qt.ItemDataRole.UserRole + 1
        self._role_fg = Qt.ItemDataRole.UserRole + 2
        self._role_bold = Qt.ItemDataRole.UserRole + 3
        self._role_border = Qt.ItemDataRole.UserRole + 4
        self._role_font_family = Qt.ItemDataRole.UserRole + 5
        self._role_font_size = Qt.ItemDataRole.UserRole + 6
        self._templates = self._load_templates()
        self._col_ratios = []
        self._row_ratios = []
        self._resizing_programmatically = False
        self._last_text_color = QColor("#000000")
        self._last_bg_color = QColor("#ffffff")
        self._last_border_color = QColor("#7f7f7f")
        self._normalize_store()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        title = QLabel("Planilha")
        title.setStyleSheet(
            "color: #0D47A1;"
            "font-weight: 800;"
            "font-size: 18px;"
            "background: transparent;"
            "border: none;"
            "padding: 0;"
        )
        header_row.addWidget(title)

        self.month_combo = QComboBox()
        self.month_combo.addItems(
            [
                "Janeiro",
                "Fevereiro",
                "Marco",
                "Abril",
                "Maio",
                "Junho",
                "Julho",
                "Agosto",
                "Setembro",
                "Outubro",
                "Novembro",
                "Dezembro",
            ]
        )
        self.month_combo.setStyleSheet(
            "QComboBox {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
            "stop:0 #E3F2FD, stop:1 #BBDEFB);"
            "border: 1px solid rgba(13,71,161,0.35);"
            "border-radius: 12px;"
            "padding: 6px 12px;"
            "color: #0D47A1;"
            "font-weight: 700;"
            "}"
            "QComboBox QAbstractItemView {"
            "color: #0D47A1;"
            "background: #FFFFFF;"
            "selection-background-color: #D6ECFF;"
            "selection-color: #0D47A1;"
            "}"
            "QComboBox::drop-down {"
            "subcontrol-origin: padding;"
            "subcontrol-position: top right;"
            "width: 24px;"
            "border-left: 1px solid rgba(13,71,161,0.25);"
            "border-top-right-radius: 12px;"
            "border-bottom-right-radius: 12px;"
            "background: rgba(13,71,161,0.06);"
            "}"
            "QComboBox::down-arrow {"
            "image: url(icons/chevron_down.svg);"
            "width: 12px;"
            "height: 12px;"
            "margin-right: 8px;"
            "}"
            "QComboBox QAbstractItemView QScrollBar:vertical {"
            "width: 10px;"
            "background: #EAF2FF;"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 6px;"
            "margin: 4px 0 4px 0;"
            "}"
            "QComboBox QAbstractItemView QScrollBar::handle:vertical {"
            "background: #64B5F6;"
            "border-radius: 5px;"
            "min-height: 24px;"
            "}"
            "QComboBox QAbstractItemView QScrollBar::handle:vertical:hover {"
            "background: #1E88E5;"
            "}"
            "QComboBox QAbstractItemView QScrollBar::add-line:vertical, "
            "QComboBox QAbstractItemView QScrollBar::sub-line:vertical {"
            "height: 12px;"
            "background: #EAF2FF;"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 6px;"
            "}"
            "QComboBox QAbstractItemView QScrollBar::add-page:vertical, "
            "QComboBox QAbstractItemView QScrollBar::sub-page:vertical {"
            "background: transparent;"
            "}"
        )
        header_row.addStretch(1)

        self.add_row_btn = QPushButton("+ Linha")
        self.remove_row_btn = QPushButton("- Linha")
        self.add_col_btn = QPushButton("+ Coluna")
        self.remove_col_btn = QPushButton("- Coluna")
        self.merge_btn = QPushButton("Mesclar")
        self.unmerge_btn = QPushButton("Desfazer mescla")
        self.bg_color_btn = QPushButton("Cor bloco")
        self.text_color_btn = QPushButton("Cor texto")
        self.bold_btn = QPushButton("Negrito")
        self.font_btn = QPushButton("Fonte")
        self.font_size_btn = QPushButton("Tamanho")
        self.border_btn = QPushButton("Borda")
        self.clear_style_btn = QPushButton("Limpar estilo")
        self.save_template_btn = QPushButton("Salvar modelo")
        self.load_template_btn = QPushButton("Abrir modelo")
        self.save_planilha_btn = QPushButton("Salvar")
        primary_style = (
            "QPushButton {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
            "stop:0 #43A047, stop:1 #2E7D32);"
            "color: #FFFFFF;"
            "border: none;"
            "border-radius: 14px;"
            "padding: 8px 16px;"
            "font-weight: 700;"
            "}"
            "QPushButton:hover {"
            "background: #2E7D32;"
            "}"
        )
        secondary_style = (
            "QPushButton {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
            "stop:0 #64B5F6, stop:1 #1E88E5);"
            "border: none;"
            "border-radius: 14px;"
            "padding: 8px 14px;"
            "color: #FFFFFF;"
            "font-weight: 700;"
            "}"
            "QPushButton:hover {"
            "background: #1E88E5;"
            "}"
        )
        for btn in (
            self.add_row_btn,
            self.remove_row_btn,
            self.add_col_btn,
            self.remove_col_btn,
            self.merge_btn,
            self.unmerge_btn,
            self.bg_color_btn,
            self.text_color_btn,
            self.bold_btn,
            self.font_btn,
            self.font_size_btn,
            self.border_btn,
            self.clear_style_btn,
            self.save_template_btn,
            self.load_template_btn,
        ):
            btn.setStyleSheet(secondary_style)
            header_row.addWidget(btn)
        btn_index = header_row.indexOf(self.add_row_btn)
        if btn_index >= 0:
            header_row.insertWidget(btn_index, self.month_combo)
        self.save_planilha_btn.setStyleSheet(primary_style)
        header_row.addStretch(1)
        header_row.addWidget(self.save_planilha_btn)
        header_row.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(header_row)

        self.table = QTableWidget(0, 0)
        self._configure_table(self.table)
        self.table.setStyleSheet(
            "QTableWidget {"
            "background: #FFFFFF;"
            "border: 1px solid rgba(30,136,229,0.18);"
            "border-radius: 10px;"
            "gridline-color: #7f7f7f;"
            "color: #000000;"
            "}"
            "QTableWidget::item:selected {"
            "background: #CFE4FF;"
            "color: #000000;"
            "}"
            "QHeaderView::section {"
            "background: #DCE9F7;"
            "color: #0D47A1;"
            "font-weight: 700;"
            "border: 1px solid #c1d7f1;"
            "padding: 6px;"
            "}"
            "QScrollBar:horizontal {"
            "height: 12px;"
            "background: #EAF2FF;"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 6px;"
            "margin: 0px 16px 0px 16px;"
            "}"
            "QScrollBar::handle:horizontal {"
            "background: #64B5F6;"
            "border-radius: 5px;"
            "min-width: 24px;"
            "}"
            "QScrollBar::handle:horizontal:hover {"
            "background: #1E88E5;"
            "}"
            "QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {"
            "width: 14px;"
            "background: #EAF2FF;"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 6px;"
            "}"
            "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {"
            "background: transparent;"
            "}"
            "QScrollBar:vertical {"
            "width: 12px;"
            "background: #EAF2FF;"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 6px;"
            "margin: 16px 0px 16px 0px;"
            "}"
            "QScrollBar::handle:vertical {"
            "background: #64B5F6;"
            "border-radius: 5px;"
            "min-height: 24px;"
            "}"
            "QScrollBar::handle:vertical:hover {"
            "background: #1E88E5;"
            "}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
            "height: 14px;"
            "background: #EAF2FF;"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 6px;"
            "}"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {"
            "background: transparent;"
            "}"
        )
        palette = self.table.palette()
        palette.setColor(QPalette.ColorRole.Text, QColor("#000000"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#000000"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
        self.table.setPalette(palette)
        self.table.setItemDelegate(TableEditorDelegate(self._role_border, self.table))
        self.top_ruler = TableRuler(Qt.Orientation.Horizontal, self.table)
        self.left_ruler = TableRuler(Qt.Orientation.Vertical, self.table)
        self.ruler_corner = QFrame()
        self.ruler_corner.setFixedSize(self.left_ruler.width(), self.top_ruler.height())
        self.ruler_corner.setStyleSheet("background: #EEF3FA;")

        table_wrap = QWidget()
        wrap_layout = QGridLayout(table_wrap)
        wrap_layout.setContentsMargins(0, 0, 0, 0)
        wrap_layout.setSpacing(0)
        wrap_layout.addWidget(self.ruler_corner, 0, 0)
        wrap_layout.addWidget(self.top_ruler, 0, 1)
        wrap_layout.addWidget(self.left_ruler, 1, 0)
        wrap_layout.addWidget(self.table, 1, 1)
        main_layout.addWidget(table_wrap, 1)

        footer = QHBoxLayout()
        footer.addStretch(1)
        close_btn = QPushButton("Fechar")
        close_btn.setStyleSheet(
            "QPushButton {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #EF5350, stop:1 #C62828);"
            "color: #FFFFFF;"
            "border: none;"
            "border-radius: 10px;"
            "padding: 6px 14px;"
            "font-weight: 700;"
            "}"
            "QPushButton:hover {"
            "background: #C62828;"
            "}"
        )
        footer.addWidget(close_btn)
        main_layout.addLayout(footer)

        self.month_combo.currentTextChanged.connect(self._on_month_changed)
        self.add_row_btn.clicked.connect(self._add_row)
        self.remove_row_btn.clicked.connect(self._remove_row)
        self.add_col_btn.clicked.connect(self._add_col)
        self.remove_col_btn.clicked.connect(self._remove_col)
        self.merge_btn.clicked.connect(self._merge_selection)
        self.unmerge_btn.clicked.connect(self._unmerge_selection)
        self.bg_color_btn.clicked.connect(self._set_background_color)
        self.text_color_btn.clicked.connect(self._set_text_color)
        self.bold_btn.clicked.connect(self._toggle_bold)
        self.font_btn.clicked.connect(self._set_font_family)
        self.font_size_btn.clicked.connect(self._set_font_size)
        self.border_btn.clicked.connect(self._set_border_color)
        self.clear_style_btn.clicked.connect(self._clear_styles)
        self.save_template_btn.clicked.connect(self._save_template)
        self.load_template_btn.clicked.connect(self._load_template)
        self.save_planilha_btn.clicked.connect(self._save)
        close_btn.clicked.connect(self.reject)
        self.table.itemChanged.connect(self._on_item_changed)
        self.table.horizontalHeader().sectionDoubleClicked.connect(self._rename_column)
        self.table.horizontalHeader().sectionResized.connect(self._on_column_resized)
        self.table.verticalHeader().sectionResized.connect(self._on_row_resized)
        self.table.horizontalHeader().sectionResized.connect(self.top_ruler.update)
        self.table.verticalHeader().sectionResized.connect(self.left_ruler.update)
        self.table.horizontalHeader().sectionMoved.connect(self.top_ruler.update)
        self.table.horizontalScrollBar().valueChanged.connect(self.top_ruler.update)
        self.table.verticalScrollBar().valueChanged.connect(self.left_ruler.update)

        self._load_month(self.month_combo.currentText())

    def get_store(self) -> dict:
        return self._store

    def showEvent(self, event):
        super().showEvent(event)
        if not self._titlebar_applied:
            self._apply_windows_titlebar_color()
            self._titlebar_applied = True

    def _apply_windows_titlebar_color(self):
        if sys.platform != "win32":
            return
        try:
            color_hex = "1565C0"
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            colorref = (b << 16) | (g << 8) | r
            DWMWA_CAPTION_COLOR = 35
            DWMWA_TEXT_COLOR = 36
            hwnd = wintypes.HWND(int(self.winId()))
            dwm = ctypes.windll.dwmapi
            dwm.DwmSetWindowAttribute(
                hwnd,
                DWMWA_CAPTION_COLOR,
                ctypes.byref(ctypes.c_int(colorref)),
                ctypes.sizeof(ctypes.c_int),
            )
            dwm.DwmSetWindowAttribute(
                hwnd,
                DWMWA_TEXT_COLOR,
                ctypes.byref(ctypes.c_int(0xFFFFFF)),
                ctypes.sizeof(ctypes.c_int),
            )
        except Exception:
            pass

    def _apply_titlebar_for(self, widget: QWidget):
        if sys.platform != "win32":
            return
        try:
            color_hex = "1565C0"
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            colorref = (b << 16) | (g << 8) | r
            DWMWA_CAPTION_COLOR = 35
            DWMWA_TEXT_COLOR = 36
            hwnd = wintypes.HWND(int(widget.winId()))
            dwm = ctypes.windll.dwmapi
            dwm.DwmSetWindowAttribute(
                hwnd,
                DWMWA_CAPTION_COLOR,
                ctypes.byref(ctypes.c_int(colorref)),
                ctypes.sizeof(ctypes.c_int),
            )
            dwm.DwmSetWindowAttribute(
                hwnd,
                DWMWA_TEXT_COLOR,
                ctypes.byref(ctypes.c_int(0xFFFFFF)),
                ctypes.sizeof(ctypes.c_int),
            )
        except Exception:
            pass

    def _resource_path(self, relative_path: str) -> str:
        if getattr(sys, "frozen", False):
            return str(Path(sys._MEIPASS) / relative_path)
        return str(Path(relative_path))

    def _normalize_store(self):
        for month, value in list(self._store.items()):
            if not isinstance(value, dict):
                continue
            if "rows" in value and "headers" in value:
                continue
            if "despesas" in value or "receitas" in value:
                self._store[month] = self._migrate_old_store(value)
            else:
                self._store[month] = {}

    def _store_current_month(self):
        month = self.month_combo.currentText()
        self._store[month] = self._export_table_state()

    def _load_month(self, month: str):
        self._loading_table = True
        data = self._store.get(month, {})
        self._apply_table_state(data)
        self._loading_table = False

    def _on_month_changed(self, month: str):
        self._store_current_month()
        self._load_month(month)

    def _add_row(self):
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        for col in range(self.table.columnCount()):
            self._ensure_item(row_idx, col)
        self._capture_size_ratios()
        self._fit_table_to_view()
        self._update_all_value_totals()

    def _remove_row(self):
        rows = sorted({idx.row() for idx in self.table.selectedIndexes()}, reverse=True)
        if not rows and self.table.currentRow() >= 0:
            rows = [self.table.currentRow()]
        for row in rows:
            self.table.removeRow(row)
        self._capture_size_ratios()
        self._fit_table_to_view()
        self._update_all_value_totals()

    def _save(self):
        self._store_current_month()
        self.accept()

    def _configure_table(self, table: QTableWidget):
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        table.horizontalHeader().setSectionsMovable(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.SelectedClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
            | QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        table.setTabKeyNavigation(True)
        table.verticalHeader().setVisible(True)

    def _on_item_changed(self, item: QTableWidgetItem):
        if getattr(self, "_loading_table", False):
            return
        self._ensure_item(item.row(), item.column())
        if not item.data(self._role_fg):
            item.setForeground(QColor("#000000"))
        text = item.text().strip()
        if text.upper() == "VALOR":
            self._format_value_column(item.column())
            self._update_value_totals(item.column())
            return
        if self._column_is_value(item.column()):
            current = item.text().strip()
            if current and not current.lower().startswith("r$"):
                formatted = self._format_currency(current)
                if formatted and formatted != current:
                    self._loading_table = True
                    item.setText(formatted)
                    self._loading_table = False
            self._update_value_totals(item.column())

    def _ensure_item(self, row: int, col: int) -> QTableWidgetItem:
        item = self.table.item(row, col)
        if item is None:
            item = QTableWidgetItem("")
            self.table.setItem(row, col, item)
        if not item.foreground().color().isValid():
            item.setForeground(QColor("#000000"))
        return item

    def _column_is_value(self, col: int) -> bool:
        header = self.table.horizontalHeaderItem(col)
        if not header:
            header_text = ""
        else:
            header_text = header.text().strip().upper()
        if "VALOR" in header_text:
            return True
        for row in range(self.table.rowCount()):
            cell = self.table.item(row, col)
            if cell and cell.text().strip().upper() == "VALOR":
                return True
        return False

    def _format_value_column(self, col: int):
        self._loading_table = True
        try:
            for row in range(self.table.rowCount()):
                cell = self.table.item(row, col)
                if not cell:
                    continue
                text = cell.text().strip()
                if not text or text.upper() == "VALOR":
                    continue
                if text.lower().startswith("r$"):
                    continue
                formatted = self._format_currency(text)
                if formatted and formatted != text:
                    cell.setText(formatted)
        finally:
            self._loading_table = False
        self._update_value_totals(col)

    def _format_currency(self, text: str) -> str | None:
        value = self._parse_currency(text)
        if value is None:
            return None
        return self._format_currency_value(value)

    def _format_currency_value(self, value: float) -> str:
        formatted = f"{value:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"

    def _parse_currency(self, text: str) -> float | None:
        if not text:
            return None
        cleaned = text.replace("R$", "").replace("TOTAL:", "").strip()
        if "," in cleaned and "." in cleaned:
            cleaned = cleaned.replace(".", "").replace(",", ".")
        elif "," in cleaned:
            cleaned = cleaned.replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None

    def _update_value_totals(self, col: int):
        row_count = self.table.rowCount()
        if row_count == 0:
            return
        last_row = row_count - 1
        total = 0.0
        for row in range(last_row):
            cell = self.table.item(row, col)
            if not cell:
                continue
            text = cell.text().strip()
            if not text:
                continue
            upper = text.upper()
            if upper == "VALOR" or upper.startswith("TOTAL"):
                continue
            value = self._parse_currency(text)
            if value is None:
                continue
            total += value
        total_cell = self._ensure_item(last_row, col)
        formatted = self._format_currency_value(total)
        display = f"TOTAL: {formatted}"
        self._loading_table = True
        try:
            total_cell.setText(display)
            font = total_cell.font()
            font.setBold(True)
            total_cell.setFont(font)
        finally:
            self._loading_table = False

    def _update_all_value_totals(self):
        for col in range(self.table.columnCount()):
            if self._column_is_value(col):
                self._update_value_totals(col)

    def _rename_column(self, logical_index: int):
        item = self.table.horizontalHeaderItem(logical_index)
        current = item.text() if item else f"Coluna {logical_index + 1}"
        text, ok = QInputDialog.getText(self, "Renomear coluna", "Nome da coluna:", text=current)
        if not ok or not text.strip():
            return
        if item is None:
            item = QTableWidgetItem()
            self.table.setHorizontalHeaderItem(logical_index, item)
        item.setText(text.strip())

    def _add_col(self):
        col_idx = self.table.columnCount()
        self.table.insertColumn(col_idx)
        header = QTableWidgetItem(f"Coluna {col_idx + 1}")
        self.table.setHorizontalHeaderItem(col_idx, header)
        for row in range(self.table.rowCount()):
            self._ensure_item(row, col_idx)
        self._capture_size_ratios()
        self._fit_table_to_view()
        self._update_all_value_totals()

    def _remove_col(self):
        cols = sorted({idx.column() for idx in self.table.selectedIndexes()}, reverse=True)
        if not cols and self.table.currentColumn() >= 0:
            cols = [self.table.currentColumn()]
        for col in cols:
            self.table.removeColumn(col)
        self._capture_size_ratios()
        self._fit_table_to_view()
        self._update_all_value_totals()

    def _merge_selection(self):
        indexes = self.table.selectedIndexes()
        if not indexes:
            return
        rows = [idx.row() for idx in indexes]
        cols = [idx.column() for idx in indexes]
        top = min(rows)
        left = min(cols)
        row_span = max(rows) - top + 1
        col_span = max(cols) - left + 1
        if row_span > 1 or col_span > 1:
            self.table.setSpan(top, left, row_span, col_span)

    def _unmerge_selection(self):
        indexes = self.table.selectedIndexes()
        if not indexes:
            return
        for idx in indexes:
            span = self._find_span_at(idx.row(), idx.column())
            if span:
                row, col, row_span, col_span = span
                self.table.setSpan(row, col, 1, 1)

    def _find_span_at(self, row: int, col: int):
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                row_span = self.table.rowSpan(r, c)
                col_span = self.table.columnSpan(r, c)
                if row_span <= 1 and col_span <= 1:
                    continue
                if r <= row < r + row_span and c <= col < c + col_span:
                    return (r, c, row_span, col_span)
        return None

    def _set_background_color(self):
        color = self._pick_color("Cor do bloco", self._last_bg_color)
        if not color.isValid():
            return
        self._last_bg_color = color
        for idx in self.table.selectedIndexes():
            item = self._ensure_item(idx.row(), idx.column())
            item.setBackground(color)
            item.setData(self._role_bg, color.name())

    def _set_text_color(self):
        color = self._pick_color("Cor do texto", self._last_text_color)
        if not color.isValid():
            return
        self._last_text_color = color
        for idx in self.table.selectedIndexes():
            item = self._ensure_item(idx.row(), idx.column())
            item.setForeground(color)
            item.setData(self._role_fg, color.name())

    def _toggle_bold(self):
        indexes = self.table.selectedIndexes()
        if not indexes:
            return
        first = self._ensure_item(indexes[0].row(), indexes[0].column())
        current = bool(first.data(self._role_bold))
        target = not current
        for idx in indexes:
            item = self._ensure_item(idx.row(), idx.column())
            font = item.font()
            font.setBold(target)
            item.setFont(font)
            item.setData(self._role_bold, target)

    def _set_font_family(self):
        indexes = self.table.selectedIndexes()
        if not indexes:
            current = self.table.currentIndex()
            if not current.isValid():
                return
            indexes = [current]
        sample = self._ensure_item(indexes[0].row(), indexes[0].column())
        current_font = sample.font()
        dlg = FontPickerDialog(current_font, self)
        if dlg.open_and_exec() != QDialog.DialogCode.Accepted:
            return
        font = dlg.selected_font()
        for idx in indexes:
            item = self._ensure_item(idx.row(), idx.column())
            item.setFont(font)
            item.setData(self._role_font_family, font.family())
            item.setData(self._role_font_size, font.pointSize())
            item.setData(self._role_bold, font.bold())

    def _set_font_size(self):
        indexes = self.table.selectedIndexes()
        if not indexes:
            current = self.table.currentIndex()
            if not current.isValid():
                return
            indexes = [current]
        sample = self._ensure_item(indexes[0].row(), indexes[0].column())
        current_font = sample.font()
        current_size = current_font.pointSize() if current_font.pointSize() > 0 else 10
        dlg = FontSizeDialog(current_size, self)
        if dlg.open_and_exec() != QDialog.DialogCode.Accepted:
            return
        size = dlg.selected_size()
        for idx in indexes:
            item = self._ensure_item(idx.row(), idx.column())
            font = QFont(item.font())
            font.setPointSize(size)
            item.setFont(font)
            item.setData(self._role_font_size, size)

    def _set_border_color(self):
        color = self._pick_color("Cor da borda", self._last_border_color)
        if not color.isValid():
            return
        self._last_border_color = color
        for idx in self.table.selectedIndexes():
            item = self._ensure_item(idx.row(), idx.column())
            item.setData(self._role_border, color.name())
        self.table.viewport().update()

    def _clear_styles(self):
        for idx in self.table.selectedIndexes():
            item = self._ensure_item(idx.row(), idx.column())
            item.setBackground(QColor())
            item.setForeground(QColor("#000000"))
            font = QFont(self.table.font())
            item.setFont(font)
            item.setData(self._role_bg, None)
            item.setData(self._role_fg, None)
            item.setData(self._role_bold, None)
            item.setData(self._role_border, None)
            item.setData(self._role_font_family, None)
            item.setData(self._role_font_size, None)
        self.table.viewport().update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit_table_to_view()

    def _capture_size_ratios(self):
        if self._resizing_programmatically:
            return
        col_count = self.table.columnCount()
        row_count = self.table.rowCount()
        col_sizes = [self.table.columnWidth(i) for i in range(col_count)]
        row_sizes = [self.table.rowHeight(i) for i in range(row_count)]

        total_cols = sum(col_sizes)
        total_rows = sum(row_sizes)

        if total_cols > 0:
            self._col_ratios = [w / total_cols for w in col_sizes]
        elif col_count:
            self._col_ratios = [1 / col_count for _ in range(col_count)]
        else:
            self._col_ratios = []

        if total_rows > 0:
            self._row_ratios = [h / total_rows for h in row_sizes]
        elif row_count:
            self._row_ratios = [1 / row_count for _ in range(row_count)]
        else:
            self._row_ratios = []

    def _fit_table_to_view(self):
        col_count = self.table.columnCount()
        row_count = self.table.rowCount()
        if not col_count or not row_count:
            return
        if not self._col_ratios or len(self._col_ratios) != col_count:
            self._capture_size_ratios()
        if not self._row_ratios or len(self._row_ratios) != row_count:
            self._capture_size_ratios()

        viewport = self.table.viewport().size()
        total_width = max(1, viewport.width())
        total_height = max(1, viewport.height())
        min_col = 60
        min_row = 22

        self._resizing_programmatically = True
        try:
            for idx in range(col_count):
                target = int(total_width * self._col_ratios[idx])
                self.table.setColumnWidth(idx, max(min_col, target))
            for idx in range(row_count):
                target = int(total_height * self._row_ratios[idx])
                self.table.setRowHeight(idx, max(min_row, target))
        finally:
            self._resizing_programmatically = False
        if hasattr(self, "top_ruler"):
            self.top_ruler.update()
        if hasattr(self, "left_ruler"):
            self.left_ruler.update()

    def _on_column_resized(self, *_args):
        if self._resizing_programmatically:
            return
        self._capture_size_ratios()

    def _on_row_resized(self, *_args):
        if self._resizing_programmatically:
            return
        self._capture_size_ratios()

    def _pick_color(self, title: str, initial: QColor | None) -> QColor:
        dlg = QColorDialog(self)
        dlg.setWindowTitle(title)
        dlg.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        dlg.setStyleSheet(
            "QDialog, QWidget { color: #0D47A1; background: #F7FAFF; }"
            "QLabel { color: #0D47A1; }"
            "QLineEdit { color: #0D47A1; background: #FFFFFF; selection-background-color: #D6ECFF; }"
            "QPushButton, QAbstractButton { color: #FFFFFF; background: #1E88E5; border-radius: 8px; padding: 4px 10px; }"
            "QGroupBox { color: #0D47A1; }"
            "QComboBox { color: #0D47A1; background: #FFFFFF; }"
        )
        if initial and initial.isValid():
            dlg.setCurrentColor(initial)
        palette = dlg.palette()
        palette.setColor(dlg.foregroundRole(), QColor("#0D47A1"))
        palette.setColor(palette.ColorRole.WindowText, QColor("#0D47A1"))
        palette.setColor(palette.ColorRole.Text, QColor("#0D47A1"))
        palette.setColor(palette.ColorRole.ButtonText, QColor("#FFFFFF"))
        palette.setColor(palette.ColorRole.Base, QColor("#FFFFFF"))
        dlg.setPalette(palette)
        self._apply_titlebar_for(dlg)
        if dlg.exec():
            return dlg.selectedColor()
        return QColor()

    def _export_table_state(self) -> dict:
        header = self.table.horizontalHeader()
        order = [header.logicalIndex(i) for i in range(header.count())]
        headers = []
        for logical in order:
            item = self.table.horizontalHeaderItem(logical)
            headers.append(item.text() if item else f"Coluna {logical + 1}")

        rows = []
        for r in range(self.table.rowCount()):
            row_data = []
            for logical in order:
                item = self.table.item(r, logical)
                row_data.append(item.text() if item else "")
            rows.append(row_data)

        col_widths = [self.table.columnWidth(logical) for logical in order]
        row_heights = [self.table.rowHeight(r) for r in range(self.table.rowCount())]

        logical_to_visual = {logical: idx for idx, logical in enumerate(order)}
        spans = []
        for r in range(self.table.rowCount()):
            for logical in range(self.table.columnCount()):
                row_span = self.table.rowSpan(r, logical)
                col_span = self.table.columnSpan(r, logical)
                if row_span <= 1 and col_span <= 1:
                    continue
                spans.append(
                    {
                        "row": r,
                        "col": logical_to_visual.get(logical, logical),
                        "rowSpan": row_span,
                        "colSpan": col_span,
                    }
                )

        styles = {}
        for r in range(self.table.rowCount()):
            for visual_col, logical in enumerate(order):
                item = self.table.item(r, logical)
                if not item:
                    continue
                style = {}
                bg = item.data(self._role_bg)
                fg = item.data(self._role_fg)
                bold = item.data(self._role_bold)
                border = item.data(self._role_border)
                if bg:
                    style["bg"] = bg
                if fg:
                    style["fg"] = fg
                if bold:
                    style["bold"] = True
                if border:
                    style["border"] = border
                font_family = item.data(self._role_font_family)
                font_size = item.data(self._role_font_size)
                if font_family:
                    style["font_family"] = font_family
                if font_size:
                    style["font_size"] = font_size
                if style:
                    styles[f"{r},{visual_col}"] = style

        return {
            "row_count": self.table.rowCount(),
            "col_count": self.table.columnCount(),
            "headers": headers,
            "rows": rows,
            "col_widths": col_widths,
            "row_heights": row_heights,
            "spans": spans,
            "styles": styles,
        }

    def _apply_table_state(self, state: dict):
        if not state:
            self._create_default_table()
            return
        headers = state.get("headers", [])
        rows = state.get("rows", [])
        row_count = state.get("row_count", len(rows) or 20)
        col_count = state.get("col_count", len(headers) or 8)

        if headers and len(headers) != col_count:
            col_count = len(headers)

        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)

        if not headers:
            headers = [f"Coluna {i + 1}" for i in range(col_count)]
        self.table.setHorizontalHeaderLabels(headers)

        for r in range(row_count):
            for c in range(col_count):
                text = ""
                if r < len(rows) and c < len(rows[r]):
                    text = rows[r][c]
                item = QTableWidgetItem(text)
                item.setForeground(QColor("#000000"))
                self.table.setItem(r, c, item)

        for idx, width in enumerate(state.get("col_widths", [])):
            if idx < col_count:
                self.table.setColumnWidth(idx, int(width))
        for idx, height in enumerate(state.get("row_heights", [])):
            if idx < row_count:
                self.table.setRowHeight(idx, int(height))

        for span in state.get("spans", []):
            row = span.get("row", 0)
            col = span.get("col", 0)
            row_span = span.get("rowSpan", 1)
            col_span = span.get("colSpan", 1)
            if row < row_count and col < col_count:
                self.table.setSpan(row, col, row_span, col_span)

        for key, style in state.get("styles", {}).items():
            try:
                row_str, col_str = key.split(",")
                row = int(row_str)
                col = int(col_str)
            except ValueError:
                continue
            if row >= row_count or col >= col_count:
                continue
            item = self._ensure_item(row, col)
            if "bg" in style:
                item.setBackground(QColor(style["bg"]))
                item.setData(self._role_bg, style["bg"])
            if "fg" in style:
                item.setForeground(QColor(style["fg"]))
                item.setData(self._role_fg, style["fg"])
            if style.get("bold"):
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setData(self._role_bold, True)
            if "border" in style:
                item.setData(self._role_border, style["border"])
            if "font_family" in style or "font_size" in style:
                font = item.font()
                if "font_family" in style:
                    font.setFamily(style["font_family"])
                    item.setData(self._role_font_family, style["font_family"])
                if "font_size" in style:
                    font.setPointSize(int(style["font_size"]))
                    item.setData(self._role_font_size, style["font_size"])
                item.setFont(font)
        self._update_all_value_totals()
        self._capture_size_ratios()
        self._fit_table_to_view()

    def _create_default_table(self):
        self.table.setRowCount(20)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([f"Coluna {i + 1}" for i in range(8)])
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                self._ensure_item(r, c)
        self._update_all_value_totals()
        self._capture_size_ratios()
        self._fit_table_to_view()

    def _save_template(self):
        name, ok = QInputDialog.getText(self, "Salvar modelo", "Nome do modelo:")
        if not ok or not name.strip():
            return
        self._templates[name.strip()] = self._export_table_state()
        self._save_templates()

    def _load_template(self):
        if not self._templates:
            return
        names = sorted(self._templates.keys())
        name, ok = QInputDialog.getItem(self, "Abrir modelo", "Escolha um modelo:", names, 0, False)
        if not ok or not name:
            return
        self._loading_table = True
        self._apply_table_state(self._templates.get(name, {}))
        self._loading_table = False

    def _template_path(self) -> Path:
        if getattr(sys, "frozen", False):
            base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
            data_dir = base / "EcoverdeApp"
            data_dir.mkdir(parents=True, exist_ok=True)
            return data_dir / "planilha_templates.json"
        return Path("planilha_templates.json")

    def _load_templates(self) -> dict:
        path = self._template_path()
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_templates(self):
        path = self._template_path()
        path.write_text(json.dumps(self._templates, ensure_ascii=False, indent=2), encoding="utf-8")

    def _migrate_old_store(self, data: dict) -> dict:
        headers = ["Tipo", "Data", "Descricao", "Categoria", "Valor (R$)", "Pago"]
        rows = []
        for row in data.get("despesas", []):
            rows.append(
                [
                    "Despesa",
                    row.get("data", ""),
                    row.get("descricao", ""),
                    row.get("categoria", ""),
                    row.get("valor", ""),
                    "Sim" if row.get("pago") else "Nao",
                ]
            )
        for row in data.get("receitas", []):
            rows.append(
                [
                    "Receita",
                    row.get("data", ""),
                    row.get("descricao", ""),
                    row.get("categoria", ""),
                    row.get("valor", ""),
                    "",
                ]
            )
        return {
            "row_count": max(20, len(rows)),
            "col_count": len(headers),
            "headers": headers,
            "rows": rows,
            "col_widths": [],
            "row_heights": [],
            "spans": [],
            "styles": {},
        }
