import sys
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFontMetrics, QIcon, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QMessageBox,
    QMenu,
    QSizePolicy,
    QSpacerItem,
    QStyle,
    QStyledItemDelegate,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from email.mime.text import MIMEText
import base64

STYLE = """
* { font-family: "Segoe UI"; }

QWidget#InboxRoot {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #E9F1F6, stop:1 #DCEAF5);
}

#WindowCard {
    background: transparent;
    border: none;
    border-radius: 0;
}

#TopBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #E3F2FD, stop:1 #BBDEFB);
    border: 1px solid rgba(30,136,229,0.25);
    border-radius: 16px;
    padding: 10px 14px;
}

#Body {
    background: transparent;
    border: none;
    border-radius: 0;
}

#Sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #E8F2FB, stop:1 #DDEBFA);
    border: 1px solid rgba(30,136,229,0.25);
    border-radius: 18px;
    padding: 14px 12px;
}

#BrandName {
    color: #0D47A1;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: 0.3px;
}

#FolderBtn {
    text-align: left;
    padding: 12px 12px;
    border-radius: 12px;
    font-size: 15px;
    color: #0D47A1;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #FFFFFF, stop:1 #E3F2FD);
    border: 1px solid rgba(30,136,229,0.25);
}
#FolderBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #E3F2FD, stop:1 #BBDEFB);
}
#FolderBtn[selected="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #1E88E5, stop:1 #0D47A1);
    color: #FFFFFF;
    border: 1px solid rgba(13,71,161,0.45);
}

#Badge {
    background: #C8E6C9;
    color: #2E7D32;
    border-radius: 10px;
    padding: 2px 8px;
    font-weight: 700;
}

#AccountChip {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #FFFFFF, stop:1 #EAF2FF);
    border-radius: 14px;
    padding: 10px;
    color: #0D47A1;
    border: 1px solid rgba(30,136,229,0.22);
}

#Search {
    background: #FFFFFF;
    border: 1px solid rgba(30,136,229,0.2);
    border-radius: 14px;
    padding: 10px 12px;
    font-size: 14px;
    color: #0D1B3D;
}

#IconBtn {
    background: #FFFFFF;
    border: 1px solid rgba(30,136,229,0.18);
    border-radius: 12px;
    padding: 8px 10px;
    color: #0D47A1;
}
#IconBtn:hover { background: #E3F2FD; }

#PanelTitle {
    color: #0D47A1;
    font-size: 16px;
    font-weight: 700;
}

#ListPanel {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #F7FBFF, stop:1 #EDF4FF);
    border: 1px solid rgba(30,136,229,0.22);
    border-radius: 18px;
}

#ReadPanel {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #FFFFFF, stop:1 #F1F7FF);
    border: 1px solid rgba(30,136,229,0.22);
    border-radius: 18px;
}

#ListHeader {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #EAF4FF, stop:1 #DDEBFF);
    border: 1px solid rgba(30,136,229,0.22);
    border-radius: 14px;
    padding: 8px 12px;
}
#ListHeader QLabel {
    color: #0D47A1;
    font-weight: 700;
}

#ListSearch {
    background: #FFFFFF;
    border: 1px solid rgba(30,136,229,0.2);
    border-radius: 12px;
    padding: 8px 10px;
    font-size: 13px;
    color: #0D1B3D;
}

#ReadHeader {
    background: rgba(13,71,161,0.05);
    border: 1px solid rgba(13,71,161,0.10);
    border-radius: 12px;
    padding: 6px 8px;
}

#ReadDivider {
    background: rgba(13,71,161,0.16);
    max-height: 1px;
    min-height: 1px;
}

QListWidget {
    background: transparent;
    border: none;
    padding: 6px;
}
QListWidget::item {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #FFFFFF, stop:1 #EAF2FF);
    border: 1px solid rgba(13,71,161,0.14);
    border-radius: 12px;
    padding: 12px;
    margin: 6px 4px;
    color: #0D1B3D;
}
QListWidget::item:selected {
    background: #E3F2FD;
    border: 1px solid #64B5F6;
    color: #0D47A1;
}

#MailFrom {
    font-size: 18px;
    font-weight: 800;
    color: #0D47A1;
}
#MailSubject {
    font-size: 13px;
    font-weight: 600;
    color: rgba(13,71,161,0.85);
}
#MailBody {
    font-size: 13px;
    color: rgba(13,27,61,0.85);
    line-height: 1.25;
}

#MiniAction {
    background: #E3F2FD;
    border: 1px solid #BBDEFB;
    border-radius: 12px;
    padding: 8px 10px;
}
#MiniAction:hover {
    background: #BBDEFB;
}

#GoogleBtn {
    text-align: left;
    padding: 10px 18px;
    border-radius: 14px;
    font-size: 14px;
    font-weight: 700;
    color: #0D47A1;
    background: #FFFFFF;
    border: 1px solid rgba(30,136,229,0.3);
}
#GoogleBtn:hover {
    background: #EAF2FF;
}
#GoogleBtn::menu-indicator {
    image: url(icons/chevron_down.svg);
    subcontrol-origin: padding;
    subcontrol-position: right center;
    right: 10px;
}

#PythonStamp {
    color: rgba(13,71,161,0.28);
    font-weight: 800;
    font-size: 32px;
}
"""


