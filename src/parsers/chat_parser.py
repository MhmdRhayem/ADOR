import re
from pathlib import Path

from transformers import pipeline

from src.models import ChatEntities

ner_pipeline = pipeline(
    "ner",
    model="dslim/bert-base-NER",
    aggregation_strategy="simple",
)

# Map BERT NER labels → ChatEntities fields
NER_LABEL_MAP = {
    "ORG": "counterparty",
}

# ISIN: 2-letter country code + 9-10 alphanumeric chars (standard format)
ISIN_RE = re.compile(r"\b([A-Z]{2}[A-Z0-9]{9,10})\b")

# Notional: number followed by a scale keyword
NOTIONAL_RE = re.compile(
    r"\b(\d+[\d,.]*\s*(?:mio|million|mn|bn|billion|k|thousand))\b",
    re.IGNORECASE,
)

# Maturity: digit(s) + time unit (Y/M/D) + optional qualifier (e.g. EVG, IMM)
MATURITY_RE = re.compile(r"\b(\d+\s*[YMD](?:\s+[A-Z]{2,5})?)\b")

# Spread: reference-rate +/- basis points (e.g. estr+45bps)
SPREAD_RE = re.compile(
    r"\b((?:estr|euribor|libor|sofr|sonia|ois)\s*[+-]\s*\d+\s*bps)\b",
    re.IGNORECASE,
)

# Underlying: uppercase ticker + optional type (FLOAT/FIXED) + date (MM/DD/YY)
UNDERLYING_RE = re.compile(
    r"\b([A-Z]{3,}(?:\s+(?:FLOAT|FIXED))?\s+\d{2}/\d{2}/\d{2,4})\b"
)

# Payment frequency keywords
FREQUENCY_RE = re.compile(
    r"\b(quarterly|monthly|semi[- ]?annually?|annually?|bi[- ]?annually?)\b",
    re.IGNORECASE,
)


def extract_entities_from_chat(file_path: str | Path) -> ChatEntities:
    text = Path(file_path).read_text(encoding="utf-8")
    entities: dict[str, str] = {}

    ner_results = ner_pipeline(text)

    for ent in ner_results:
        label = ent["entity_group"]
        word = ent["word"]
        score = ent["score"]
        print(f"  {label:10} {word:30} score={score:.3f}")

        field = NER_LABEL_MAP.get(label)
        if field and field not in entities:
            entities[field] = word

    # ISIN
    isin_match = ISIN_RE.search(text)
    if isin_match:
        entities.setdefault("isin", isin_match.group(1))

    # Notional
    notional_match = NOTIONAL_RE.search(text)
    if notional_match:
        entities.setdefault("notional", notional_match.group(1).strip())

    # Underlying
    underlying_match = UNDERLYING_RE.search(text)
    if underlying_match:
        # Normalize tabs/whitespace to single spaces
        underlying = re.sub(r"\s+", " ", underlying_match.group(1))
        entities.setdefault("underlying", underlying)

    # Maturity — pick the most detailed match (with qualifier if present)
    maturity_matches = MATURITY_RE.findall(text)
    if maturity_matches:
        entities.setdefault("maturity", max(maturity_matches, key=len).strip())

    # Bid / Offer — first spread found is bid, second is offer
    spreads = SPREAD_RE.findall(text)
    if spreads:
        entities.setdefault("bid", spreads[0])
    if len(spreads) > 1:
        entities.setdefault("offer", spreads[1])

    # Payment frequency
    freq_match = FREQUENCY_RE.search(text)
    if freq_match:
        entities.setdefault("payment_frequency", freq_match.group(1))

    return ChatEntities(**entities)
