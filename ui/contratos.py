from __future__ import annotations

import re
import uuid
from datetime import date, timedelta
from pathlib import Path

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config import COMPANY
from database.db import Base, SessionLocal, engine
from database.models import ClienteFornecedor, Contrato, HistoricoAlteracao, ModeloContrato
from utils.contract_templates import ensure_default_templates
from utils.template_renderer import render_template


def _safe_filename(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[^\w\-\. ]+", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", " ", value)
    return value.replace(" ", "_")[:80] or "contrato"


class ContratosDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Contratos")
        self.setMinimumSize(650, 650)

        self._logo_path = str(Path(COMPANY.logo_path))

        layout = QVBoxLayout()
        form = QFormLayout()

        self.cliente_combo = QComboBox()
        self.tipo_combo = QComboBox()
        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate())

        self.valor_total = QLineEdit()
        self.condicoes_pagamento = QLineEdit()
        self.responsavel_insumos = QComboBox()
        self.responsavel_insumos.addItems(["Contratante", "Contratada (Ecoverde)", "A combinar"])

        self.prazo_garantia_dias = QLineEdit("7")
        self.aviso_previo_dias = QLineEdit("30")
        self.foro = QLineEdit(COMPANY.cidade_uf)

        self.escopo = QTextEdit()
        self.escopo.setPlaceholderText(
            "- Limpeza e capina\n- Poda e condução\n- Irrigacao (quando aplicavel)\n- Coleta e destinacao de residuos\n"
        )

        self.logo_label = QLabel(self._logo_path)
        self.logo_btn = QPushButton("Escolher logo...")
        self.logo_btn.clicked.connect(self._choose_logo)

        form.addRow("Cliente:", self.cliente_combo)
        form.addRow("Tipo de contrato:", self.tipo_combo)
        form.addRow("Data de inicio:", self.data_inicio)
        form.addRow("Valor total:", self.valor_total)
        form.addRow("Condicoes de pagamento:", self.condicoes_pagamento)
        form.addRow("Insumos:", self.responsavel_insumos)
        form.addRow("Prazo garantia (dias):", self.prazo_garantia_dias)
        form.addRow("Aviso previo (dias):", self.aviso_previo_dias)
        form.addRow("Foro:", self.foro)
        form.addRow("Escopo dos servicos:", self.escopo)

        logo_row = QHBoxLayout()
        logo_row.addWidget(self.logo_label, stretch=1)
        logo_row.addWidget(self.logo_btn)
        form.addRow("Logo:", logo_row)

        layout.addLayout(form)

        buttons = QHBoxLayout()
        self.btn_gerar = QPushButton("Gerar PDF e salvar")
        self.btn_cancelar = QPushButton("Fechar")
        self.btn_gerar.clicked.connect(self._generate)
        self.btn_cancelar.clicked.connect(self.reject)
        buttons.addStretch(1)
        buttons.addWidget(self.btn_gerar)
        buttons.addWidget(self.btn_cancelar)
        layout.addLayout(buttons)

        self.setLayout(layout)

        self._load_data()

    def _choose_logo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar logo",
            "",
            "Imagens (*.png *.jpg *.jpeg);;Todos os arquivos (*.*)",
        )
        if not path:
            return
        self._logo_path = path
        self.logo_label.setText(path)

    def _load_data(self) -> None:
        Base.metadata.create_all(engine)
        session = SessionLocal()
        try:
            ensure_default_templates(session)

            clientes = session.query(ClienteFornecedor).all()
            self._clientes = clientes
            self.cliente_combo.clear()
            for cliente in clientes:
                self.cliente_combo.addItem(f"{cliente.nome} - {cliente.documento}", cliente.id)

            modelos = session.query(ModeloContrato).order_by(ModeloContrato.tipo.asc()).all()
            self._modelos = {m.tipo: m for m in modelos}
            self.tipo_combo.clear()
            for modelo in modelos:
                self.tipo_combo.addItem(modelo.tipo)
        finally:
            session.close()

    def _generate(self) -> None:
        cliente_id = self.cliente_combo.currentData()
        tipo = self.tipo_combo.currentText().strip()
        if not cliente_id or not tipo:
            QMessageBox.warning(self, "Erro", "Selecione um cliente e o tipo de contrato.")
            return

        session = SessionLocal()
        try:
            cliente = session.query(ClienteFornecedor).get(int(cliente_id))
            modelo = session.query(ModeloContrato).filter(ModeloContrato.tipo == tipo).first()
            if not cliente or not modelo:
                QMessageBox.warning(self, "Erro", "Cliente/modelo nao encontrado.")
                return

            inicio = self.data_inicio.date().toPyDate()
            fim = inicio + timedelta(days=365)

            contract_number = f"ECV-{inicio.strftime('%Y%m%d')}-{cliente.id}-{uuid.uuid4().hex[:6].upper()}"

            values = {
                "empresa_nome": COMPANY.nome,
                "empresa_cnpj": COMPANY.cnpj,
                "empresa_endereco": COMPANY.endereco,
                "empresa_cidade_uf": COMPANY.cidade_uf,
                "empresa_contato": f"{COMPANY.email} | {COMPANY.telefone}",
                "cliente_nome": cliente.nome,
                "cliente_documento": cliente.documento or "",
                "cliente_endereco": cliente.endereco or "",
                "cliente_contato": cliente.contato or "",
                "data_inicio": inicio.strftime("%d/%m/%Y"),
                "data_fim": fim.strftime("%d/%m/%Y"),
                "valor_total": self._format_currency(self.valor_total.text().strip()),
                "condicoes_pagamento": self.condicoes_pagamento.text().strip() or "(preencher condicoes)",
                "escopo_servicos": self.escopo.toPlainText().strip() or "(descrever escopo)",
                "prazo_garantia_dias": self.prazo_garantia_dias.text().strip() or "7",
                "aviso_previo_dias": self.aviso_previo_dias.text().strip() or "30",
                "responsavel_insumos": self.responsavel_insumos.currentText(),
                "foro": self.foro.text().strip() or COMPANY.cidade_uf,
                "cidade_data_assinatura": f"{COMPANY.cidade_uf}, {date.today().strftime('%d/%m/%Y')}",
            }

            content = render_template(modelo.conteudo, values)

            out_dir = Path("contracts")
            filename = _safe_filename(f"{contract_number}_{cliente.nome}_{tipo}.pdf")
            out_path = out_dir / filename

            try:
                from utils.pdf_contract import generate_contract_pdf
            except Exception as exc:
                QMessageBox.critical(
                    self,
                    "Erro",
                    "Nao foi possivel carregar o gerador de PDF.\n"
                    "Instale as dependencias com: python -m pip install reportlab\n\n"
                    f"Detalhe: {exc}",
                )
                return

            saved_path = generate_contract_pdf(
                str(out_path),
                title="CONTRATO DE PRESTACAO DE SERVICOS",
                contract_number=contract_number,
                issuer=COMPANY.nome,
                body_text=content,
                logo_path=self._logo_path,
            )

            contrato = Contrato(
                titulo=f"Contrato {tipo} - {cliente.nome}",
                cliente_id=cliente.id,
                tipo=tipo,
                data_inicio=inicio,
                data_fim=fim,
                arquivo=saved_path,
                status="Ativo",
            )
            session.add(contrato)
            session.commit()

            session.add(
                HistoricoAlteracao(
                    contrato_id=contrato.id,
                    descricao=f"Contrato gerado: {contract_number}",
                )
            )
            session.commit()

            QMessageBox.information(self, "Sucesso", f"Contrato salvo em:\n{saved_path}")
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Erro", f"Falha ao gerar contrato:\n{exc}")
        finally:
            session.close()

    def _format_currency(self, raw: str) -> str:
        value = raw.strip() if raw else ""
        if not value:
            return "(preencher valor)"
        cleaned = value.replace("R$", "").replace("r$", "").replace(" ", "")
        normalized = cleaned
        if "," in cleaned and "." in cleaned:
            normalized = cleaned.replace(".", "").replace(",", ".")
        elif "," in cleaned:
            normalized = cleaned.replace(",", ".")
        try:
            amount = float(normalized)
        except ValueError:
            if not cleaned.upper().startswith("R$"):
                return f"R$ {value}"
            return value
        formatted = f"{amount:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"


class ContratosWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        self._logo_path = str(Path(COMPANY.logo_path))

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        main_layout.addWidget(scroll, 1)

        container = QWidget()
        scroll.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
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
        label_pane.setFixedWidth(220)
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

        fields_pane = QFrame()
        fields_layout = QVBoxLayout(fields_pane)
        fields_layout.setContentsMargins(18, 16, 18, 16)
        fields_layout.setSpacing(12)

        self.cliente_combo = QComboBox()
        self.tipo_combo = QComboBox()
        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate())

        self.valor_total = QLineEdit()
        self.condicoes_pagamento = QLineEdit()
        self.responsavel_insumos = QComboBox()
        self.responsavel_insumos.addItems(["Contratante", "Contratada (Ecoverde)", "A combinar"])

        self.prazo_garantia_dias = QLineEdit("7")
        self.aviso_previo_dias = QLineEdit("30")
        self.foro = QLineEdit(COMPANY.cidade_uf)

        self.escopo = QTextEdit()
        self.escopo.setFixedHeight(140)
        self.escopo.setPlaceholderText(
            "- Limpeza e capina\n- Poda e conducao\n- Irrigacao (quando aplicavel)\n- Coleta e destinacao de residuos\n"
        )
        self.escopo.setStyleSheet(
            "QTextEdit {"
            "background: #FFFFFF;"
            "border: 1px solid #C9D8EA;"
            "border-radius: 8px;"
            "padding: 8px;"
            "font-size: 14px;"
            "color: #2c3e50;"
            "}"
        )

        self.logo_path = QLineEdit(self._logo_path)
        self.logo_path.setReadOnly(True)
        self.logo_btn = QPushButton("Escolher logo")
        self.logo_btn.clicked.connect(self._choose_logo)

        label_layout.addWidget(self._label("Cliente"))
        label_layout.addWidget(self._label("Tipo de contrato"))
        label_layout.addWidget(self._label("Data inicio"))
        label_layout.addWidget(self._label("Valor total"))
        label_layout.addWidget(self._label("Condicoes de pagamento"))
        label_layout.addWidget(self._label("Insumos"))
        label_layout.addWidget(self._label("Prazo garantia (dias)"))
        label_layout.addWidget(self._label("Aviso previo (dias)"))
        label_layout.addWidget(self._label("Foro"))
        label_layout.addWidget(self._label("Escopo dos servicos"))
        label_layout.addWidget(self._label("Logo"))
        label_layout.addStretch(1)

        fields_layout.addWidget(self._input_frame(self.cliente_combo))
        fields_layout.addWidget(self._input_frame(self.tipo_combo))
        fields_layout.addWidget(self._input_frame(self.data_inicio))
        fields_layout.addWidget(self._input_frame(self.valor_total))
        fields_layout.addWidget(self._input_frame(self.condicoes_pagamento))
        fields_layout.addWidget(self._input_frame(self.responsavel_insumos))
        fields_layout.addWidget(self._input_frame(self.prazo_garantia_dias))
        fields_layout.addWidget(self._input_frame(self.aviso_previo_dias))
        fields_layout.addWidget(self._input_frame(self.foro))
        fields_layout.addWidget(self.escopo)
        fields_layout.addWidget(self._logo_row())
        fields_layout.addStretch(1)

        card_layout.addWidget(label_pane)
        card_layout.addWidget(fields_pane, 1)
        layout.addWidget(card)

        buttons_row = QHBoxLayout()
        buttons_row.addStretch(1)
        self.btn_gerar = QPushButton("Gerar PDF")
        self.btn_gerar.setStyleSheet(
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
        self.btn_gerar.clicked.connect(self._generate)
        buttons_row.addWidget(self.btn_gerar)
        layout.addLayout(buttons_row)

        self._load_data()

    def _label(self, text: str) -> QLabel:
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

    def _input_frame(self, widget: QWidget) -> QFrame:
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
        if isinstance(widget, (QLineEdit, QComboBox, QDateEdit)):
            widget.setStyleSheet(
                "QLineEdit, QComboBox, QDateEdit {"
                "border: none;"
                "background: transparent;"
                "font-size: 14px;"
                "color: #2c3e50;"
                "}"
                "QComboBox QAbstractItemView {"
                "background: #FFFFFF;"
                "color: #2c3e50;"
                "selection-background-color: #D6ECFF;"
                "selection-color: #0D47A1;"
                "}"
            )
        return frame

    def _logo_row(self) -> QFrame:
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
        self.logo_path.setStyleSheet(
            "QLineEdit {"
            "border: none;"
            "background: transparent;"
            "font-size: 13px;"
            "color: #2c3e50;"
            "}"
        )
        self.logo_btn.setStyleSheet(
            "QPushButton {"
            "background: #E3F2FD;"
            "color: #0D47A1;"
            "border: 1px solid rgba(30,136,229,0.25);"
            "border-radius: 6px;"
            "padding: 4px 10px;"
            "font-weight: 600;"
            "}"
        )
        inner.addWidget(self.logo_path, 1)
        inner.addWidget(self.logo_btn)
        return frame

    def _choose_logo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar logo",
            "",
            "Imagens (*.png *.jpg *.jpeg);;Todos os arquivos (*.*)",
        )
        if not path:
            return
        self._logo_path = path
        self.logo_path.setText(path)

    def _load_data(self) -> None:
        Base.metadata.create_all(engine)
        session = SessionLocal()
        try:
            ensure_default_templates(session)

            clientes = session.query(ClienteFornecedor).all()
            self._clientes = clientes
            self.cliente_combo.clear()
            for cliente in clientes:
                self.cliente_combo.addItem(f"{cliente.nome} - {cliente.documento}", cliente.id)

            modelos = session.query(ModeloContrato).order_by(ModeloContrato.tipo.asc()).all()
            self._modelos = {m.tipo: m for m in modelos}
            self.tipo_combo.clear()
            for modelo in modelos:
                self.tipo_combo.addItem(modelo.tipo)
        finally:
            session.close()

    def _generate(self) -> None:
        cliente_id = self.cliente_combo.currentData()
        tipo = self.tipo_combo.currentText().strip()
        if not cliente_id or not tipo:
            QMessageBox.warning(self, "Erro", "Selecione um cliente e o tipo de contrato.")
            return

        session = SessionLocal()
        try:
            cliente = session.query(ClienteFornecedor).get(int(cliente_id))
            modelo = session.query(ModeloContrato).filter(ModeloContrato.tipo == tipo).first()
            if not cliente or not modelo:
                QMessageBox.warning(self, "Erro", "Cliente/modelo nao encontrado.")
                return

            inicio = self.data_inicio.date().toPyDate()
            fim = inicio + timedelta(days=365)

            contract_number = f"ECV-{inicio.strftime('%Y%m%d')}-{cliente.id}-{uuid.uuid4().hex[:6].upper()}"

            values = {
                "empresa_nome": COMPANY.nome,
                "empresa_cnpj": COMPANY.cnpj,
                "empresa_endereco": COMPANY.endereco,
                "empresa_cidade_uf": COMPANY.cidade_uf,
                "empresa_contato": f"{COMPANY.email} | {COMPANY.telefone}",
                "cliente_nome": cliente.nome,
                "cliente_documento": cliente.documento or "",
                "cliente_endereco": cliente.endereco or "",
                "cliente_contato": cliente.contato or "",
                "data_inicio": inicio.strftime("%d/%m/%Y"),
                "data_fim": fim.strftime("%d/%m/%Y"),
                "valor_total": self._format_currency(self.valor_total.text().strip()),
                "condicoes_pagamento": self.condicoes_pagamento.text().strip() or "(preencher condicoes)",
                "escopo_servicos": self.escopo.toPlainText().strip() or "(descrever escopo)",
                "prazo_garantia_dias": self.prazo_garantia_dias.text().strip() or "7",
                "aviso_previo_dias": self.aviso_previo_dias.text().strip() or "30",
                "responsavel_insumos": self.responsavel_insumos.currentText(),
                "foro": self.foro.text().strip() or COMPANY.cidade_uf,
                "cidade_data_assinatura": f"{COMPANY.cidade_uf}, {date.today().strftime('%d/%m/%Y')}",
            }

            content = render_template(modelo.conteudo, values)

            out_dir = Path("contracts") / "contratos"
            out_dir.mkdir(parents=True, exist_ok=True)
            filename = _safe_filename(f"{contract_number}_{cliente.nome}_{tipo}.pdf")
            default_path = str((out_dir / filename).resolve())
            output_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar PDF do Contrato",
                default_path,
                "PDF (*.pdf)",
            )
            if not output_path:
                return

            try:
                from utils.pdf_contract import generate_contract_pdf
            except Exception as exc:
                QMessageBox.critical(
                    self,
                    "Erro",
                    "Nao foi possivel carregar o gerador de PDF.\n"
                    "Instale as dependencias com: python -m pip install reportlab\n\n"
                    f"Detalhe: {exc}",
                )
                return

            saved_path = generate_contract_pdf(
                output_path,
                title="CONTRATO DE PRESTACAO DE SERVICOS",
                contract_number=contract_number,
                issuer=COMPANY.nome,
                body_text=content,
                logo_path=self._logo_path,
            )

            contrato = Contrato(
                titulo=f"Contrato {tipo} - {cliente.nome}",
                cliente_id=cliente.id,
                tipo=tipo,
                data_inicio=inicio,
                data_fim=fim,
                arquivo=saved_path,
                status="Ativo",
            )
            session.add(contrato)
            session.commit()

            session.add(
                HistoricoAlteracao(
                    contrato_id=contrato.id,
                    descricao=f"Contrato gerado: {contract_number}",
                )
            )
            session.commit()
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Erro", f"Falha ao gerar contrato:\n{exc}")
            return
        finally:
            session.close()

        self.btn_gerar.setText("PDF Gerado")
        self.btn_gerar.setStyleSheet(
            "QPushButton {"
            "background: #2E7D32;"
            "color: #FFFFFF;"
            "border: none;"
            "border-radius: 8px;"
            "padding: 8px 18px;"
            "font-weight: 700;"
            "}"
            "QPushButton:hover {"
            "background: #1B5E20;"
            "}"
        )

    def _format_currency(self, raw: str) -> str:
        value = raw.strip() if raw else ""
        if not value:
            return "(preencher valor)"
        cleaned = value.replace("R$", "").replace("r$", "").replace(" ", "")
        normalized = cleaned
        if "," in cleaned and "." in cleaned:
            normalized = cleaned.replace(".", "").replace(",", ".")
        elif "," in cleaned:
            normalized = cleaned.replace(",", ".")
        try:
            amount = float(normalized)
        except ValueError:
            if not cleaned.upper().startswith("R$"):
                return f"R$ {value}"
            return value
        formatted = f"{amount:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"
