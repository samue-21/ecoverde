from __future__ import annotations

from datetime import date
from pathlib import Path

from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QFileDialog,
)

from config import COMPANY
from database.db import SessionLocal, ensure_cliente_columns
from database.models import ClienteFornecedor
from utils.pdf_contract import generate_orcamento_pdf


def _safe_filename(value: str) -> str:
    value = "".join(c for c in value if c.isalnum() or c in (" ", "-", "_"))
    value = " ".join(value.split())
    return (value.replace(" ", "_")[:80] or "orcamento")


def _resolve_logo_path() -> str | None:
    candidates = [
        getattr(COMPANY, "logo_path", None),
        r"assets\logo 4.png",
        r"assets\logo 3.png",
        r"assets\logo 2.png",
        r"assets\logo.ico",
    ]
    for path in candidates:
        if path and Path(path).exists():
            return path
    return None


class OrcamentoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

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

        fields_pane = QFrame()
        fields_layout = QVBoxLayout(fields_pane)
        fields_layout.setContentsMargins(18, 16, 18, 16)
        fields_layout.setSpacing(12)

        self.cliente_selector = QComboBox()
        self.cliente_selector.setStyleSheet(
            "QComboBox {"
            "background: #FFFFFF;"
            "border: 1px solid #C9D8EA;"
            "border-radius: 8px;"
            "padding: 6px 10px;"
            "font-size: 14px;"
            "color: #2c3e50;"
            "}"
        )

        self.cliente_nome = QLineEdit()
        self.cliente_documento = QLineEdit()
        self.cliente_endereco = QLineEdit()
        self.cliente_cidade = QLineEdit()
        self.cliente_contato = QLineEdit()

        for field in [
            self.cliente_nome,
            self.cliente_documento,
            self.cliente_endereco,
            self.cliente_cidade,
            self.cliente_contato,
        ]:
            field.setReadOnly(True)

        self.servicos = QTextEdit()
        self.servicos.setPlaceholderText("- Corte de grama\n- Poda leve\n- Limpeza do quintal")
        self.servicos.setFixedHeight(140)
        self.servicos.setStyleSheet(
            "QTextEdit {"
            "background: #FFFFFF;"
            "border: 1px solid #C9D8EA;"
            "border-radius: 8px;"
            "padding: 8px;"
            "font-size: 14px;"
            "color: #2c3e50;"
            "}"
        )

        self.valor_total = QLineEdit()
        self.valor_total.setPlaceholderText("Digite o valor total")

        self.observacoes = QTextEdit()
        self.observacoes.setFixedHeight(120)
        self.observacoes.setStyleSheet(
            "QTextEdit {"
            "background: #FFFFFF;"
            "border: 1px solid #C9D8EA;"
            "border-radius: 8px;"
            "padding: 8px;"
            "font-size: 14px;"
            "color: #2c3e50;"
            "}"
        )
        self.observacoes.setPlainText(
            "- Este orcamento contempla somente os servicos descritos acima.\n"
            "- Materiais, adubos e insumos nao estao incluidos, salvo acordo previo.\n"
            "- Descarte de residuos fora do local sera cobrado a parte.\n"
            "- Atividades extras devem ser aprovadas antes da execucao."
        )

        label_layout.addWidget(self._label("Cliente"))
        label_layout.addWidget(self._label("Nome"))
        label_layout.addWidget(self._label("Documento"))
        label_layout.addWidget(self._label("Endereco"))
        label_layout.addWidget(self._label("Cidade/UF"))
        label_layout.addWidget(self._label("Contato"))
        label_layout.addWidget(self._label("Servicos"))
        label_layout.addWidget(self._label("Valor Total"))
        label_layout.addWidget(self._label("Observacoes"))
        label_layout.addStretch(1)

        fields_layout.addWidget(self._input_frame(self.cliente_selector))
        fields_layout.addWidget(self._input_frame(self.cliente_nome))
        fields_layout.addWidget(self._input_frame(self.cliente_documento))
        fields_layout.addWidget(self._input_frame(self.cliente_endereco))
        fields_layout.addWidget(self._input_frame(self.cliente_cidade))
        fields_layout.addWidget(self._input_frame(self.cliente_contato))
        fields_layout.addWidget(self.servicos)
        fields_layout.addWidget(self._input_frame(self.valor_total))
        fields_layout.addWidget(self.observacoes)
        fields_layout.addStretch(1)

        card_layout.addWidget(label_pane)
        card_layout.addWidget(fields_pane, 1)
        layout.addWidget(card)

        buttons_row = QHBoxLayout()
        buttons_row.addStretch(1)
        self.btn_pdf = QPushButton("Gerar PDF")
        self.btn_pdf.setStyleSheet(
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
        self.btn_pdf.clicked.connect(self.gerar_pdf)
        buttons_row.addWidget(self.btn_pdf)
        layout.addLayout(buttons_row)

        self.cliente_selector.currentIndexChanged.connect(self._on_select)
        self.load_clientes()

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
        if isinstance(widget, (QLineEdit, QComboBox)):
            widget.setStyleSheet(
                "QLineEdit, QComboBox {"
                "border: none;"
                "background: transparent;"
                "font-size: 14px;"
                "color: #2c3e50;"
                "}"
            )
        return frame

    def load_clientes(self):
        self._load_clientes()

    def _load_clientes(self):
        ensure_cliente_columns()
        session = SessionLocal()
        try:
            self._clientes = session.query(ClienteFornecedor).all()
        finally:
            session.close()
        self.cliente_selector.blockSignals(True)
        self.cliente_selector.clear()
        for cliente in self._clientes:
            self.cliente_selector.addItem(cliente.nome, cliente.id)
        self.cliente_selector.blockSignals(False)
        if self._clientes:
            self.cliente_selector.setCurrentIndex(0)
            self._fill_cliente(self._clientes[0])

    def _on_select(self, idx: int):
        if idx < 0 or idx >= len(self._clientes):
            return
        self._fill_cliente(self._clientes[idx])

    def _fill_cliente(self, cliente: ClienteFornecedor):
        self.cliente_nome.setText(cliente.nome or "")
        self.cliente_documento.setText(cliente.documento or "")
        self.cliente_endereco.setText(cliente.endereco or "")
        self.cliente_cidade.setText("")
        contato = cliente.contato or ""
        telefone = getattr(cliente, "telefone", "") or ""
        self.cliente_contato.setText(" / ".join([c for c in [contato, telefone] if c]))

    def gerar_pdf(self):
        if not self._clientes:
            QMessageBox.warning(self, "Orcamento", "Nenhum cliente encontrado.")
            return
        idx = self.cliente_selector.currentIndex()
        if idx < 0:
            QMessageBox.warning(self, "Orcamento", "Selecione um cliente.")
            return
        cliente = self._clientes[idx]
        valor_total = self._format_currency(self.valor_total.text().strip())
        servicos_raw = self.servicos.toPlainText().strip()
        observacoes = self.observacoes.toPlainText().strip() or "(sem observacoes)"
        numero = f"ORC-{date.today().strftime('%Y%m%d')}-{cliente.id}"

        servicos_list = []
        if servicos_raw:
            for line in servicos_raw.splitlines():
                item = line.strip().lstrip("-").strip()
                if item:
                    servicos_list.append(item)

        cliente_email = cliente.contato or ""
        cliente_tel = getattr(cliente, "telefone", "") or ""

        default_dir = Path("contracts") / "orcamentos"
        default_dir.mkdir(parents=True, exist_ok=True)
        filename = _safe_filename(f"{numero}_{cliente.nome}.pdf")
        default_path = str((default_dir / filename).resolve())
        output_path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar PDF do Orcamento",
            default_path,
            "PDF (*.pdf)",
        )
        if not output_path_str:
            return
        try:
            generate_orcamento_pdf(
                output_path_str,
                company={
                    "nome": COMPANY.nome,
                    "cnpj": COMPANY.cnpj,
                    "endereco": COMPANY.endereco,
                    "cidade_uf": COMPANY.cidade_uf,
                    "email": COMPANY.email,
                    "telefone": COMPANY.telefone,
                },
                cliente={
                    "nome": cliente.nome or "",
                    "documento": cliente.documento or "",
                    "endereco": cliente.endereco or "",
                    "cidade_uf": "",
                    "email": cliente_email,
                    "telefone": cliente_tel,
                },
                servicos=servicos_list,
                valor_total=valor_total,
                observacoes=observacoes,
                numero=numero,
                logo_path=_resolve_logo_path(),
            )
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Falha ao gerar PDF: {exc}")
            return
        self.btn_pdf.setText("PDF Gerado")
        self.btn_pdf.setStyleSheet(
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
