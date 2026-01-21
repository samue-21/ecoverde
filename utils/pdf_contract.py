from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

def _file_exists(path: str) -> bool:
    try:
        return Path(path).exists()
    except OSError:
        return False


def generate_contract_pdf(
    output_path: str,
    *,
    title: str,
    contract_number: str,
    issuer: str,
    body_text: str,
    logo_path: str | None = None,
) -> str:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            Image,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Dependencia ausente: reportlab. Instale com: python -m pip install reportlab"
        ) from exc

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    normal = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        spaceAfter=8,
    )
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        alignment=1,  # center
        spaceAfter=10,
    )

    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
        title=title,
    )

    story: list[object] = []

    header_cells: list[list[object]] = []
    logo_cell: object
    if logo_path and _file_exists(logo_path):
        logo_cell = Image(logo_path, width=3.2 * cm, height=3.2 * cm)
    else:
        logo_cell = Paragraph("<b>Ecoverde</b>", normal)

    header_cells.append(
        [
            logo_cell,
            Paragraph(f"<b>{title}</b>", h1),
        ]
    )
    header_table = Table(header_cells, colWidths=[3.6 * cm, 13.4 * cm])
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(header_table)

    meta = Table(
        [
            [Paragraph(f"<b>No:</b> {contract_number}", normal), Paragraph(f"<b>Emissor:</b> {issuer}", normal)],
            [Paragraph(f"<b>Data:</b> {date.today().strftime('%d/%m/%Y')}", normal), Paragraph("", normal)],
        ],
        colWidths=[8.5 * cm, 8.5 * cm],
    )
    meta.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(meta)
    story.append(Spacer(1, 10))

    for raw_line in body_text.splitlines():
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue
        if line.isupper() and len(line) <= 80:
            story.append(Paragraph(f"<b>{line}</b>", normal))
            continue
        story.append(Paragraph(line.replace("\t", " " * 4), normal))

    doc.build(story)
    return str(output)


def generate_orcamento_pdf(
    output_path: str,
    *,
    company: dict[str, str],
    cliente: dict[str, str],
    servicos: list[str],
    valor_total: str,
    observacoes: str,
    numero: str,
    logo_path: str | None = None,
    validade_dias: int = 30,
) -> str:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            Image,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Dependencia ausente: reportlab. Instale com: python -m pip install reportlab"
        ) from exc

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    normal = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=12,
        spaceAfter=4,
    )
    small = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
    )
    title = ParagraphStyle(
        "Title",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=16,
        alignment=1,
        spaceAfter=6,
    )

    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=1.4 * cm,
        rightMargin=1.4 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
        title="Orcamento",
    )

    story: list[object] = []

    if logo_path and _file_exists(logo_path):
        logo_cell = Image(logo_path, width=2.4 * cm, height=2.4 * cm)
    else:
        logo_cell = Paragraph("<b>Ecoverde</b>", normal)

    company_lines = "<br/>".join(
        [
            f"<b>{company.get('nome', '')}</b>",
            company.get("endereco", ""),
            company.get("cidade_uf", ""),
            f"CNPJ: {company.get('cnpj', '')}",
            f"Tel.: {company.get('telefone', '')}",
            f"E-mail: {company.get('email', '')}",
        ]
    )
    company_info = Paragraph(company_lines, small)
    table_width = 18.0 * cm
    meta_width = 6.0 * cm
    header_left_width = table_width - meta_width

    meta_table = Table(
        [
            ["Criado em", date.today().strftime("%d/%m/%Y")],
            ["Valido ate", (date.today() + timedelta(days=validade_dias)).strftime("%d/%m/%Y")],
            ["Orcamento no", numero],
        ],
        colWidths=[2.6 * cm, meta_width - (2.6 * cm)],
    )
    meta_table.hAlign = "RIGHT"
    meta_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.8, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONT", (0, 0), (-1, -1), "Helvetica", 8.5),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    header_left = Table(
        [[logo_cell, company_info]],
        colWidths=[2.6 * cm, header_left_width - (2.6 * cm)],
    )
    header_left.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    header_table = Table(
        [[header_left, meta_table]],
        colWidths=[header_left_width, meta_width],
    )
    header_table.hAlign = "LEFT"
    header_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph("Orcamento", title))

    cliente_rows = [
        ["Cliente:", cliente.get("nome", ""), "CPF/CNPJ:", cliente.get("documento", "")],
        ["Contato:", cliente.get("telefone", ""), "E-mail:", cliente.get("email", "")],
        ["Endereco:", cliente.get("endereco", ""), "Cidade/UF:", cliente.get("cidade_uf", "")],
    ]
    cliente_table = Table(
        cliente_rows,
        colWidths=[2.4 * cm, 6.6 * cm, 2.4 * cm, 6.6 * cm],
    )
    cliente_table.hAlign = "LEFT"
    cliente_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(cliente_table)
    story.append(Spacer(1, 6))

    service_rows = [["SERVICO A SER REALIZADO"]]
    if not servicos:
        servicos = ["(descrever servicos)"]
    for item in servicos:
        service_rows.append([Paragraph(item, normal)])

    servicos_table = Table(service_rows, colWidths=[table_width])
    servicos_table.hAlign = "LEFT"
    servicos_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8.5),
                ("FONT", (0, 1), (-1, -1), "Helvetica", 8.5),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(servicos_table)
    story.append(Spacer(1, 6))

    resumo_table = Table(
        [
            ["VALOR FINAL R$", valor_total],
        ],
        colWidths=[3.4 * cm, 3.4 * cm],
    )
    resumo_table.hAlign = "CENTER"
    resumo_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONT", (0, 0), (-1, -1), "Helvetica", 8.5),
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    resumo_wrap = Table([[resumo_table]], colWidths=[table_width])
    resumo_wrap.hAlign = "LEFT"
    resumo_wrap.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(resumo_wrap)
    story.append(Spacer(1, 6))

    obs_title = Table(
        [[Paragraph("<b>Observacoes:</b>", ParagraphStyle("ObsTitle", parent=normal, textColor=colors.white))]],
        colWidths=[table_width],
    )
    obs_title.hAlign = "LEFT"
    obs_title.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.black),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(obs_title)

    obs_body = Paragraph(observacoes.replace("\n", "<br/>"), normal)
    obs_table = Table([[obs_body]], colWidths=[table_width])
    obs_table.hAlign = "LEFT"
    obs_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(obs_table)

    doc.build(story)
    return str(output)
