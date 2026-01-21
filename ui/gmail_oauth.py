import os
import pickle
import sys
from pathlib import Path
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

class GmailOAuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Login com Google')
        self.setMinimumSize(400, 200)
        self.setStyleSheet('background: #f5f7fa;')
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)
        # Título estilizado
        title = QLabel('Acesse seu E-mail Empresarial')
        title.setStyleSheet('font-size: 24px; color: #1976D2; font-weight: bold; margin-top: 30px; margin-bottom: 20px;')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        self.label = QLabel('Clique para fazer login com sua conta Google:')
        self.label.setStyleSheet('font-size: 16px; color: #333; margin-bottom: 18px;')
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.login_btn = QPushButton('  Entrar com Google')
        self.login_btn.setIcon(QIcon(self._resource_path("assets/google_icon.png")))
        self.login_btn.setIconSize(QSize(32, 32))
        self.login_btn.setMinimumHeight(44)
        self.login_btn.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #42A5F5, stop:1 #1976D2);
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                border: none;
                padding: 10px 0;
                margin: 0 60px 24px 60px;
            }
            QPushButton:hover {
                background: #1565C0;
            }
        ''')
        self.login_btn.clicked.connect(self.login_google)
        layout.addWidget(self.login_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.status_label = QLabel('')
        self.status_label.setStyleSheet('font-size: 14px; color: #388e3c; margin-bottom: 10px;')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        self.creds = None

    def _resource_path(self, relative_path: str) -> str:
        if getattr(sys, "frozen", False):
            return str(Path(sys._MEIPASS) / relative_path)
        return str(Path(relative_path))

    def _token_path(self) -> Path:
        if getattr(sys, "frozen", False):
            base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
            data_dir = base / "EcoverdeApp"
            data_dir.mkdir(parents=True, exist_ok=True)
            return data_dir / "token.pickle"
        return Path("token.pickle")

    def login_google(self):
        try:
            credentials_path = self._resource_path("credentials.json")
            if not os.path.exists(credentials_path):
                QMessageBox.critical(self, 'Erro', 'credentials.json nao encontrado.')
                return
            creds = None
            token_path = self._token_path()
            if token_path.exists():
                with token_path.open('rb') as token:
                    creds = pickle.load(token)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                with token_path.open('wb') as token:
                    pickle.dump(creds, token)
            self.creds = creds
            self.status_label.setText('Login realizado com sucesso!')
            self.accept()  # Fecha o diálogo automaticamente
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Falha no login Google: {e}')

    def get_gmail_service(self):
        if self.creds:
            return build('gmail', 'v1', credentials=self.creds)
        return None
