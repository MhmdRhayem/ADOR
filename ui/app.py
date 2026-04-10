"""Streamlit UI for ADOR — upload documents and view extracted entities."""

import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="ADOR — Augmented Document Reader", layout="wide")
st.title("ADOR — Augmented Document Reader")
st.markdown("Upload a financial document to extract named entities.")

uploaded_file = st.file_uploader(
    "Choose a file",
    type=["txt", "docx", "pdf"],
    help="Supported formats: .txt (chat), .docx (term sheet), .pdf (verbose document)",
)

if uploaded_file is not None:
    st.divider()
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Document Info")
        st.write(f"**Filename:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
        st.write(f"**Type:** {uploaded_file.type}")

    with col2:
        with st.spinner("Extracting entities..."):
            try:
                response = requests.post(
                    f"{API_URL}/extract",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue())},
                    timeout=30,
                )
                response.raise_for_status()
                result = response.json()

                st.subheader("Extracted Entities")
                st.write(f"**Document type:** {result['doc_type']}")

                entities = result["entities"]

                # PDF entities are nested under "entities" key
                if result["doc_type"] == "pdf" and "entities" in entities:
                    entities = entities["entities"]

                # Display as a clean table
                table_data = {
                    "Entity": [],
                    "Value": [],
                }
                for key, value in entities.items():
                    if value is not None:
                        table_data["Entity"].append(key.replace("_", " ").title())
                        table_data["Value"].append(str(value))

                st.table(table_data)

                # Raw JSON expandable
                with st.expander("Raw JSON Response"):
                    st.json(result)

            except requests.ConnectionError:
                st.error(
                    "Could not connect to the API. "
                    "Make sure the FastAPI server is running: `uvicorn src.api:app`"
                )
            except requests.HTTPError as e:
                st.error(f"API error: {e.response.text}")
