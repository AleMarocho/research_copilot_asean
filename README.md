# 🤖 Research Copilot: ASEAN & RCEP Academic Assistant

*An advanced Retrieval-Augmented Generation (RAG) system specialized in the study of ASEAN centrality, regionalism, and the Regional Comprehensive Economic Partnership (RCEP).*

---

## 1. Project Title and Description
**Research Copilot (ASEAN & RCEP Edition)**
This project implements a complete RAG (Retrieval-Augmented Generation) pipeline that functions as an intelligent academic assistant. It is loaded with a curated corpus of 20 academic papers related to Southeast Asian political economy, specifically focusing on the Association of Southeast Asian Nations (ASEAN) and the RCEP mega-regional agreement. It allows users to query complex geopolitical data and receive academically precise answers with direct in-text APA citations.

## 2. Features
- **Intelligent RAG Pipeline**: Extracts context directly from PDFs, generating semantically accurate responses.
- **Strict APA Citation System**: All responses automatically include inline citations and references to the specific authors and years of the provided literature.
- **Multiple Prompt Engineering Strategies**: Allows the ultimate user to dynamically switch between four testing models: *Standard (Clear Instructions)*, *JSON Output*, *Few-Shot Learning*, and *Chain-of-Thought*.
- **Conversation Memory**: Remembers up to 3 previous interactions, allowing for follow-up questions without losing context.
- **Interactive Filtering**: Lets you search by specific documents or years via the sidebar.
- **Cloud Interface**: Accessible from anywhere via Streamlit Community Cloud.

**Live Application:** [**Launch Research Copilot on Streamlit**](https://researchcopilotasean-cb9rewv9vpqqfdphnmfy8e.streamlit.app/)

## 3. Architecture
The architecture strictly follows a modular paradigm separating ingestion from presentation.
- **Ingestion (`src/ingestion`)**: PyMuPDF (`fitz`) handles the rigorous extraction and cleaning of PDF text.
- **Chunking (`src/chunking`)**: `tiktoken` splits the text intelligently via tokens (size: 512, overlap: 51) to keep logical coherence, avoiding cutoff sentences.
- **Embedding & Vector Storage (`src/embedding`, `src/vectorstore`)**: Uses OpenAI's `text-embedding-3-small` stored persistently on ChromaDB.
- **Generation (`src/generation`)**: Leverages `gpt-4o-mini` with strict system constraints.
- **UI Presentation (`app`)**: Developed in Streamlit for an interactive chat, sidebar configuration, and citation visualizers.

## 4. Installation
To run this application locally from scratch:

```bash
# 1. Clone the repository
git clone https://github.com/TU_USUARIO/research_copilot_asean.git
cd research_copilot_asean

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your Environment key
# Copy .env.example to .env and insert your OpenAI API Key
echo 'OPENAI_API_KEY="sk-YOUR-API-KEY"' > .env

# 4. Run the Streamlit Application
streamlit run app/main.py
```

## 5. Usage
Upon launching the application or visiting the [Cloud Link](https://researchcopilotasean-cb9rewv9vpqqfdphnmfy8e.streamlit.app/):
1. **Wait for Initialization**: If it's your first time, the vector database will index the 20 PDFs (takes ~2 mins).
2. **Select Parameters**: Use the left sidebar to choose a Prompt Strategy (e.g., *Chain-of-Thought* to see the reasoning) or filter particular papers.
3. **Ask a Question**: Type an inquiry into the chat.
   * *Example Query 1 (Factual)*: "¿Qué es el RCEP y en qué año se firmó?"
   * *Example Query 2 (Analytical)*: "¿Cuál es la principal diferencia del RCEP frente al TPP según la literatura?"
4. **Review References**: Click the "Ver Fuentes Referenciadas" dropdown under the assistant's replies to check the raw citations.

## 6. Technical Details
- **Base LLM**: `gpt-4o-mini` (Temperature 0.3 for academic rigor)
- **Embedding Model**: `text-embedding-3-small`
- **Chunking Strategy used**: Tokenized Chunking via `tiktoken`. We utilized a chunk size of 512 tokens with a ~10% overlap (51 tokens) to balance the API context limits with sufficient logical spacing for complex economic paragraphs.

## 7. Prompt Strategies & Evaluation Results Comparison
We implemented 4 distinct prompt evaluation strategies. The model performs differently on each:

| Prompt Strategy | Best Used For | Format Adherence | Hallucination / Tone |
| :--- | :--- | :--- | :--- |
| **Standard (V1)** | General factual QA | Good (Conversational) | Highly reliable, though sometimes brief. Strong citation adherence. |
| **JSON Output (V2)** | API Integration | Excellent (Strict JSON) | Very low hallucination. Fails only if asked a question outside the DB. |
| **Few-Shot (V3)** | High-level academic synthesis | Very Good (Scholarly) | Adopts a highly refined, professional tone thanks to the provided positive samples. |
| **Chain-of-Thought (V4)**| Analyzing complex topics | Reasonable | Best performance on cross-document synthesis. "Thinks" explicitly, reducing logic jumps. |

## 8. Limitations & Future Improvements
1. **Context Window Constraint**: Selecting more than 5 highly dense chunks sometimes overflows the context boundaries or dilutes the Assistant's attention regarding the actual user question versus the injected text.
2. **ChromaDB Cloud Wipe**: The SQLite persistent storage for ChromaDB is generated "on the fly" in Streamlit Cloud. If the instance hibernates, the DB has to be re-indexed, which costs time and API credits each time. *Improvement: Migrate vector storage to Pinecone or a managed Chroma cloud.*
3. **Language Mapping**: While the assistant is prompted to answer in Spanish, some deeply technical acronyms or extracts remain stuck in English from the original PDF layout.
4. *Future Improvement*: Adding a Rerank layer (like Cohere Rerank) between retrieval and generation specifically for multi-topic questions over 20+ papers.

## 9. Author Information
- **Name**: Alessandra Marocho
- **Course**: Prompt Engineering
- **Date**: March 2026
