# Research Copilot: Asistente Académico para ASEAN y RCEP
---

## 1. Título y Descripción del Proyecto
**Research Copilot (Edición ASEAN y RCEP)**  
Este proyecto implementa una tubería (pipeline) completa de RAG que funciona como un asistente académico inteligente. Está cargado con un corpus seleccionado de 20 artículos académicos sobre economía política del sudeste asiático, centrándose específicamente en la Asociación de Naciones del Sudeste Asiático (ASEAN) y el megatrámite de Libre Comercio (RCEP). Permite a los usuarios realizar consultas profundas y recibir respuestas precisas e informadas, incluyendo citas directas en formato APA.

## 2. Características (Features)
- **Pipeline Inteligente RAG**: Extrae el contexto directamente de archivos PDF y genera respuestas semánticamente acertadas.
- **Sistema Estricto de Citas APA**: Todas las respuestas incluyen automáticamente citas textuales y una sección de Referencias para mostrar los autores y años de la literatura utilizada.
- **Múltiples Estrategias de "Prompt Engineering"**: Permite cambiar dinámicamente entre cuatro modelos de prueba diferentes: *Estándar (Instrucciones Claras)*, *Salida en JSON*, *Aprendizaje Few-Shot* y *Cadena de Pensamiento (Chain-of-Thought)*.
- **Memoria de Conversación**: Recuerda hasta 3 interacciones anteriores.
- **Filtrado Interactivo**: Permite acotar la búsqueda a documentos específicos usando la barra lateral.
- **Interfaz en la Nube**: Totalmente accesible para cualquier evaluador mediante **Streamlit**.

