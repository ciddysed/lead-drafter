"""
Configuration loader. Reads secrets from environment variables ONLY —
never hardcode keys in source. Copy .env.example to .env and fill in
your own values before running anything.
"""
import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional; env vars can be set directly instead


@dataclass
class Config:
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")  # "openai" or "anthropic"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    google_sheets_creds_path: str = os.getenv("GOOGLE_SHEETS_CREDS_PATH", "credentials.json")
    google_sheet_id: str = os.getenv("GOOGLE_SHEET_ID", "")
    review_confidence_threshold: float = float(os.getenv("REVIEW_CONFIDENCE_THRESHOLD", "0.75"))

    def validate(self):
        missing = []
        if self.llm_provider == "openai" and not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")
        if not self.google_sheet_id:
            missing.append("GOOGLE_SHEET_ID")
        if missing:
            raise RuntimeError(
                f"Missing required config: {', '.join(missing)}. "
                f"Set these in your .env file (see .env.example)."
            )


config = Config()
