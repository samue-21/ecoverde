from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QMessageBox, QCheckBox, QTabWidget
from PyQt6.QtCore import Qt
import imaplib
import smtplib
import email
from email.header import decode_header, make_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('E-mail Empresarial')
        self.setMinimumSize(1200, 800)
        self.setStyleSheet('''
            QDialog {
                background: #f5f7fa;
                border-radius: 16px;
                border: 1px solid #e3e3e3;
            }
        ''')
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Título estilizado
        title = QLabel('Acesse seu E-mail Empresarial')
        title.setStyleSheet('font-size: 28px; color: #1976D2; font-weight: bold; margin-top: 40px; margin-bottom: 30px;')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        # Login OAuth2 via Google
        from ui.gmail_oauth import GmailOAuthDialog
        self.gmail_service = None
        from PyQt6.QtGui import QIcon
        self.login_btn = QPushButton('  Entrar com Google')
        self.login_btn.setIcon(QIcon('assets/google_icon.png'))  # Adicione um ícone PNG do Google em assets/
        from PyQt6.QtCore import QSize
        self.login_btn.setIconSize(QSize(32, 32))
        self.login_btn.setMinimumHeight(48)
        self.login_btn.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #42A5F5, stop:1 #1976D2);
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 12px;
                border: none;
                padding: 12px 0;
                margin: 0 120px 32px 120px;
            }
            QPushButton:hover {
                background: #1565C0;
            }
        ''')
        self.login_btn.clicked.connect(self.login_google)
        self.layout.addWidget(self.login_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Abas para separar as caixas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet('''
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background: #e3f2fd;
                color: #1976D2;
                font-size: 17px;
                font-weight: bold;
                border-radius: 8px 8px 0 0;
                padding: 10px 32px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #42A5F5;
                color: white;
            }
        ''')
        self.layout.addWidget(self.tabs)

        email_list_style = '''
            QListWidget {
                background: #fff;
                border-radius: 10px;
                font-size: 15px;
                color: #333;
                padding: 4px;
            }
            QListWidget::item {
                border-bottom: 1px solid #e3e3e3;
                padding: 6px 4px 6px 4px;
                margin-bottom: 1px;
            }
            QListWidget::item:selected {
                background: #e3f2fd;
                color: #1976D2;
                font-weight: bold;
                border-left: 3px solid #42A5F5;
            }
            QListWidget::item:hover {
                background: #f5f7fa;
            }
        '''
        # Caixa de entrada
        self.inbox_widget = QListWidget()
        self.inbox_widget.setStyleSheet(email_list_style)
        self.tabs.addTab(self.inbox_widget, 'Caixa de Entrada')
        # Enviados
        self.sent_widget = QListWidget()
        self.sent_widget.setStyleSheet(email_list_style)
        self.tabs.addTab(self.sent_widget, 'Enviados')
        # Rascunhos
        self.draft_widget = QListWidget()
        self.draft_widget.setStyleSheet(email_list_style)
        self.tabs.addTab(self.draft_widget, 'Rascunhos')

    def login_google(self):
        from ui.gmail_oauth import GmailOAuthDialog
        dlg = GmailOAuthDialog(self)
        dlg.exec()
        service = dlg.get_gmail_service()
        if service:
            self.gmail_service = service
            self.layout.removeWidget(self.login_btn)
            self.login_btn.hide()
            QMessageBox.information(self, 'Login', 'Login Google realizado! Agora você pode buscar seus e-mails.')

        # Botão para buscar dados
        self.fetch_btn = QPushButton('Buscar E-mails')
        self.fetch_btn.clicked.connect(self.fetch_emails)
        self.layout.addWidget(self.fetch_btn)

        # Lista de e-mails/resultados
        self.email_list = QListWidget()
        self.layout.addWidget(self.email_list, stretch=1)

        # Área de detalhes do e-mail
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.layout.addWidget(self.details, stretch=2)

        # Botão para responder/enviar e-mail (esqueleto)
        self.reply_btn = QPushButton('Responder / Enviar E-mail')
        self.reply_btn.clicked.connect(self.reply_email)
        self.layout.addWidget(self.reply_btn)

        # Checkbox moderno e estilizado
        self.advanced_checkbox = QCheckBox('Modo avançado')
        self.advanced_checkbox.setStyleSheet('''
            QCheckBox {
                font-size: 16px;
                color: #1976D2;
                padding-left: 8px;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
                border-radius: 8px;
                border: 2px solid #42A5F5;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fff, stop:1 #e3f2fd);
                margin-right: 8px;
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #42A5F5, stop:1 #1976D2);
                border: 2px solid #1976D2;
            }
        ''')
        self.layout.insertWidget(0, self.advanced_checkbox, alignment=Qt.AlignmentFlag.AlignLeft)

        self.email_list.itemClicked.connect(self.show_details)
        self.emails_data = []

        # Estilizar o botão 'Buscar E-mails' para visual moderno, grande, cor personalizada, bordas arredondadas e sombra.
        self.fetch_btn.setMinimumHeight(44)
        self.fetch_btn.setStyleSheet('''
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
        self.reply_btn.setMinimumHeight(44)
        self.reply_btn.setStyleSheet('''
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
    def fetch_emails(self):
        if not self.gmail_service:
            QMessageBox.warning(self, 'Login necessário', 'Faça login com Google antes de buscar e-mails.')
            return
        try:
            # Caixa de entrada
            results = self.gmail_service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=5).execute()
            messages = results.get('messages', [])
            self.inbox_widget.clear()
            self.emails_data = []
            for msg in messages:
                msg_detail = self.gmail_service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                headers = msg_detail['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(Sem assunto)')
                from_ = next((h['value'] for h in headers if h['name'] == 'From'), '')
                date_ = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                item_text = f"{subject} | {from_} | {date_}"
                self.inbox_widget.addItem(item_text)
                self.emails_data.append(msg_detail)
            # Enviados
            sent_results = self.gmail_service.users().messages().list(userId='me', labelIds=['SENT'], maxResults=5).execute()
            sent_messages = sent_results.get('messages', [])
            self.sent_widget.clear()
            for msg in sent_messages:
                msg_detail = self.gmail_service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                headers = msg_detail['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(Sem assunto)')
                to_ = next((h['value'] for h in headers if h['name'] == 'To'), '')
                date_ = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                item_text = f"{subject} | {to_} | {date_}"
                self.sent_widget.addItem(item_text)
            # Rascunhos
            draft_results = self.gmail_service.users().messages().list(userId='me', labelIds=['DRAFT'], maxResults=5).execute()
            draft_messages = draft_results.get('messages', [])
            self.draft_widget.clear()
            for msg in draft_messages:
                msg_detail = self.gmail_service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                headers = msg_detail['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(Sem assunto)')
                to_ = next((h['value'] for h in headers if h['name'] == 'To'), '')
                date_ = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                item_text = f"{subject} | {to_} | {date_}"
                self.draft_widget.addItem(item_text)
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Falha ao buscar e-mails: {e}')

    def show_details(self, item):
        idx = self.email_list.currentRow()
        if idx < 0 or idx >= len(self.emails_data):
            return
        msg = self.emails_data[idx]
        headers = msg['payload'].get('headers', [])
        details = []
        details.append(f"De: {next((h['value'] for h in headers if h['name'] == 'From'), '')}")
        details.append(f"Para: {next((h['value'] for h in headers if h['name'] == 'To'), '')}")
        details.append(f"Assunto: {next((h['value'] for h in headers if h['name'] == 'Subject'), '')}")
        details.append(f"Data: {next((h['value'] for h in headers if h['name'] == 'Date'), '')}")
        # Corpo do e-mail (apenas texto simples)
        body = ''
        parts = msg['payload'].get('parts', [])
        for part in parts:
            if part['mimeType'] == 'text/plain':
                import base64
                body = base64.urlsafe_b64decode(part['body']['data']).decode(errors='ignore')
                break
        details.append(f"\n{body}")
        self.details.setText('\n'.join(details))

    def reply_email(self):
        if not self.gmail_service:
            QMessageBox.warning(self, 'Login necessário', 'Faça login com Google antes de enviar e-mails.')
            return
        idx = self.email_list.currentRow()
        if idx < 0 or idx >= len(self.emails_data):
            QMessageBox.warning(self, 'Selecione um e-mail', 'Selecione um e-mail para responder.')
            return
        msg = self.emails_data[idx]
        headers = msg['payload'].get('headers', [])
        to_addr = next((h['value'] for h in headers if h['name'] == 'From'), '')
        subject = 'Re: ' + next((h['value'] for h in headers if h['name'] == 'Subject'), '(Sem assunto)')
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getMultiLineText(self, 'Responder E-mail', f'Responder para: {to_addr}\nAssunto: {subject}', '')
        if ok and text.strip():
            try:
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                import base64
                message = MIMEMultipart()
                message['to'] = to_addr
                message['subject'] = subject
                message.attach(MIMEText(text, 'plain'))
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
                send_message = {'raw': raw_message}
                self.gmail_service.users().messages().send(userId='me', body=send_message).execute()
                QMessageBox.information(self, 'Enviado', 'E-mail enviado com sucesso!')
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Falha ao enviar e-mail: {e}')
