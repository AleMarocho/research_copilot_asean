import tiktoken

class TokenChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50, model: str = "gpt-4"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoder = tiktoken.encoding_for_model(model)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))

    def chunk_text(self, text: str, metadata: dict = None) -> list[dict]:
        """
        Split text into overlapping chunks.
        Returns: List of chunk dictionaries with text and metadata
        """
        tokens = self.encoder.encode(text)
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoder.decode(chunk_tokens)
            
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "token_count": len(chunk_tokens),
                "start_token": start,
                "end_token": end,
                "metadata": metadata or {}
            })
            
            # If we've reached the end of the text, break
            if end == len(tokens):
                break
                
            start += self.chunk_size - self.chunk_overlap
            chunk_id += 1
            
        return chunks
