import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Repository Intelligence Platform API"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api"
    
    # GitHub API configuration
    GITHUB_API_BASE_URL: str = "https://api.github.com"
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "").strip()
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        origin.strip() 
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173").split(",")
        if origin.strip()
    ]
    
    # Network timeout for external calls (seconds)
    REQUEST_TIMEOUT_SECONDS: float = 12.0

settings = Settings()
