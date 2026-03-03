# 🤖 Research Copilot: ASEAN Centrality & RCEP
### Tarea Calificada 1 - Prompt Engineering
**Estudiante:** Alessandra Marcela Marocho Pacheco  
**Proyecto de Tesis:** *Más allá del comercio: la centralidad ASEAN en las dinámicas de regionalismo en el Este asiático (2012-2022)*.

---

## 📝 Descripción del Proyecto
Este proyecto es un asistente de investigación inteligente basado en la arquitectura **RAG (Retrieval-Augmented Generation)**. Su objetivo es facilitar la revisión de literatura académica permitiendo realizar consultas naturales sobre una base de datos de 20 artículos especializados en la diplomacia de la ASEAN y las negociaciones del RCEP.

El sistema no solo responde preguntas, sino que fundamenta cada respuesta con **citas bibliográficas automáticas en formato APA**, asegurando el rigor académico necesario para una investigación de posgrado.

## 🚀 Características Técnicas
* **Motor de Búsqueda:** Búsqueda semántica utilizando `ChromaDB` como base de datos vectorial.
* **LLM:** Generación de respuestas mediante `OpenAI GPT-4o-mini`.
* **Procesamiento de Datos:** Extracción y limpieza de texto de PDFs mediante `PyMuPDF (fitz)`.
* **Interfaz de Usuario:** Interfaz web intuitiva y profesional desarrollada con `Gradio`, optimizada para una experiencia de usuario fluida.

## 📂 Estructura del Repositorio
* `TC1_Marocho_Alessandra_Research_Copilot.ipynb`: Notebook principal con todo el flujo de desarrollo (ETL, Embeddings y RAG).
* `app.py`: Script de la Interfaz Web independiente generado con asistencia de **Claude Code**.
* `papers/`: Directorio que contiene los 20 artículos académicos en formato PDF.
* `requirements.txt`: Lista de librerías necesarias para ejecutar el proyecto.

## 🛠️ Instalación y Uso
1. **Requisitos:** Tener instalada una versión de Python 3.9+ y una clave de API de OpenAI.
2. **Instalación:**
   ```bash
   pip install -r requirements.txt
