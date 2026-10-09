"""Remote AI client for llama.cpp API."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

import httpx
from typing import Optional
from ...models import AIComparisonResponse, Visibility, HeadRelative, TorsoRelative, ChangeMagnitude


class AIClientError(Exception):
    """Base exception for AI client errors."""
    pass


class ConnectionError(AIClientError):
    """AI server connection error."""
    pass


class ValidationError(AIClientError):
    """AI response validation error."""
    pass


class AIClient:
    """Client for remote llama.cpp API."""
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        model: Optional[str] = None
    ):
        self.base_url = self._normalize_url(base_url)
        self.api_key = api_key
        self.timeout = timeout
        self.model = model or "Qwen/Qwen3-VL-4B-Instruct-GGUF:Q4_K_M"
        self._client: Optional[httpx.Client] = None
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL to always include /v1."""
        url = url.strip()
        if not url.endswith("/v1"):
            url += "/v1"
        return url
    
    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers={},
                timeout=self.timeout
            )
            if self.api_key:
                self._client.headers["Authorization"] = f"Bearer {self.api_key}"
        return self._client
    
    def _build_prompt(self, reference_image: bytes, current_image: bytes) -> str:
        """Build comparison prompt for AI model."""
        import base64
        
        def encode_image(img_data: bytes) -> str:
            return f"data:image/jpeg;base64,{base64.b64encode(img_data).decode()}"
        
        prompt = """You are a posture analysis assistant. Analyze these two images of the same person from a fixed webcam.

IMAGE_1 shows the reference sitting posture.
IMAGE_2 shows the current sitting posture.

Determine:
- Whether the head has moved forward relative to the shoulders.
- Whether the entire upper torso has moved toward the camera.
- Whether the head and torso are simply closer to the camera together.
- Whether the body is reclining backward.
- Whether there is insufficient visual evidence.

Important rules:
- Looking upward is not sufficient evidence of forward head posture.
- A larger head in the image does not prove forward head posture.
- Distinguish isolated head movement from whole-torso movement.
- Do not infer the shape of invisible body parts.
- Account for perspective differences.
- Do not classify normal reclining as bad posture.
- Return UNKNOWN whenever the distinction cannot be established.

Return ONLY valid JSON with no markdown formatting:
{
    "visibility": "SUFFICIENT" or "INSUFFICIENT",
    "head_relative_to_shoulders": "FORWARD" | "UNCHANGED" | "UNKNOWN",
    "torso_relative_to_reference": "FORWARD" | "UNCHANGED" | "BACKWARD" | "UNKNOWN",
    "change_magnitude": "NONE" | "SMALL" | "MODERATE" | "LARGE" | "UNKNOWN",
    "possible_camera_change": true or false,
    "visual_evidence": "short description",
    "observation_notes": "additional notes"
}
"""
        return prompt
    
    async def get_models(self) -> list[dict]:
        """Get available models from server."""
        async with httpx.AsyncClient(timeout=self.timeout) as async_client:
            try:
                response = await async_client.get(f"{self.base_url}/v1/models")
                response.raise_for_status()
                return response.json()
            except httpx.RequestError:
                raise ConnectionError(f"Failed to connect to AI server at {self.base_url}")
    
    async def test_connection(self) -> bool:
        """Test connection to AI server."""
        async with httpx.AsyncClient(timeout=self.timeout) as async_client:
            try:
                response = await async_client.get(f"{self.base_url}/v1/models")
                response.raise_for_status()
                return True
            except httpx.RequestError:
                return False
    
    async def compare_postures(
        self,
        reference_image: bytes,
        current_image: bytes,
        max_tokens: int = 200,
        temperature: float = 0.0
    ) -> AIComparisonResponse:
        """Compare two images and return structured analysis."""
        async with httpx.AsyncClient(timeout=self.timeout) as async_client:
            try:
                # Build multi-image content
                content = [
                    {
                        "type": "text",
                        "text": self._build_prompt(reference_image, current_image)
                    }
                ]
                
                # Add images as separate messages for better handling
                content = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "IMAGE_1: Reference posture"},
                            {"type": "image", "image": encode_image(reference_image)},
                            {"type": "text", "text": "IMAGE_2: Current posture"},
                            {"type": "image", "image": encode_image(current_image)},
                            {"type": "text", "text": "Compare these images and return ONLY valid JSON with no markdown formatting. Use the schema defined above."}
                        ]
                    }
                ]
                
                response = await async_client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json={
                        "model": self.model,
                        "messages": content,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "response_format": {"type": "json_object"}
                    }
                )
                response.raise_for_status()
                
                try:
                    data = response.json()
                    choices = data.get("choices", [])
                    if not choices:
                        raise ValidationError("No choices in response")
                    
                    raw_response = choices[0].message.content
                    parsed = AIComparisonResponse.model_validate_json(raw_response)
                    return parsed
                    
                except json.JSONDecodeError:
                    raise ValidationError("Invalid JSON response from AI")
                    
            except httpx.RequestError:
                raise ConnectionError(f"Failed to connect to AI server")
            except AIComparisonResponseValidationError:
                raise ValidationError("Failed to parse AI response")
