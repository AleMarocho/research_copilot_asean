import os
import re
import json
import fitz
import chromadb
import gradio as gr
from openai import OpenAI

# ─── Configuración ──────────────────────────────────────────────────────────────
PAPERS_FOLDER = "papers/"
COLLECTION_NAME = "asean_research_papers"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

CATALOG = {
    "papers": [
        {
            "id": "paper_001",
            "title": "From APEC to mega-regionals: the evolution of the Asia-Pacific trade architecture",
            "authors": ["Mireya Solís", "Jeffrey D. Wilson"],
            "year": 2017,
            "filename": "From APEC to mega-regionals the evolution of the Asia-Pacific trade architecture.pdf",
        },
        {
            "id": "paper_002",
            "title": "RCEP from the middle powers' Perspective",
            "authors": ["Fukunari Kimura"],
            "year": 2021,
            "filename": "RCEP from the middle powers Perspective .pdf",
        },
        {
            "id": "paper_003",
            "title": "ASEAN's inheritance: the regionalization of Southeast Asia, 1941-61",
            "authors": ["Philip Charrier"],
            "year": 2001,
            "filename": "ASEAN s inheritance  the regionalization of Southeast Asia  1941 61.pdf",
        },
        {
            "id": "paper_004",
            "title": "Asean's inclusive regionalism: ambitious at three levels",
            "authors": ["Astanah Abdul Aziz", "Anthony Milner"],
            "year": 2024,
            "filename": "ASEAN inclusive regionalism ambitious at three levels .pdf",
        },
        {
            "id": "paper_005",
            "title": "Investigating merchandise trade structure in the RCEP region from the perspective of regional integration",
            "authors": ["CHEN Xiaoqiang", "YUAN Lihua", "SONG Changqing"],
            "year": 2023,
            "filename": "Investigating merchandise trade structure in the RCEP region from the perspective of regional integration.pdf",
        },
        {
            "id": "paper_006",
            "title": "Hedging via Institutions: ASEAN-led Multilateralism in the Age of the Indo-Pacific",
            "authors": ["Cheng-Chwee Kuik"],
            "year": 2022,
            "filename": "Hedging via Institutions ASEAN-led Multilateralism in the Age of the Indo-Pacific.pdf",
        },
        {
            "id": "paper_007",
            "title": "Assessing the Impact of the Regional Comprehensive Economic Partnership on ASEAN Trade",
            "authors": ["Sithanonxay Suvannaphakdy"],
            "year": 2021,
            "filename": "Assessing the Impact of the Regional Comprehensive Economic Partnership on ASEAN Trade.pdf",
        },
        {
            "id": "paper_008",
            "title": "Mega-Regional Trade Deals in the Asia-Pacific: Choosing Between the TPP and RCEP?",
            "authors": ["Jeffrey D. Wilson"],
            "year": 2015,
            "filename": "Mega-Regional Trade Deals in the Asia-Pacific Choosing Between the TPP and RCEP.pdf",
        },
        {
            "id": "paper_009",
            "title": "RCEP: a strategic opportunity for multilateralism",
            "authors": ["Peter Drysdale", "Shiro Armstrong"],
            "year": 2021,
            "filename": "RCEP a strategic opportunity for multilateralism.pdf",
        },
        {
            "id": "paper_010",
            "title": "Towards a New ASEAN Regionalism: Navigating the Outlook on Indo-Pacific in Post-RCEP Beyond 2020",
            "authors": ["Hino Samuel Jose", "Hree Dharma Santhi Putri Samudra"],
            "year": 2022,
            "filename": "Towards a New ASEAN Regionalism.pdf",
        },
        {
            "id": "paper_011",
            "title": "Building ASEAN Identity Through Regional Diplomacy",
            "authors": ["Elaine Tan"],
            "year": 2022,
            "filename": "Building ASEAN Identity Through Regional Diplomacy.pdf",
        },
        {
            "id": "paper_012",
            "title": "Beyond the 'new' regionalism",
            "authors": ["Björn Hettne"],
            "year": 2005,
            "filename": "Beyond the 'New' Regionalism.pdf",
        },
        {
            "id": "paper_013",
            "title": "Doomed by Dialogue: Will ASEAN Survive Great Power Rivalry in Asia?",
            "authors": ["Amitav Acharya"],
            "year": 2018,
            "filename": "Doomed by Dialogue Will ASEAN Survive Great Power Rivalry in Asia.pdf",
        },
        {
            "id": "paper_014",
            "title": "Thirty years of ASEAN: achievements and challenges",
            "authors": ["Jörn Dosch", "Manfred Mols"],
            "year": 1998,
            "filename": "Thirty years of ASEAN Achievements and challenges.pdf",
        },
        {
            "id": "paper_015",
            "title": "The Emergence and Proliferation of Free Trade Agreements in East Asia",
            "authors": ["Shujiro Urata"],
            "year": 2004,
            "filename": "The Emergence and Proliferation of Free Trade Agreements in East Asia.pdf",
        },
        {
            "id": "paper_016",
            "title": "Trade Diversion and Creation Effect of Free Trade Agreements in ASEAN: Do Institutions Matter?",
            "authors": ["Abdulkareem Alhassan", "Cem Payaslioğlu"],
            "year": 2023,
            "filename": "Trade Diversion and Creation Effect of Free Trade Agreements in ASEAN Do Institutions Matter.pdf",
        },
        {
            "id": "paper_017",
            "title": "China's rising assertiveness and the decline in the East Asian regionalism narrative",
            "authors": ["Andrew Yeo"],
            "year": 2020,
            "filename": "China's rising assertiveness and the decline in the East Asian regionalism narrative.pdf",
        },
        {
            "id": "paper_018",
            "title": "Why Asian states cooperate in regional arrangements: Asian regionalism in comparative perspective",
            "authors": ["Diana Panke", "Jürgen Rüland"],
            "year": 2022,
            "filename": "Why Asian states cooperate in regional arrangements Asian regionalism in comparative perspective.pdf",
        },
        {
            "id": "paper_019",
            "title": "The ASEAN Economic Community and the RCEP in the world economy",
            "authors": ["Kazushi Shimizu"],
            "year": 2021,
            "filename": "The ASEAN Economic Community and the RCEP in the world economy.pdf",
        },
        {
            "id": "paper_020",
            "title": "China's Approach to Regional Free Trade Frameworks in the Asia Pacific: RCEP as a Prime Example of Economic Diplomacy?",
            "authors": ["David Groten"],
            "year": 2017,
            "filename": "China's Approach to Regional Free Trade Frameworks in the Asia Pacific RCEP as a Prime Example of Economic Diplomacy.pdf",
        },
    ]
}

