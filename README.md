# ADOR — Augmented Document Reader

Extracts financial entities from chat (.txt), term sheet (.docx), and PDF documents.

## Setup

```bash
pip install -r requirements.txt
```

For PDF extraction, create a `.env` file with your OpenAI key:

```
OPENAI_API_KEY=your-key-here
```

## Run

```bash
# Start the API
uvicorn src.api:app

# Start the UI (in another terminal)
python -m streamlit run ui/app.py
```