**Aplicación Desplegada:** [**Inicia el Research Copilot en Streamlit**](https://researchcopilotasean-cb9rewv9vpqqfdphnmfy8e.streamlit.app/)

## 3. Arquitectura
La arquitectura sigue un esquema estrictamente modular, separando la ingesta de documentos de la presentación hacia el usuario:
- **Ingesta (`src/ingestion`)**: Usa la librería PyMuPDF (`fitz`) para extraer de manera rigurosa y limpiar el texto de los PDFs.
- **Fragmentación o Chunking (`src/chunking`)**: Se utiliza `tiktoken` para fraccionar el texto inteligentemente (tamaño: 512 tokens, superposición: 51), manteniendo la coherencia y evitando cortar oraciones de ideas complejas.
- **Embeddings y Base Vectorial (`src/embedding`, `src/vectorstore`)**: Usa el modelo de OpenAI `text-embedding-3-small` y almacena los datos persistentemente usando la base vectorial ChromaDB.
- **Generación (`src/generation`)**: Aprovecha el poder de `gpt-4o-mini` con restricciones estrictas de prompt.
- **Presentación Visual UI (`app`)**: Interfaz desarrollada en Streamlit, incluyendo el chat interactivo, la configuración de estrategias y el visualizador de fuentes referenciadas.

## 4. Instalación
Para correr esta aplicación de manera local desde cero:

```bash
# 1. Clona el repositorio
git clone https://github.com/TU_USUARIO/research_copilot_asean.git
cd research_copilot_asean

# 2. Instala las dependencias necesarias
pip install -r requirements.txt

# 3. Configura tu credencial de API
# Copia .env.example hacia .env y agrega tu llave de OpenAI
echo 'OPENAI_API_KEY="sk-TU-LLAVE-AQUI"' > .env

# 4. Inicia la aplicación local de Streamlit
streamlit run app/main.py
```

## 5. Uso de la Aplicación
Ya sea al abrir en el [Enlace en la Nube](https://researchcopilotasean-cb9rewv9vpqqfdphnmfy8e.streamlit.app/) o local:
1. **Inicialización**: Si es la primera vez, el servidor extrae e indexará todos los PDFs en la base de datos (tomará ~2 minutos y saldrá un aviso amarillo).
2. **Selecciona Parámetros**: Desde la barra lateral izquierda escoge una Estrategia de Prompt. Si quieres ver cómo el robot razona, elige *Chain-of-Thought*.
3. **Realiza Consultas**: Escribe tu duda académica sobre ASEAN en la caja inferior.
   * *Pregunta Ejemplo 1 (Factual)*: "¿Qué es el RCEP y en qué año se firmó?"
   * *Pregunta Ejemplo 2 (Analítica)*: "¿Cuál es la principal diferencia del RCEP frente al TPP según la literatura académica proporcionada?"
4. **Validación de Fuentes**: Oprime la caja colapsable "Ver Fuentes Referenciadas" que sale debajo de cada interacción para revisar visualmente la procedencia (autor, año, título) de las citas incluidas.

## 6. Detalles Técnicos
- **LLM Base de Generación**: `gpt-4o-mini` (Parámetro Temperatura = 0.3 para preservar rigor académico y evitar alucinaciones excesivas)
- **Modelo de Embeddings**: `text-embedding-3-small`
- **Estrategia de Chunking**: Tokenización implementada usando la librería oficial `tiktoken`. Se estableció un límite estricto de **512 tokens** por chunk, acompañado de un "overlap" (superposición) de 51 tokens (~10%) que previene perder contexto o "saltar ideas" en medio de descripciones económicas densas.

## 7. Resultados de la Evaluación (Estrategias de Prompts)
Se desarrollaron bajo requerimiento 4 distintas técnicas de Prompt Engineering y se midió cómo variaba la respuesta del RAG:

| Estrategia de Prompt | Uso Ideal (Best Used For) | Adherencia de Formato | Alucinaciones / Tono |
| :--- | :--- | :--- | :--- |
| **Estándar (V1)** | Respuestas Directas / Factuales | Bueno (Fluido y Natural) | Muy poco propenso a inventar, aunque la respuesta final tiende a ser corta y demasiado al grano. |
| **JSON Output (V2)**| Analítica de software conectada | Excelente (JSON Válido estrictamente) | Excelente exactitud. Devuelve datos limpios y variables directas. |
| **Few-Shot (V3)** | Síntesis a nivel Universitario | Muy Bueno (Académico Elegante) | Adopta un modo altamente referenciado basándose en los ejemplos previos inyectados. |
| **Chain-of-Thought (V4)**| Razonamiento analítico o de contrastes múltiples| Aceptable (Muestra el proceso real) | Es la mejor extrayendo detalles ocultos, pues muestra todo su paso deductivo uno por uno antes de dictar su respuesta en español. |

## 8. Limitaciones y Mejoras a Futuro
1. **Pérdida de ventana de contexto**: Seleccionar un número excesivo de "chunks" para recuperar sobrepasa ocasionalmente el foco de `gpt-4o-mini`, dificultando que relacione apropiadamente todos los textos con la pregunta raíz.
2. **Re-Indexación Persistente en la Nube (Chroma SQLite)**: Puesto que usamos SQLite para emular el servidor Chroma de manera local, y la nube de Streamlit "duerme" sus clústers; toda la base de datos de referencias desaparece después de horas de inactividad obligando a usar CPU/API nuevamente para re-indexar los PDFs. *Mejora posible a futuro: Usar Pinecone Data.*
3. **Sesgos de Lenguaje Técnico**: Se impuso por *Prompt System* que el bot siempre responda en Español, no obstante, dado que los 20 artículos madre están en lenguaje técnico especializado Anglosajón, la app suele arrastrar siglas no traducidas.
4. *Mejora a Futuro*: Añadir una etapa de "Rerank" de validación superior empleando software intermedio (por ejemplo integrando Cohere) para mejorar el factor *Recall* cuando se pregunten tópicos combinados.

## 9. Información del Autor del Trabajo
- **Nombre**: Alessandra Marocho
- **Curso**: Ing. de Prompts (Prompt Engineering)
- **Fecha de Entrega**: Marzo de 2026
