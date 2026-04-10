import json
from pathlib import Path

import pdfplumber
from openai import OpenAI

from src.models import PdfEntities

SYSTEM_PROMPT = """
You are a financial document analyst. Extract all named entities from the provided document text.

Return a flat JSON object where keys are entity names (snake_case) and values are the extracted values as strings.
Only include entities that are actually present in the document. Use null for ambiguous values.

Example output format:
{"company": "Technological Technologies", "investor": "Infuse Capital", "amount": "10M USD"}"""


def extract_text_from_pdf(file_path: str | Path) -> str:
    text_parts = []
    with pdfplumber.open(str(file_path)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


def extract_entities_from_pdf(
    file_path: str | Path,
    model: str = "gpt-4o-mini",
) -> PdfEntities:
    text = extract_text_from_pdf(file_path)

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract entities from this document:\n\n{text}"},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    entities = json.loads(response.choices[0].message.content)
    return PdfEntities(entities=entities)
