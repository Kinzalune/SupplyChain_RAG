import os
from typing import List
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from ingest import run_ingestion, CHROMA_PATH, COLLECTION_NAME
from rag import ask_rag
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

app = FastAPI(
    title="Supply Chain RAG API",
    description="Local RAG API powered by Ollama and ChromaDB",
    version="1.0"
)

class QuestionRequest(BaseModel):
    question: str
    top_k: int = 6

@app.post("/ingest")
async def ingest_files(files: List[UploadFile] = File(...)):
    temp_dir = "./data"
    os.makedirs(temp_dir, exist_ok=True)
    
    for file in files:
        contents = await file.read()
        with open(os.path.join(temp_dir, file.filename), "wb") as f:
            f.write(contents)
            
    run_ingestion()
    return {"message": f"Successfully ingested {len(files)} files into ChromaDB."}

@app.post("/ask")
async def ask_question(req: QuestionRequest):
    return ask_rag(req.question, top_k=req.top_k)

@app.get("/stats")
async def get_stats():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    total_chunks = vectorstore._collection.count()
    
    return {
        "collection_name": COLLECTION_NAME,
        "total_chunks": total_chunks,
        "embedding_model": "nomic-embed-text",
        "llm_model": "llama3.2"
    }