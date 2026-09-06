import httpx
from typing import List
from app.core.config import settings
from app.schemas.query import SourceCitation
from app.utils.logging_config import logger

class GenerationService:
    def __init__(self, model_name: str = None, base_url: str = None):
        self.model_name = model_name or settings.OLLAMA_MODEL
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")

    def generate_grounded_answer(self, question: str, sources: List[SourceCitation]) -> str:
        if not sources:
            return "No relevant technical documentation context was found in the knowledge base to answer your query."
            
        context_blocks = []
        for idx, src in enumerate(sources, 1):
            source_tag = f"[Source {idx}: Page {src.page}]"
            context_blocks.append(f"{source_tag}\n{src.content_snippet}")
            
        context_str = "\n\n".join(context_blocks)
        
        prompt = f"""You are an expert Enterprise Technical Support Engineer. Answer the user's question clearly, thoroughly, and professionally using ONLY the provided technical knowledge base context.

INSTRUCTIONS:
1. Provide a direct, cohesive summary and clear step-by-step diagnostic or remediation procedures based strictly on the retrieved runbooks.
2. Cite sources inline where relevant using [Source X: Page Y] (e.g. commands, registry keys, diagnostic tools).
3. Format commands, file paths, registry keys, and event IDs in markdown code blocks or backticks.
4. Do NOT say "Based on the text" repeatedly; write naturally and authoritatively.
5. If the context does not contain enough detail to answer completely, answer what is present and state what additional details are needed.

=== RETRIEVED TECHNICAL CONTEXT ===
{context_str}

=== USER QUESTION ===
{question}

=== AUTHORITATIVE IT SUPPORT RESOLUTION ==="""

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_predict": 1024
            }
        }

        try:
            logger.info(f"Generating answer with Ollama model '{self.model_name}'...")
            # Allow up to 120 seconds for local LLM inference
            response = httpx.post(url, json=payload, timeout=120.0)
            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "").strip()
                if answer:
                    return answer
            else:
                logger.warning(f"Ollama returned status code {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"Ollama request error or timeout ({e}). Using structured context synthesis.")
            
        # Grounded context synthesis fallback if Ollama is unreachable
        fallback_lines = [
            f"### Technical Diagnostic Summary: {question}\n",
            "The following authoritative runbook guidance was retrieved from the Master Technical Knowledge Base:\n"
        ]
        for idx, src in enumerate(sources, 1):
            fallback_lines.append(f"#### Runbook Reference {idx} ([Source {idx}: Page {src.page}])")
            # Clean up snippet for better readability
            clean_lines = [line.strip() for line in src.content_snippet.splitlines() if line.strip()]
            formatted_snippet = "\n".join(clean_lines[:10])
            fallback_lines.append(f"{formatted_snippet}\n")
            
        return "\n".join(fallback_lines)

generation_service = GenerationService()
