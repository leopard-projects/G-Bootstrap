def build_or_load_vectorstore(source_path, pkl_path, client):
    # ✅ Try loading existing FAISS vectorstore
    if os.path.exists(pkl_path):
        print(f"📂 Loading existing FAISS vectorstore from {pkl_path}")
        with open(pkl_path, "rb") as f:
            data = pickle.load(f)

        # If it’s already a FAISS object → return directly
        if hasattr(data, "similarity_search_by_vector"):
            return data

        # Otherwise rebuild FAISS from dict format
        elif isinstance(data, dict):
            print("⚠️ Detected legacy dict embedding format — rebuilding FAISS vectorstore.")
            texts, embeddings = data.get("documents", []), data.get("embeddings", [])
            if not texts or not embeddings:
                raise ValueError("❌ Invalid pickle: no documents or embeddings.")
            vectorstore = FAISS.from_embeddings(list(zip(texts, embeddings)))

            with open(pkl_path, "wb") as f2:
                pickle.dump(vectorstore, f2)
            print("✅ Rebuilt FAISS vectorstore successfully.")
            return vectorstore

        else:
            raise ValueError("❌ Unknown pickle format.")

    # ✅ If no pickle file exists, build new one
    print("🚀 Building new FAISS vectorstore with Titan embeddings...")
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

    print(f"✅ Vectorstore built and saved to {pkl_path}")
    return vectorstore