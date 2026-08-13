import streamlit as st
import os
import tempfile
from ingest import run_ingestion
from rag import ask_rag

st.set_page_config(page_title="Meridian Supply Chain Assistant", layout="wide")
st.title("📦 Meridian Supply Chain Intelligence Assistant")

# Sidebar - Document Ingestion
st.sidebar.header("Document Ingestion")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDFs", 
    type=["pdf"], 
    accept_multiple_files=True
)

if st.sidebar.button("Index Documents"):
    if uploaded_files:
        temp_dir = "./data"
        os.makedirs(temp_dir, exist_ok=True)
        
        saved_paths = []
        for file in uploaded_files:
            file_path = os.path.join(temp_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            saved_paths.append(file_path)
            
        run_ingestion()
        st.sidebar.success("Documents processed and saved to ChromaDB.")
    else:
        st.sidebar.warning("Please upload at least one PDF file.")

# Main UI - QA System
st.subheader("Ask a Question")
question = st.text_input("Enter your policy or supply chain question:")

if st.button("Submit Question") and question:
    with st.spinner("Retrieving facts..."):
        try:
            result = ask_rag(question)
            
            st.markdown("### Answer")
            st.write(result["answer"])
            
            st.markdown("### Sources Referenced")
            for src in result["sources"]:
                st.markdown(f"- **Document:** `{src['file']}` | **Page:** {src['page']}")
        except Exception as e:
            st.error(f"Error executing query: {e}")