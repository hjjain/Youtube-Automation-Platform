"""
Voiceover Generation Service - ElevenLabs
Generates Hindi voiceover using ElevenLabs API
With DYNAMIC voice selection based on content mood
"""
import httpx
import asyncio
from pathlib import Path
from typing import Optional
from loguru import logger

from app.core.config import settings
from app.models.video import VideoScript


class VoiceoverGeneratorService:
    """
    Service to generate Hindi voiceover using ElevenLabs
    Dynamically selects voice based on content mood
    """
    
    # ElevenLabs API
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    # BUNTY - Reel Perfect Voice (Hindi, optimized for reels)
    DEFAULT_VOICE_ID = "FZkK3TvQ0pjyDmT8fzIW"
    
    # Voice settings optimized for CLEAR Hindi pronunciation
    VOICE_SETTINGS = {
        "stability": 0.7,         # HIGH - clearer pronunciation
        "similarity_boost": 0.75,
        "style": 0.15,            # LOW - focused on clarity, not expression
        "use_speaker_boost": True
    }
    
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
    
    async def generate_voiceover(
        self,
        script: VideoScript,
        project_id: str,
        voice_id: Optional[str] = None
    ) -> str:
        """
        Generate voiceover for the script
        Uses BUNTY - Reel Perfect Voice for all videos
        Returns path to the audio file
        """
        logger.info(f"🎙️ Generating Hindi voiceover for project {project_id}")
        
        # Use Bunty - Reel Perfect Voice (or override if provided)
        selected_voice = voice_id or self.DEFAULT_VOICE_ID
        logger.info(f"   🎤 Voice: Bunty - Reel Perfect ({selected_voice[:12]}...)")
        logger.info(f"   ⚙️  Settings: stability=0.7, style=0.15 (optimized for clarity)")
        
        # Prepare the narration text
        narration_text = self._prepare_narration(script)
        logger.info(f"   📝 Narration length: {len(narration_text)} characters")
        
        try:
            # Call ElevenLabs API
            audio_data = await self._generate_audio(narration_text, selected_voice)
            
            # Save audio file
            project_dir = settings.TEMP_DIR / project_id
            project_dir.mkdir(parents=True, exist_ok=True)
            output_path = project_dir / "voiceover.mp3"
            
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            logger.info(f"   ✅ Voiceover saved: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ Voiceover generation failed: {e}")
            raise
    
    def _prepare_narration(self, script: VideoScript) -> str:
        """
        Prepare narration text for TTS
        Adds natural pauses and formatting for better speech
        """
        narration_parts = []
        
        for segment in script.segments:
            text = segment.narration_text.strip()
            if text:
                narration_parts.append(text)
        
        # Join with pauses (... creates natural pause in ElevenLabs)
        full_text = "\n\n".join(narration_parts)
        
        return full_text
    
    async def _generate_audio(self, text: str, voice_id: str) -> bytes:
        """Call ElevenLabs TTS API"""
        
        url = f"{self.BASE_URL}/text-to-speech/{voice_id}"
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "voice_id": voice_id,
            "model_id": "eleven_multilingual_v2",  # Best for Hindi
            "voice_settings": self.VOICE_SETTINGS
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                raise Exception(f"ElevenLabs API failed: {response.text}")
            
            return response.content
    
    async def list_available_voices(self) -> list:
        """List available voices from ElevenLabs"""
        
        url = f"{self.BASE_URL}/voices"
        headers = {"xi-api-key": self.api_key}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code != 200:
                    return []
                
                data = response.json()
                voices = data.get("voices", [])
                
                return [
                    {
                        "voice_id": v.get("voice_id"),
                        "name": v.get("name"),
                        "labels": v.get("labels", {})
                    }
                    for v in voices
                ]
                
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return []


# Singleton instance
voiceover_generator = VoiceoverGeneratorService()
