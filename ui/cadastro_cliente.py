from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QMessageBox,
    QHBoxLayout,
    QFrame,
    QToolButton,
    QWidget,
    QLabel,
)
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap


class CadastroClienteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Cadastro de Cliente')
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout()
        form = QFormLayout()

        self._row_height = 36
        self.nome = QLineEdit()
        self.contato = QLineEdit()
        self.telefone = QLineEdit()
        self.endereco = QLineEdit()
        self.documento = QLineEdit()
        self.tipo = QComboBox()
        self.tipo.addItems(['Cliente', 'Fornecedor'])
        self.tipo_contrato = QComboBox()
        self.tipo_contrato.addItems(['Anual', 'Temporario', 'Por servico'])

        email_field = self._build_email_field()

        form.addRow('Nome:', self.nome)
        form.addRow('E-mail:', email_field)
        form.addRow('Telefone:', self.telefone)
        form.addRow('Endereco:', self.endereco)
        form.addRow('Documento (CPF/CNPJ):', self.documento)
        form.addRow('Tipo:', self.tipo)
        form.addRow('Tipo de Contrato:', self.tipo_contrato)

        layout.addLayout(form)
        self.btn_salvar = QPushButton('Salvar')
        self.btn_salvar.setStyleSheet(
            "QPushButton {"
            "background-color: #2196F3;"
            "color: white;"
            "border-radius: 8px;"
            "font-size: 20px;"
            "padding: 10px 0;"
            "}"
            "QPushButton:hover {"
            "background-color: #1976D2;"
            "}"
        )
        layout.addWidget(self.btn_salvar)

        self.setLayout(layout)

        self.documento.textChanged.connect(self.formatar_documento)
        self.btn_salvar.clicked.connect(self.salvar_cliente)
        self.nome.textChanged.connect(self._buscar_cliente_por_nome)

    def _build_email_field(self):
        self.contato.setPlaceholderText('Digite o e-mail')
        self.contato.setMinimumHeight(32)
        self.contato.setStyleSheet(
            "QLineEdit {"
            "border: none;"
            "background: transparent;"
            "padding: 6px 10px;"
            "font-size: 14px;"
            "color: #2c3e50;"
            "}"
            "QLineEdit::placeholder {"
            "color: #90a4ae;"
            "}"
        )

        email_field = QFrame()
        email_field.setObjectName('emailField')
        email_field.setFixedHeight(self._row_height)
        email_field.setStyleSheet(
            "QFrame#emailField {"
            "background: #ffffff;"
            "border: 1px solid #cfd8dc;"
            "border-radius: 8px;"
            "}"
        )

        layout = QHBoxLayout(email_field)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.contato)

        icon_btn = QToolButton()
        icon_btn.setObjectName('emailIconButton')
        icon_btn.setIcon(self._build_email_icon())
        icon_btn.setIconSize(QSize(16, 16))
        icon_btn.setEnabled(False)
        icon_btn.setFixedWidth(36)
        icon_btn.setStyleSheet(
            "QToolButton#emailIconButton {"
            "background: #f1f6fb;"
            "border: none;"
            "border-left: 1px solid #cfd8dc;"
            "border-top-right-radius: 8px;"
            "border-bottom-right-radius: 8px;"
            "}"
        )
        layout.addWidget(icon_btn)

        return email_field

    def _build_email_icon(self):
        size = 18
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pen = QPen(QColor('#6a8fb3'))
        pen.setWidth(2)
        painter.setPen(pen)
        rect = QRect(2, 4, size - 4, size - 8)
        painter.drawRoundedRect(rect, 2, 2)
        painter.drawLine(rect.left(), rect.top(), rect.center().x(), rect.center().y())
        painter.drawLine(rect.right(), rect.top(), rect.center().x(), rect.center().y())
        painter.end()
        return QIcon(pixmap)

    def carregar_cliente(self, cliente):
        self.nome.setText(cliente.nome)
        self.contato.setText(cliente.contato)
        self.telefone.setText(getattr(cliente, "telefone", "") or "")
        self.endereco.setText(cliente.endereco)
        self.documento.setText(cliente.documento)
        idx_tipo = self.tipo.findText(cliente.tipo)
        if idx_tipo >= 0:
            self.tipo.setCurrentIndex(idx_tipo)
        self._cliente_id = cliente.id

    def formatar_documento(self):
        texto = self.documento.text()
        numeros = ''.join(filter(str.isdigit, texto))
        if len(numeros) <= 11:
            partes = []
            if len(numeros) > 3:
                partes.append(numeros[:3])
                if len(numeros) > 6:
                    partes.append(numeros[3:6])
                    if len(numeros) > 9:
                        partes.append(numeros[6:9])
                        partes.append(numeros[9:11])
                    else:
                        partes.append(numeros[6:])
                else:
                    partes.append(numeros[3:])
            else:
                partes.append(numeros)
            if len(numeros) > 9:
                formatado = f"{partes[0]}.{partes[1]}.{partes[2]}-{partes[3]}"
            elif len(numeros) > 6:
                formatado = f"{partes[0]}.{partes[1]}.{partes[2]}"
            elif len(numeros) > 3:
                formatado = f"{partes[0]}.{partes[1]}"
            else:
                formatado = partes[0]
        else:
            partes = []
            if len(numeros) > 2:
                partes.append(numeros[:2])
                if len(numeros) > 5:
                    partes.append(numeros[2:5])
                    if len(numeros) > 8:
                        partes.append(numeros[5:8])
                        if len(numeros) > 12:
                            partes.append(numeros[8:12])
                            partes.append(numeros[12:14])
                        else:
                            partes.append(numeros[8:])
                    else:
                        partes.append(numeros[5:])
                else:
                    partes.append(numeros[2:])
            else:
                partes.append(numeros)
            if len(numeros) > 12:
                formatado = f"{partes[0]}.{partes[1]}.{partes[2]}/{partes[3]}-{partes[4]}"
            elif len(numeros) > 8:
                formatado = f"{partes[0]}.{partes[1]}.{partes[2]}/{partes[3]}"
            elif len(numeros) > 5:
                formatado = f"{partes[0]}.{partes[1]}.{partes[2]}"
            elif len(numeros) > 2:
                formatado = f"{partes[0]}.{partes[1]}"
            else:
                formatado = partes[0]
        if texto != formatado:
            self.documento.blockSignals(True)
            self.documento.setText(formatado)
            self.documento.blockSignals(False)

    def salvar_cliente(self):
        from database.db import SessionLocal, ensure_cliente_columns
        from database.models import ClienteFornecedor, Contrato
        ensure_cliente_columns()
        session = SessionLocal()
        cliente = ClienteFornecedor(
            nome=self.nome.text(),
            contato=self.contato.text(),
            telefone=self.telefone.text(),
            endereco=self.endereco.text(),
            documento=self.documento.text(),
            tipo=self.tipo.currentText()
        )
        session.add(cliente)
        session.commit()
        contrato = Contrato(
            titulo=f"Contrato {self.tipo_contrato.currentText()} de {cliente.nome}",
            cliente_id=cliente.id,
            tipo=self.tipo_contrato.currentText()
        )
        session.add(contrato)
        session.commit()
        session.close()
        QMessageBox.information(self, 'Sucesso', 'Cliente cadastrado com sucesso!')
        self.accept()


class CadastroClienteWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        card = QFrame()
        card.setStyleSheet(
            "background: #FFFFFF;"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 12px;"
        )
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        label_pane = QFrame()
        label_pane.setFixedWidth(200)
        label_pane.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            "stop:0 #D7ECFF, stop:1 #EAF4FF);"
            "border-top-left-radius: 12px;"
            "border-bottom-left-radius: 12px;"
        )
        self._row_height = 44
        label_layout = QVBoxLayout(label_pane)
        label_layout.setContentsMargins(16, 16, 16, 16)
        label_layout.setSpacing(12)

        self.nome = QLineEdit()
        self.contato = QLineEdit()
        self.telefone = QLineEdit()
        self.endereco = QLineEdit()
        self.documento = QLineEdit()
        self.tipo = QComboBox()
        self.tipo.addItems(['Cliente', 'Fornecedor'])
        self.tipo_contrato = QComboBox()
        self.tipo_contrato.addItems(['Anual', 'Temporario', 'Por servico'])

        self.nome.setPlaceholderText("Digite o nome completo")
        self.contato.setPlaceholderText("Digite o e-mail")
        self.telefone.setPlaceholderText("Digite o telefone")
        self.endereco.setPlaceholderText("Digite o endereco")
        self.documento.setPlaceholderText("Digite o CPF/CNPJ")

        label_layout.addWidget(self._label("Nome Completo"))
        label_layout.addWidget(self._label("E-mail"))
        label_layout.addWidget(self._label("Telefone"))
        label_layout.addWidget(self._label("Endereco"))
        label_layout.addWidget(self._label("Documento"))
        label_layout.addWidget(self._label("Tipo"))
        label_layout.addWidget(self._label("Tipo de Contrato"))
        label_layout.addStretch(1)

        fields_pane = QFrame()
        fields_pane.setStyleSheet("background: transparent;")
        fields_layout = QVBoxLayout(fields_pane)
        fields_layout.setContentsMargins(18, 16, 18, 16)
        fields_layout.setSpacing(12)

        fields_layout.addWidget(self._input_frame(self.nome))
        fields_layout.addWidget(self._build_email_field())
        fields_layout.addWidget(self._input_frame(self.telefone))
        fields_layout.addWidget(self._input_frame(self.endereco))
        fields_layout.addWidget(self._input_frame(self.documento))
        fields_layout.addWidget(self._input_frame(self.tipo))
        fields_layout.addWidget(self._input_frame(self.tipo_contrato))
        fields_layout.addStretch(1)

        card_layout.addWidget(label_pane)
        card_layout.addWidget(fields_pane, 1)
        layout.addWidget(card, 1)

        buttons_row = QHBoxLayout()
        buttons_row.addStretch(1)
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setStyleSheet(
            "QPushButton {"
            "background: #E3F2FD;"
            "color: #0D47A1;"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 8px;"
            "padding: 8px 18px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover {"
            "background: #D6ECFF;"
            "}"
        )
        self.btn_cancelar.clicked.connect(self._clear_form)
        self.btn_remover = QPushButton("Remover Cadastro")
        self.btn_remover.setStyleSheet(
            "QPushButton {"
            "background: #FFEBEE;"
            "color: #C62828;"
            "border: 1px solid rgba(198,40,40,0.35);"
            "border-radius: 8px;"
            "padding: 8px 18px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover {"
            "background: #FFCDD2;"
            "}"
        )
        self.btn_remover.clicked.connect(self.remover_cliente)
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setStyleSheet(
            "QPushButton {"
            "background: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            "stop:0 #66BB6A, stop:1 #43A047);"
            "color: white;"
            "border-radius: 8px;"
            "padding: 8px 20px;"
            "font-weight: 700;"
            "}"
            "QPushButton:hover {"
            "background: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            "stop:0 #76C97C, stop:1 #4CAF50);"
            "}"
        )
        buttons_row.addWidget(self.btn_remover)
        buttons_row.addWidget(self.btn_cancelar)
        buttons_row.addWidget(self.btn_salvar)
        layout.addLayout(buttons_row)

        self.setLayout(layout)

        self.documento.textChanged.connect(self.formatar_documento)
        self.btn_salvar.clicked.connect(self.salvar_cliente)

    def _build_email_field(self):
        self.contato.setPlaceholderText('Digite o e-mail')
        self.contato.setMinimumHeight(32)
        self.contato.setStyleSheet(
            "QLineEdit {"
            "border: none;"
            "background: transparent;"
            "padding: 6px 10px;"
            "font-size: 14px;"
            "color: #2c3e50;"
            "}"
            "QLineEdit::placeholder {"
            "color: #90a4ae;"
            "}"
        )

        email_field = QFrame()
        email_field.setObjectName('emailField')
        email_field.setFixedHeight(self._row_height)
        email_field.setStyleSheet(
            "QFrame#emailField {"
            "background: #ffffff;"
            "border: 1px solid #cfd8dc;"
            "border-radius: 8px;"
            "}"
        )

        layout = QHBoxLayout(email_field)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.contato)

        icon_btn = QToolButton()
        icon_btn.setObjectName('emailIconButton')
        icon_btn.setIcon(self._build_email_icon())
        icon_btn.setIconSize(QSize(16, 16))
        icon_btn.setEnabled(False)
        icon_btn.setFixedWidth(36)
        icon_btn.setStyleSheet(
            "QToolButton#emailIconButton {"
            "background: #f1f6fb;"
            "border: none;"
            "border-left: 1px solid #cfd8dc;"
            "border-top-right-radius: 8px;"
            "border-bottom-right-radius: 8px;"
            "}"
        )
        layout.addWidget(icon_btn)

        return email_field

    def _build_email_icon(self):
        size = 18
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pen = QPen(QColor('#6a8fb3'))
        pen.setWidth(2)
        painter.setPen(pen)
        rect = QRect(2, 4, size - 4, size - 8)
        painter.drawRoundedRect(rect, 2, 2)
        painter.drawLine(rect.left(), rect.top(), rect.center().x(), rect.center().y())
        painter.drawLine(rect.right(), rect.top(), rect.center().x(), rect.center().y())
        painter.end()
        return QIcon(pixmap)

    def _input_frame(self, widget):
        frame = QFrame()
        frame.setFixedHeight(self._row_height)
        frame.setStyleSheet(
            "QFrame {"
            "background: #FFFFFF;"
            "border: 1px solid #C9D8EA;"
            "border-radius: 8px;"
            "}"
        )
        inner = QHBoxLayout(frame)
        inner.setContentsMargins(10, 6, 10, 6)
        inner.addWidget(widget)
        if isinstance(widget, QLineEdit):
            widget.setStyleSheet(
                "QLineEdit {"
                "border: none;"
                "background: transparent;"
                "font-size: 14px;"
                "color: #2c3e50;"
                "}"
            )
            widget.setMinimumHeight(30)
        else:
            widget.setStyleSheet(
                "QComboBox {"
                "border: none;"
                "background: transparent;"
                "font-size: 14px;"
                "color: #2c3e50;"
                "}"
            )
            widget.setMinimumHeight(30)
        return frame

    def _label(self, text):
        label = QLabel(text)
        label.setStyleSheet(
            "color: #0B3D91;"
            "font-weight: 700;"
            "font-size: 13px;"
            "padding: 6px 10px;"
            "background: rgba(255,255,255,0.6);"
            "border: 1px solid rgba(30,136,229,0.18);"
            "border-radius: 8px;"
        )
        label.setFixedHeight(self._row_height)
        return label

    def _clear_form(self):
        self.nome.clear()
        self.contato.clear()
        self.telefone.clear()
        self.endereco.clear()
        self.documento.clear()
        self.tipo.setCurrentIndex(0)
        self.tipo_contrato.setCurrentIndex(0)

    def formatar_documento(self):
        texto = self.documento.text()
        numeros = ''.join(filter(str.isdigit, texto))
        if len(numeros) <= 11:
            partes = []
            if len(numeros) > 3:
                partes.append(numeros[:3])
                if len(numeros) > 6:
                    partes.append(numeros[3:6])
                    if len(numeros) > 9:
                        partes.append(numeros[6:9])
                        partes.append(numeros[9:11])
                    else:
                        partes.append(numeros[6:])
                else:
                    partes.append(numeros[3:])
            else:
                partes.append(numeros)
            if len(numeros) > 9:
                formatado = f"{partes[0]}.{partes[1]}.{partes[2]}-{partes[3]}"
            elif len(numeros) > 6:
                formatado = f"{partes[0]}.{partes[1]}.{partes[2]}"
            elif len(numeros) > 3:
                formatado = f"{partes[0]}.{partes[1]}"
            else:
                formatado = partes[0]
        else:
            partes = []
            if len(numeros) > 2:
                partes.append(numeros[:2])
                if len(numeros) > 5:
                    partes.append(numeros[2:5])
                    if len(numeros) > 8:
                        partes.append(numeros[5:8])
                        if len(numeros) > 12:
                            partes.append(numeros[8:12])
                            partes.append(numeros[12:14])
                        else:
                            partes.append(numeros[8:])
                    else:
                        partes.append(numeros[5:])
                else:
                    partes.append(numeros[2:])
            else:
                partes.append(numeros)
            if len(numeros) > 12:
                formatado = f"{partes[0]}.{partes[1]}.{partes[2]}/{partes[3]}-{partes[4]}"
            elif len(numeros) > 8:
                formatado = f"{partes[0]}.{partes[1]}.{partes[2]}/{partes[3]}"
            elif len(numeros) > 5:
                formatado = f"{partes[0]}.{partes[1]}.{partes[2]}"
            elif len(numeros) > 2:
                formatado = f"{partes[0]}.{partes[1]}"
            else:
                formatado = partes[0]
        if texto != formatado:
            self.documento.blockSignals(True)
            self.documento.setText(formatado)
            self.documento.blockSignals(False)

    def set_read_only(self, read_only: bool):
        self.nome.setReadOnly(read_only)
        self.contato.setReadOnly(read_only)
        self.telefone.setReadOnly(read_only)
        self.endereco.setReadOnly(read_only)
        self.documento.setReadOnly(read_only)
        self.tipo.setEnabled(not read_only)
        self.tipo_contrato.setEnabled(not read_only)
        self.btn_salvar.setEnabled(not read_only)
        self.btn_salvar.setVisible(not read_only)
        self.btn_cancelar.setVisible(not read_only)
        self.btn_remover.setVisible(not read_only)

    def carregar_cliente(self, cliente):
        self.nome.setText(cliente.nome or "")
        self.contato.setText(cliente.contato or "")
        self.telefone.setText(getattr(cliente, "telefone", "") or "")
        self.endereco.setText(cliente.endereco or "")
        self.documento.setText(cliente.documento or "")
        idx_tipo = self.tipo.findText(cliente.tipo or "")
        if idx_tipo >= 0:
            self.tipo.setCurrentIndex(idx_tipo)

    def salvar_cliente(self):
        from database.db import SessionLocal, ensure_cliente_columns
        from database.models import ClienteFornecedor, Contrato
        ensure_cliente_columns()
        session = SessionLocal()
        cliente = ClienteFornecedor(
            nome=self.nome.text(),
            contato=self.contato.text(),
            telefone=self.telefone.text(),
            endereco=self.endereco.text(),
            documento=self.documento.text(),
            tipo=self.tipo.currentText()
        )
        session.add(cliente)
        session.commit()
        contrato = Contrato(
            titulo=f"Contrato {self.tipo_contrato.currentText()} de {cliente.nome}",
            cliente_id=cliente.id,
            tipo=self.tipo_contrato.currentText()
        )
        session.add(contrato)
        session.commit()
        session.close()
        self._show_message(QMessageBox.Icon.Information, "Sucesso", "Cliente cadastrado com sucesso!")
        self._clear_form()

    def remover_cliente(self):
        from database.db import SessionLocal, ensure_cliente_columns
        from database.models import ClienteFornecedor
        ensure_cliente_columns()
        nome = self.nome.text().strip()
        if not nome:
            nome = self._prompt_nome_para_remover()
            if not nome:
                return
        confirm = self._confirm_message(
            "Remover",
            "Deseja remover este cadastro?",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        session = SessionLocal()
        try:
            cliente = (
                session.query(ClienteFornecedor)
                .filter(ClienteFornecedor.nome.ilike(f"%{nome}%"))
                .order_by(ClienteFornecedor.id.desc())
                .first()
            )
            if not cliente:
                self._show_message(QMessageBox.Icon.Warning, "Remover", "Cliente nao encontrado.")
                return
            session.delete(cliente)
            session.commit()
        finally:
            session.close()
        self._show_message(QMessageBox.Icon.Information, "Remover", "Cadastro removido com sucesso.")
        self._clear_form()

    def _prompt_nome_para_remover(self) -> str:
        dialog = QDialog(self)
        dialog.setWindowTitle("Remover")
        dialog.setModal(True)
        dialog.setStyleSheet(
            "QDialog {"
            "background: #F7FBFF;"
            "color: #0D47A1;"
            "}"
            "QLabel {"
            "color: #0D47A1;"
            "font-size: 13px;"
            "}"
            "QLineEdit {"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 6px;"
            "padding: 6px 10px;"
            "font-size: 13px;"
            "color: #0D47A1;"
            "background: #FFFFFF;"
            "}"
            "QPushButton {"
            "background: #E3F2FD;"
            "color: #0D47A1;"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 6px;"
            "padding: 6px 14px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover {"
            "background: #D6ECFF;"
            "}"
        )

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        label = QLabel("Informe o nome do cliente para remover:")
        input_nome = QLineEdit()
        input_nome.setPlaceholderText("Digite o nome")
        input_nome.setStyleSheet("")

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancelar")
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        buttons.addWidget(btn_cancel)
        buttons.addWidget(btn_ok)

        layout.addWidget(label)
        layout.addWidget(input_nome)
        layout.addLayout(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return ""
        return input_nome.text().strip()

    def _buscar_cliente_por_nome(self, texto: str) -> None:
        nome = texto.strip()
        if not nome:
            return
        from database.db import SessionLocal
        from database.models import ClienteFornecedor
        session = SessionLocal()
        try:
            cliente = (
                session.query(ClienteFornecedor)
                .filter(ClienteFornecedor.nome.ilike(f"%{nome}%"))
                .order_by(ClienteFornecedor.id.desc())
                .first()
            )
            if cliente:
                self.carregar_cliente(cliente)
        finally:
            session.close()

    def _message_style(self) -> str:
        return (
            "QMessageBox {"
            "background: #F7FBFF;"
            "color: #0D47A1;"
            "font-size: 13px;"
            "}"
            "QLabel {"
            "color: #0D47A1;"
            "}"
            "QPushButton {"
            "background: #E3F2FD;"
            "color: #0D47A1;"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 6px;"
            "padding: 6px 14px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover {"
            "background: #D6ECFF;"
            "}"
        )

    def _show_message(self, icon: QMessageBox.Icon, title: str, text: str) -> None:
        msg = QMessageBox(self)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setStyleSheet(self._message_style())
        msg.exec()

    def _confirm_message(self, title: str, text: str) -> QMessageBox.StandardButton:
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet(self._message_style())
        return msg.exec()


class CadastroClienteListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setContentsMargins(8, 0, 8, 0)
        title = QLabel("Cliente cadastrado")
        title.setStyleSheet("color: #0D47A1; font-weight: 700;")
        header.addWidget(title)
        header.addStretch(1)
        layout.addLayout(header)

        self.selector = QComboBox()
        self.selector.setStyleSheet(
            "QComboBox {"
            "background: #FFFFFF;"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 8px;"
            "padding: 6px 10px;"
            "font-size: 14px;"
            "color: #0D47A1;"
            "}"
        )
        layout.addWidget(self.selector)

        self.form = CadastroClienteWidget()
        self.form.set_read_only(True)
        layout.addWidget(self.form, 1)

        self.setLayout(layout)
        self.selector.currentIndexChanged.connect(self._on_select)
        self.load_clientes()

    def load_clientes(self):
        from database.db import SessionLocal, ensure_cliente_columns
        from database.models import ClienteFornecedor
        ensure_cliente_columns()
        session = SessionLocal()
        try:
            self._clientes = session.query(ClienteFornecedor).all()
        finally:
            session.close()
        self.selector.blockSignals(True)
        self.selector.clear()
        for cliente in self._clientes:
            label = f"{cliente.nome}".strip()
            self.selector.addItem(label, cliente.id)
        self.selector.blockSignals(False)
        if self._clientes:
            self.selector.setCurrentIndex(0)
            self.form.carregar_cliente(self._clientes[0])
        else:
            self.form._clear_form()

    def _on_select(self, idx: int):
        if idx < 0 or idx >= len(self._clientes):
            return
        self.form.carregar_cliente(self._clientes[idx])