EXAMPLES = [
    "¿Cómo se define la centralidad de ASEAN en el contexto de las negociaciones del RCEP?",
    "¿Cuál fue el rol de China en las negociaciones del RCEP entre 2012 y 2022?",
    "¿Qué diferencias existen entre el TPP y el RCEP como mega-acuerdos regionales?",
    "¿Cómo impactó el RCEP en la estructura comercial de los países miembros de ASEAN?",
    "¿Qué estrategias utilizó ASEAN para preservar su relevancia frente a las grandes potencias?",
]


# ─── Procesamiento de PDFs ──────────────────────────────────────────────────────
def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"Error al leer {pdf_path}: {e}")
    return text


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def get_chunks(text: str, chunk_size: int = 1000) -> list[str]:
    words = text.split()
    return [" ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)]


# ─── Construcción de la colección ChromaDB ──────────────────────────────────────
def build_collection() -> chromadb.Collection:
    chroma_client = chromadb.Client()
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    collection = chroma_client.create_collection(name=COLLECTION_NAME)
    all_chunks, chunk_metadata = [], []

    # Intentar cargar catálogo externo; si no, usar el embebido
    json_path = os.path.join(PAPERS_FOLDER, "paper_catalog.json")
    catalog = CATALOG
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)

    print("Procesando documentos...")
    for paper in catalog["papers"]:
        file_path = os.path.join(PAPERS_FOLDER, paper["filename"])
        if not os.path.exists(file_path):
            print(f"  [OMITIDO] {paper['filename']}")
            continue

        print(f"  -> {paper['title']}")
        raw = extract_text_from_pdf(file_path)
        cleaned = clean_text(raw)
        chunks = get_chunks(cleaned)

        authors = paper["authors"]
        author_str = ", ".join(authors) if isinstance(authors, list) else authors

        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            chunk_metadata.append(
                {
                    "paper_id": paper["id"],
                    "title": paper["title"],
                    "author": author_str,
                    "year": str(paper["year"]),
                    "chunk_index": i,
                }
            )

    ids = [f"id_chunk_{i}" for i in range(len(all_chunks))]
    collection.add(documents=all_chunks, metadatas=chunk_metadata, ids=ids)
    print(f"\nColección '{COLLECTION_NAME}' lista — {collection.count()} fragmentos indexados.\n")
    return collection


