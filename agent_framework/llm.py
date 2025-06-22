"""LLM client for the agent framework."""
import json
import base64
from typing import Dict, Any, Optional, Union, List
import requests
from pathlib import Path

from .config import OPENROUTER_API_KEY, MODEL_NAME, MODEL_TEMPERATURE, MODEL_MAX_TOKENS
from .actions import Action, ALL_ACTION_TYPES
from .prompts.system import SYSTEM_PROMPT

class LLMClient:
    """Client for interacting with LLMs via OpenRouter."""
    
    def __init__(self, model: str = MODEL_NAME, temperature: float = MODEL_TEMPERATURE):
        """Initialize the LLM client.
        
        Args:
            model: The model to use (e.g., 'openai/gpt-4-turbo')
            temperature: Sampling temperature (0-1)
        """
        self.api_key = OPENROUTER_API_KEY
        self.model = model
        self.temperature = temperature
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _encode_image(self, image_path: Union[str, Path]) -> str:
        """Encode an image to base64."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _process_image(self, image: Union[str, bytes, None]) -> Optional[Dict[str, str]]:
        """
        Process an image for the API request.
        
        Args:
            image: Base64-encoded image string or bytes
            
        Returns:
            Formatted image data for the API or None if invalid
        """
        if not image:
            return None
            
        try:
            if isinstance(image, bytes):
                # Convert bytes to base64 string
                image_data = base64.b64encode(image).decode('utf-8')
            elif isinstance(image, str):
                # Assume it's already base64 encoded
                image_data = image
            else:
                self.log(f"Unsupported image type: {type(image)}")
                return None
                
            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_data}"
                }
            }
            
        except Exception as e:
            self.log(f"Error processing image: {str(e)}")
            return None
    
    def _process_html(self, html: Optional[str]) -> Optional[Dict[str, str]]:
        """Process HTML content for the API request."""
        if not html:
            return None
            
        return {
            "type": "text",
            "text": f"Current page HTML (simplified):\n{html[:4000]}..."  # Truncate to avoid token limits
        }
    
    def get_next_action(
        self,
        prompt: str,
        image: Optional[Union[str, bytes]] = None,
        html: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get the next action from the LLM.
        
        Args:
            prompt: The user's prompt/instruction
            image: Optional base64-encoded image string or bytes for vision models
            html: Optional HTML content of the current page
            
        Returns:
            Dictionary containing the action and reasoning
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": []}
        ]
        
        # Add text prompt
        messages[1]["content"].append({"type": "text", "text": prompt})
        
        # Add HTML content if provided
        if html_content := self._process_html(html):
            messages[1]["content"].append(html_content)
        
        # Handle image - can be base64 string or bytes
        if image:
            if isinstance(image, str):
                # Already base64 string
                image_data = image
            elif isinstance(image, bytes):
                # Convert bytes to base64 string
                image_data = base64.b64encode(image).decode('utf-8')
            else:
                self.log(f"Unsupported image type: {type(image)}")
                image_data = None
                
            if image_data:
                messages[1]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_data}"
                    }
                })
        
        # If content is a list with a single item, unwrap it
        if len(messages[1]["content"]) == 1:
            messages[1]["content"] = messages[1]["content"][0]["text"]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": MODEL_MAX_TOKENS,
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse the JSON response
            try:
                action_data = json.loads(content)
                action = action_data.get("action", {})
                
                # Validate action type
                action_type = action.get("action_type")
                if action_type not in ALL_ACTION_TYPES:
                    return {
                        "action": {"action_type": "error", "message": f"Invalid action type: {action_type}"},
                        "reasoning": f"Received invalid action type: {action_type}"
                    }
                
                return action_data
                
            except json.JSONDecodeError:
                return {
                    "action": {"action_type": "error", "message": "Invalid JSON response from LLM"},
                    "reasoning": "The response could not be parsed as JSON"
                }
                
        except Exception as e:
            return {
                "action": {"action_type": "error", "message": str(e)},
                "reasoning": f"Error calling OpenRouter API: {str(e)}"
            }
