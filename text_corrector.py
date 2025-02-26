import requests
import json
from config_manager import load_config
import anthropic
import openai
from typing import Tuple

class TextCorrector:
    def __init__(self):
        self.config = load_config()
        self.setup_service()
        
    def setup_service(self):
        service = self.config.get('service')
        if service == "OpenAI":
            openai.api_key = self.config.get('api_key')
            self.correct_text = self.openai_correct
        elif service == "Anthropic":
            self.claude = anthropic.Anthropic(api_key=self.config.get('api_key'))
            self.correct_text = self.anthropic_correct
        elif service == "Mixtral":
            self.correct_text = self.mixtral_correct
            
    def openai_correct(self, word: str, context: str) -> Tuple[str, bool]:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "Eres un asistente que corrige cualquier texto a español correcto. No expliques las correcciones, solo devuelve el texto corregido."
                }, {
                    "role": "user",
                    "content": f"{context}"
                }],
                temperature=0.1,
                max_tokens=50
            )
            correction = response.choices[0].message.content.strip()
            return correction, correction != word
        except Exception as e:
            print(f"Error: {e}")
            return word, False
        
    def anthropic_correct(self, word: str, context: str) -> Tuple[str, bool]:
        try:
            message = self.claude.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=50,
                temperature=0.1,
                system="Eres un asistente que corrige cualquier texto a español correcto. No expliques las correcciones, solo devuelve el texto corregido.",
                messages=[{
                    "role": "user",
                    "content": f"{context}"
                }]
            )
            correction = message.content[0].text.strip()
            return correction, correction != word
        except Exception as e:
            print(f"Error: {e}")
            return word, False
        
    def mixtral_correct(self, word: str, context: str) -> Tuple[str, bool]:
        try:
            response = requests.post(
                "https://api.together.xyz/inference",
                headers={
                    "Authorization": f"Bearer {self.config.get('api_key')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                    "prompt": f"Sistema: Eres un asistente que corrige cualquier texto a español correcto. No expliques las correcciones, solo devuelve el texto corregido.\nUsuario: {context}",
                    "temperature": 0.1,
                    "max_tokens": 50,
                    "stop": ["\n"]
                }
            )
            correction = response.json()['output']['choices'][0]['text'].strip()
            return correction, correction != word
        except Exception as e:
            print(f"Error: {e}")
            return word, False