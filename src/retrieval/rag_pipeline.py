import json
import os
from src.chunking.chunker import TokenChunker
from src.embedding.embedder import OpenAIEmbedder
from src.vectorstore.chroma_store import ChromaVectorStore
from src.ingestion.pdf_extractor import extract_text_from_pdf, clean_extracted_text

class RAGPipeline:
    def __init__(self, collection_name="asean_research_papers"):
        self.embedder = OpenAIEmbedder()
        self.vector_store = ChromaVectorStore()
        self.vector_store.create_collection(collection_name)

    def process_and_index_documents(self, catalog_path: str, papers_dir: str, chunk_size=512):
        """Processes PDFs, creates chunks, embeds them, and stores in VectorDB."""
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)["papers"]

        chunker = TokenChunker(chunk_size=chunk_size, chunk_overlap=int(chunk_size * 0.1))

        all_chunks = []
        all_metadata = []
        all_ids = []

        print(f"Indexing documents with chunk config size: {chunk_size}")

        for paper in catalog:
            file_path = os.path.join(papers_dir, paper["filename"])
            if not os.path.exists(file_path):
                continue
            
            # 1. Extraction
            extraction_res = extract_text_from_pdf(file_path)
            raw_text = extraction_res["text"]
            
            # 2. Cleaning
            cleaned_text = clean_extracted_text(raw_text)
            
            # Metadata pre-processing
            authors = paper.get("authors", "Anónimo")
            author_str = ", ".join(authors) if isinstance(authors, list) else authors

            # 3. Chunking
            chunks = chunker.chunk_text(cleaned_text)
            for chunk in chunks:
                chunk_meta = {
                    "paper_id": paper["id"],
                    "title": paper["title"],
                    "author": author_str,
                    "year": str(paper["year"]),
                    "chunk_index": chunk["chunk_id"]
                }
                
                # We save everything needed
                all_chunks.append(chunk["text"])
                all_metadata.append(chunk_meta)
                all_ids.append(f"{paper['id']}_chunk_{chunk['chunk_id']}")

        # 4. Storage (VectorDB manages embeddings via its own OpenAI wrapper internally 
        # normally, but if using our custom embedder, we would compute them first. 
        # Here we rely on the vector store directly querying OpenAI or passing plain texts if 
        # it has its own embedding function set up. ChromaDB handles this easily.
        if all_chunks:
            self.vector_store.add_documents(
                ids=all_ids,
                documents=all_chunks,
                metadatas=all_metadata
            )
        
        return len(all_chunks)

    def retrieve(self, query: str, n_results=4, filters: dict=None):
        where = None
        if filters:
            where_conditions = []
            if "years" in filters and filters["years"]:
                where_conditions.append({"year": {"$in": [str(y) for y in filters["years"]]}})
            if "papers" in filters and filters["papers"]:
                where_conditions.append({"title": {"$in": filters["papers"]}})
            
            if len(where_conditions) == 2:
                where = {"$and": where_conditions}
            elif len(where_conditions) == 1:
                where = where_conditions[0]
        try:
            results = self.vector_store.query(query_text=query, n_results=n_results, where=where)
            return results
        except Exception as e:
            # Fallback if filters fail
            return self.vector_store.query(query_text=query, n_results=n_results)
