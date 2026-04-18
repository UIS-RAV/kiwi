from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Cm, Pt

import config
import re
from datetime import datetime
from app.images import download_image, extract_image_paths
from app.parser import clean_inline_formatting, split_case_text


def _ensure_output_dir() -> Path:
    output_dir = Path(config.OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)
    return output_dir


def _set_paragraph_spacing(paragraph, before: int = 0, after: int = 0, line_spacing: float = 1.0) -> None:
    fmt = paragraph.paragraph_format
    fmt.space_before = Pt(before)
    fmt.space_after = Pt(after)
    fmt.line_spacing = line_spacing


def _set_doc_style(document: Document) -> None:
    style = document.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)

    fmt = style.paragraph_format
    fmt.space_before = Pt(0)
    fmt.space_after = Pt(0)
    fmt.line_spacing = 1.0

    for section in document.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)


def _add_images_to_container(container, raw_text: str | None, width_cm: float) -> None:
    image_paths = extract_image_paths(raw_text)

    for image_path in image_paths:
        local_file = download_image(image_path)

        if local_file and local_file.exists():
            try:
                paragraph = container.add_paragraph()
                run = paragraph.add_run()
                run.add_picture(str(local_file), width=Cm(width_cm))
                _set_paragraph_spacing(paragraph)
            except Exception as exc:
                container.add_paragraph(f"[Nie udało się wstawić obrazka: {local_file.name}]")
                print(f"Błąd przy wstawianiu obrazka: {exc}")


def _add_paragraph(document: Document, text: str) -> None:
    cleaned = clean_inline_formatting(text)
    if cleaned:
        paragraph = document.add_paragraph(cleaned)
        _set_paragraph_spacing(paragraph)

    _add_images_to_container(document, text, width_cm=12)


def _add_bullet(document: Document, text: str) -> None:
    cleaned = clean_inline_formatting(text)
    if cleaned:
        paragraph = document.add_paragraph(style="List Bullet")
        paragraph.add_run(cleaned)

        fmt = paragraph.paragraph_format
        fmt.left_indent = Cm(0.6)
        fmt.first_line_indent = Cm(0)
        fmt.space_before = Pt(0)
        fmt.space_after = Pt(0)
        fmt.line_spacing = 1.0

    _add_images_to_container(document, text, width_cm=12)


def _add_sub_bullet(document: Document, text: str) -> None:
    cleaned = clean_inline_formatting(text)

    if cleaned:
        p = document.add_paragraph(f"- {cleaned}")  # <- kreska zamiast kropki

        fmt = p.paragraph_format
        fmt.left_indent = Cm(1.3)   # wcięcie (zostaje)
        fmt.first_line_indent = Cm(0)
        fmt.space_before = Pt(0)
        fmt.space_after = Pt(0)
        fmt.line_spacing = 1.0

    _add_images_to_container(document, text, width_cm=12)


from docx.shared import Cm


def _set_column_width(table, col_idx: int, width_cm: float) -> None:
    """Ustawia szerokość całej kolumny we wszystkich wierszach."""
    for row in table.rows:
        row.cells[col_idx].width = Cm(width_cm)


def _is_steps_table(rows: list[list[str]]) -> bool:
    """Sprawdza, czy to tabela kroków testowych."""
    if not rows:
        return False

    header = [str(cell).strip().lower() for cell in rows[0]]
    return len(header) >= 3 and header[0] == "krok"


from docx import Document
from docx.shared import Cm


def _set_column_width(table, col_idx: int, width_cm: float) -> None:
    for row in table.rows:
        row.cells[col_idx].width = Cm(width_cm)


def _is_steps_table(rows: list[list[str]]) -> bool:
    if not rows:
        return False

    header = [str(cell).strip().lower() for cell in rows[0]]
    return len(header) >= 3 and header[0] == "krok"


def _add_table(document: Document, rows: list[list[str]]) -> None:
    if not rows:
        return

    col_count = max(len(row) for row in rows)
    table = document.add_table(rows=1, cols=col_count)
    table.style = "Table Grid"
    table.autofit = False

    header_cells = table.rows[0].cells
    for index, value in enumerate(rows[0]):
        header_cells[index].text = clean_inline_formatting(value)

    for row_data in rows[1:]:
        row_cells = table.add_row().cells
        for index, value in enumerate(row_data):
            if index < len(row_cells):
                row_cells[index].text = clean_inline_formatting(value)
                _add_images_to_container(row_cells[index], value, width_cm=6.5)

    if _is_steps_table(rows) and col_count >= 3:
        # szerokość zbliżona do górnej tabeli
        widths = [1.2, 8.1, 8.1]   # razem 17.4 cm
        for col_idx, width in enumerate(widths):
            _set_column_width(table, col_idx, width)

    document.add_paragraph("")


def _add_case_content(document: Document, raw_text: str | None) -> None:
    blocks = split_case_text(raw_text)

    for block in blocks:
        block_type = block["type"]

        if block_type == "heading":
            document.add_paragraph(block["text"], style="Heading 3")
        elif block_type == "paragraph":
            _add_paragraph(document, block["text"])
        elif block_type == "bullet":
            _add_bullet(document, block["text"])
        elif block_type == "sub_bullet":
            _add_sub_bullet(document, block["text"])
        elif block_type == "table":
            _add_table(document, block["rows"])


