import os
import requests
from dotenv import load_dotenv

load_dotenv()

class APIClient:
    def __init__(self, base_url: str = None):
        self.base_url = (base_url or os.getenv("API_BASE_URL", "http://localhost:8000")).rstrip("/")

    def check_health(self) -> dict:
        url = f"{self.base_url}/health"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}

    def query(self, question: str, top_k: int = 4, image_data: str = None) -> dict:
        url = f"{self.base_url}/query"
        payload = {
            "question": question,
            "top_k": top_k,
            "image_data": image_data
        }
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_json = e.response.json()
                    error_detail = error_json.get("detail", error_detail)
                except Exception:
                    pass
            return {"error": True, "message": f"API Request Failed: {error_detail}"}
