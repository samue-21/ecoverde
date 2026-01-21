from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import QSize, Qt, QTimer
import sys
from pathlib import Path
import ctypes
from ctypes import wintypes


def resource_path(relative_path: str) -> str:
    if getattr(sys, "frozen", False):
        return str(Path(sys._MEIPASS) / relative_path)
    return str(Path(relative_path))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Ecoverde - Gestão Empresarial')
        self.setWindowIcon(QIcon(resource_path('assets/logo.ico')))
        self.setFixedSize(1180, 600)
        self._titlebar_applied = False
        self._backup_timer = None
        self.initUI()
        self._init_backup_timer()

    def _init_backup_timer(self):
        from utils.backup_client import BackupClient
        self._backup_client = BackupClient()
        self._backup_timer = QTimer(self)
        self._backup_timer.setInterval(3600000)
        self._backup_timer.timeout.connect(self._auto_backup)
        self._backup_timer.start()
        self._auto_backup()

    def _auto_backup(self):
        try:
            self._backup_client.auto_backup_if_changed()
        except Exception:
            pass

    def initUI(self):
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            "stop:0 #B3E5FC, stop:1 #90CAF9);"
        )
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(18)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(
            "background: rgba(255,255,255,0.55);"
            "border: none;"
            "border-radius: 12px;"
        )
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(14, 14, 14, 14)
        sb.setSpacing(12)

        self.sidebar_btn_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #64B5F6, stop:1 #42A5F5);
                color: #ffffff;
                border-radius: 10px;
                padding: 10px 14px;
                text-align: left;
                font-size: 16px;
                font-weight: 600;
                border: none;
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4FC3F7, stop:1 #1E88E5);
            }
        """

        def make_sidebar_btn(text, icon_path=None, checked=False):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setChecked(checked)
            btn.setStyleSheet(self.sidebar_btn_style)
            if icon_path:
                btn.setIcon(QIcon(resource_path(icon_path)))
                btn.setIconSize(QSize(20, 20))
            return btn

        sb_menu = make_sidebar_btn("Menu", "icons/cadastros.svg", False)
        sb_clientes = make_sidebar_btn("Clientes", "icons/clientes.svg", True)
        sb_cadastros = make_sidebar_btn("Cadastros", "icons/cadastros.svg")
        sb_relatorios = make_sidebar_btn("Relatorios", "icons/relatorios.svg")
        sb_orcamentos = make_sidebar_btn("Orcamentos", "icons/orcamentos.svg")
        sb_email = make_sidebar_btn("E-mail", "icons/att-cadastral.svg")
        sb_contratos = make_sidebar_btn("Contratos", "icons/contratos.svg")
        sb.addWidget(sb_menu)
        sb.addWidget(sb_clientes)
        sb.addWidget(sb_cadastros)
        sb.addWidget(sb_relatorios)
        sb.addWidget(sb_orcamentos)
        sb.addWidget(sb_email)
        sb.addWidget(sb_contratos)

        
        sb.addStretch(1)
        sb.addSpacing(6)

        self.sidebar_logo_chip = QWidget()
        self.sidebar_logo_chip.setStyleSheet("background: transparent;")
        chip_layout = QHBoxLayout(self.sidebar_logo_chip)
        chip_layout.setContentsMargins(0, 0, 0, 0)
        chip_layout.setSpacing(0)
        chip_logo = QLabel()
        logo_pixmap = QPixmap(resource_path("assets/logo 4.png"))
        if not logo_pixmap.isNull():
            chip_logo.setPixmap(
                logo_pixmap.scaled(
                    220,
                    180,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        chip_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chip_layout.addWidget(chip_logo, 1)
        sb.addWidget(self.sidebar_logo_chip)

        # Content
        content = QWidget()
        content.setStyleSheet(
            "background: rgba(255,255,255,0.85);"
            "border: 1px solid rgba(30,136,229,0.35);"
            "border-radius: 12px;"
        )
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(18, 18, 18, 18)
        content_layout.setSpacing(16)

        

        self.title_frame = QWidget()
        self.title_frame.setStyleSheet(
            "background: rgba(255,255,255,0.7);"
            "border: 1px solid rgba(30,136,229,0.35);"
            "border-radius: 10px;"
        )
        self.title_frame.setFixedHeight(40)
        title_row = QHBoxLayout(self.title_frame)
        title_row.setContentsMargins(10, 4, 10, 4)
        title_row.setSpacing(10)
        self.title_icon_btn = QPushButton()
        self.title_icon_btn.setEnabled(False)
        self.title_icon_btn.setFixedSize(26, 26)
        self.title_icon_btn.setIcon(QIcon(resource_path("icons/clientes.svg")))
        self.title_icon_btn.setIconSize(QSize(18, 18))
        self.title_icon_btn.setStyleSheet("background: #90CAF9; border-radius: 13px; border: none;")
        self.title_label = QLabel("Cadastro de Cliente")
        self.title_label.setStyleSheet(
            "color: #0D47A1; font-size: 16px; font-weight: 700; background: transparent;"
        )
        title_row.addWidget(self.title_icon_btn)
        title_row.addWidget(self.title_label, 1)
        content_layout.addWidget(self.title_frame)

        def set_header(title, icon_path, show_header=True, show_sidebar_logo=True):
            self.title_label.setText(title)
            self.title_icon_btn.setIcon(QIcon(resource_path(icon_path)))
            self.title_frame.setVisible(show_header)
            self.divider.setVisible(show_header)
            self.sidebar_logo_chip.setVisible(show_sidebar_logo)

        self.divider = QWidget()
        self.divider.setStyleSheet("background: rgba(30,136,229,0.35); max-height: 2px; min-height: 2px;")
        content_layout.addWidget(self.divider)

        self.button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #64B5F6, stop:1 #2196F3);
                color: white;
                border-radius: 18px;
                font-size: 20px;
                font-weight: 700;
                padding: 26px 0;
                min-width: 180px;
                min-height: 130px;
                border: 2px solid rgba(255,255,255,0.2);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #81D4FA, stop:1 #42A5F5);
            }
        """
        self.icon_size = QSize(46, 46)
        self.grid = QGridLayout()
        self.grid.setSpacing(16)

        # Botao Cadastros
        btn_atendimento = QPushButton('Cadastros')
        btn_atendimento.setFont(QFont('Arial', 22, QFont.Weight.Bold))
        btn_atendimento.setStyleSheet(self.button_style)
        btn_atendimento.setIcon(QIcon(resource_path('icons/cadastros.svg')))
        btn_atendimento.setIconSize(self.icon_size)
        self.grid.addWidget(btn_atendimento, 0, 1)

        def abrir_cadastro_cliente():
            from ui.cadastro_cliente import CadastroClienteDialog
            dialog = CadastroClienteDialog(self)
            dialog.exec()
        btn_atendimento.clicked.connect(
            lambda: (set_header("Cadastro de Cliente", "icons/clientes.svg", True, True), self.content_stack.setCurrentIndex(1))
        )

        # Abrir tela de clientes cadastrados ao clicar
        from PyQt6.QtWidgets import QDialog, QListWidget, QMessageBox
        from database.models import ClienteFornecedor
        from database.db import SessionLocal

        def abrir_lista_clientes():
            class ListaClientesDialog(QDialog):
                def __init__(self, parent=None):
                    super().__init__(parent)
                    self.setWindowTitle('Clientes Cadastrados')
                    self.setMinimumSize(400, 300)
                    main_layout = QVBoxLayout()
                    self.lista = QListWidget()
                    main_layout.addWidget(self.lista, stretch=1)
                    session = SessionLocal()
                    clientes = session.query(ClienteFornecedor).all()
                    self._clientes = clientes
                    for cliente in clientes:
                        tipo_contrato = ""
                        if cliente.contratos:
                            tipo_contrato = cliente.contratos[0].tipo or ""
                        self.lista.addItem(
                            f"{cliente.nome} - {cliente.documento} - {cliente.contato} - {cliente.endereco} - {cliente.tipo} - {tipo_contrato}"
                        )
                    session.close()
                    botoes_layout = QHBoxLayout()
                    btn_editar = QPushButton('Editar')
                    btn_remover = QPushButton('Remover')
                    botoes_layout.addStretch(1)
                    botoes_layout.addWidget(btn_editar)
                    botoes_layout.addWidget(btn_remover)
                    botoes_layout.addStretch(1)
                    main_layout.addLayout(botoes_layout)
                    self.setLayout(main_layout)

                    self.lista.itemDoubleClicked.connect(self.abrir_edicao_cliente)
                    btn_editar.clicked.connect(self.editar_cliente)
                    btn_remover.clicked.connect(self.remover_cliente)

                def abrir_edicao_cliente(self, item):
                    idx = self.lista.currentRow()
                    if idx < 0 or idx >= len(self._clientes):
                        return
                    cliente = self._clientes[idx]
                    from ui.cadastro_cliente import CadastroClienteDialog
                    dialog = CadastroClienteDialog(self)
                    dialog.carregar_cliente(cliente)
                    dialog.exec()
                    self.atualizar_lista()

                def editar_cliente(self):
                    idx = self.lista.currentRow()
                    if idx < 0 or idx >= len(self._clientes):
                        return
                    cliente = self._clientes[idx]
                    from ui.cadastro_cliente import CadastroClienteDialog
                    dialog = CadastroClienteDialog(self)
                    dialog.carregar_cliente(cliente)
                    dialog.exec()
                    self.atualizar_lista()

                def remover_cliente(self):
                    idx = self.lista.currentRow()
                    if idx < 0 or idx >= len(self._clientes):
                        return
                    cliente = self._clientes[idx]
                    session = SessionLocal()
                    cliente_db = session.query(ClienteFornecedor).get(cliente.id)
                    if cliente_db:
                        session.delete(cliente_db)
                        session.commit()
                        QMessageBox.information(self, 'Remover', 'Cliente removido com sucesso!')
                    else:
                        QMessageBox.warning(self, 'Remover', 'Cliente nao encontrado.')
                    session.close()
                    self.atualizar_lista()

                def atualizar_lista(self):
                    session = SessionLocal()
                    self._clientes = session.query(ClienteFornecedor).all()
                    self.lista.clear()
                    for cliente in self._clientes:
                        tipo_contrato = ""
                        if cliente.contratos:
                            tipo_contrato = cliente.contratos[0].tipo or ""
                        self.lista.addItem(
                            f"{cliente.nome} - {cliente.documento} - {cliente.contato} - {cliente.endereco} - {cliente.tipo} - {tipo_contrato}"
                        )
                    session.close()
            dialog = ListaClientesDialog(self)
            dialog.exec()

        btn_clientes = QPushButton('Clientes')
        btn_clientes.setFont(QFont('Arial', 22, QFont.Weight.Bold))
        btn_clientes.setStyleSheet(self.button_style)
        btn_clientes.setIcon(QIcon(resource_path('icons/clientes.svg')))
        btn_clientes.setIconSize(self.icon_size)
        self.grid.addWidget(btn_clientes, 0, 0)
        btn_clientes.clicked.connect(
            lambda: (set_header("Clientes", "icons/clientes.svg", True, True), self.content_stack.setCurrentIndex(2), self.clientes_page.load_clientes())
        )

        btn_relatorios = QPushButton('Relatorios')
        btn_relatorios.setFont(QFont('Arial', 22, QFont.Weight.Bold))
        btn_relatorios.setStyleSheet(self.button_style)
        btn_relatorios.setIcon(QIcon(resource_path('icons/relatorios.svg')))
        btn_relatorios.setIconSize(self.icon_size)
        self.grid.addWidget(btn_relatorios, 0, 2)
        btn_relatorios.clicked.connect(
            lambda: (
                set_header("Relatorios", "icons/relatorios.svg", True, True),
                self.content_stack.setCurrentIndex(6),
                self.relatorios_page.refresh(),
            )
        )

        from PyQt6.QtWidgets import QFrame
        row_divider = QFrame()
        row_divider.setFrameShape(QFrame.Shape.HLine)
        row_divider.setFrameShadow(QFrame.Shadow.Sunken)
        row_divider.setStyleSheet(
            "background-color: rgba(30,136,229,0.35); max-height: 2px; min-height: 2px;"
        )
        self.grid.addWidget(row_divider, 1, 0, 1, 3)

        btn_agenda = QPushButton('Orcamentos')
        btn_agenda.setFont(QFont('Arial', 22, QFont.Weight.Bold))
        btn_agenda.setStyleSheet(self.button_style)
        btn_agenda.setIcon(QIcon(resource_path('icons/orcamentos.svg')))
        btn_agenda.setIconSize(self.icon_size)
        self.grid.addWidget(btn_agenda, 2, 0)
        btn_agenda.clicked.connect(
            lambda: (
                set_header("Orcamentos", "icons/orcamentos.svg", True, True),
                self.content_stack.setCurrentIndex(3),
                self.orcamento_page.load_clientes(),
            )
        )

        btn_dica = QPushButton('E-mail')
        btn_dica.setFont(QFont('Arial', 22, QFont.Weight.Bold))
        btn_dica.setStyleSheet(self.button_style)
        btn_dica.setIcon(QIcon(resource_path('icons/att-cadastral.svg')))
        btn_dica.setIconSize(QSize(36, 36))
        self.grid.addWidget(btn_dica, 2, 1)
        btn_dica.clicked.connect(
            lambda: (set_header("E-mail", "icons/att-cadastral.svg", False, True), self.content_stack.setCurrentIndex(5))
        )

        btn_transferir = QPushButton('Contratos')
        btn_transferir.setFont(QFont('Arial', 22, QFont.Weight.Bold))
        btn_transferir.setStyleSheet(self.button_style)
        btn_transferir.setIcon(QIcon(resource_path('icons/contratos.svg')))
        btn_transferir.setIconSize(self.icon_size)
        self.grid.addWidget(btn_transferir, 2, 2)
        btn_transferir.clicked.connect(
            lambda: (set_header("Contratos", "icons/contratos.svg", True, True), self.content_stack.setCurrentIndex(4))
        )

        sb_menu.clicked.connect(lambda: (set_header("Cadastro de Cliente", "icons/clientes.svg", True, True), self.content_stack.setCurrentIndex(0)))
        sb_clientes.clicked.connect(lambda: btn_clientes.click())
        sb_cadastros.clicked.connect(lambda: btn_atendimento.click())
        sb_relatorios.clicked.connect(lambda: btn_relatorios.click())
        sb_orcamentos.clicked.connect(lambda: btn_agenda.click())
        sb_email.clicked.connect(lambda: btn_dica.click())
        sb_contratos.clicked.connect(lambda: btn_transferir.click())

        for row in range(3):
            self.grid.setRowStretch(row, 1)
        for col in range(3):
            self.grid.setColumnStretch(col, 1)

        cards_page = QWidget()
        cards_page.setLayout(self.grid)

        from ui.cadastro_cliente import CadastroClienteWidget, CadastroClienteListWidget
        from ui.orcamento_widget import OrcamentoWidget
        from ui.contratos import ContratosWidget
        from ui_inbox import InboxWidget
        from ui.relatorios_widget import RelatoriosWidget
        cadastro_page = CadastroClienteWidget()
        self.clientes_page = CadastroClienteListWidget()
        self.orcamento_page = OrcamentoWidget()
        self.contratos_page = ContratosWidget()
        self.email_page = InboxWidget()
        self.relatorios_page = RelatoriosWidget()

        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(cards_page)
        self.content_stack.addWidget(cadastro_page)
        self.content_stack.addWidget(self.clientes_page)
        self.content_stack.addWidget(self.orcamento_page)
        self.content_stack.addWidget(self.contratos_page)
        self.content_stack.addWidget(self.email_page)
        self.content_stack.addWidget(self.relatorios_page)
        self.content_stack.setCurrentIndex(0)

        content_layout.addWidget(self.content_stack, 1)
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content, 1)
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

    def abrir_email_dialog(self):
        from ui_inbox import InboxDialog
        if hasattr(self, 'gmail_service') and self.gmail_service:
            dlg = InboxDialog(gmail_service=self.gmail_service)
        else:
            dlg = InboxDialog()
        dlg.exec()

    def abrir_contratos(self):
        from ui.contratos import ContratosDialog
        dialog = ContratosDialog(self)
        dialog.exec()

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

if __name__ == '__main__':
    from database.db import Base, engine, ensure_cliente_columns
    import database.models  # Ensure models are registered before create_all
    Base.metadata.create_all(engine)
    ensure_cliente_columns()

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setWindowIcon(QIcon(resource_path('assets/logo.ico')))
    app.setStyleSheet(
        "QMessageBox { background: #F7FAFF; }"
        "QMessageBox QLabel { color: #0D47A1; font-weight: 600; }"
        "QMessageBox QPushButton {"
        "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #64B5F6, stop:1 #1E88E5);"
        "color: #FFFFFF;"
        "border: none;"
        "border-radius: 10px;"
        "padding: 7px 14px;"
        "font-weight: 700;"
        "}"
    )
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
