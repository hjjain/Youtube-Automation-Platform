"""
Configuration settings for the Viral Reel Creator Platform
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # ===========================================
    # API Keys
    # ===========================================
    REPLICATE_API_TOKEN: str = ""
    ELEVENLABS_API_KEY: str = ""
    YOUTUBE_API_KEY: Optional[str] = None
    JAMENDO_CLIENT_ID: Optional[str] = None  # Free! Get from jamendo.com/developers
    
    # ===========================================
    # ElevenLabs Voice Settings
    # ===========================================
    # Default Hindi voice optimized for narration
    ELEVENLABS_VOICE_ID: str = "yoZ06aMxZJJ28mfd3POQ"
    
    # ===========================================
    # Video Settings
    # ===========================================
    VIDEO_DURATION_SECONDS: int = 40
    VIDEO_WIDTH: int = 1080
    VIDEO_HEIGHT: int = 1920
    FPS: int = 30
    
    # ===========================================
    # Image Generation
    # ===========================================
    IMAGES_PER_VIDEO: int = 8
    # SeeDream 4.5 model on Replicate
    IMAGE_MODEL: str = "bytedance/seedream-4.5"
    
    # ===========================================
    # Video Generation
    # ===========================================
    # Kling v2.1 model on Replicate
    VIDEO_MODEL: str = "kwaivgi/kling-v2.1"
    VIDEO_CLIP_DURATION: int = 5  # seconds per clip
    
    # ===========================================
    # LLM Model (GPT-5.2 on Replicate)
    # ===========================================
    SCRIPT_MODEL: str = "openai/gpt-5.2"
    LLM_REASONING_EFFORT: str = "medium"  # low, medium, high
    LLM_VERBOSITY: str = "medium"  # low, medium, high
    
    # ===========================================
    # Paths
    # ===========================================
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    OUTPUT_DIR: Path = Path("./output")
    MUSIC_DIR: Path = Path("./music")
    TEMP_DIR: Path = Path("./temp")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Convert relative paths to absolute
        self.OUTPUT_DIR = self.BASE_DIR / self.OUTPUT_DIR
        self.MUSIC_DIR = self.BASE_DIR / self.MUSIC_DIR
        self.TEMP_DIR = self.BASE_DIR / self.TEMP_DIR
        
        # Create directories if they don't exist
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.MUSIC_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
