#!/usr/bin/env python3
"""
bedrock_titan_ast_code_contextchain.py
--------------------------------------
Reads precomputed Titan embeddings of Java AST/code (in .pkl format)
and builds a LangChain ConversationalRetrievalChain using Claude on Bedrock.

Usage:
    python bedrock_titan_ast_code_contextchain.py path/to/java_ast_embeddings.pkl
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

# ---------- Configuration ----------
REGION = "us-east-1"
CLAUDE_MODEL = "anthropic.claude-3-sonnet-20240229-v1:0"
bedrock = boto3.client("bedrock-runtime", region_name=REGION)


# ---------- Claude LLM Wrapper ----------
class ClaudeLLM(LLM):
    model_id: str = CLAUDE_MODEL

    def _call(self, prompt: str, stop=None) -> str:
        body = json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 1000,
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


# ---------- Dummy Titan Embedding Wrapper ----------
class TitanEmbeddingStub(Embeddings):
    def embed_documents(self, texts: List[str]): raise NotImplementedError
    def embed_query(self, text: str): raise NotImplementedError


# ---------- Load PKL with AST or Code ----------
def load_ast_embeddings(pkl_path: str):
    """
    Supported formats:
    [
      {"code": "public class Foo {...}", "embedding": [...], "metadata": {...}},
      {"source": "...", "embedding": [...]},
      {"ast": "...", "embedding": [...]}
    ]
    OR
    {"snippets": [...], "embeddings": [...]}
    """
    print(f"📦 Loading AST embeddings from: {pkl_path}")
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)

    texts, embeddings = [], []

    # Case 1: list of dicts
    if isinstance(data, list):
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                print(f"⚠️ Skipping non-dict entry at index {i}")
                continue

            text = (
                item.get("code")
                or item.get("source")
                or item.get("snippet")
                or item.get("ast")
                or item.get("text")
            )
            emb = item.get("embedding") or item.get("vector")

            if text and emb:
                texts.append(text)
                embeddings.append(emb)
            else:
                print(f"⚠️ Missing code or embedding at index {i}, skipping.")

    # Case 2: dict with separate lists
    elif isinstance(data, dict):
        keys = data.keys()
        possible_text_keys = ["snippets", "codes", "sources", "texts"]
        text_key = next((k for k in possible_text_keys if k in keys), None)
        emb_key = "embeddings" if "embeddings" in keys else "vectors" if "vectors" in keys else None

        if text_key and emb_key:
            texts = data[text_key]
            embeddings = data[emb_key]
        else:
            raise ValueError(f"Could not find text or embedding keys in {keys}")

    else:
        raise ValueError(f"❌ Unsupported PKL format type: {type(data)}")

    embeddings = np.array(embeddings, dtype=np.float32)
    print(f"✅ Loaded {len(texts)} code embeddings, dim={embeddings.shape[1]}")
    docs = [Document(page_content=code) for code in texts]
    return docs, embeddings


# ---------- Build Vectorstore ----------
def build_vectorstore(docs, embeddings):
    print("🔧 Building FAISS index for Java code embeddings...")
    store = FAISS.from_embeddings(
        embeddings=embeddings,
        documents=docs,
        embedding=TitanEmbeddingStub()
    )
    return store


# ---------- Build Conversational RAG Chain ----------
def build_code_context_chain(vectorstore):
    llm = ClaudeLLM()
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
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
        print("Usage: python bedrock_titan_ast_code_contextchain.py path/to/java_ast_embeddings.pkl")
        sys.exit(1)

    pkl_path = sys.argv[1]
    if not os.path.exists(pkl_path):
        print(f"❌ File not found: {pkl_path}")
        sys.exit(1)

    docs, embeddings = load_ast_embeddings(pkl_path)
    vectorstore = build_vectorstore(docs, embeddings)
    chain = build_code_context_chain(vectorstore)

    print("\n🤖 Claude is ready to answer about your Java code embeddings.")
    print("Ask migration or refactoring questions. Type 'exit' to quit.\n")

    while True:
        query = input("You: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("👋 Exiting.")
            break

        try:
            result = chain({"question": query})
            print(f"\nClaude:\n{result['answer']}\n")
        except Exception as e:
            print(f"⚠️ Error: {e}\n")


if __name__ == "__main__":
    main()