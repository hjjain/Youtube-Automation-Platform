"""
Video Composition Service with EMOTION-AWARE AUDIO
Merges video clips + voiceover + background music into final reel
Target: 35-40 seconds, 9:16 format

AUDIO PHILOSOPHY:
- Music creates FELT EMOTION, not just background noise
- Dynamic volume based on emotional arc
- Music starts immediately (no silence in first 2 seconds)
"""
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    CompositeAudioClip,
    concatenate_videoclips,
    concatenate_audioclips,
    vfx,
    afx
)

from app.core.config import settings
from app.models.video import MusicMood, EmotionalState
from app.services.caption_generator import caption_generator


class VideoComposerService:
    """
    Service to compose final video with EMOTION-AWARE audio mixing.
    Music volume dynamically adjusts based on emotional arc of the story.
    
    Key principles:
    - Music must be FELT, not just heard
    - Higher volume during emotional peaks
    - Music starts immediately (no dead air)
    """
    
    # Target duration
    TARGET_DURATION = 40  # seconds
    MAX_DURATION = 45
    MIN_DURATION = 35
    
    # Audio mixing levels - HIGHER than before for emotional impact
    VOICEOVER_VOLUME = 1.0   # 100% - Primary audio
    
    # Base music volume (increased from 0.18 for more emotional impact)
    BASE_MUSIC_VOLUME = 0.30  # 30% - default, more presence
    
    # EMOTION-BASED MUSIC VOLUME MULTIPLIERS
    # These create dynamic audio that matches the emotional arc
    EMOTION_MUSIC_VOLUME = {
        EmotionalState.TENSION: 0.35,      # Building unease - slightly elevated
        EmotionalState.FEAR: 0.40,         # Danger/stakes - higher intensity
        EmotionalState.DECISION: 0.45,     # Pivotal moment - peak intensity
        EmotionalState.IMPACT: 0.38,       # Consequence - still intense but settling
        EmotionalState.REFLECTION: 0.25,   # Meaning - quieter, contemplative
    }
    
    def __init__(self):
        self.output_dir = settings.OUTPUT_DIR
    
    async def compose_final_video(
        self,
        video_clips: List[Dict],
        voiceover_path: str,
        music_path: Optional[str],
        project_id: str,
        target_duration: int = 40,
        script_segments: Optional[List[Dict]] = None,
        add_captions: bool = True,
        caption_style: str = 'cinematic'
    ) -> str:
        """
        Compose final video with EMOTION-AWARE audio mixing.
        
        Args:
            video_clips: List of video clip data
            voiceover_path: Path to voiceover audio
            music_path: Path to background music
            project_id: Unique project identifier
            target_duration: Target video duration
            script_segments: Script segments for captions [{narration_text, duration_seconds, emotional_state}]
            add_captions: Whether to burn in captions
            caption_style: Caption style preset (cinematic, tiktok, golden, etc.)
        
        Returns path to final video
        """
        logger.info(f"🎬 Composing final video for project {project_id}")
        
        # Step 1: Merge video clips
        logger.info("📹 Step 1: Merging video clips...")
        merged_video_path = await self._merge_video_clips(video_clips, project_id)
        
        # Step 2: Load and adjust audio
        logger.info("🔊 Step 2: Processing audio with EMOTION-AWARE mixing...")
        video = VideoFileClip(merged_video_path)
        video_duration = video.duration
        
        logger.info(f"   Video duration: {video_duration:.1f}s")
        
        # Load voiceover
        voiceover = AudioFileClip(voiceover_path)
        voiceover_duration = voiceover.duration
        logger.info(f"   Voiceover duration: {voiceover_duration:.1f}s")
        
        # Adjust video speed if needed to match voiceover
        if abs(video_duration - voiceover_duration) > 3:
            # Need to adjust
            speed_factor = video_duration / voiceover_duration
            if 0.85 <= speed_factor <= 1.15:
                # Acceptable range - adjust video speed
                video = video.with_effects([vfx.MultiplySpeed(speed_factor)])
                video_duration = video.duration
                logger.info(f"   Adjusted video speed by {speed_factor:.2f}x")
        
        # Set voiceover volume (MoviePy v2 API)
        voiceover = voiceover.with_volume_scaled(self.VOICEOVER_VOLUME)
        
        # Calculate average music volume based on emotional arc
        avg_music_volume = self._calculate_average_music_volume(script_segments)
        logger.info(f"   🎵 Music volume (emotion-based): {avg_music_volume*100:.0f}%")
        
        # Process background music
        final_audio = voiceover
        music = None
        
        if music_path and os.path.exists(music_path):
            logger.info("🎵 Adding background music (emotion-aware)...")
            music = AudioFileClip(music_path)
            
            # Loop or trim music to match video
            if music.duration < video_duration:
                # Loop music
                loops_needed = int(video_duration / music.duration) + 1
                music_clips = [music] * loops_needed
                music = concatenate_audioclips(music_clips)
            
            # Trim to video duration (MoviePy v2 API)
            music = music.subclipped(0, video_duration)
            
            # Apply emotion-based volume (higher than before for impact)
            music = music.with_volume_scaled(avg_music_volume)
            
            # Fade out at end (MoviePy v2 API)
            music = music.with_effects([afx.AudioFadeOut(2)])
            
            # IMPORTANT: Music starts immediately - no silence at start
            # The fade-in is kept very short (0.5s) to maintain immediate presence
            music = music.with_effects([afx.AudioFadeIn(0.5)])
            
            # Combine voiceover and music
            final_audio = CompositeAudioClip([music, voiceover])
        
        # Step 3: Set audio to video (MoviePy v2 API)
        logger.info("🔗 Step 3: Adding audio to video...")
        final_video = video.with_audio(final_audio)
        
        # Step 4: Export final video
        logger.info("💾 Step 4: Exporting final video...")
        output_path = self.output_dir / f"reel_{project_id}.mp4"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            threads=4,
            logger=None  # Suppress moviepy logging
        )
        
        # Cleanup
        video.close()
        voiceover.close()
        if music is not None:
            music.close()
        final_video.close()
        
        # Step 5: Add burned-in captions (TikTok style)
        if add_captions and script_segments:
            logger.info(f"📝 Step 5: Adding {caption_style} captions...")
            
            # Create caption segments synced with voiceover
            captions = caption_generator.create_captions_from_script(
                script_segments, 
                voiceover_duration
            )
            
            # Output path for captioned video
            captioned_path = self.output_dir / f"reel_{project_id}_captioned.mp4"
            
            # Add captions to video
            await caption_generator.add_captions_to_video(
                video_path=str(output_path),
                captions=captions,
                output_path=str(captioned_path),
                style=caption_style,
                position='bottom',
                animate=True
            )
            
            # Replace original with captioned version
            import shutil
            shutil.move(str(captioned_path), str(output_path))
            logger.info(f"✅ Captions added with {caption_style} style")
        
        logger.info(f"✅ Final video saved: {output_path}")
        return str(output_path)
    
    def _calculate_average_music_volume(self, script_segments: Optional[List[Dict]]) -> float:
        """
        Calculate average music volume based on emotional arc of segments.
        This creates dynamic audio that matches the story's emotional intensity.
        """
        if not script_segments:
            return self.BASE_MUSIC_VOLUME
        
        volumes = []
        for segment in script_segments:
            # Get emotional state from segment
            emotion = segment.get('emotional_state', EmotionalState.TENSION)
            
            # Handle if it's a string
            if isinstance(emotion, str):
                try:
                    emotion = EmotionalState(emotion)
                except ValueError:
                    emotion = EmotionalState.TENSION
            
            # Get volume for this emotion
            volume = self.EMOTION_MUSIC_VOLUME.get(emotion, self.BASE_MUSIC_VOLUME)
            volumes.append(volume)
        
        # Return weighted average (slightly higher weight to decision/impact moments)
        if volumes:
            avg_volume = sum(volumes) / len(volumes)
            # Ensure minimum presence
            return max(avg_volume, 0.25)
        
        return self.BASE_MUSIC_VOLUME
    
    async def _merge_video_clips(self, video_clips: List[Dict], project_id: str) -> str:
        """Merge individual video clips into one"""
        
        # Sort clips by segment number
        sorted_clips = sorted(video_clips, key=lambda x: x['segment_number'])
        
        # Load all clips
        clips = []
        for clip_data in sorted_clips:
            video_path = clip_data.get('video_path')
            if video_path and os.path.exists(video_path):
                clip = VideoFileClip(video_path)
                clips.append(clip)
        
        if not clips:
            raise Exception("No valid video clips to merge")
        
        logger.info(f"   Merging {len(clips)} video clips...")
        
        # Concatenate clips
        merged = concatenate_videoclips(clips, method="compose")
        
        # Check duration and adjust if needed
        total_duration = merged.duration
        logger.info(f"   Total merged duration: {total_duration:.1f}s")
        
        if total_duration > self.MAX_DURATION:
            # Need to speed up or trim (MoviePy v2 API)
            speed_factor = total_duration / self.TARGET_DURATION
            merged = merged.with_effects([vfx.MultiplySpeed(speed_factor)])
            logger.info(f"   Sped up video by {speed_factor:.2f}x to fit target duration")
        
        # Save merged video
        output_path = settings.TEMP_DIR / project_id / "merged_video.mp4"
        merged.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            audio=False,  # No audio yet
            preset='ultrafast',
            threads=4,
            logger=None
        )
        
        # Cleanup individual clips
        for clip in clips:
            clip.close()
        merged.close()
        
        return str(output_path)
    
    def list_available_music(self) -> dict:
        """List available local music files by mood"""
        music_library = {}
        
        for mood in MusicMood:
            mood_dir = settings.MUSIC_DIR / mood.value
            if mood_dir.exists():
                files = list(mood_dir.glob("*.mp3")) + list(mood_dir.glob("*.wav"))
                music_library[mood.value] = [f.name for f in files]
            else:
                music_library[mood.value] = []
        
        # General folder
        general_files = list(settings.MUSIC_DIR.glob("*.mp3")) + list(settings.MUSIC_DIR.glob("*.wav"))
        music_library['general'] = [f.name for f in general_files]
        
        return music_library


# Singleton instance
video_composer = VideoComposerService()
