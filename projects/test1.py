#!/usr/bin/env python3
"""
bedrock_titan_contextchain_from_pkl_fixed.py
--------------------------------------------
Load precomputed Titan embeddings from a .pkl file and use them
to create a LangChain ConversationalRetrievalChain with Claude on Bedrock.
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

# ---------- Config ----------
REGION = "us-east-1"
CLAUDE_MODEL = "anthropic.claude-3-sonnet-20240229-v1:0"
bedrock = boto3.client(service_name="bedrock-runtime", region_name=REGION)

# ---------- Claude LLM ----------
class ClaudeLLM(LLM):
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

# ---------- Dummy Embeddings (for FAISS) ----------
class TitanEmbeddingLoader(Embeddings):
    def embed_documents(self, texts: List[str]): raise NotImplementedError
    def embed_query(self, text: str): raise NotImplementedError

# ---------- Load PKL ----------
def load_pkl_embeddings(pkl_path: str):
    print(f"Loading PKL from: {pkl_path}")
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)

    print(f"Loaded PKL type: {type(data)}")

    texts, embeddings = None, None

    # Case 1: dict with "texts" and "embeddings"
    if isinstance(data, dict) and "texts" in data and "embeddings" in data:
        texts = data["texts"]
        embeddings = np.array(data["embeddings"], dtype=np.float32)

    # Case 2: list of dicts (each with "text" and "embedding")
    elif isinstance(data, list) and all(isinstance(d, dict) for d in data):
        texts, embs = [], []
        for i, d in enumerate(data):
            t = d.get("text") or d.get("content") or ""
            e = d.get("embedding") or d.get("vector") or None
            if t and e:
                texts.append(t)
                embs.append(e)
            else:
                print(f"⚠️ Skipping item {i}: missing text or embedding.")
        embeddings = np.array(embs, dtype=np.float32)

    # Case 3: Unexpected structure
    else:
        print("❌ Unsupported PKL structure. Example expected format:")
        print("""
{
  "texts": ["doc1 text", "doc2 text"],
  "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]]
}
OR
[
  {"text": "doc1 text", "embedding": [0.1, 0.2, ...]},
  {"text": "doc2 text", "embedding": [0.3, 0.4, ...]}
]
""")
        raise ValueError("Unsupported PKL structure")

    print(f"✅ Loaded {len(texts)} documents with embedding dim = {len(embeddings[0])}")
    docs = [Document(page_content=t) for t in texts]
    return docs, embeddings

# ---------- Build FAISS ----------
def build_vectorstore(docs, embeddings):
    print("Building FAISS index in memory...")
    store = FAISS.from_embeddings(
        embeddings=embeddings,
        documents=docs,
        embedding=TitanEmbeddingLoader()
    )
    return store

# ---------- Build Conversational Chain ----------
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

# ---------- Main ----------
def main():
    if len(sys.argv) < 2:
        print("Usage: python bedrock_titan_contextchain_from_pkl_fixed.py path/to/embeddings.pkl")
        sys.exit(1)

    pkl_path = sys.argv[1]
    if not os.path.exists(pkl_path):
        print(f"❌ File not found: {pkl_path}")
        sys.exit(1)

    docs, embeddings = load_pkl_embeddings(pkl_path)
    vectorstore = build_vectorstore(docs, embeddings)
    chain = build_context_chain(vectorstore)

    print("\n✅ Titan embedding context chain ready. Type your questions below.")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("You: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("Goodbye 👋")
            break

        try:
            result = chain({"question": query})
            print(f"\nClaude: {result['answer']}\n")
        except Exception as e:
            print(f"⚠️ Error during query: {e}\n")

if __name__ == "__main__":
    main()