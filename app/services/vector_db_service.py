from scripts.ingest import build_vector_documents
from sentence_transformers import SentenceTransformer
import chromadb
import os
from dotenv import load_dotenv

load_dotenv()


class VectorDB:

    def __init__(
        self,
        db_path=os.getenv("VECTOR_DB_PATH", "./chroma_db"),
        collection_name=os.getenv("COLLECTION_NAME", "api_docs"),
        embedding_model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    ):
        # --- embedding model ---
        self.embedding_model = SentenceTransformer(embedding_model_name)

        # --- chroma client ---
        self.client = chromadb.PersistentClient(path=db_path)

        self.collection_name = collection_name

        # --- get or create collection ---
        self.collection = self._get_or_create_collection()


    # Internal Methods
    def _get_or_create_collection(self):
        try:
            return self.client.get_collection(self.collection_name)
        except:
            return self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )

    def _embed(self, texts):
        return self.embedding_model.encode(texts).tolist()

    # Public Methods
    def reset_collection(self):
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass

        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def ingest_from_url(self, url):
        documents = build_vector_documents(url)
        self.add_documents(documents)

    def reset_and_ingest(self, url):
        self.reset_collection()
        self.ingest_from_url(url)

    def add_documents(self, documents):

        texts = [doc["text"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]

        embeddings = self._embed(texts)

        ids = [f"doc_{i}" for i in range(len(texts))]

        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, query, k=3):

        query_embedding = self._embed([query])[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )

        return results

    def search_with_parsing(self, query, k=3):

        results = self.search(query, k)

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        parsed = []

        for idx, (doc, meta) in enumerate(zip(documents, metadatas)):
            parsed.append({
                "id": idx,
                "text": doc,
                "metadata": meta
            })

        return parsed