from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatEntities(BaseModel):
    counterparty: Optional[str] = None
    notional: Optional[str] = None
    isin: Optional[str] = None
    underlying: Optional[str] = None
    maturity: Optional[str] = None
    bid: Optional[str] = None
    offer: Optional[str] = None
    payment_frequency: Optional[str] = None


class DocxEntities(BaseModel):
    counterparty: Optional[str] = None
    initial_valuation_date: Optional[str] = None
    notional: Optional[str] = None
    valuation_date: Optional[str] = None
    maturity: Optional[str] = None
    underlying: Optional[str] = None
    coupon: Optional[str] = None
    barrier: Optional[str] = None
    calendar: Optional[str] = None


class PdfEntities(BaseModel):
    entities: dict[str, Optional[str]] = Field(
        default_factory=dict,
        description="Key-value pairs of extracted entity names and values",
    )


class ExtractionResult(BaseModel):
    doc_type: str = Field(description="Document type: chat, docx, or pdf")
    filename: str
    entities: ChatEntities | DocxEntities | PdfEntities
    timestamp: datetime = Field(default_factory=datetime.now)
