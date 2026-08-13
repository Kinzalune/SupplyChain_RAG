import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "supply_chain"

def run_ingestion():
    pdf_files = glob.glob("./data/*.pdf")
    if not pdf_files:
        print("No PDFs found in data/ directory.")
        return

    documents = []
    for pdf_path in pdf_files:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        filename = os.path.basename(pdf_path)
        for doc in docs:
            doc.metadata["source"] = filename
        documents.extend(docs)

    # 1200 chars keeps tables, scorecards, and policy clauses intact
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH
    )

    print(f"Processed {len(pdf_files)} files into {len(chunks)} chunks.")

if __name__ == "__main__":
    run_ingestion()