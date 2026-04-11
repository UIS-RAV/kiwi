import re
from typing import Any


def clean_inline_formatting(text: str | None) -> str:
    if not text:
        return ""

    value = str(text)
    value = re.sub(r"\*\*(.*?)\*\*", r"\1", value)
    value = re.sub(r'!\[.*?\]\((/uploads/attachments/[^)]+)\)', "", value)
    return value.strip()


def parse_markdown_table(lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue

        if re.match(r"^\|[\-\s|:]+\|?$", stripped):
            continue

        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        rows.append(cells)

    return rows


def split_case_text(raw_text: str | None) -> list[dict[str, Any]]:
    if not raw_text:
        return [{"type": "paragraph", "text": "Brak treści"}]

    blocks: list[dict[str, Any]] = []
    lines = str(raw_text).splitlines()
    index = 0

    while index < len(lines):
        line = lines[index].strip()

        if not line:
            index += 1
            continue

        heading_match = re.match(r"<h2>\s*(.*?)\s*</h2>", line, re.IGNORECASE)
        if heading_match:
            blocks.append(
                {"type": "heading", "text": clean_inline_formatting(heading_match.group(1))}
            )
            index += 1
            continue

        if line.startswith("|"):
            table_lines: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1

            blocks.append({"type": "table", "rows": parse_markdown_table(table_lines)})
            continue

        if line.startswith("* "):
            blocks.append({"type": "bullet", "text": line[2:]})
            index += 1
            continue

        if line.startswith("- "):
            blocks.append({"type": "sub_bullet", "text": line[2:]})
            index += 1
            continue

        blocks.append({"type": "paragraph", "text": line})
        index += 1

    return blocks