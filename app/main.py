import os
import sys

# Agregar la raíz del proyecto al path para que Python encuentre la carpeta "src" correctamente
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import streamlit as st
from src.retrieval.rag_pipeline import RAGPipeline
from src.generation.generator import Generator

st.set_page_config(
    page_title="Research Copilot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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

# Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = RAGPipeline()
if "generator" not in st.session_state:
    st.session_state.generator = Generator()
if "catalog_papers" not in st.session_state: # Simulated for simplified UI, read from utils
    try:
        import json
        with open("papers/paper_catalog.json","r") as f:
            st.session_state.catalog_papers = json.load(f)["papers"]
    except:
        st.session_state.catalog_papers = []

def get_all_paper_titles():
    return [p["title"] for p in st.session_state.catalog_papers]

# Sidebar components
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/8/87/ASEAN_Emblem.svg/1200px-ASEAN_Emblem.svg.png", width=120)
st.sidebar.title("Config & Filters")

selected_papers = st.sidebar.multiselect(
    "Filter by papers:",
    options=get_all_paper_titles()
)

strategy = st.sidebar.selectbox(
    "Prompt Strategy:",
    ["Standard", "JSON Output", "Few-Shot", "Chain-of-Thought"]
)

if st.sidebar.button("🧹 Clear Conversation"):
    st.session_state.messages = []
    st.rerun()

st.title("🤖 Research Copilot (RCEP & ASEAN)")

# Render Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("citations"):
            with st.expander("Ver Fuentes Referenciadas"):
                for c in message["citations"]:
                    st.markdown(f'<div class="citation-box">{c}</div>', unsafe_allow_html=True)

# Main action
if prompt := st.chat_input("Ask a question about your papers..."):
    # Create the filter dictionary
    filters = {}
    if selected_papers:
         filters["papers"] = selected_papers

    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
         st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching papers..."):
            # 1. Retrieve
            raw_results = st.session_state.rag_pipeline.retrieve(prompt, n_results=4, filters=filters)
            
            # Format context and explicit citations
            context = ""
            citations = set()
            try:
                retrieved_chunks = raw_results["documents"][0]
                metadatas = raw_results["metadatas"][0]
                
                for i, text in enumerate(retrieved_chunks):
                    autor = metadatas[i].get("author", "Anónimo")
                    anio = metadatas[i].get("year", "s.f.")
                    titulo = metadatas[i].get("title", "")
                    context += f'--- FUENTE: ({autor}, {anio}) Título: "{titulo}" ---\n{text}\n\n'
                    citations.add(f"{autor} ({anio}). {titulo}")
            except Exception as e:
                context = "No context could be found or DB is empty."

            # 2. Get generation matching memory history constraint
            response = st.session_state.generator.generate_response(
                 query=prompt,
                 context=context,
                 strategy=strategy,
                 history=st.session_state.messages
            )

            st.markdown(response)
            if citations:
                with st.expander("Ver Fuentes Referenciadas"):
                    for c in citations:
                         st.markdown(f'<div class="citation-box">{c}</div>', unsafe_allow_html=True)

        st.session_state.messages.append({
            "role": "assistant", 
            "content": response, 
            "citations": list(citations)
        })
