"""
Ollama API client for Invoice Data Extractor.
Handles communication with local Ollama instance for text generation.
"""
import requests
import json
from typing import List, Dict, Any, Optional
from src.logger import setup_logger

logger = setup_logger(__name__)

class OllamaClient:
    """Client for interacting with local Ollama service."""
    
    def __init__(self, base_url: str):
        """
        Initialize the Ollama client.
        
        Args:
            base_url: Base URL of the Ollama service (e.g., http://localhost:11434)
        """
        self.base_url = base_url.rstrip('/')
        logger.info(f"Ollama client initialized with base URL: {self.base_url}")
        
    def list_models(self) -> List[str]:
        """
        Fetch the list of available local models from Ollama.
        
        Returns:
            List of model names
        """
        try:
            logger.debug(f"Fetching tags from {self.base_url}/api/tags")
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                logger.info(f"Found {len(models)} local Ollama models")
                return models
            else:
                logger.warning(f"Failed to fetch Ollama models. Status: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error connecting to Ollama: {e}")
            return []
            
    def generate(self, model: str, prompt: str, system: str = "", options: Dict[str, Any] = None) -> Optional[str]:
        """
        Generate text using an Ollama model.
        
        Args:
            model: Name of the model to use
            prompt: User prompt
            system: System instruction
            options: Additional generation options (temperature, top_p, etc.)
            
        Returns:
            Generated text or None if failed
        """
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": options or {}
            }
            
            logger.info(f"Sending generation request to Ollama model: {model}")
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '')
                logger.debug(f"Ollama generation response: {generated_text[:100]}...")
                return generated_text
            else:
                logger.error(f"Ollama generation failed with status {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Ollama generation request failed: {e}")
            return None

    def is_available(self) -> bool:
        """
        Check if Ollama service is reachable.
        
        Returns:
            True if service is reachable
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
