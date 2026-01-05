"""
Music Service - LOCAL MUSIC ONLY
Selects background music from local music/ folder based on mood
No external APIs - uses manually provided songs
"""
import os
import random
from pathlib import Path
from typing import Optional, List, Dict
from loguru import logger
import shutil

from app.core.config import settings
from app.models.video import MusicMood


class MusicService:
    """
    Service to select background music from local files
    Organizes music by mood in the music/ directory
    
    Directory structure:
    music/
    ├── dramatic/
    │   ├── epic_battle.mp3
    │   └── intense_moment.mp3
    ├── suspense/
    │   ├── mystery.mp3
    │   └── tension.mp3
    ├── inspiring/
    │   ├── uplifting.mp3
    │   └── hope.mp3
    ├── emotional/
    │   └── sad_piano.mp3
    └── general/
        └── ambient.mp3
    """
    
    def __init__(self):
        self.music_dir = settings.MUSIC_DIR
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create mood-based subdirectories if they don't exist"""
        for mood in MusicMood:
            mood_dir = self.music_dir / mood.value
            mood_dir.mkdir(parents=True, exist_ok=True)
        
        # Also create a general folder
        general_dir = self.music_dir / "general"
        general_dir.mkdir(parents=True, exist_ok=True)
    
    async def get_background_music(
        self,
        mood: MusicMood,
        project_id: str,
        target_duration: int = 40
    ) -> Optional[str]:
        """
        Get background music for the given mood
        Returns path to the music file (copied to project temp dir)
        """
        logger.info(f"🎵 Selecting background music for mood: {mood.value}")
        
        # Find music file for this mood
        music_file = self._find_music_for_mood(mood)
        
        if not music_file:
            logger.warning(f"⚠️ No music found for mood '{mood.value}'")
            logger.info(f"   Add MP3 files to: {self.music_dir / mood.value}/")
            return None
        
        logger.info(f"   ✅ Selected: {music_file.name}")
        
        # Copy to project temp directory
        project_dir = settings.TEMP_DIR / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        dest_path = project_dir / "background_music.mp3"
        shutil.copy2(music_file, dest_path)
        
        logger.info(f"   📁 Copied to: {dest_path}")
        return str(dest_path)
    
    def _find_music_for_mood(self, mood: MusicMood) -> Optional[Path]:
        """Find a music file for the given mood"""
        
        # Priority order:
        # 1. Mood-specific folder
        # 2. General folder
        
        # Check mood-specific folder
        mood_dir = self.music_dir / mood.value
        if mood_dir.exists():
            files = list(mood_dir.glob("*.mp3")) + list(mood_dir.glob("*.wav"))
            if files:
                # Random selection for variety
                selected = random.choice(files)
                logger.info(f"   Found in '{mood.value}' folder")
                return selected
        
        # Check general folder
        general_dir = self.music_dir / "general"
        if general_dir.exists():
            files = list(general_dir.glob("*.mp3")) + list(general_dir.glob("*.wav"))
            if files:
                selected = random.choice(files)
                logger.info(f"   Found in 'general' folder")
                return selected
        
        # Check root music folder
        root_files = list(self.music_dir.glob("*.mp3")) + list(self.music_dir.glob("*.wav"))
        if root_files:
            selected = random.choice(root_files)
            logger.info(f"   Found in root music folder")
            return selected
        
        return None
    
    def list_available_music(self) -> Dict[str, List[str]]:
        """List all available music files organized by mood"""
        music_library = {}
        
        for mood in MusicMood:
            mood_dir = self.music_dir / mood.value
            if mood_dir.exists():
                files = list(mood_dir.glob("*.mp3")) + list(mood_dir.glob("*.wav"))
                music_library[mood.value] = [f.name for f in files]
            else:
                music_library[mood.value] = []
        
        # General folder
        general_dir = self.music_dir / "general"
        if general_dir.exists():
            files = list(general_dir.glob("*.mp3")) + list(general_dir.glob("*.wav"))
            music_library['general'] = [f.name for f in files]
        else:
            music_library['general'] = []
        
        # Root folder
        root_files = list(self.music_dir.glob("*.mp3")) + list(self.music_dir.glob("*.wav"))
        music_library['root'] = [f.name for f in root_files]
        
        return music_library
    
    def get_music_status(self) -> Dict:
        """Get status of music library"""
        library = self.list_available_music()
        
        total_files = sum(len(files) for files in library.values())
        
        status = {
            "total_files": total_files,
            "music_directory": str(self.music_dir),
            "library": library,
            "instructions": []
        }
        
        if total_files == 0:
            status["instructions"] = [
                "No music files found!",
                f"Add MP3 files to: {self.music_dir}",
                "Organize by mood for best results:",
                f"  {self.music_dir}/dramatic/ - for intense scenes",
                f"  {self.music_dir}/suspense/ - for mysterious scenes",
                f"  {self.music_dir}/inspiring/ - for uplifting scenes",
                f"  {self.music_dir}/emotional/ - for emotional scenes",
                f"  {self.music_dir}/general/ - fallback music"
            ]
        
        return status


# Singleton instance
music_service = MusicService()
