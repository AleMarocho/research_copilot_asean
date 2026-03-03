import os
from openai import OpenAI
from prompts.system_prompts import SYSTEM_PROMPT_V1, SYSTEM_PROMPT_V2, SYSTEM_PROMPT_V3, SYSTEM_PROMPT_V4

class Generator:
    def __init__(self, model="gpt-4o-mini"):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
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
