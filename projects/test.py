#!/usr/bin/env python3
"""
bedrock_titan_contextchain_from_pkl.py
--------------------------------------
Load precomputed Titan embeddings from a .pkl file and build a LangChain
ConversationalRetrievalChain using Claude on Bedrock.

Usage:
    python bedrock_titan_contextchain_from_pkl.py path/to/embeddings.pkl
"""

import os
import sys
import json
import pickle
import boto3
import numpy as np
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

bedrock = boto3.client(service_name="bedrock-runtime", region_name=REGION)


# ---------------- LLM Wrapper ----------------

class ClaudeLLM(LLM):
    """LangChain-compatible wrapper for Claude on Bedrock."""
    model_id: str = CLAUDE_MODEL

    def _call(self, prompt: str, stop=None) -> str:
        body = json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 800,
            "temperature": 0.2
        })
        response = bedrock.invoke_model(modelId=self.model_id, body=body)
        result = json.loads(response["body"].read())
        return result.get("completion", "")

    @property
    def _identifying_params(self):
        return {"model_id": self.model_id}

    @property
    def _llm_type(self):
        return "bedrock_claude"


# ---------------- Dummy Embedding Wrapper ----------------

class TitanEmbeddingLoader(Embeddings):
    """
    Placeholder embeddings class — required by LangChain for FAISS.
    Since embeddings are already precomputed in .pkl, we don't call Titan again.
    """
    def __init__(self):
        pass

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("Precomputed embeddings are used instead.")

    def embed_query(self, text: str) -> List[float]:
        raise NotImplementedError("Precomputed embeddings are used instead.")


# ---------------- Load Precomputed Embeddings ----------------

def load_pkl_embeddings(pkl_path: str):
    """
    Expected .pkl format:
    {
        "texts": [ "text1", "text2", ... ],
        "embeddings": [ [float, float, ...], ... ]
    }
    or a list of dicts like: [ {"text": ..., "embedding": [...]}, ... ]
    """
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)

    if isinstance(data, dict) and "texts" in data and "embeddings" in data:
        texts = data["texts"]
        embeddings = np.array(data["embeddings"]).astype("float32")
    elif isinstance(data, list) and all(isinstance(d, dict) and "embedding" in d for d in data):
        texts = [d.get("text") or d.get("content", "") for d in data]
        embeddings = np.array([d["embedding"] for d in data]).astype("float32")
    else:
        raise ValueError("Unsupported PKL structure. Expected dict with 'texts' and 'embeddings' or list of dicts.")

    docs = [Document(page_content=t) for t in texts]
    return docs, embeddings


# ---------------- Build FAISS Vectorstore ----------------

def build_vectorstore_from_embeddings(docs, embeddings):
    """Manually create FAISS store using given embeddings."""
    dim = len(embeddings[0])
    index = FAISS.from_embeddings(
        embeddings=embeddings,
        documents=docs,
        embedding=TitanEmbeddingLoader()
    )
    return index


# ---------------- Build Context Chain ----------------

def build_context_chain(vectorstore):
    llm = ClaudeLLM()
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
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
        print("Usage: python bedrock_titan_contextchain_from_pkl.py path/to/embeddings.pkl")
        sys.exit(1)

    pkl_path = sys.argv[1]
    if not os.path.exists(pkl_path):
        print(f"Error: File not found: {pkl_path}")
        sys.exit(1)

    print(f"Loading precomputed Titan embeddings from {pkl_path}...")
    docs, embeddings = load_pkl_embeddings(pkl_path)
    print(f"Loaded {len(docs)} documents, embedding dim = {len(embeddings[0])}")

    vectorstore = build_vectorstore_from_embeddings(docs, embeddings)
    chain = build_context_chain(vectorstore)

    print("\n✅ Knowledge base ready. You can now chat with Claude using this context.")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("You: ").strip()
        if not query or query.lower() in ["exit", "quit"]:
            print("Goodbye 👋")
            break

        result = chain({"question": query})
        answer = result["answer"]
        print(f"\nClaude: {answer}\n")


if __name__ == "__main__":
    main()