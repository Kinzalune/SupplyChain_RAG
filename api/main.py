import os
import tempfile
from typing import List
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from ingest import run_ingestion, CHROMA_PATH, COLLECTION_NAME
from rag import ask_rag
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

app = FastAPI(title="Supply Chain RAG API", version="1.0")

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
    return {"message": "Files successfully ingested"}

@app.post("/ask")
async def ask_question(req: QuestionRequest):
    return ask_rag(req.question, top_k=req.top_k)

@app.get("/stats")
async def get_stats():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    total_chunks = vectorstore._collection.count()
    
    return {
        "collection_name": COLLECTION_NAME,
        "total_chunks": total_chunks,
        "embedding_model": "text-embedding-3-small",
        "llm_model": "gpt-4o"
    }