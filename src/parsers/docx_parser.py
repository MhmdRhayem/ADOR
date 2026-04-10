"""Rule-based parser for extracting financial entities from .docx term sheets."""

from pathlib import Path

from docx import Document

from src.models import DocxEntities

# Direct mapping from DOCX table labels to entity field names
LABEL_TO_FIELD = {
    "Party A": "counterparty",
    "Initial Valuation Date": "initial_valuation_date",
    "Notional Amount (N)": "notional",
    "Valuation Date": "valuation_date",
    "Termination Date": "maturity",
    "Underlying": "underlying",
    "Coupon (C)": "coupon",
    "Barrier (B)": "barrier",
    "Business Day": "calendar",
}


def extract_entities_from_docx(file_path: str | Path) -> DocxEntities:
    doc = Document(str(file_path))
    extracted = {}

    for table in doc.tables:
        for row in table.rows:
            label = row.cells[0].text.strip()
            value = row.cells[1].text.strip()

            if label in LABEL_TO_FIELD:
                field = LABEL_TO_FIELD[label]
                extracted[field] = value

    return DocxEntities(**extracted)
