import os
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import Chroma

load_dotenv()

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "supply_chain"

SYSTEM_PROMPT = """Answer only from the context provided below. If the context does not contain the answer, say the information is not available in the uploaded documents.

Context:
{context}"""

def ask_rag(question: str, top_k: int = 6):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )

    docs = vectorstore.similarity_search(question, k=top_k)

    context_parts = []
    sources = []
    for doc in docs:
        src = doc.metadata.get("source", "Unknown")
        pg = doc.metadata.get("page", 0) + 1
        context_parts.append(f"[Document: {src}, Page: {pg}]\n{doc.page_content}")
        
        src_dict = {"file": src, "page": pg}
        if src_dict not in sources:
            sources.append(src_dict)

    context_text = "\n\n---\n\n".join(context_parts)

    llm = ChatOllama(model="llama3.2", temperature=0.1)
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(context=context_text)},
        {"role": "user", "content": question}
    ]

    response = llm.invoke(messages)

    return {
        "answer": response.content,
        "sources": sources
    }