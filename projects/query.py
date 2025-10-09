import os
import pickle
import argparse
from pathlib import Path
import boto3
import javalang

from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Bedrock
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document


# ─────────────────────────────
# 1️⃣ Create Titan Embedding Model Wrapper
# ─────────────────────────────
def get_titan_embeddings(region="us-east-1"):
    bedrock_client = boto3.client("bedrock-runtime", region_name=region)
    embeddings = BedrockEmbeddings(
        client=bedrock_client,
        model_id="amazon.titan-embed-text-v2:0"
    )
    return embeddings


# ─────────────────────────────
# 2️⃣ Parse Java AST to Extract Structured Info
# ─────────────────────────────
def parse_java_ast(java_code, file_path):
    """Parse Java code using javalang and return AST summary for embedding."""
    try:
        tree = javalang.parse.parse(java_code)
        classes = [path.name for path in tree.types if hasattr(path, "name")]
        imports = [imp.path for imp in tree.imports]
        methods = []
        for _, node in tree.filter(javalang.tree.MethodDeclaration):
            methods.append(node.name)
        fields = []
        for _, node in tree.filter(javalang.tree.FieldDeclaration):
            for decl in node.declarators:
                fields.append(decl.name)

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
        return java_code[:2000]  # fallback to truncated raw code


# ─────────────────────────────
# 3️⃣ Load Java Files and Build Documents
# ─────────────────────────────
def load_java_documents(source_path):
    docs = []
    for path in Path(source_path).rglob("*.java"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read().strip()
                if code:
                    ast_summary = parse_java_ast(code, str(path))
                    docs.append(Document(page_content=ast_summary, metadata={"source": str(path)}))
        except Exception as e:
            print(f"⚠️ Skipping {path}: {e}")
    print(f"✅ Parsed and loaded {len(docs)} Java files with AST summaries.")
    return docs


# ─────────────────────────────
# 4️⃣ Build or Load FAISS Vectorstore
# ─────────────────────────────
def build_or_load_vectorstore(source_path, pkl_path, region="us-east-1"):
    if os.path.exists(pkl_path):
        print(f"📂 Loading existing FAISS vectorstore from {pkl_path}")
        with open(pkl_path, "rb") as f:
            vectorstore = pickle.load(f)
        return vectorstore

    print("🚀 Building new FAISS vectorstore with Titan embeddings...")
    docs = load_java_documents(source_path)
    titan_embeddings = get_titan_embeddings(region)
    vectorstore = FAISS.from_documents(docs, titan_embeddings)

    with open(pkl_path, "wb") as f:
        pickle.dump(vectorstore, f)

    print(f"✅ Vectorstore saved to {pkl_path}")
    return vectorstore


# ─────────────────────────────
# 5️⃣ Claude LLM via Bedrock
# ─────────────────────────────
def get_claude_llm(region="us-east-1"):
    bedrock_client = boto3.client("bedrock-runtime", region_name=region)
    llm = Bedrock(
        client=bedrock_client,
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        model_kwargs={"temperature": 0.3, "max_tokens": 1024}
    )
    return llm


# ─────────────────────────────
# 6️⃣ Build RAG Chain
# ─────────────────────────────
def build_rag_chain(vectorstore, llm):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    return qa


# ─────────────────────────────
# 7️⃣ Run Query from Text File
# ─────────────────────────────
def run_query_from_file(query_file, qa_chain):
    if not os.path.exists(query_file):
        raise FileNotFoundError(f"Query file not found: {query_file}")

    with open(query_file, "r", encoding="utf-8") as f:
        query = f.read().strip()

    if not query:
        raise ValueError("Query file is empty.")

    print(f"\n💬 Query: {query}\n")
    result = qa_chain.invoke({"query": query})

    print("🧠 Claude Answer:\n", result.get("result", "No response"))
    print("\n📚 Context Files:")
    for doc in result.get("source_documents", []):
        print("-", doc.metadata.get("source", "unknown file"))


# ─────────────────────────────
# 8️⃣ CLI Entrypoint
# ─────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Titan + Claude RAG with Java AST Embeddings")
    parser.add_argument("--source", required=True, help="Path to Java project folder")
    parser.add_argument("--pkl", default="titan_ast_embeddings.pkl", help="Path to save/load FAISS vectorstore")
    parser.add_argument("--query", required=True, help="Path to text file containing query")
    parser.add_argument("--region", default="us-east-1", help="AWS region for Bedrock")

    args = parser.parse_args()

    vectorstore = build_or_load_vectorstore(args.source, args.pkl, args.region)
    llm = get_claude_llm(args.region)
    qa_chain = build_rag_chain(vectorstore, llm)

    run_query_from_file(args.query, qa_chain)


if __name__ == "__main__":
    main()