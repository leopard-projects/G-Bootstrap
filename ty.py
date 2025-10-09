import os
import pickle
import json
import argparse
from pathlib import Path
import boto3
import javalang
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

# ─────────────────────────────
# 1️⃣ Bedrock Client Setup
# ─────────────────────────────
def get_bedrock_client(region="us-east-1"):
    return boto3.client("bedrock-runtime", region_name=region)


# ─────────────────────────────
# 2️⃣ Titan Embedding using invoke_model
# ─────────────────────────────
def get_titan_embedding(client, text: str):
    body = json.dumps({"inputText": text})
    response = client.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=body
    )
    result = json.loads(response["body"].read())
    return np.array(result["embedding"])


# ─────────────────────────────
# 3️⃣ Parse Java Files with AST
# ─────────────────────────────
def parse_java_ast(java_code, file_path):
    try:
        tree = javalang.parse.parse(java_code)
        classes = [cls.name for cls in tree.types if hasattr(cls, "name")]
        imports = [imp.path for imp in tree.imports]
        methods = [node.name for _, node in tree.filter(javalang.tree.MethodDeclaration)]
        fields = [
            decl.name
            for _, node in tree.filter(javalang.tree.FieldDeclaration)
            for decl in node.declarators
        ]
        summary = f"""
        File: {file_path}
        Classes: {classes}
        Imports: {imports}
        Methods: {methods}
        Fields: {fields}
        """
        return summary.strip()
    except Exception as e:
        print(f"⚠️ AST parse failed for {file_path}: {e}")
        return java_code[:2000]


# ─────────────────────────────
# 4️⃣ Build or Load Vectorstore
# ─────────────────────────────
def build_or_load_vectorstore(source_path, pkl_path, client):
    if os.path.exists(pkl_path):
        print(f"📂 Loading existing FAISS vectorstore from {pkl_path}")
        with open(pkl_path, "rb") as f:
            return pickle.load(f)

    print("🚀 Building FAISS vectorstore with Titan embeddings...")
    docs, texts, embeddings = [], [], []

    for path in Path(source_path).rglob("*.java"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read().strip()
                if code:
                    summary = parse_java_ast(code, str(path))
                    embedding = get_titan_embedding(client, summary)
                    docs.append(Document(page_content=summary, metadata={"source": str(path)}))
                    texts.append(summary)
                    embeddings.append(embedding)
        except Exception as e:
            print(f"⚠️ Skipping {path}: {e}")

    embeddings = np.vstack(embeddings)
    vectorstore = FAISS.from_embeddings(list(zip(texts, embeddings)))

    with open(pkl_path, "wb") as f:
        pickle.dump(vectorstore, f)

    print(f"✅ Vectorstore saved to {pkl_path}")
    return vectorstore


# ─────────────────────────────
# 5️⃣ Claude Query with Context Chain
# ─────────────────────────────
def query_claude(client, messages, temperature=0.3, max_tokens=1024):
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages
    })

    response = client.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=body
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


# ─────────────────────────────
# 6️⃣ Context Chaining Logic
# ─────────────────────────────
def context_chain_query(client, vectorstore, query, chain_depth=3):
    query_embedding = get_titan_embedding(client, query)
    retrieved_docs = vectorstore.similarity_search_by_vector(query_embedding, k=5)

    # Initialize conversation history
    messages = [{"role": "user", "content": query}]
    aggregated_context = ""

    for i in range(min(chain_depth, len(retrieved_docs))):
        doc = retrieved_docs[i]
        context = doc.page_content
        aggregated_context += f"\n\nContext {i+1}:\n{context}"

        # Ask Claude with previous answers + new context
        prompt = f"""
Use the following context to improve or extend your previous reasoning.
Query: {query}
Context chunk {i+1}:
{context}

Previous answer (if any):
{messages[-1]['content'] if len(messages) > 1 else 'N/A'}

Provide an improved, merged, and context-aware response.
"""
        messages.append({"role": "user", "content": prompt})
        answer = query_claude(client, messages)
        messages.append({"role": "assistant", "content": answer})

    final_answer = messages[-1]["content"]
    return final_answer, [d.metadata.get("source", "unknown file") for d in retrieved_docs]


# ─────────────────────────────
# 7️⃣ Entry: Query from Text File
# ─────────────────────────────
def run_query_from_file(query_file, vectorstore, client):
    with open(query_file, "r", encoding="utf-8") as f:
        query = f.read().strip()
    if not query:
        raise ValueError("Empty query file")

    print(f"\n💬 Query: {query}\n")

    answer, sources = context_chain_query(client, vectorstore, query)

    print("🧠 Claude Final Answer:\n", answer)
    print("\n📚 Context Sources:")
    for s in sources:
        print("-", s)


# ─────────────────────────────
# 8️⃣ Main
# ─────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Titan + Claude Context Chain via invoke_model")
    parser.add_argument("--source", required=True, help="Java project path")
    parser.add_argument("--pkl", default="titan_ast_embeddings.pkl", help="Pickle for FAISS store")
    parser.add_argument("--query", required=True, help="Text file with query")
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    args = parser.parse_args()

    client = get_bedrock_client(args.region)
    vectorstore = build_or_load_vectorstore(args.source, args.pkl, client)
    run_query_from_file(args.query, vectorstore, client)


if __name__ == "__main__":
    main()