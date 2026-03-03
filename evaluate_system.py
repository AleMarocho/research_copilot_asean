import json
import time
import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from src.retrieval.rag_pipeline import RAGPipeline
from src.generation.generator import Generator

def evaluate_system():
    print("="*50)
    print("Iniciando Evaluación del Research Copilot (RCEP)")
    print("="*50)
    
    # Initialize pipeline
    pipeline = RAGPipeline()
    generator = Generator()
    
    # Load questions
    questions_path = "evaluation_questions.json"
    if not os.path.exists(questions_path):
        print("No se encontró el archivo de evaluación.")
        return
        
    with open(questions_path, "r", encoding="utf-8") as f:
        queries = json.load(f)
        
    for q in queries[:20]: # Evaluar las 20
        print(f"\n[ID: {q['id']}] Tipo: {q['type'].upper()}")
        print(f"Pregunta: {q['question']}")
        
        # Retrieval
        start_time = time.time()
        results = pipeline.retrieve(q["question"], n_results=4)
        
        context = ""
        try:
            chunks = results["documents"][0]
            for c in chunks:
                context += c + "\n\n"
        except:
            pass
            
        retrieval_time = time.time() - start_time
        
        # Generation (Usando V1)
        gen_start = time.time()
        answer = generator.generate_response(
            query=q["question"],
            context=context,
            strategy="Standard"
        )
        gen_time = time.time() - gen_start
        
        print(f"-> Respuesta (Tomó {retrieval_time+gen_time:.2f}s):\n{answer[:250]}...")
        print("-" * 50)
        
if __name__ == "__main__":
    evaluate_system()
