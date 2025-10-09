#!/usr/bin/env python3
"""
rag_titan_claude_ast_pipeline_fixed.py

End-to-end:
  1️⃣ Parse Java code using AST (via javalang)
  2️⃣ Generate Titan embeddings via AWS Bedrock
  3️⃣ Save to .pkl
  4️⃣ Query .pkl using Claude RAG chain (LangChain)
"""

import os
import sys
import json
import pickle
import argparse
import boto3
import numpy as np
import javalang
from pathlib import Path
from langchain.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain_community.llms.bedrock import Bedrock


# ---------- AWS + Models ----------
REGION = os.environ.get("AWS_REGION", "us-east-1")
TITAN_MODEL = os.environ.get("TITAN_MODEL", "amazon.titan-embed-text-v1")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0")

bedrock = boto3.client("bedrock-runtime", region_name=REGION)


# ---------- Titan Embedding Wrapper ----------
class BedrockTitanEmbeddings(Embeddings):
    """Titan embedding wrapper for LangChain."""
    def __init__(self, model_id: str = TITAN_MODEL):
        self.model_id = model_id

    def _embed(self, text: str):
        text = text.strip()
        if not text:
            raise ValueError("Cannot embed empty text.")
        body = json.dumps({"inputText": text}).encode("utf-8")
        resp = bedrock.invoke_model(modelId=self.model_id, body=body)
        data = resp["body"].read()
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        result = json.loads(data)
        emb = result.get("embedding") or (result.get("embeddings")[0] if "embeddings" in result else None)
        if emb is None:
            raise ValueError(f"Malformed Titan response: {result}")
        return emb

    def embed_documents(self, texts):
        return [self._embed(t) for t in texts]

    def embed_query(self, text):
        return self._embed(text)


# ---------- Claude LLM ----------
def get_claude_llm(model_id: str = CLAUDE_MODEL):
    return Bedrock(
        model_id=model_id,
        region_name=REGION,
        model_kwargs={
            "max_tokens_to_sample": 1500,
            "temperature": 0.3
        }
    )


# ---------- Java Parser ----------
def extract_java_code_units(source_dir: str):
    """Parse Java files and extract class & method signatures."""
    code_units = []
    java_files = list(Path(source_dir).rglob("*.java"))

    for jf in java_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                code = f.read()
            tree = javalang.parse.parse(code)
            for path, node in tree:
                if isinstance(node, javalang.tree.ClassDeclaration):
                    snippet = f"class {node.name}"
                    code_units.append({"path": str(jf), "type": "class", "text": snippet})
                elif isinstance(node, javalang.tree.MethodDeclaration):
                    params = ", ".join([p.type.name for p in node.parameters]) if node.parameters else ""
                    snippet = f"method {node.name}({params})"
                    code_units.append({"path": str(jf), "type": "method", "text": snippet})
        except Exception as e:
            print(f"⚠️ Failed to parse {jf}: {e}")

    print(f"✅ Extracted {len(code_units)} code units from {len(java_files)} files.")
    return code_units


# ---------- Titan Embedding Generation ----------
def create_titan_embeddings(code_units, embedder):
    embeddings = []
    texts = []
    metadata = []

    for unit in code_units:
        text = unit["text"]
        emb = embedder._embed(text)
        embeddings.append(emb)
        texts.append(text)
        metadata.append({"path": unit["path"], "type": unit["type"]})

    print(f"✅ Created {len(embeddings)} Titan embeddings.")
    return {"documents": texts, "embeddings": embeddings, "metadata": metadata}


# ---------- Save/Load Embeddings ----------
def save_embeddings_pickle(data, output_path):
    with open(output_path, "wb") as f:
        pickle.dump(data, f)
    print(f"💾 Saved embeddings to {output_path}")


def load_embeddings_pickle(pkl_path):
    print(f"📦 Loading embeddings from: {pkl_path}")
    with open(pkl_path, "rb") as f:
        kb = pickle.load(f)
    docs = kb["documents"]
    embeds = kb["embeddings"]
    meta = kb["metadata"]
    print(f"✅ Loaded {len(docs)} documents from pickle.")
    return docs, embeds, meta


# ---------- Build FAISS Vectorstore ----------
def build_vectorstore(docs, embedder, metadata):
    print("🧠 Building FAISS in-memory vectorstore...")
    store = FAISS.from_texts(texts=docs, embedding=embedder, metadatas=metadata)
    print(f"✅ Vectorstore ready with {len(docs)} entries.")
    return store


# ---------- Build RAG Chain ----------
def build_rag_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    llm = get_claude_llm()
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        memory=memory,
        verbose=True
    )
    return qa


# ---------- Main ----------
def main():
    parser = argparse.ArgumentParser(description="Titan + Claude RAG pipeline for Java code using AST and Bedrock.")
    parser.add_argument("--index", action="store_true", help="Index Java project and create embeddings.")
    parser.add_argument("--query", action="store_true", help="Query existing embeddings.")
    parser.add_argument("--src", type=str, help="Source code directory for indexing.")
    parser.add_argument("--out", type=str, help="Output .pkl file for embeddings.")
    parser.add_argument("--pkl", type=str, help="Path to .pkl file for querying.")
    parser.add_argument("--query-file", type=str, help="Path to .txt file containing natural-language query.")
    args = parser.parse_args()

    embedder = BedrockTitanEmbeddings()

    if args.index:
        if not args.src or not args.out:
            print("❌ Please specify --src and --out for indexing.")
            sys.exit(1)
        code_units = extract_java_code_units(args.src)
        kb = create_titan_embeddings(code_units, embedder)
        save_embeddings_pickle(kb, args.out)

    elif args.query:
        if not args.pkl or not args.query_file:
            print("❌ Please specify --pkl and --query-file for querying.")
            sys.exit(1)

        with open(args.query_file, "r", encoding="utf-8") as f:
            query = f.read().strip()
        if not query:
            print("❌ Query file is empty.")
            sys.exit(1)

        print(f"\n🔍 Query:\n{query}\n")
        docs, embeds, meta = load_embeddings_pickle(args.pkl)
        store = build_vectorstore(docs, embedder, meta)
        chain = build_rag_chain(store)

        print("\n🚀 Running RAG query with Claude...\n")
        result = chain.invoke({"query": query})

        print("\n=== 🧠 Claude Answer ===\n")
        print(result.get("result") or result)

    else:
        print("❌ Must specify either --index or --query.")
        sys.exit(1)


if __name__ == "__main__":
    main()