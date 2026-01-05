"""
Voice Selector Service
Automatically selects the best ElevenLabs voice based on content type
"""
from typing import Dict, List, Optional
from loguru import logger

from elevenlabs import ElevenLabs

from app.core.config import settings


class VoiceSelectorService:
    """
    Service to automatically select the best voice for content
    based on topic, mood, and available voices
    """
    
    # Voice preferences based on content mood
    # These are general characteristics to look for in voice metadata
    MOOD_VOICE_PREFERENCES = {
        "dramatic": {
            "style": ["dramatic", "intense", "powerful", "deep"],
            "gender_preference": "male",
            "age_preference": ["middle-aged", "mature"]
        },
        "suspense": {
            "style": ["mysterious", "calm", "intense", "whispery"],
            "gender_preference": "male",
            "age_preference": ["young", "middle-aged"]
        },
        "inspiring": {
            "style": ["warm", "inspiring", "confident", "clear"],
            "gender_preference": None,  # Either works
            "age_preference": ["middle-aged", "mature"]
        },
        "emotional": {
            "style": ["emotional", "expressive", "warm", "soft"],
            "gender_preference": None,
            "age_preference": ["young", "middle-aged"]
        },
        "adventure": {
            "style": ["energetic", "exciting", "dynamic", "bold"],
            "gender_preference": "male",
            "age_preference": ["young", "middle-aged"]
        }
    }
    
    # Known good Hindi voices on ElevenLabs (manually curated)
    # These are popular voices that work well for Hindi content
    RECOMMENDED_HINDI_VOICES = [
        {
            "voice_id": "pNInz6obpgDQGcFmaJgB",  # Adam
            "name": "Adam",
            "best_for": ["dramatic", "suspense", "adventure"],
            "description": "Deep male voice, great for intense narration"
        },
        {
            "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella
            "name": "Bella", 
            "best_for": ["emotional", "inspiring"],
            "description": "Warm female voice, good for emotional content"
        },
        {
            "voice_id": "ErXwobaYiN019PkySvjV",  # Antoni
            "name": "Antoni",
            "best_for": ["dramatic", "adventure", "inspiring"],
            "description": "Young male voice, energetic and clear"
        },
        {
            "voice_id": "VR6AewLTigWG4xSOukaG",  # Arnold
            "name": "Arnold",
            "best_for": ["dramatic", "suspense"],
            "description": "Deep authoritative voice"
        },
        {
            "voice_id": "onwK4e9ZLuTAKqWW03F9",  # Daniel
            "name": "Daniel",
            "best_for": ["inspiring", "emotional", "dramatic"],
            "description": "British accent, very clear, works well with Hindi"
        },
    ]
    
    def __init__(self):
        self.client = None
        self.cached_voices = None
    
    def _get_client(self) -> ElevenLabs:
        """Get or create ElevenLabs client"""
        if self.client is None:
            self.client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        return self.client
    
    async def select_voice(self, mood: str, topic: str = "") -> str:
        """
        Select the best voice for the given mood and topic
        Returns the voice_id
        """
        logger.info(f"Selecting voice for mood: {mood}, topic: {topic}")
        
        # First, try to get voices from API
        available_voices = await self._get_available_voices()
        
        if available_voices:
            # Score each voice based on mood preferences
            best_voice = self._score_and_select_voice(available_voices, mood)
            if best_voice:
                logger.info(f"Selected voice: {best_voice.get('name', 'Unknown')} ({best_voice['voice_id']})")
                return best_voice['voice_id']
        
        # Fallback to recommended voices
        recommended = self._get_recommended_voice(mood)
        logger.info(f"Using recommended voice: {recommended['name']} ({recommended['voice_id']})")
        return recommended['voice_id']
    
    async def _get_available_voices(self) -> List[Dict]:
        """Get list of available voices from ElevenLabs"""
        
        if self.cached_voices:
            return self.cached_voices
        
        try:
            client = self._get_client()
            voices_response = client.voices.get_all()
            
            voices = []
            for voice in voices_response.voices:
                voice_data = {
                    'voice_id': voice.voice_id,
                    'name': voice.name,
                    'labels': voice.labels or {},
                    'description': getattr(voice, 'description', ''),
                    'preview_url': getattr(voice, 'preview_url', ''),
                }
                voices.append(voice_data)
            
            self.cached_voices = voices
            logger.info(f"Found {len(voices)} available voices")
            return voices
            
        except Exception as e:
            logger.error(f"Failed to get voices from ElevenLabs: {e}")
            return []
    
    def _score_and_select_voice(self, voices: List[Dict], mood: str) -> Optional[Dict]:
        """Score voices based on mood preferences and select the best one"""
        
        preferences = self.MOOD_VOICE_PREFERENCES.get(mood, self.MOOD_VOICE_PREFERENCES['dramatic'])
        
        scored_voices = []
        
        for voice in voices:
            score = 0
            labels = voice.get('labels', {})
            name = voice.get('name', '').lower()
            description = voice.get('description', '').lower()
            
            # Check for style matches
            for style in preferences.get('style', []):
                if style in str(labels).lower() or style in description:
                    score += 10
            
            # Check gender preference
            gender_pref = preferences.get('gender_preference')
            if gender_pref:
                voice_gender = labels.get('gender', '').lower()
                if voice_gender == gender_pref:
                    score += 5
            
            # Check age preference
            age_prefs = preferences.get('age_preference', [])
            voice_age = labels.get('age', '').lower()
            if any(age in voice_age for age in age_prefs):
                score += 3
            
            # Bonus for multilingual voices (better for Hindi)
            if 'multilingual' in str(labels).lower() or 'hindi' in str(labels).lower():
                score += 15
            
            # Check if it's in our recommended list
            for rec in self.RECOMMENDED_HINDI_VOICES:
                if rec['voice_id'] == voice['voice_id']:
                    if mood in rec.get('best_for', []):
                        score += 20
                    else:
                        score += 10
                    break
            
            scored_voices.append((voice, score))
        
        # Sort by score descending
        scored_voices.sort(key=lambda x: x[1], reverse=True)
        
        if scored_voices and scored_voices[0][1] > 0:
            return scored_voices[0][0]
        
        return None
    
    def _get_recommended_voice(self, mood: str) -> Dict:
        """Get a recommended voice based on mood"""
        
        # Find best matching recommended voice
        for voice in self.RECOMMENDED_HINDI_VOICES:
            if mood in voice.get('best_for', []):
                return voice
        
        # Default to first recommended voice
        return self.RECOMMENDED_HINDI_VOICES[0]
    
    async def list_all_voices(self) -> List[Dict]:
        """List all available voices with details"""
        voices = await self._get_available_voices()
        
        result = []
        for voice in voices:
            result.append({
                'voice_id': voice['voice_id'],
                'name': voice['name'],
                'labels': voice.get('labels', {}),
                'recommended_for': self._get_recommended_moods(voice['voice_id'])
            })
        
        return result
    
    def _get_recommended_moods(self, voice_id: str) -> List[str]:
        """Get recommended moods for a voice"""
        for rec in self.RECOMMENDED_HINDI_VOICES:
            if rec['voice_id'] == voice_id:
                return rec.get('best_for', [])
        return []


# Singleton instance
voice_selector = VoiceSelectorService()