def _folder_row(btn: QPushButton, badge: str = "") -> QWidget:
    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(10, 0, 10, 0)
    h.setSpacing(10)
    h.addWidget(btn, 1)
    if badge:
        b = QLabel(badge)
        b.setObjectName("Badge")
        h.addWidget(b, 0, Qt.AlignmentFlag.AlignRight)
    return w


def _load_icon(path: str) -> QIcon:
    icon = QIcon(path)
    return icon


class InboxWidget(QWidget):
    def __init__(self, gmail_service=None):
        super().__init__()
        self.setObjectName("InboxRoot")
        self.setStyleSheet(STYLE)
        self.gmail_service = gmail_service
        self.emails_data = {}
        self.current_label = "INBOX"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("WindowCard")
        layout.addWidget(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        top = QFrame()
        top.setObjectName("TopBar")
        top.setVisible(True)
        card_layout.addWidget(top)

        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(14, 12, 14, 12)
        top_layout.setSpacing(10)

        left_icons = [
            "icons/mail_menu.svg",
            "icons/mail_search.svg",
        ]
        for icon_path in left_icons:
            b = QPushButton()
            b.setObjectName("IconBtn")
            b.setFixedSize(44, 36)
            b.setIcon(_load_icon(icon_path))
            b.setIconSize(QSize(18, 18))
            top_layout.addWidget(b)

        top_layout.addSpacing(8)

        search = QLineEdit()
        search.setObjectName("Search")
        search.setPlaceholderText("Pesquisar...")
        search.setFixedHeight(40)
        top_layout.addWidget(search, 1)

        mid_icons = [
            "icons/mail_refresh.svg",
            "icons/mail_trash.svg",
        ]
        for icon_path in mid_icons:
            b = QPushButton()
            b.setObjectName("IconBtn")
            b.setFixedSize(44, 36)
            b.setIcon(_load_icon(icon_path))
            b.setIconSize(QSize(18, 18))
            top_layout.addWidget(b)

        top_layout.addSpacing(10)

        self.login_btn = QPushButton()
        self.login_btn.setObjectName("IconBtn")
        self.login_btn.setFixedSize(44, 36)
        self.login_btn.setIcon(_load_icon("icons/mail_sent.svg"))
        self.login_btn.setIconSize(QSize(18, 18))
        self.login_btn.setToolTip("Entrar com Google")
        self.login_btn.clicked.connect(self.login_google)
        top_layout.addWidget(self.login_btn)

        self.refresh_btn = QPushButton()
        self.refresh_btn.setObjectName("IconBtn")
        self.refresh_btn.setFixedSize(44, 36)
        self.refresh_btn.setIcon(_load_icon("icons/mail_refresh.svg"))
        self.refresh_btn.setIconSize(QSize(18, 18))
        self.refresh_btn.setToolTip("Atualizar inbox")
        self.refresh_btn.clicked.connect(self.load_gmail_emails)
        top_layout.addWidget(self.refresh_btn)

        help_btn = QPushButton()
        help_btn.setObjectName("IconBtn")
        help_btn.setFixedSize(44, 36)
        help_btn.setIcon(_load_icon("icons/mail_menu.svg"))
        help_btn.setIconSize(QSize(18, 18))
        help_btn.setToolTip("Ajuda")
        top_layout.addWidget(help_btn)

        body = QFrame()
        body.setObjectName("Body")
        card_layout.addWidget(body, 1)

        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(12)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)
        body_layout.addWidget(sidebar)

        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(10, 10, 10, 10)
        sb.setSpacing(12)

        brand_row = QHBoxLayout()
        logo = QLabel("EV")
        logo.setFixedSize(46, 46)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(
            "background: rgba(30,136,229,0.12);"
            "border-radius: 12px;"
            "color: #0D47A1;"
            "font-size: 22px;"
        )
        brand = QLabel("Ecoverde")
        brand.setObjectName("BrandName")

        brand_row.addWidget(logo)
        brand_row.addSpacing(10)
        brand_row.addWidget(brand, 1)
        sb.addLayout(brand_row)

        sb.addSpacing(6)

        self.inbox_btn = self._make_folder_btn(
            _load_icon("icons/mail_inbox.svg"),
            "Caixa de Entrada",
            "INBOX",
            selected=True,
        )
        sb.addWidget(_folder_row(self.inbox_btn, "3"))
        self.sent_btn = self._make_folder_btn(
            _load_icon("icons/mail_sent.svg"),
            "Enviados",
            "SENT",
        )
        sb.addWidget(_folder_row(self.sent_btn))
        self.spam_btn = self._make_folder_btn(
            _load_icon("icons/mail_spam.svg"),
            "Spam",
            "SPAM",
        )
        sb.addWidget(_folder_row(self.spam_btn))
        self.trash_btn = self._make_folder_btn(
            _load_icon("icons/mail_trash.svg"),
            "Lixeira",
            "TRASH",
        )
        sb.addWidget(_folder_row(self.trash_btn))

        sb.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.acc = QFrame()
        self.acc.setObjectName("AccountChip")
        self.acc_l = QHBoxLayout(self.acc)
        self.acc_l.setContentsMargins(10, 10, 10, 10)
        self.acc_l.setSpacing(10)
        self.login_action_btn = QPushButton("Entrar com Google")
        self.login_action_btn.setObjectName("GoogleBtn")
        self.login_action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_action_btn.setIcon(self._google_icon())
        self.login_action_btn.setIconSize(QSize(20, 20))
        self.login_action_btn.setFixedHeight(42)
        self.login_action_btn.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.login_action_btn.setMenu(QMenu(self.login_action_btn))
        self.login_action_btn.setStyleSheet(
            "#GoogleBtn {"
            "text-align: left;"
            "padding-left: 12px;"
            "padding-right: 28px;"
            "border-radius: 12px;"
            "font-size: 14px;"
            "font-weight: 700;"
            "color: #0D47A1;"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
            "stop:0 #FFFFFF, stop:1 #E8F0FE);"
            "border: 1px solid rgba(30,136,229,0.35);"
            "}"
            "#GoogleBtn:hover {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
            "stop:0 #FFFFFF, stop:1 #D6E4FF);"
            "}"
            "#GoogleBtn::menu-indicator {"
            "image: url(icons/chevron_down.svg);"
            "subcontrol-origin: padding;"
            "subcontrol-position: right center;"
            "right: 10px;"
            "}"
        )
        self.login_action_btn.clicked.connect(self.login_google)
        self.acc_l.addWidget(self.login_action_btn, 1)

        self.acc_logo = QLabel()

        sb.addWidget(self.acc)

        list_panel = QFrame()
        list_panel.setObjectName("ListPanel")
        body_layout.addWidget(list_panel, 1)

        lp = QVBoxLayout(list_panel)
        lp.setContentsMargins(12, 12, 12, 12)
        lp.setSpacing(10)

        list_header = QFrame()
        list_header.setObjectName("ListHeader")
        list_header.setFixedHeight(46)
        title_row = QHBoxLayout(list_header)
        title_row.setContentsMargins(8, 4, 8, 4)
        title_icon = QLabel()
        title_icon.setPixmap(_load_icon("icons/mail_inbox.svg").pixmap(20, 20))
        self.list_title = QLabel("Caixa de Entrada")
        self.list_title.setObjectName("PanelTitle")
        title_row.addWidget(title_icon)
        title_row.addWidget(self.list_title)
        title_row.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        lp.addWidget(list_header)

        list_search = QLineEdit()
        list_search.setObjectName("ListSearch")
        list_search.setPlaceholderText("Pesquisar")
        list_search.setFixedHeight(36)
        lp.addWidget(list_search)

        self.listw = QListWidget()
        self.listw.setWordWrap(False)
        self.listw.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.listw.setSelectionBehavior(QListWidget.SelectionBehavior.SelectItems)
        self.listw.setUniformItemSizes(True)
        self.listw.setItemDelegate(FixedHeightDelegate(72))
        lp.addWidget(self.listw, 1)

        self.empty_label = QLabel("Conecte sua conta Google para carregar os e-mails.")
        self.empty_label.setStyleSheet("color: #5c6f91; padding: 8px;")
        lp.addWidget(self.empty_label)

        self.send_btn = QPushButton("Enviar Mensagem")
        self.send_btn.setFixedHeight(36)
        self.send_btn.setStyleSheet(
            "QPushButton {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
            "stop:0 #64B5F6, stop:1 #1E88E5);"
            "color: #FFFFFF;"
            "border: none;"
            "border-radius: 10px;"
            "padding: 6px 16px;"
            "font-weight: 700;"
            "}"
            "QPushButton:hover {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
            "stop:0 #7EC8FF, stop:1 #2196F3);"
            "}"
        )
        self.send_btn.clicked.connect(self.open_compose)
        lp.addWidget(self.send_btn)

        read_panel = QFrame()
        read_panel.setObjectName("ReadPanel")
        body_layout.addWidget(read_panel, 1)

        rp = QVBoxLayout(read_panel)
        rp.setContentsMargins(14, 14, 14, 14)
        rp.setSpacing(10)

        self.read_title = QLabel("Nenhuma mensagem selecionada.")
        self.read_title.setStyleSheet("color: #0D47A1; font-size: 16px; font-weight: 700;")
        self.read_hint = QLabel("Selecione uma mensagem ao lado para leitura.")
        self.read_hint.setStyleSheet("color: #5c6f91; font-size: 12px;")
        rp.addWidget(self.read_title)
        rp.addWidget(self.read_hint)

        self.mail_from = QLabel("")
        self.mail_from.setObjectName("MailFrom")
        self.mail_from.setWordWrap(True)
        self.mail_subject = QLabel("")
        self.mail_subject.setObjectName("MailSubject")
        self.mail_subject.setWordWrap(True)
        self.mail_body = QLabel("")
        self.mail_body.setObjectName("MailBody")
        self.mail_body.setWordWrap(True)
        self.mail_body.setStyleSheet("padding-top: 8px;")
        self.mail_from.setVisible(False)
        self.mail_subject.setVisible(False)
        self.mail_body.setVisible(False)
        rp.addWidget(self.mail_from)
        rp.addWidget(self.mail_subject)
        rp.addWidget(self.mail_body, 1)

        self.inline_box = QFrame()
        self.inline_box.setObjectName("ReadPanel")
        self.inline_box.setVisible(False)
        inline_layout = QVBoxLayout(self.inline_box)
        inline_layout.setContentsMargins(12, 12, 12, 12)
        inline_layout.setSpacing(8)

        self.inline_title = QLabel("")
        self.inline_title.setObjectName("MailFrom")
        self.inline_title.setWordWrap(True)
        self.inline_sender = QLabel("")
        self.inline_sender.setObjectName("MailSubject")
        self.inline_sender.setWordWrap(True)

        self.inline_body = QTextEdit()
        self.inline_body.setReadOnly(True)
        self.inline_body.setStyleSheet(
            "QTextEdit {"
            "background: #F6FAFF;"
            "border: 1px solid rgba(13,71,161,0.12);"
            "border-radius: 12px;"
            "padding: 10px;"
            "font-size: 13px;"
            "color: #0D1B3D;"
            "}"
        )

        inline_layout.addWidget(self.inline_title)
        inline_layout.addWidget(self.inline_sender)
        inline_layout.addWidget(self.inline_body, 1)
        lp.addWidget(self.inline_box, 1)

        self.listw.currentRowChanged.connect(self.on_mail_selected)
        self.listw.itemClicked.connect(self.on_mail_item_clicked)
        self.listw.itemActivated.connect(self.on_mail_item_clicked)
        self._set_auth_state(bool(self.gmail_service))
        if self.gmail_service:
            self.load_gmail_emails()

    def on_mail_selected(self, row: int):
        if row < 0:
            return
        item = self.listw.item(row)
        if not item:
            return
        msg_id = item.data(Qt.ItemDataRole.UserRole)
        if msg_id not in self.emails_data:
            self._set_status("Nao foi possivel carregar este email.")
            return
        msg = self.emails_data.get(msg_id)
        headers = msg.get("payload", {}).get("headers", [])
        subject = next((h["value"] for h in headers if h.get("name") == "Subject"), "")
        from_ = next((h["value"] for h in headers if h.get("name") == "From"), "")
        body = self._get_body_text(msg)
        self.mail_from.setText(from_)
        self.mail_subject.setText(subject)
        self.mail_body.setText(body or "(Sem conteudo)")
        self.read_title.setVisible(False)
        self.read_hint.setVisible(False)
        self.mail_from.setVisible(True)
        self.mail_subject.setVisible(True)
        self.mail_body.setVisible(True)

    def on_mail_item_clicked(self, item):
        if not item:
            return
        row = self.listw.row(item)
        self.listw.setCurrentRow(row)
        self.on_mail_selected(row)
        return

    def login_google(self):
        from ui.gmail_oauth import GmailOAuthDialog
        dlg = GmailOAuthDialog(self)
        dlg.exec()
        service = dlg.get_gmail_service()
        if service:
            self.gmail_service = service
            self._set_auth_state(True)
            self.load_gmail_emails()
        else:
            QMessageBox.warning(self, "Login", "Login nao concluido.")

    def load_gmail_emails(self):
        if not self.gmail_service:
            QMessageBox.warning(self, "Login", "Entre com Google antes de atualizar.")
            return
        try:
            results = (
                self.gmail_service.users()
                .messages()
                .list(userId="me", labelIds=[self.current_label], maxResults=15)
                .execute()
            )
            messages = results.get("messages", [])
            self.emails_data = {}
            self.listw.clear()
            for msg in messages:
                msg_detail = (
                    self.gmail_service.users()
                    .messages()
                    .get(userId="me", id=msg["id"], format="full")
                    .execute()
                )
                headers = msg_detail.get("payload", {}).get("headers", [])
                subject = next((h["value"] for h in headers if h.get("name") == "Subject"), "(Sem assunto)")
                from_ = next((h["value"] for h in headers if h.get("name") == "From"), "")
                date_ = next((h["value"] for h in headers if h.get("name") == "Date"), "")
                item = QListWidgetItem()
                item.setText(self._format_list_item(from_, subject, date_))
                item.setData(Qt.ItemDataRole.UserRole, msg_detail.get("id"))
                self.listw.addItem(item)
                self.emails_data[msg_detail.get("id")] = msg_detail
            if self.empty_label:
                self.empty_label.hide()
            if not messages:
                self._set_status("Nenhum e-mail encontrado.")
            if self.listw.count() > 0:
                self.listw.setCurrentRow(0)
        except Exception as exc:
            self.listw.clear()
            self._set_status(f"Erro ao buscar e-mails: {exc}")

    def open_compose(self):
        if not self.gmail_service:
            QMessageBox.warning(self, "E-mail", "Conecte sua conta Google antes de enviar.")
            return
        dlg = ComposeDialog(self, gmail_service=self.gmail_service)
        dlg.exec()

    def _set_auth_state(self, is_authed: bool):
        self.login_btn.setVisible(not is_authed)
        self.login_action_btn.setVisible(not is_authed)
        self.refresh_btn.setEnabled(is_authed)
        if is_authed:
            self.acc.setStyleSheet("background: transparent; border: none;")
        else:
            self.acc.setStyleSheet(
                "background: rgba(255,255,255,0.0);"
                "border: 1px solid rgba(255,255,255,0.12);"
                "border-radius: 14px;"
            )
        if is_authed:
            self._set_status("Conectado. Atualize para carregar e-mails.")

    def _set_status(self, text: str):
        if self.empty_label:
            self.empty_label.setText(text)
            self.empty_label.show()

    def _make_folder_btn(self, icon: QIcon, label: str, label_id: str, selected: bool = False) -> QPushButton:
        btn = QPushButton(label)
        btn.setObjectName("FolderBtn")
        btn.setProperty("selected", "true" if selected else "false")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setIcon(icon)
        btn.setIconSize(QSize(18, 18))
        btn.clicked.connect(lambda: self._switch_label(label_id))
        return btn

    def _switch_label(self, label_id: str):
        self.current_label = label_id
        self._set_list_title(label_id)
        for btn, lbl in [
            (self.inbox_btn, "INBOX"),
            (self.sent_btn, "SENT"),
            (self.spam_btn, "SPAM"),
            (self.trash_btn, "TRASH"),
        ]:
            btn.setProperty("selected", "true" if lbl == label_id else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.load_gmail_emails()

    def _set_list_title(self, label_id: str):
        title_map = {
            "INBOX": "Caixa de Entrada",
            "SENT": "Enviados",
            "SPAM": "Spam",
            "TRASH": "Lixeira",
        }
        self.list_title.setText(title_map.get(label_id, "Caixa de Entrada"))

    def _format_list_item(self, from_, subject, date_):
        safe_from = (from_ or "").strip()
        safe_subject = (subject or "").strip()
        safe_date = (date_ or "").strip()
        metrics = QFontMetrics(self.listw.font())
        max_width = max(200, self.listw.viewport().width() - 40)
        line_1 = metrics.elidedText(safe_from, Qt.TextElideMode.ElideRight, max_width)
        line_2 = metrics.elidedText(
            f"{safe_subject}     {safe_date}".strip(),
            Qt.TextElideMode.ElideRight,
            max_width,
        )
        return f"o  {line_1}\n{line_2}"

    def _get_body_text(self, msg):
        payload = msg.get("payload", {})
        if payload.get("body", {}).get("data"):
            return self._decode_body(payload["body"]["data"])
        for part in payload.get("parts", []) or []:
            if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                return self._decode_body(part["body"]["data"])
        return msg.get("snippet", "")

    def _show_email_inline(self, msg):
        return

    def _decode_body(self, data):
        import base64
        try:
            return base64.urlsafe_b64decode(data).decode(errors="ignore")
        except Exception:
            return ""

    def _google_icon(self):
        size = 18
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setBrush(QColor("#FFFFFF"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, size - 1, size - 1)
        painter.setPen(QPen(QColor("#4285F4"), 2))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "G")
        painter.end()
        return QIcon(pixmap)

    def _update_read_header_text(self):
        return

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_read_header_text()


class InboxDialog(QDialog):
    def __init__(self, gmail_service=None):
        super().__init__()
        self.setWindowTitle("Ecoverde - Inbox")
        self.setMinimumSize(1200, 780)
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        widget = InboxWidget(gmail_service=gmail_service)
        layout.addWidget(widget)


class ComposeDialog(QDialog):
    def __init__(self, parent=None, gmail_service=None):
        super().__init__(parent)
        self.gmail_service = gmail_service
        self.setWindowTitle("Enviar Mensagem")
        self.setMinimumSize(420, 360)
        self.setStyleSheet(
            "QDialog {"
            "background: #F7FBFF;"
            "}"
            "QLabel {"
            "color: #0D47A1;"
            "font-weight: 600;"
            "}"
            "QLineEdit, QTextEdit {"
            "background: #FFFFFF;"
            "border: 1px solid rgba(30,136,229,0.2);"
            "border-radius: 8px;"
            "padding: 6px 10px;"
            "font-size: 13px;"
            "color: #0D1B3D;"
            "}"
            "QPushButton {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
            "stop:0 #64B5F6, stop:1 #1E88E5);"
            "color: #FFFFFF;"
            "border: none;"
            "border-radius: 8px;"
            "padding: 8px 14px;"
            "font-weight: 700;"
            "}"
            "QPushButton:hover {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
            "stop:0 #7EC8FF, stop:1 #2196F3);"
            "}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        to_label = QLabel("Para")
        self.to_input = QLineEdit()
        subject_label = QLabel("Assunto")
        self.subject_input = QLineEdit()
        body_label = QLabel("Mensagem")
        self.body_input = QTextEdit()

        layout.addWidget(to_label)
        layout.addWidget(self.to_input)
        layout.addWidget(subject_label)
        layout.addWidget(self.subject_input)
        layout.addWidget(body_label)
        layout.addWidget(self.body_input, 1)

        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(
            "QPushButton {"
            "background: #E3F2FD;"
            "color: #0D47A1;"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 8px;"
            "padding: 8px 14px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover {"
            "background: #D6ECFF;"
            "}"
        )
        send_btn = QPushButton("Enviar")
        send_btn.clicked.connect(self._send_email)
        cancel_btn.clicked.connect(self.reject)
        actions.addWidget(cancel_btn)
        actions.addWidget(send_btn)
        layout.addLayout(actions)

    def _send_email(self):
        to_addr = self.to_input.text().strip()
        subject = self.subject_input.text().strip()
        body = self.body_input.toPlainText().strip()
        if not to_addr:
            QMessageBox.warning(self, "Enviar", "Informe o destinatario.")
            return
        if not body:
            QMessageBox.warning(self, "Enviar", "Digite a mensagem.")
            return
        message = MIMEText(body)
        message["to"] = to_addr
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        try:
            self.gmail_service.users().messages().send(
                userId="me", body={"raw": raw}
            ).execute()
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Falha ao enviar: {exc}")
            return
        QMessageBox.information(self, "Enviar", "Mensagem enviada com sucesso.")
        self.accept()


class FixedHeightDelegate(QStyledItemDelegate):
    def __init__(self, height: int, parent=None):
        super().__init__(parent)
        self._height = height

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(self._height)
        return size


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    w = InboxDialog()
    w.exec()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
