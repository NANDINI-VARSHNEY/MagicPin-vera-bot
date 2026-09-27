import os
from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "Vera Bot - magicpin AI Challenge"
    team_name: str = os.environ.get("TEAM_NAME", "Team Antigravity")
    team_members: list[str] = ["Nishant Gupta"]
    contact_email: str = os.environ.get("CONTACT_EMAIL", "nishant@example.com")
    version: str = "1.0.0"
    
    # LLM Settings
    llm_provider: str = os.environ.get("LLM_PROVIDER", "gemini")  # gemini, openai, anthropic, groq, deepseek, ollama, or none
    llm_model: str = os.environ.get("LLM_MODEL", "")
    llm_api_key: str = os.environ.get("LLM_API_KEY", os.environ.get("GEMINI_API_KEY", os.environ.get("OPENAI_API_KEY", "")))
    llm_timeout: float = 6.0  # Keep tight so tick/reply finishes in << 30s
    
    # Proactive Tick limits
    max_actions_per_tick: int = 10
    cooldown_seconds_per_merchant: int = 300

settings = Settings()
