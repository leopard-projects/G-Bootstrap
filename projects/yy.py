#!/usr/bin/env python3
"""
java_knowledgebase_query_option2.py

Load Java AST/code embeddings from a .pkl and perform RAG queries using Claude on Bedrock.
Uses precomputed embeddings via (text, embedding) tuples with FAISS.from_embeddings.

Usage:
    python java_knowledgebase_query_option2.py path/to/java_embeddings.pkl
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
    """Required for FAISS; we use precomputed embeddings."""
    def embed_documents(self, texts: List[str]):
        raise NotImplementedError
    def embed_query(self, text: str):
        raise NotImplementedError

# ---------------- Load Knowledge Base ----------------
def load_knowledge_base(pkl_path: str):
    """
    Load a .pkl Java embedding file (FAISS/LangChain-style) and extract texts + embeddings.
    Flexible for keys: page_content/text/code/content, embedding/vector.
    Returns: docs (Document list), embeddings (np.ndarray)
    """
    print(f"📦 Loading Java embeddings from: {pkl_path}")
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)

    if isinstance(data, dict) and "documents" in data:
        docs = []
        embeddings = []
        for i, doc in enumerate(data["documents"]):
            # Flexible key handling
            text = (
                getattr(doc, "page_content", None)
                or getattr(doc, "text", None)
                or getattr(doc, "code", None)
                or getattr(doc, "content", None)
                or doc.get("page_content")
                or doc.get("text")
                or doc.get("code")
                or doc.get("content")
            )

            emb = (
                getattr(doc, "embedding", None)
                or getattr(doc, "vector", None)
                or doc.get("embedding")
                or doc.get("vector")
            )

            if text is None or emb is None:
                print(f"⚠️ Skipping document {i}: missing text or embedding")
                continue

            docs.append(Document(page_content=text))
            embeddings.append(np.array(emb, dtype=np.float32))

        print(f"✅ Loaded {len(docs)} documents with embeddings, dim={embeddings[0].shape[0] if embeddings else 0}")
        return docs, embeddings
    else:
        raise ValueError(f"Unsupported .pkl structure: {type(data)}")

# ---------------- Build FAISS Vectorstore ----------------
def build_vectorstore(docs, embeddings):
    """
    Build FAISS vectorstore using (text, embedding) tuples.
    """
    print("🔧 Building FAISS vectorstore from precomputed embeddings...")
    text_embedding_tuples = [(doc.page_content, emb) for doc, emb in zip(docs, embeddings)]
    store = FAISS.from_embeddings(
        text_embeddings=text_embedding_tuples,
        embedding=TitanEmbeddingStub()
    )
    print("✅ FAISS vectorstore built.")
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
        print("Usage: python java_knowledgebase_query_option2.py path/to/java_embeddings.pkl")
        sys.exit(1)

    pkl_path = sys.argv[1]
    if not os.path.exists(pkl_path):
        print(f"❌ File not found: {pkl_path}")
        sys.exit(1)

    # Load knowledge base
    docs, embeddings = load_knowledge_base(pkl_path)

    # Build vectorstore using precomputed embeddings
    vectorstore = build_vectorstore(docs, embeddings)

    # Build context chain
    chain = build_context_chain(vectorstore)

    print("\n🤖 Claude is ready to answer questions using the Java knowledge base.")
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