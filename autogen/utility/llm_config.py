# llm_config.py
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class AzureOpenAIConfig:
    model: str
    api_type: str = "azure"
    max_tokens: int = 2000
    api_version: str = "2024-02-15-preview"
    base_url: Optional[str] = None
    azure_ad_token_provider: Optional[Any] = None

@dataclass
class OpenAIConfig:
    model: str
    api_key: Optional[str] = None

class LLMConfigurationError(Exception):
    """Custom exception for LLM configuration errors"""
    pass

class LLMConfig:
    def __init__(
        self, 
        seed: int = 42,
        temperature: float = 0,
        is_azure_open_ai: bool = True,
        model_name: str = "gpt-4"
    ):
        self.seed = seed
        self.temperature = temperature
        self.is_azure_open_ai = is_azure_open_ai
        self.model_name = model_name
        self.config_list = self._initialize_config()

    def _initialize_config(self) -> List[Dict[str, Any]]:
        """Initialize the configuration based on the provider"""
        try:
            if self.is_azure_open_ai:
                return self._get_azure__openai_config()
            return self._get_openai_config()
        except Exception as e:
            raise LLMConfigurationError(f"Failed to initialize config: {str(e)}")

    def _get_azure__openai_config(self) -> List[Dict[str, Any]]:
        """Get Azure OpenAI configuration"""
        azure_endpoint = os.getenv("AZURE_OPENAI_API_URI")
        if not azure_endpoint:
            raise LLMConfigurationError("Azure OpenAI endpoint not found in environment variables")

        try:
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(),
                "https://cognitiveservices.azure.com/.default"
            )
        except Exception as e:
            raise LLMConfigurationError(f"Failed to initialize Azure credentials: {str(e)}")

        config = AzureOpenAIConfig(
            model=self.model_name,
            base_url=azure_endpoint,
            azure_ad_token_provider=token_provider
        )
        return [config.__dict__]

    def _get_openai_config(self) -> List[Dict[str, Any]]:
        """Get OpenAI configuration"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMConfigurationError("OpenAI API key not found in environment variables")

        config = OpenAIConfig(
            model=self.model_name,
            api_key=api_key
        )
        return [config.__dict__]

    @property
    def llm_config(self) -> Dict[str, Any]:
        """Get the complete LLM configuration"""
        return {
            "seed": self.seed,
            "temperature": self.temperature,
            "config_list": self.config_list
        }
    