def _add_case_section(document: Document, case: dict[str, Any]) -> None:
    case_id = case.get("id", "")
    summary = case.get("summary", "Brak nazwy")
    text = case.get("text", "Brak treści")

    heading = document.add_paragraph(style="Heading 2")
    heading.add_run(f"TC-{case_id}: {summary}")

    info_table = document.add_table(rows=2, cols=2)
    info_table.style = "Table Grid"
    info_table.autofit = False

    # ustaw szerokości kolumn
    for row in info_table.rows:
        row.cells[0].width = Cm(2.5)  # etykiety (ID, Nazwa)
        row.cells[1].width = Cm(15)  # wartości

    # wypełnienie danych
    row1 = info_table.rows[0].cells
    row1[0].text = "ID"
    row1[1].text = str(case_id)

    row2 = info_table.rows[1].cells
    row2[0].text = "Nazwa"
    row2[1].text = str(summary)

    document.add_paragraph("")
    _add_case_content(document, text)
    document.add_paragraph("")

def _group_cases_by_category(
    tcms,
    cases: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """
    Grupuje test case po kategorii.
    Jeśli case ma tylko ID kategorii, pobiera nazwy kategorii z Kiwi.
    """
    grouped: dict[str, list[dict[str, Any]]] = {}

    categories = tcms.exec.Category.filter({})
    category_map = {
        category["id"]: category["name"]
        for category in categories
    }

    for case in cases:
        category_id = case.get("category")
        category_name = category_map.get(category_id, "Bez kategorii")

        grouped.setdefault(str(category_name), []).append(case)

    return grouped

from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def _add_table_of_contents(document):
    """Dodaje spis treści do dokumentu Word."""
    paragraph = document.add_paragraph()

    run = paragraph.add_run()
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')

    instrText = OxmlElement('w:instrText')
    instrText.text = 'TOC \\o "1-2" \\h \\z \\u'

    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')

    fldChar3 = OxmlElement('w:t')
    fldChar3.text = "Spis treści (zaktualizuj w Wordzie)"

    fldChar4 = OxmlElement('w:fldChar')
    fldChar4.set(qn('w:fldCharType'), 'end')

    run._r.append(fldChar)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)
    run._r.append(fldChar4)

def export_plan_to_docx(
    tcms,
    plan_name: str,
    plan_id: int,
    cases: list[dict[str, Any]],
) -> Path:
    document = Document()
    _set_doc_style(document)

    title = document.add_paragraph()
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    title_run = title.add_run(f"Test Plan: {plan_name}")
    title_run.bold = True
    title_run.font.size = Pt(16)

    subtitle = document.add_paragraph()
    subtitle.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    subtitle.add_run(f"ID planu: {plan_id}")

    summary = document.add_paragraph()
    summary.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    summary.add_run(f"Liczba test case: {len(cases)}")

    document.add_paragraph("")

    toc_heading = document.add_paragraph(style="Heading 1")
    toc_heading.add_run("Spis treści")
    _add_table_of_contents(document)

    document.add_page_break()

    grouped_cases = _group_cases_by_category(tcms, cases)

    for category_name in sorted(grouped_cases.keys()):
        category_cases = grouped_cases[category_name]
        category_count = len(category_cases)

        category_heading = document.add_paragraph(style="Heading 1")
        category_heading.add_run(
            f"Kategoria: {category_name} ({category_count} Test Cases)"
        )

        for case in sorted(category_cases, key=lambda x: x.get("id", 0)):
            _add_case_section(document, case)

    output_dir = _ensure_output_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", plan_name).strip("_")
    output_path = output_dir / f"{safe_name}_(ID_{plan_id})_{timestamp}.docx"

    document.save(output_path)
    return output_path

def export_product_to_docx(
    tcms,
    product_name: str,
    product_id: int,
    cases: list[dict[str, Any]],
    category_name: str | None = None,
) -> Path:
    document = Document()
    _set_doc_style(document)

    title_text = f"Test Cases: Projekt {product_name}"
    if category_name:
        title_text += f" / Kategoria {category_name}"

    title = document.add_paragraph()
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    title_run = title.add_run(title_text)
    title_run.bold = True
    title_run.font.size = Pt(16)

    subtitle = document.add_paragraph()
    subtitle.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    subtitle_text = f"ID projektu: {product_id}"
    if category_name:
        subtitle_text += f" | Kategoria: {category_name}"
    subtitle.add_run(subtitle_text)

    summary = document.add_paragraph()
    summary.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    summary.add_run(f"Liczba test case: {len(cases)}")

    document.add_paragraph("")

    toc_heading = document.add_paragraph()
    toc_run = toc_heading.add_run("Spis treści")
    toc_run.bold = True
    toc_run.font.size = Pt(14)

    _add_table_of_contents(document)

    document.add_page_break()

    grouped_cases = _group_cases_by_category(tcms, cases)

    for current_category_name in sorted(grouped_cases.keys()):
        category_cases = grouped_cases[current_category_name]
        category_count = len(category_cases)

        category_heading = document.add_paragraph(style="Heading 1")
        category_heading.add_run(
            f"Kategoria: {current_category_name} ({category_count} Test Cases)"
        )

        for case in sorted(category_cases, key=lambda x: x.get("id", 0)):
            _add_case_section(document, case)

    output_dir = _ensure_output_dir()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_product_name = re.sub(r"[^a-zA-Z0-9]+", "_", product_name).strip("_")

    if category_name:
        safe_category_name = re.sub(r"[^a-zA-Z0-9]+", "_", category_name).strip("_")
        file_name = f"Test Cases - Projekt {safe_product_name} - Kategoria {safe_category_name}_{timestamp}.docx"
    else:
        file_name = f"Test Cases - Projekt {safe_product_name}_{timestamp}.docx"

    output_path = output_dir / file_name
    document.save(output_path)

    return output_path