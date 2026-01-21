from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QPushButton, QSplitter, QWidget, QFrame, QStyledItemDelegate
from PyQt6.QtCore import Qt, QSize, QRect
from PyQt6.QtGui import QIcon, QFont, QPainter, QColor

class EmailListDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()
        rect = option.rect
        data = index.data()
        # Separar dados
        lines = data.split('\n')
        from_ = lines[0] if len(lines) > 0 else ''
        subject = lines[1] if len(lines) > 1 else ''
        snippet = lines[2] if len(lines) > 2 else ''
        # Avatar
        avatar_rect = QRect(rect.left()+8, rect.top()+8, 32, 32)
        painter.setBrush(QColor('#e0e0e0'))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(avatar_rect)
        painter.setPen(QColor('#222'))
        font = QFont('Arial', 14, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(avatar_rect, Qt.AlignmentFlag.AlignCenter, from_[0].upper() if from_ else '?')
        # Assunto
        font = QFont('Arial', 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor('#222'))
        painter.drawText(rect.left()+52, rect.top()+12, rect.width()-60, 20, Qt.AlignmentFlag.AlignLeft, subject)
        # Remetente
        font = QFont('Arial', 10)
        painter.setFont(font)
        painter.setPen(QColor('#666'))
        painter.drawText(rect.left()+52, rect.top()+32, rect.width()-60, 16, Qt.AlignmentFlag.AlignLeft, from_)
        # Snippet
        font = QFont('Arial', 10)
        painter.setFont(font)
        painter.setPen(QColor('#444'))
        painter.drawText(rect.left()+52, rect.top()+48, rect.width()-60, 16, Qt.AlignmentFlag.AlignLeft, snippet)
        # Status de leitura
        painter.setPen(QColor('#1976d2'))
        painter.drawText(rect.right()-60, rect.top()+12, 50, 16, Qt.AlignmentFlag.AlignRight, 'Não lido')
        painter.restore()
    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 72)

