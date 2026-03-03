import chromadb
from chromadb.config import Settings

class ChromaVectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = None

    def create_collection(self, name: str):
        """Create or get a collection."""
        self.collection = self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]] = None,
        metadatas: list[dict] = None
    ):
        """Add documents with embeddings and metadata."""
        if embeddings:
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
        else:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )

    def query(
        self,
        query_text: str = None,
        query_embedding: list[float] = None,
        n_results: int = 5,
        where: dict = None
    ) -> dict:
        """Query similar documents. Can use raw text or pre-computed embeddings."""
        if query_embedding:
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
        else:
            return self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
