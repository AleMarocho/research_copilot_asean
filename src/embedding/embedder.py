import os
from openai import OpenAI

class OpenAIEmbedder:
    def __init__(self, model: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
        self.model = model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]

    def embed_query(self, query: str) -> list[float]:
        """Generate embedding for a single query."""
        if not query:
            return []
        return self.embed_texts([query])[0]
