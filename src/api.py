import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile

from src.models import ExtractionResult

load_dotenv()

app = FastAPI(title="ADOR — Augmented Document Reader", version="1.0.0")

SUPPORTED_EXTENSIONS = {".txt", ".docx", ".pdf"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractionResult)
async def extract_entities(file: UploadFile):
    suffix = Path(file.filename).suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Supported: {SUPPORTED_EXTENSIONS}",
        )

    # Save uploaded file to a temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        if suffix == ".txt":
            from src.parsers.chat_parser import extract_entities_from_chat
            entities = extract_entities_from_chat(tmp_path)
            doc_type = "chat"

        elif suffix == ".docx":
            from src.parsers.docx_parser import extract_entities_from_docx
            entities = extract_entities_from_docx(tmp_path)
            doc_type = "docx"

        elif suffix == ".pdf":
            from src.llm.pdf_extractor import extract_entities_from_pdf
            entities = extract_entities_from_pdf(tmp_path)
            doc_type = "pdf"

    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return ExtractionResult(
        doc_type=doc_type,
        filename=file.filename,
        entities=entities,
    )
