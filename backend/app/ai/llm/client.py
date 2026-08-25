import os
import logging
import re
from typing import Optional, List
import httpx
from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.ai import ChatMessage, AIChatResponse

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Multi-Provider LLM Client supporting:
    1. Ollama (100% Free, Local LLM running on your Mac - $0 Cost, No API Key needed)
    2. Google Gemini API (Cloud LLM)
    3. Dev Fallback Mock (If offline)
    """
    DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
    PRICE_PER_1K_INPUT = 0.000075
    PRICE_PER_1K_OUTPUT = 0.000300

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        self._gemini_client: Optional[genai.Client] = None

        if self.api_key and self.api_key != "your_gemini_api_key_here":
            try:
                self._gemini_client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")

    async def generate_chat_response(
        self,
        prompt: str,
        system_instruction: str = "You are a helpful Enterprise AI assistant.",
        temperature: float = 0.7,
        history: Optional[List[ChatMessage]] = None
    ) -> AIChatResponse:
        """
        Routes generation to Ollama (Local Free LLM) or Gemini API based on settings.
        """
        if self.provider == "ollama":
            return await self._generate_ollama_response(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                history=history
            )
        elif self.provider == "gemini" and self._gemini_client:
            return await self._generate_gemini_response(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                history=history
            )
        else:
            return self._generate_mock_response(prompt, system_instruction)

    async def _generate_ollama_response(
        self,
        prompt: str,
        system_instruction: str,
        temperature: float,
        history: Optional[List[ChatMessage]]
    ) -> AIChatResponse:
        """
        Calls local Ollama instance running on your Mac at http://localhost:11434 ($0 Cost).
        """
        ollama_url = f"{settings.OLLAMA_HOST}/api/generate"
        model_name = settings.OLLAMA_MODEL

        full_prompt = f"System: {system_instruction}\n"
        if history:
            for msg in history:
                full_prompt += f"{msg.role.capitalize()}: {msg.content}\n"
        full_prompt += f"User: {prompt}\nAssistant:"

        payload = {
            "model": model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {"temperature": temperature}
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(ollama_url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    answer_text = data.get("response", "")
                    input_tokens = data.get("prompt_eval_count", len(full_prompt.split()))
                    output_tokens = data.get("eval_count", len(answer_text.split()))

                    return AIChatResponse(
                        answer=answer_text,
                        model_name=f"ollama/{model_name} (Local $0)",
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        total_tokens=input_tokens + output_tokens,
                        estimated_cost_usd=0.0,
                    )
                else:
                    return self._generate_mock_response(prompt, system_instruction, provider_note="Ollama returned error")

        except Exception as e:
            return self._generate_mock_response(
                prompt,
                system_instruction,
                provider_note="Ollama is offline. Dev fallback activated."
            )

    async def _generate_gemini_response(
        self,
        prompt: str,
        system_instruction: str,
        temperature: float,
        history: Optional[List[ChatMessage]]
    ) -> AIChatResponse:
        contents = []
        if history:
            for msg in history:
                contents.append(types.Content(
                    role="user" if msg.role == "user" else "model",
                    parts=[types.Part.from_text(text=msg.content)]
                ))
        contents.append(prompt)

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
        )

        response = self._gemini_client.models.generate_content(
            model=self.DEFAULT_GEMINI_MODEL,
            contents=contents,
            config=config
        )

        answer_text = response.text or ""
        input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) if hasattr(response, "usage_metadata") else len(prompt.split()) * 2
        output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) if hasattr(response, "usage_metadata") else len(answer_text.split()) * 2
        total_tokens = input_tokens + output_tokens
        cost_usd = (input_tokens / 1000.0) * self.PRICE_PER_1K_INPUT + (output_tokens / 1000.0) * self.PRICE_PER_1K_OUTPUT

        return AIChatResponse(
            answer=answer_text,
            model_name=self.DEFAULT_GEMINI_MODEL,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=round(cost_usd, 6),
        )

    def _generate_mock_response(self, prompt: str, system_instruction: str, provider_note: str = "") -> AIChatResponse:
        """
        Zero-cost intelligent mock generator for testing agent reasoning loops and tool execution.
        """
        prompt_lower = prompt.lower()

        # If system instruction specifies tools and tool observation is not yet present:
        if "TOOL OBSERVATION RESULT" not in prompt:
            if "emp-" in prompt_lower or "employee" in prompt_lower:
                emp_match = re.search(r"emp-\d+", prompt_lower)
                emp_id = emp_match.group(0).upper() if emp_match else "EMP-9942"
                answer = f'{{"tool": "get_employee_info", "args": {{"identifier": "{emp_id}"}}}}'
            elif "sales" in prompt_lower or "revenue" in prompt_lower:
                answer = '{"tool": "get_sales_report", "args": {"period": "Q3"}}'
            elif "ticket" in prompt_lower or "support" in prompt_lower:
                priority = "urgent" if "urgent" in prompt_lower else "high"
                answer = f'{{"tool": "create_support_ticket", "args": {{"title": "Server Down", "priority": "{priority}"}}}}'
            elif "search" in prompt_lower or "policy" in prompt_lower or "document" in prompt_lower:
                answer = '{"tool": "search_documents", "args": {"query": "policy"}}'
            else:
                answer = f"[LOCAL $0 DEV RESPONSE]: Received prompt: '{prompt}'."
        else:
            answer = f"Based on the tool results: I have processed the request for '{prompt.splitlines()[-1]}'."

        in_t = len(prompt.split()) + len(system_instruction.split())
        out_t = len(answer.split())
        return AIChatResponse(
            answer=answer,
            model_name="local-free-mock",
            input_tokens=in_t,
            output_tokens=out_t,
            total_tokens=in_t + out_t,
            estimated_cost_usd=0.0,
        )


llm_client = LLMClient()
