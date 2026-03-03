import os
import re
import json
import fitz
import chromadb
import pandas as pd
import plotly.express as px
import streamlit as st
from openai import OpenAI

# ─── Configuración Inicial ────────────────────────────────────────────────────────
st.set_page_config(page_title="Research Copilot", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

PAPERS_FOLDER = "papers/"
COLLECTION_NAME = "asean_research_papers"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

# ─── Estilos Personalizados (CSS) ────────────────────────────────────────────────
st.markdown("""
<style>
.main-header { font-family: 'Georgia', serif; color: #1a1a2e; }
.citation-box { 
    background-color: #f0f0f5; 
    border-left: 4px solid #4a4a8a; 
    padding: 10px; 
    margin: 10px 0; 
    color: #333;
    font-size: 0.9em;
}
</style>
""", unsafe_allow_html=True)

# ─── Funciones Core (Cachéadas) ──────────────────────────────────────────────────
@st.cache_data
def load_catalog():
    """Carga el catálogo de papers desde el JSON."""
    json_path = os.path.join(PAPERS_FOLDER, "paper_catalog.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)["papers"]
    return []

@st.cache_resource(show_spinner="Construyendo Base de Datos Vectorial...")
def get_collection():
    """Inicializa ChromaDB y procesa los PDFs para cargar los embeddings de texto (Ingestion & Vector DB)."""
    catalog = load_catalog()
    chroma_client = chromadb.Client()
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    collection = chroma_client.create_collection(name=COLLECTION_NAME)
    
    all_chunks, chunk_metadata = [], []
    for paper in catalog:
        file_path = os.path.join(PAPERS_FOLDER, paper.get("filename", ""))
        if not os.path.exists(file_path): 
            continue
        
        text = ""
        try:
            with fitz.open(file_path) as doc:
                for page in doc: 
                    text += page.get_text("text") + "\n"
        except Exception:
            pass
        
        # Limpieza sencilla
        cleaned = re.sub(r"\s+", " ", text).strip()
        words = cleaned.split()
        # Segmentación en chunks de ~1000 palabras
        chunks = [" ".join(words[i : i + 1000]) for i in range(0, len(words), 1000)]
        
        authors = paper.get("authors", "Anónimo")
        author_str = ", ".join(authors) if isinstance(authors, list) else authors
        
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            chunk_metadata.append({
                "paper_id": paper.get("id", ""),
                "title": paper.get("title", ""),
                "author": author_str,
                "year": str(paper.get("year", "")),
                "chunk_index": i,
            })
    
    if all_chunks:
        ids = [f"id_chunk_{i}" for i in range(len(all_chunks))]
        collection.add(documents=all_chunks, metadatas=chunk_metadata, ids=ids)
    
    return collection

collection = get_collection()
catalog = load_catalog()

# ─── Pipeline RAG ─────────────────────────────────────────────────────────────────
def query_copilot(user_query, strategy, filter_years=None, filter_papers=None):
    """Ejecuta Retrieval y Generation según la estrategia seleccionada y filtros."""
    where_conditions = {}
    if filter_years:
        where_conditions["year"] = {"$in": [str(y) for y in filter_years]}
    if filter_papers:
        where_conditions["title"] = {"$in": filter_papers}
        
    where = None
    if filter_years and filter_papers:
        where = {"$and": [{"year": {"$in": [str(y) for y in filter_years]}}, {"title": {"$in": filter_papers}}]}
    elif filter_years:
        where = {"year": {"$in": [str(y) for y in filter_years]}}
    elif filter_papers:
        where = {"title": {"$in": filter_papers}}

    try:
        if where:
            results = collection.query(query_texts=[user_query], n_results=4, where=where)
        else:
            results = collection.query(query_texts=[user_query], n_results=4)
    except Exception as e:
        results = collection.query(query_texts=[user_query], n_results=4)

    if not results["documents"] or not sum(len(d) for d in results["documents"]):
        return "No se encontró información relevante en los documentos.", []

    retrieved_chunks = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = ""
    citations = []
    for i, text in enumerate(retrieved_chunks):
        autor = metadatas[i].get("author", "Anónimo")
        anio = metadatas[i].get("year", "s.f.")
        titulo = metadatas[i].get("title", "")
        context += f'--- FUENTE: ({autor}, {anio}) | Título: "{titulo}" ---\n{text}\n\n'
        citations.append(f"{autor} ({anio}). {titulo}.")

    # Aplicación de Estrategias de Prompting (Requisito 7.1)
    sys_msg = "Eres un asistente académico experto en RCEP y Centralidad de ASEAN."
    
    if strategy == "Chain-of-Thought":
        prompt_instruction = "Piensa paso a paso tu razonamiento antes de responder (Chain of Thought). Estructura el análisis y termina con tu conclusión. Cita usando formato APA."
    elif strategy == "JSON Output":
        prompt_instruction = "Responde ESTRICTAMENTE en un formato JSON estructurado que incluya dos llaves: 'respuesta' y 'referencias'. Usa citas APA dentro del texto."
        sys_msg += " Responde sólo en JSON."
    elif strategy == "Few-Shot":
        prompt_instruction = "Usa este formato estructurado para tu respuesta. Pregunta: [Tu pregunta]\nAnálisis: [Tu análisis breve]\nRespuesta: [Respuesta concreta usando citas APA].\nReferencias: \n- [Lista]"
    else:  # Standard / Clear Instructions
        prompt_instruction = "Instrucción clara: responde de forma rigurosa, objetiva y usa formato de cita APA en el texto. Añade una lista de referencias al final."

    prompt = f\"\"\"{prompt_instruction}

CONTEXTO ACADÉMICO:
{context}

PREGUNTA:
{user_query}

RESPUESTA:\"\"\"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content, set(citations)
    except Exception as e:
        return f"Error de OpenAI: {e}", []

# ─── Interfaz de Usuario (UI) ────────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/8/87/ASEAN_Emblem.svg/1200px-ASEAN_Emblem.svg.png", width=120)
st.sidebar.title("Configuración y Filtros")

# Extracción de filtros
all_titles = [p.get("title", "") for p in catalog]
all_years = sorted(list(set([int(p.get("year", 0)) for p in catalog if p.get("year")])))

# Sidebar controls
strategy = st.sidebar.selectbox("Estrategia de Prompt", ["Standard", "JSON Output", "Few-Shot", "Chain-of-Thought"])
st.sidebar.markdown("---")
filter_papers = st.sidebar.multiselect("Filtrar por Papers:", all_titles)
filter_years = st.sidebar.multiselect("Filtrar por Año:", all_years)

if st.sidebar.button("🧹 Limpiar Conversación"):
    st.session_state.messages = []
    st.rerun()

st.title("🤖 Research Copilot")
st.markdown("*Asistente académico basado en RAG para la tesis sobre la centralidad de ASEAN y el RCEP.*")

# Navegación por Pestañas
tab1, tab2, tab3 = st.tabs(["💬 Chat Interface", "📚 Paper Browser", "📊 Analytics Dashboard"])

with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Render histórico de chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "citations" in msg and msg["citations"]:
                with st.expander("Ver Fuentes Referenciadas"):
                    for c in msg["citations"]:
                        st.markdown(f'<div class="citation-box">{c}</div>', unsafe_allow_html=True)
                        
    # Input usuario
    if prompt := st.chat_input("Escribe tu pregunta sobre ASEAN y el RCEP..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("📚 Consultando documentos requeridos..."):
                response, citations = query_copilot(prompt, strategy, filter_years, filter_papers)
                st.markdown(response)
                
                if citations:
                    with st.expander("Ver Fuentes Referenciadas"):
                        for c in citations:
                            st.markdown(f'<div class="citation-box">{c}</div>', unsafe_allow_html=True)
                            
                st.session_state.messages.append({"role": "assistant", "content": response, "citations": citations})

with tab2:
    st.subheader("Catálogo de Publicaciones Integradas")
    if catalog:
        df_papers = pd.DataFrame(catalog)
        st.dataframe(df_papers[['title', 'authors', 'year']], use_container_width=True)
        
        st.markdown("---")
        st.subheader("Ver Metadatos Detallados")
        selected_paper = st.selectbox("Selecciona un paper:", df_papers['title'])
        if selected_paper:
            details = df_papers[df_papers['title'] == selected_paper].iloc[0]
            st.write(f"**Título:** {details['title']}")
            
            authors_fmt = ", ".join(details['authors']) if isinstance(details['authors'], list) else details['authors']
            st.write(f"**Autores:** {authors_fmt}")
            st.write(f"**Año:** {details['year']}")
            
            if "topics" in details and pd.notna(details['topics']).any():
                topics_fmt = ", ".join(details['topics']) if isinstance(details['topics'], list) else details['topics']
                st.write(f"**Temas Clave:** {topics_fmt}")
                
            if "abstract" in details and pd.notna(details["abstract"]):
                with st.expander("Resumen (Abstract)"):
                    st.write(details['abstract'])
    else:
        st.info("No se encontró el catálogo de papers. Procesamiento incompleto.")

with tab3:
    st.subheader("Visualización del Corpus Académico")
    if catalog:
        df_papers = pd.DataFrame(catalog)
        
        col1, col2 = st.columns(2)
        with col1:
            if 'year' in df_papers.columns:
                df_year = df_papers['year'].value_counts().reset_index()
                df_year.columns = ['Año', 'Cantidad']
                df_year = df_year.sort_values(by="Año")
                fig1 = px.bar(df_year, x="Año", y="Cantidad", title="Documentos por Año de Publicación", 
                              color_discrete_sequence=['#4a4a8a'])
                st.plotly_chart(fig1, use_container_width=True)
                
        with col2:
            if 'topics' in df_papers.columns:
                all_topics = []
                for topics in df_papers['topics'].dropna():
                    if isinstance(topics, list):
                        all_topics.extend(topics)
                    else:
                        all_topics.append(topics)
                
                if all_topics:
                    df_topics = pd.DataFrame(all_topics, columns=['Topic']).value_counts().reset_index()
                    df_topics.columns = ['Topic', 'Count']
                    fig2 = px.pie(df_topics, values='Count', names='Topic', title="Cobertura Temática")
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("No se han registrado temas (topics) explícitos en el catálogo para graficar.")
    else:
        st.info("Datos insuficientes para generar métricas estadísticas.")
