import requests
from config import HF_API_TOKEN

class Generator:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
        self.headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(self.api_url, headers=self.headers, json={"inputs": prompt})
            response.raise_for_status()
            json_response = response.json()
            print("HF response:", json_response)
            if isinstance(json_response, list) and json_response[0].get("generated_text"):
                return json_response[0]["generated_text"]
            elif json_response.get("generated_text"):
                return json_response["generated_text"]
            else:
                return f"Unexpected HF response format: {json_response}"
        except Exception as e:
            print("Error calling Hugging Face API:", str(e))
            return "Sorry, I couldn't generate an answer at this time."