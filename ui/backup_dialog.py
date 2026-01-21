from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QWidget,
)
from uuid import uuid4
import sys
import ctypes
from ctypes import wintypes
from reportlab.pdfgen import canvas

from utils.backup_client import BackupClient, BackupConfig


class BackupDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Backup na nuvem")
        self.setMinimumSize(520, 260)
        self.setStyleSheet("background: #F7FAFF;")
        self._titlebar_applied = False

        self.client = BackupClient()
        self.cfg = self.client.load_config()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header = QLabel("Backup na nuvem")
        header.setStyleSheet("font-weight: 700; color: #0D47A1;")
        header_card = QWidget()
        header_card.setStyleSheet(
            "background: rgba(255,255,255,0.9);"
            "border: 1px solid rgba(30,136,229,0.35);"
            "border-radius: 12px;"
        )
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(12, 8, 12, 8)
        header_layout.addWidget(header)
        layout.addWidget(header_card)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #5c6f91;")
        status_card = QWidget()
        status_card.setStyleSheet(
            "background: rgba(255,255,255,0.9);"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 12px;"
        )
        status_layout = QHBoxLayout(status_card)
        status_layout.setContentsMargins(12, 8, 12, 8)
        status_layout.addWidget(self.status_label)
        layout.addWidget(status_card)

        form = QFormLayout()
        self.api_url_input = QLineEdit(self.cfg.api_url)
        if not self.api_url_input.text().strip():
            self.api_url_input.setText("http://72.60.244.240:8080")
        self.key_input = QLineEdit(self.cfg.backup_key)
        self.token_input = QLineEdit(self.cfg.api_token)
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        input_style = (
            "QLineEdit {"
            "color: #0D47A1;"
            "background: #FFFFFF;"
            "border: 1px solid rgba(13,71,161,0.25);"
            "border-radius: 10px;"
            "padding: 6px 10px;"
            "}"
        )
        self.key_input.setStyleSheet(input_style)
        self.token_input.setStyleSheet(input_style)
        self.enabled_checkbox = QCheckBox("Backup automatico")
        self.enabled_checkbox.setChecked(True)
        self.enabled_checkbox.setEnabled(False)
        self.enabled_checkbox.setVisible(False)

        self.api_url_input.setVisible(False)
        self.key_label = QLabel("Chave de backup")
        form.addRow(self.key_label, self.key_input)
        self.token_label = QLabel("Token (opcional)")
        form.addRow(self.token_label, self.token_input)
        form.addRow("", self.enabled_checkbox)
        layout.addLayout(form)

        actions = QHBoxLayout()
        self.generate_key_btn = QPushButton("Gerar chave")
        self.save_pdf_btn = QPushButton("Salvar chave em PDF")
        self.save_btn = QPushButton("Salvar")
        self.test_btn = None
        self.backup_btn = QPushButton("Backup agora")
        self.restore_btn = QPushButton("Restaurar")
        primary_style = (
            "QPushButton {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
            "stop:0 #64B5F6, stop:1 #1E88E5);"
            "color: #FFFFFF;"
            "border: none;"
            "border-radius: 12px;"
            "padding: 8px 16px;"
            "font-weight: 700;"
            "}"
            "QPushButton:hover {"
            "background: #1E88E5;"
            "}"
        )
        secondary_style = (
            "QPushButton {"
            "background: rgba(255,255,255,0.9);"
            "color: #0D47A1;"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 12px;"
            "padding: 8px 16px;"
            "font-weight: 700;"
            "}"
            "QPushButton:hover {"
            "background: #D6ECFF;"
            "}"
        )
        for btn in (
            self.generate_key_btn,
            self.save_pdf_btn,
            self.save_btn,
        ):
            btn.setStyleSheet(secondary_style)
        self.backup_btn.setStyleSheet(primary_style)
        self.restore_btn.setStyleSheet(secondary_style)
        actions.addWidget(self.generate_key_btn)
        actions.addWidget(self.save_pdf_btn)
        actions.addWidget(self.save_btn)
        actions.addWidget(self.backup_btn)
        actions.addWidget(self.restore_btn)
        actions.addStretch(1)
        layout.addLayout(actions)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.setStyleSheet(
            "QDialogButtonBox QPushButton {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #EF5350, stop:1 #C62828);"
            "color: #FFFFFF;"
            "border: none;"
            "border-radius: 12px;"
            "padding: 8px 16px;"
            "font-weight: 700;"
            "}"
            "QDialogButtonBox QPushButton:hover {"
            "background: #C62828;"
            "}"
        )
        layout.addWidget(buttons)
        close_btn = buttons.button(QDialogButtonBox.StandardButton.Close)
        if close_btn is not None:
            close_btn.setText("Fechar")

        self.save_btn.clicked.connect(self._save)
        self.generate_key_btn.clicked.connect(self._generate_key)
        self.save_pdf_btn.clicked.connect(self._save_key_pdf)
        self.backup_btn.clicked.connect(self._backup_now)
        self.restore_btn.clicked.connect(self._restore_now)
        buttons.rejected.connect(self.reject)
        self._update_ui_mode()

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

    def _save(self):
        self.cfg.api_url = self.api_url_input.text().strip()
        self.cfg.backup_key = self.key_input.text().strip()
        self.cfg.api_token = self.token_input.text().strip()
        self.cfg.enabled = bool(self.cfg.api_url and self.cfg.backup_key)
        self.client.save_config(self.cfg)
        self._update_ui_mode()
        QMessageBox.information(self, "Backup", "Configuracao salva.")

    def _generate_key(self):
        key = uuid4().hex
        self.key_input.setText(key)
        self.key_input.setCursorPosition(0)
        QMessageBox.information(self, "Backup", f"Chave gerada: {key}")

    def _save_key_pdf(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Backup", "Gere a chave antes de salvar.")
            return
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar chave em PDF",
            "chave-backup.pdf",
            "PDF (*.pdf)",
        )
        if not filename:
            return
        self._write_key_pdf(filename, key)
        QMessageBox.information(self, "Backup", "PDF salvo com sucesso.")

    def _update_ui_mode(self):
        activated = bool(self.cfg.enabled and self.cfg.backup_key and self.cfg.api_url)
        self.status_label.setText(
            "Backup automatico a cada 1 hora."
            if activated
            else "Gere a chave e salve para ativar o backup automatico."
        )
        for widget in (
            self.generate_key_btn,
            self.save_pdf_btn,
            self.save_btn,
            self.token_input,
            self.api_url_input,
            self.key_input,
        ):
            widget.setVisible(not activated)
        self.token_label.setVisible(not activated)
        self.key_label.setVisible(not activated)
        self.backup_btn.setVisible(True)
        self.restore_btn.setVisible(True)

    def _write_key_pdf(self, filename: str, key: str):
        c = canvas.Canvas(filename)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, 750, "Chave de Backup")
        c.setFont("Helvetica", 12)
        c.drawString(72, 720, "Guarde esta chave para restaurar seus dados.")
        c.setFont("Helvetica-Bold", 12)
        c.drawString(72, 690, key)
        c.showPage()
        c.save()

    def _backup_now(self):
        self._save()
        ok = self.client.send_backup(self.cfg)
        if ok:
            QMessageBox.information(self, "Backup", "Backup enviado com sucesso.")
        else:
            QMessageBox.warning(self, "Backup", "Falha ao enviar backup.")

    def _restore_now(self):
        self._save()
        confirm = QMessageBox.question(
            self,
            "Restaurar backup",
            "Isso vai sobrescrever os arquivos locais. Deseja continuar?",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        ok = self.client.restore_backup(self.cfg)
        if ok:
            QMessageBox.information(
                self,
                "Backup",
                "Restauracao concluida. Reinicie o aplicativo.",
            )
        else:
            QMessageBox.warning(self, "Backup", "Falha ao restaurar backup.")
