import os
import streamlit as st
from openai import OpenAI
from prompts.system_prompts import SYSTEM_PROMPT_V1, SYSTEM_PROMPT_V2, SYSTEM_PROMPT_V3, SYSTEM_PROMPT_V4

class Generator:
    def __init__(self, model="gpt-4o-mini"):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            try:
                api_key = st.secrets.get("OPENAI_API_KEY")
            except Exception:
                pass
                
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_response(self, query: str, context: str, strategy: str = "Standard", history: list = None) -> str:
        
        # Load the selected prompt
        if strategy == "JSON Output":
            base_prompt = SYSTEM_PROMPT_V2
        elif strategy == "Few-Shot":
            base_prompt = SYSTEM_PROMPT_V3
        elif strategy == "Chain-of-Thought":
            base_prompt = SYSTEM_PROMPT_V4
        else:
            base_prompt = SYSTEM_PROMPT_V1
            
        history_str = ""
        if history:
            for hp in history[-3:]: # only last 3 turns
                history_str += f"{hp['role'].upper()}: {hp['content']}\n"

        prompt = base_prompt.format(context=context, question=query, history=history_str)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Research Copilot specialized in RCEP and ASEAN Centrality."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error while generating the response: {e}"
