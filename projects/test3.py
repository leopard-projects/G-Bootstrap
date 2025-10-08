#!/usr/bin/env python3
"""
java_bedrock_rag.py

Load Java AST/code embeddings (from .pkl) and perform RAG using Claude on Bedrock.

Usage:
    python java_bedrock_rag.py path/to/java_embeddings.pkl
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


# ---------------- Load Java AST / Code Embeddings ----------------
def load_java_embeddings(pkl_path: str):
    """
    Supported formats:
    1) List of dicts: [{"code"/"ast"/"snippet": "...", "embedding": [...], "metadata": {...}}]
    2) Dict: {"snippets": [...], "embeddings": [[...], ...]}
    """
    print(f"📦 Loading Java embeddings from {pkl_path}")
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)

    texts, embeddings = [], []

    # List of dicts
    if isinstance(data, list):
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                print(f"⚠️ Skipping non-dict item {i}")
                continue
            text = item.get("code") or item.get("ast") or item.get("snippet") or item.get("source") or item.get("text")
            emb = item.get("embedding") or item.get("vector")
            if text and emb:
                texts.append(text)
                embeddings.append(emb)
            else:
                print(f"⚠️ Missing text or embedding at index {i}, skipping")
    # Dict format
    elif isinstance(data, dict):
        text_key = next((k for k in ["snippets", "codes", "sources", "texts"] if k in data), None)
        emb_key = next((k for k in ["embeddings", "vectors"] if k in data), None)
        if text_key and emb_key:
            texts = data[text_key]
            embeddings = data[emb_key]
        else:
            raise ValueError(f"Cannot detect text/embedding keys in {list(data.keys())}")
    else:
        raise ValueError(f"Unsupported PKL type: {type(data)}")

    embeddings = np.array(embeddings, dtype=np.float32)
    print(f"✅ Loaded {len(texts)} code embeddings, dim={embeddings.shape[1]}")
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
        print("Usage: python java_bedrock_rag.py path/to/java_embeddings.pkl")
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