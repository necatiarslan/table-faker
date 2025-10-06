"""
LLM client for generating semantic descriptions using OpenAI-compatible APIs.
"""
import yaml
import json
from os import path
from typing import Optional, Dict, Any


class LLMClient:
    """Client for interacting with OpenAI-compatible LLM APIs."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize LLM client with configuration.
        
        Args:
            config_path: Path to llm.config file (YAML). If None, looks for llm.config in current dir.
        """
        self.config = self._load_config(config_path)
        self.api_key = self.config.get("api_key") or "not-required"
        
        # Handle base_url - strip /chat/completions if present
        base_url = self.config.get("base_url", "https://api.openai.com/v1")
        if base_url.endswith("/chat/completions"):
            base_url = base_url[:-len("/chat/completions")]
        self.base_url = base_url
        
        self.model = self.config.get("model", "gpt-4")
        
        # Optional parameters - only set if provided
        self.temperature = self.config.get("temperature")
        self.max_tokens = self.config.get("max_tokens")
        
        # Lazy import to avoid requiring openai if not used
        self._client = None
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load LLM configuration from YAML file."""
        if config_path is None:
            # Look for llm.config in current directory
            if path.exists("llm.config"):
                config_path = "llm.config"
            elif path.exists("llm.config.yaml"):
                config_path = "llm.config.yaml"
            else:
                # Return default config
                return {
                    "enabled": False,
                    "api_key": None,
                    "base_url": "https://api.openai.com/v1",
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 500
                }
        
        if not path.exists(config_path):
            raise FileNotFoundError(f"LLM config file not found: {config_path}")
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        return config or {}
    
    def is_enabled(self) -> bool:
        """Check if LLM is enabled and configured."""
        return self.config.get("enabled", False)
    
    def _get_client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            try:
                openai = __import__("openai")
                self._client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                raise ImportError(
                    "openai package is required for LLM integration. "
                    "Install it with: pip install openai"
                )
        return self._client
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context
        
        Returns:
            Generated text response
        """
        if not self.is_enabled():
            raise RuntimeError("LLM is not enabled or configured")
        
        client = self._get_client()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Build request parameters, only including optional params if they're set
        request_params = {
            "model": self.model,
            "messages": messages
        }
        
        if self.temperature is not None:
            request_params["temperature"] = self.temperature
        if self.max_tokens is not None:
            request_params["max_tokens"] = self.max_tokens
        
        try:
            response = client.chat.completions.create(**request_params)
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"LLM API call failed: {str(e)}")
    
    def generate_table_description(self, table_name: str, column_names: list) -> str:
        """Generate a description for a database table."""
        system_prompt = (
            "You are a data analyst expert. Generate concise, business-friendly "
            "descriptions for database tables based on their name and columns."
        )
        
        prompt = f"""Generate a brief 1-2 sentence description for a database table.

Table Name: {table_name}
Columns: {', '.join(column_names)}

Describe what business entity or concept this table represents and what kind of data it contains.
Only return the description text, no additional formatting or explanation."""
        
        return self.generate(prompt, system_prompt)
    
    def generate_column_description(self, table_name: str, column_name: str,
                                   column_type: str, data_expression: str,
                                   classification: str) -> str:
        """Generate a description for a database column."""
        # Skip LLM for obvious ID fields
        col_lower = column_name.lower()
        if col_lower == 'id' or col_lower.endswith('_id'):
            if col_lower == 'id':
                return f"Unique identifier for {table_name}"
            else:
                # Extract referenced table name from foreign key column
                ref_table = col_lower[:-3]  # Remove '_id' suffix
                return f"Foreign key reference to {ref_table}"
        
        system_prompt = (
            "You are a data analyst expert. Generate concise, business-friendly "
            "descriptions for database columns based on their context."
        )
        
        # Truncate data expression if too long
        data_expr_preview = data_expression[:200] if data_expression else "N/A"
        
        prompt = f"""Generate a brief 1-2 sentence description for a database column.

Table: {table_name}
Column: {column_name}
Data Type: {column_type}
Classification: {classification}
Generation Logic: {data_expr_preview}

Describe what this column represents in business terms. Focus on the business meaning, not technical details.
Only return the description text, no additional formatting or explanation."""
        
        return self.generate(prompt, system_prompt)
    
    def generate_model_description(self, table_names: list) -> str:
        """Generate a description for the semantic model."""
        system_prompt = (
            "You are a data analyst expert. Generate concise descriptions for "
            "semantic models based on the tables they contain."
        )
        
        prompt = f"""Generate a brief 1-2 sentence description for a semantic model.

Tables included: {', '.join(table_names)}

Describe what business domain or analytical capability this semantic model provides.
Only return the description text, no additional formatting or explanation."""
        
        return self.generate(prompt, system_prompt)
    
    def generate_synonyms(self, name: str, description: str, count: int = 3) -> list:
        """Generate synonyms for a field name."""
        system_prompt = (
            "You are a data analyst expert. Generate alternative names/phrases "
            "that users might use to refer to database fields."
        )
        
        prompt = f"""Generate {count} alternative names or phrases for this field.

Field Name: {name}
Description: {description}

Provide {count} common alternative terms that business users might use to refer to this field.
Return only the synonyms as a comma-separated list, no additional text."""
        
        response = self.generate(prompt, system_prompt)
        # Parse comma-separated list
        synonyms = [s.strip().strip('"').strip("'") for s in response.split(",")]
        return [s for s in synonyms if s][:count]


def create_sample_config(output_path: str = "llm.config"):
    """
    Copy the llm.config.example file to create a sample config.
    This ensures users get the properly formatted example with all comments.
    """
    example_path = path.join(path.dirname(__file__), "..", "llm.config.example")
    
    if not path.exists(example_path):
        raise FileNotFoundError(
            f"llm.config.example not found at {example_path}. "
            "Please ensure llm.config.example exists in the project root."
        )
    
    # Copy the example file
    with open(example_path, "r", encoding="utf-8") as src:
        content = src.read()
    
    with open(output_path, "w", encoding="utf-8") as dest:
        dest.write(content)
    
    return output_path