class EmailGmailStyleDialog(QDialog):
    def setup_ui(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # Barra lateral
        sidebar = QWidget()
        sidebar.setStyleSheet('background: #e8f5e9; border-radius: 16px;')
        sidebar_layout = QVBoxLayout()
        sidebar.setLayout(sidebar_layout)
        logo = QLabel()
        logo.setPixmap(QIcon('assets/logo.png').pixmap(64, 64))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo)
        app_name = QLabel('Ecoverde')
        app_name.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        app_name.setStyleSheet('color: #388e3c; margin-bottom: 24px;')
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(app_name)
        # Categorias
        for icon, text in [
            ('assets/inbox_icon.png', 'Inbox'),
            ('assets/sent_icon.png', 'Sent'),
            ('assets/spam_icon.png', 'Spam'),
            ('assets/trash_icon.png', 'Trash')
        ]:
            btn = QPushButton(f'  {text}')
            btn.setIcon(QIcon(icon))
            btn.setIconSize(QSize(24, 24))
            btn.setMinimumHeight(40)
            btn.setStyleSheet('''
                QPushButton {
                    background: transparent;
                    color: #388e3c;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 18px;
                }
                QPushButton:hover {
                    background: #c8e6c9;
                }
            ''')
            sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch(1)
        splitter.addWidget(sidebar)
        sidebar.setMinimumWidth(220)

        # Lista de e-mails
        email_list_frame = QFrame()
        email_list_frame.setStyleSheet('background: #fff; border-radius: 16px;')
        email_list_layout = QVBoxLayout()
        email_list_frame.setLayout(email_list_layout)
        search = QLabel('🔍  Search...')
        search.setStyleSheet('font-size: 16px; color: #888; margin: 12px 0 8px 12px;')
        email_list_layout.addWidget(search)
        self.email_list = QListWidget()
        self.email_list.setStyleSheet('''
            QListWidget {
                background: #fff;
                border-radius: 10px;
                font-size: 16px;
                color: #333;
                padding: 4px;
            }
            QListWidget::item {
                border-bottom: 1px solid #e3e3e3;
                padding: 12px 8px 12px 8px;
                margin-bottom: 1px;
            }
            QListWidget::item:selected {
                background: #e3f2fd;
                color: #1976D2;
                font-weight: bold;
                border-left: 4px solid #42A5F5;
            }
            QListWidget::item:hover {
                background: #f5f7fa;
            }
        ''')
        email_list_layout.addWidget(self.email_list)
        splitter.addWidget(email_list_frame)
        email_list_frame.setMinimumWidth(350)

        # Painel de leitura detalhado
        self.read_panel = QFrame()
        self.read_panel.setStyleSheet('background: #fff; border-radius: 12px; border: 1px solid #e0e0e0;')
        self.read_panel_layout = QVBoxLayout(self.read_panel)
        self.read_panel_layout.setContentsMargins(24, 24, 24, 24)
        self.read_panel_layout.setSpacing(16)

        # Avatar do remetente
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(48, 48)
        self.avatar_label.setStyleSheet('border-radius: 24px; background: #e0e0e0;')
        self.read_panel_layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Assunto
        self.subject_label = QLabel('Assunto')
        self.subject_label.setStyleSheet('font-size: 22px; font-weight: bold; color: #222;')
        self.read_panel_layout.addWidget(self.subject_label)

        # Remetente
        self.from_label = QLabel('Remetente')
        self.from_label.setStyleSheet('font-size: 16px; color: #666;')
        self.read_panel_layout.addWidget(self.from_label)

        # Snippet
        self.snippet_label = QLabel('Snippet')
        self.snippet_label.setStyleSheet('font-size: 15px; color: #444;')
        self.snippet_label.setWordWrap(True)
        self.read_panel_layout.addWidget(self.snippet_label)

        # Ícones de ação
        self.action_layout = QHBoxLayout()
        self.reply_btn = QPushButton(QIcon('assets/reply.png'), '')
        self.reply_btn.setToolTip('Responder')
        self.reply_btn.setFixedSize(36, 36)
        self.reply_btn.setStyleSheet('border: none; background: #f5f7fa; border-radius: 18px;')
        self.action_layout.addWidget(self.reply_btn)
        self.archive_btn = QPushButton(QIcon('assets/archive.png'), '')
        self.archive_btn.setToolTip('Arquivar')
        self.archive_btn.setFixedSize(36, 36)
        self.archive_btn.setStyleSheet('border: none; background: #f5f7fa; border-radius: 18px;')
        self.action_layout.addWidget(self.archive_btn)
        self.delete_btn = QPushButton(QIcon('assets/delete.png'), '')
        self.delete_btn.setToolTip('Excluir')
        self.delete_btn.setFixedSize(36, 36)
        self.delete_btn.setStyleSheet('border: none; background: #f5f7fa; border-radius: 18px;')
        self.action_layout.addWidget(self.delete_btn)
        self.read_panel_layout.addLayout(self.action_layout)

        # Status de leitura
        self.status_label = QLabel('Não lido')
        self.status_label.setStyleSheet('font-size: 13px; color: #1976d2;')
        self.read_panel_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignRight)

        # Adicionar painel de leitura ao layout principal
        splitter.addWidget(self.read_panel)
        self.read_panel.setMinimumWidth(500)

        # Buscar e-mails reais do Gmail
        self.load_gmail_emails()
        self.email_list.currentRowChanged.connect(self.show_email)
        self.email_list.setItemDelegate(EmailListDelegate())

    def __init__(self, parent=None, gmail_service=None):
        super().__init__(parent)
        self.setWindowTitle('E-mail Empresarial - Modelo Gmail')
        self.setMinimumSize(1200, 800)
        self.setStyleSheet('background: #f5f7fa; border-radius: 16px;')
        self.gmail_service = gmail_service
        self.setup_ui()

    def load_gmail_emails(self):
        if not self.gmail_service:
            return
        try:
            results = self.gmail_service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10).execute()
            messages = results.get('messages', [])
            self.emails_data = []
            self.email_list.clear()
            for msg in messages:
                msg_detail = self.gmail_service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                headers = msg_detail['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(Sem assunto)')
                from_ = next((h['value'] for h in headers if h['name'] == 'From'), '')
                snippet = msg_detail.get('snippet', '')
                item = QListWidgetItem()
                item.setText(f'{from_}\n{subject}\n{snippet[:60]}...')
                self.email_list.addItem(item)
                self.emails_data.append(msg_detail)
        except Exception as e:
            self.email_list.addItem(f'Erro ao buscar e-mails: {e}')

    def show_email(self, idx):
        if idx < 0 or idx >= len(self.emails_data):
            return
        msg = self.emails_data[idx]
        headers = msg['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(Sem assunto)')
        from_ = next((h['value'] for h in headers if h['name'] == 'From'), '')
        snippet = msg.get('snippet', '')
        # Avatar: usa inicial do remetente
        avatar_text = from_[0].upper() if from_ else '?' 
        self.avatar_label.setText(avatar_text)
        self.subject_label.setText(subject)
        self.from_label.setText(from_)
        self.snippet_label.setText(snippet)
        # Status de leitura
        is_unread = 'UNREAD' in msg.get('labelIds', [])
        self.status_label.setText('Não lido' if is_unread else 'Lido')
