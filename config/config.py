import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # Application Configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50"))  # MB
    MAX_ROWS: int = int(os.getenv("MAX_ROWS", "1000"))
    
    # SQL Configuration
    SQL_TIMEOUT: int = int(os.getenv("SQL_TIMEOUT", "30"))  # seconds
    MAX_SQL_CANDIDATES: int = int(os.getenv("MAX_SQL_CANDIDATES", "3"))
    
    # Streamlit Configuration
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8000"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        return True