# ─── Lógica RAG ─────────────────────────────────────────────────────────────────
def query_research_copilot(user_query: str) -> str:
    results = collection.query(query_texts=[user_query], n_results=4)
    retrieved_chunks = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = ""
    for i, text in enumerate(retrieved_chunks):
        autor = metadatas[i].get("author", "Anónimo")
        anio = metadatas[i].get("year", "s.f.")
        titulo = metadatas[i].get("title", "")
        context += f'--- FUENTE: ({autor}, {anio}) | Título: "{titulo}" ---\n{text}\n\n'

    prompt = f"""Eres un asistente de investigación académica especializado en Relaciones Internacionales, \
con dominio experto en la Asociación de Naciones del Sudeste Asiático (ASEAN) y el acuerdo RCEP.
Responde ÚNICAMENTE con base en el contexto académico proporcionado.

REGLAS ESTRICTAS:
1. Usa citas APA en el cuerpo del texto: (Apellido, Año) o (Apellido & Apellido, Año) para dos autores; \
(Apellido et al., Año) para tres o más.
2. Mantén un tono académico, objetivo y preciso.
3. Si la respuesta no está en el contexto, responde exactamente: \
"Lo siento, la información disponible en los documentos no me permite responder a esa pregunta con precisión."
4. Al final de tu respuesta, incluye una sección "**Referencias:**" con las fuentes usadas en formato APA completo.

EJEMPLO DE FORMATO:
La centralidad de ASEAN se entiende como su rol conductor en la arquitectura regional (Solís & Wilson, 2017). \
Este principio ha guiado las negociaciones del RCEP (Kimura, 2021).

**Referencias:**
- Solís, M. & Wilson, J. D. (2017). From APEC to mega-regionals... *The Pacific Review*.
- Kimura, F. (2021). RCEP from the middle powers' perspective. *China Economic Journal*.

CONTEXTO ACADÉMICO:
{context}

PREGUNTA:
{user_query}

RESPUESTA:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un experto académico en RCEP y Centralidad de ASEAN. "
                        "Respondes con rigor académico y citas APA estrictas."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al generar la respuesta: {e}"


# ─── Inicialización ──────────────────────────────────────────────────────────────
print("=" * 60)
print("  Research Copilot: Centralidad de ASEAN & RCEP")
print("=" * 60)
collection = build_collection()


# ─── Interfaz Gradio ─────────────────────────────────────────────────────────────
def interface_fn(message: str, history: list) -> str:
    return query_research_copilot(message)


demo = gr.ChatInterface(
    fn=interface_fn,
    title="🤖 Research Copilot: Centralidad de ASEAN & RCEP",
    description=(
        "Asistente académico basado en RAG para la tesis de Alessandra Marocho. "
        "Consulta los 20 artículos académicos sobre la centralidad de ASEAN "
        "durante las negociaciones del RCEP (2012-2022). "
        "Las respuestas incluyen **citas APA estrictas**."
    ),
    examples=EXAMPLES,
    cache_examples=False,
)

if __name__ == "__main__":
    demo.launch(share=True)
