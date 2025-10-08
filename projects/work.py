#!/usr/bin/env python3
"""
java_bedrock_rag_full.py

Load Java AST/code embeddings from a .pkl (FAISS/LangChain format) and perform RAG using Claude on Bedrock.

Usage:
    python java_bedrock_rag_full.py path/to/java_embeddings.pkl
"""

import os
import sys
import pickle
import json
import numpy as np
import boto3
from typing import List

from langchain.schema import Document
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain.llms.base import LLM
from langchain.chains import ConversationalRetrievalChain

# ---------------- Configuration ----------------
REGION = "us-east-1"
CLAUDE_MODEL = "anthropic.claude-3-sonnet-20240229-v1:0"
RETRIEVE_TOP_K = 4

bedrock = boto3.client("bedrock-runtime", region_name=REGION)

# ---------------- LLM Wrapper ----------------
class ClaudeLLM(LLM):
    """LangChain wrapper for Claude on Bedrock."""
    model_id: str = CLAUDE_MODEL

    def _call(self, prompt: str, stop=None) -> str:
        body = json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 1000,
            "temperature": 0.2
        })
        resp = bedrock.invoke_model(modelId=self.model_id, body=body)
        result = json.loads(resp['body'].read())
        return result.get("completion", "")

    @property
    def _identifying_params(self):
        return {"model_id": self.model_id}

    @property
    def _llm_type(self):
        return "bedrock_claude"


# ---------------- Dummy Embeddings Wrapper ----------------
class TitanEmbeddingStub(Embeddings):
    """Required for FAISS, we use precomputed embeddings."""
    def embed_documents(self, texts: List[str]):
        raise NotImplementedError
    def embed_query(self, text: str):
        raise NotImplementedError


# ---------------- Load Java Embeddings (.pkl) ----------------
def load_java_embeddings(pkl_path: str):
    """
    Handles .pkl saved in FAISS/LangChain dict format:
    {'documents': [...], 'last_updated': ...}
    Each document must have 'page_content' and 'embedding'.
    """
    print(f"📦 Loading Java embeddings from: {pkl_path}")
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)

    if isinstance(data, dict) and "documents" in data:
        texts = []
        embeddings = []
        for i, doc in enumerate(data["documents"]):
            page_content = getattr(doc, "page_content", None) or doc.get("page_content", None)
            emb = getattr(doc, "embedding", None) or doc.get("embedding", None)
            if page_content is None or emb is None:
                print(f"⚠️ Skipping document {i}, missing text or embedding")
                continue
            texts.append(page_content)
            embeddings.append(emb)
    else:
        raise ValueError(f"Unsupported .pkl structure: {data.keys() if isinstance(data, dict) else type(data)}")

    embeddings = np.array(embeddings, dtype=np.float32)
    print(f"✅ Loaded {len(texts)} documents with embedding dim={embeddings.shape[1]}")
    docs = [Document(page_content=t) for t in texts]
    return docs, embeddings


# ---------------- Build FAISS Vectorstore ----------------
def build_vectorstore(docs, embeddings):
    print("🔧 Building FAISS vectorstore from precomputed embeddings...")
    store = FAISS.from_embeddings(
        embeddings=embeddings,
        documents=docs,
        embedding=TitanEmbeddingStub()
    )
    return store


# ---------------- Build Context Chain ----------------
def build_context_chain(vectorstore):
    llm = ClaudeLLM()
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    retriever = vectorstore.as_retriever(search_kwargs={"k": RETRIEVE_TOP_K})
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True
    )
    return chain


# ---------------- Main ----------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python java_bedrock_rag_full.py path/to/java_embeddings.pkl")
        sys.exit(1)

    pkl_path = sys.argv[1]
    if not os.path.exists(pkl_path):
        print(f"❌ File not found: {pkl_path}")
        sys.exit(1)

    docs, embeddings = load_java_embeddings(pkl_path)
    vectorstore = build_vectorstore(docs, embeddings)
    chain = build_context_chain(vectorstore)

    print("\n🤖 Claude is ready to answer questions using Java code embeddings!")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("You: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("👋 Exiting.")
            break
        try:
            result = chain({"question": query})
            print(f"\nClaude:\n{result['answer']}\n")
        except Exception as e:
            print(f"⚠️ Error during query: {e}\n")


if __name__ == "__main__":
    main()