"""
Video Creation Pipeline - POV-FIRST MAIN ORCHESTRATOR
NEW FLOW: Voiceover FIRST, then calculate video segments

POV Engine Integration:
- Trend researcher uses story lens for consistent brand
- Scripts include emotional arc for video/audio styling
- All components use emotional states for cohesive output
"""
import asyncio
import shutil
import time
import math
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
from loguru import logger
from moviepy import AudioFileClip

from app.core.config import settings
from app.models.video import (
    VideoProject, 
    VideoRequest, 
    VideoStatus,
    MusicMood,
    StoryLens
)
from app.services.trend_researcher import trend_researcher
from app.services.script_generator import script_generator
from app.services.image_generator import image_generator
from app.services.video_generator import video_generator
from app.services.voiceover_generator import voiceover_generator
from app.services.music_service import music_service
from app.services.video_composer import video_composer
from app.services.youtube_uploader import youtube_uploader
from app.services.creator_metrics import creator_metrics


class VideoPipeline:
    """
    Main pipeline orchestrator for viral reel creation
    
    NEW FLOW:
    1. Generate Script (with complete story)
    2. Generate Voiceover FIRST
    3. Measure voiceover duration
    4. Calculate number of scenes needed
    5. Generate Images
    6. Generate Video Clips
    7. Compose Final Video
    """
    
    def __init__(self):
        self.active_projects: dict = {}
        self.step_times: dict = {}
    
    def _log_step_start(self, step_name: str):
        """Log step start with timestamp"""
        self.step_times[step_name] = time.time()
        logger.info(f"\n{'='*60}")
        logger.info(f"⏱️  STARTING: {step_name}")
        logger.info(f"📅 Time: {datetime.now().strftime('%H:%M:%S')}")
        logger.info(f"{'='*60}")
    
    def _log_step_end(self, step_name: str, success: bool = True):
        """Log step end with duration"""
        start_time = self.step_times.get(step_name, time.time())
        duration = time.time() - start_time
        
        status = "✅" if success else "❌"
        logger.info(f"{status} COMPLETED: {step_name}")
        logger.info(f"⏱️  Duration: {duration:.1f} seconds ({duration/60:.1f} min)")
        
        return duration
    
    def _calculate_video_duration(self, voiceover_duration: float) -> tuple:
        """
        Calculate video duration and number of scenes based on voiceover
        
        Rules:
        - Video should be slightly longer than voiceover (2-5 seconds buffer)
        - Each scene is 5 seconds
        - Minimum 30 seconds voiceover
        
        Returns: (video_duration, num_scenes)
        """
        # Round up to nearest 5 seconds with 2-3 second buffer
        buffer = 2
        target_duration = voiceover_duration + buffer
        
        # Round up to nearest 5
        video_duration = math.ceil(target_duration / 5) * 5
        
        # Calculate number of 5-second scenes
        num_scenes = video_duration // 5
        
        # Minimum 6 scenes, maximum 10
        num_scenes = max(6, min(10, num_scenes))
        video_duration = num_scenes * 5
        
        return video_duration, num_scenes
    
    async def create_video_auto(self, lens: Optional[StoryLens] = None) -> VideoProject:
        """
        Create a POV-FIRST reel with auto-selected topic.
        
        Args:
            lens: Optional story lens override. If None, uses trend_researcher's current lens.
        
        NEW FLOW:
        1. POV-first topic selection (70% curated pool, 30% trend-mapped)
        2. Voiceover first, then calculate scenes
        3. Emotional arc throughout
        """
        pipeline_start = time.time()
        
        logger.info("\n" + "🎬"*30)
        logger.info("🎬 POV-FIRST CREATOR PIPELINE - START")
        logger.info(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("🎬"*30)
        
        # ============================================
        # STEP 0: POV-First Topic Research
        # ============================================
        self._log_step_start("STEP 0: POV-First Topic Research")
        
        # Get topic through POV lens (70% curated, 30% trend)
        topic_data = await trend_researcher.get_trending_topic(lens=lens)
        
        logger.info(f"🎯 Story Lens: {topic_data.get('story_lens', 'N/A')}")
        logger.info(f"📚 Source: {topic_data.get('source', 'N/A')}")
        logger.info(f"📝 Selected Topic: {topic_data['topic']}")
        logger.info(f"🕰️  Era: {topic_data['era']}")
        logger.info(f"🎭 Mood: {topic_data['mood']}")
        logger.info(f"🎯 Hook: {topic_data.get('hook', 'N/A')[:50]}...")
        
        self._log_step_end("STEP 0: POV-First Topic Research")
        
        # Get story lens from topic data or use provided/default
        story_lens = lens
        if not story_lens:
            lens_value = topic_data.get('story_lens', 'single_decision_moments')
            try:
                story_lens = StoryLens(lens_value)
            except ValueError:
                story_lens = StoryLens.TURNING_POINT
        
        # Create initial request with story lens
        request = VideoRequest(
            topic=topic_data['topic'],
            era=topic_data['era'],
            num_segments=8,  # Will be recalculated
            target_duration=40,  # Will be recalculated
            music_mood=MusicMood(topic_data.get('mood', 'dramatic')),
            story_lens=story_lens
        )
        
        # Execute pipeline with POV-first flow
        project = await self.create_video(request)
        
        # Final summary
        total_time = time.time() - pipeline_start
        
        logger.info("\n" + "🎉"*30)
        logger.info("🎉 POV-FIRST PIPELINE COMPLETE!")
        logger.info(f"⏱️  TOTAL TIME: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        logger.info(f"🎯 Story Lens: {story_lens.value}")
        logger.info("🎉"*30)
        
        return project
    
    async def create_video(self, request: VideoRequest) -> VideoProject:
        """
        Execute the complete video creation pipeline
        
        NEW FLOW:
        1. Script → 2. Voiceover → 3. Calculate scenes → 4. Images → 5. Videos → 6. Music → 7. Compose
        """
        # Initialize project
        project = VideoProject(topic=request.topic)
        self.active_projects[project.id] = project
        
        logger.info(f"\n🆔 Project ID: {project.id}")
        logger.info(f"📝 Topic: {request.topic}")
        logger.info(f"🕰️  Era: {request.era}")
        
        try:
            # ============================================
            # STEP 1: Generate Script (Full Story)
            # ============================================
            self._log_step_start("STEP 1: Script Generation (LLM)")
            project.status = VideoStatus.GENERATING_SCRIPT
            
            logger.info("🤖 Calling LLM for script generation...")
            logger.info("📝 Creating complete story in Hindi (with answer, not just curiosity)...")
            
            script = await script_generator.generate_script(request)
            project.script = script
            
            logger.info(f"✓ Script generated!")
            logger.info(f"  📌 Hook: {script.hook[:60]}...")
            logger.info(f"  📌 Segments: {len(script.segments)}")
            
            # Log narration preview
            full_narration = " ".join([seg.narration_text for seg in script.segments])
            logger.info(f"  📝 Full narration: {len(full_narration)} chars")
            
            step1_time = self._log_step_end("STEP 1: Script Generation (LLM)")
            
            # ============================================
            # STEP 2: Generate Voiceover FIRST
            # ============================================
            self._log_step_start("STEP 2: Voiceover (ElevenLabs) - FIRST!")
            project.status = VideoStatus.GENERATING_VOICEOVER
            
            logger.info("🎙️  Generating Hindi voiceover FIRST...")
            logger.info("🗣️  Voice: Bunty - Reel Perfect")
            logger.info("📝 This determines video length!")
            
            voiceover_path = await voiceover_generator.generate_voiceover(
                script=script,
                project_id=project.id
            )
            project.voiceover_path = voiceover_path
            
            # Get actual voiceover duration
            audio = AudioFileClip(voiceover_path)
            voiceover_duration = audio.duration
            audio.close()
            
            logger.info(f"✓ Voiceover saved: {Path(voiceover_path).name}")
            logger.info(f"  🎙️  VOICEOVER DURATION: {voiceover_duration:.1f} seconds")
            
            step2_time = self._log_step_end("STEP 2: Voiceover (ElevenLabs) - FIRST!")
            
            # ============================================
            # STEP 3: Calculate Video Parameters
            # ============================================
            self._log_step_start("STEP 3: Calculate Video Parameters")
            
            video_duration, num_scenes = self._calculate_video_duration(voiceover_duration)
            
            logger.info(f"📊 CALCULATED PARAMETERS:")
            logger.info(f"  🎙️  Voiceover: {voiceover_duration:.1f}s")
            logger.info(f"  📹 Video Duration: {video_duration}s")
            logger.info(f"  🖼️  Number of Scenes: {num_scenes}")
            logger.info(f"  ⏱️  Each Scene: 5 seconds")
            
            # Update request with calculated values
            request.num_segments = num_scenes
            request.target_duration = video_duration
            
            step3_time = self._log_step_end("STEP 3: Calculate Video Parameters")
            
            # ============================================
            # STEP 4: Generate Images (SeeDream 4.5)
            # ============================================
            self._log_step_start("STEP 4: Image Generation (SeeDream 4.5)")
            project.status = VideoStatus.GENERATING_IMAGES
            
            logger.info(f"🖼️  Generating {num_scenes} sequential images...")
            logger.info("🎨 Model: bytedance/seedream-4.5")
            logger.info("📐 Format: 9:16, 2K quality")
            logger.info("⏳ This may take 2-5 minutes...")
            
            images = await image_generator.generate_images(
                script=script,
                project_id=project.id,
                num_images=num_scenes
            )
            project.images = images
            
            valid_images = [img for img in images if img.local_path]
            logger.info(f"✓ Generated {len(valid_images)}/{num_scenes} images")
            
            step4_time = self._log_step_end("STEP 4: Image Generation (SeeDream 4.5)")
            
            # ============================================
            # STEP 5: Generate Video Clips (Kling v2.1)
            # ============================================
            self._log_step_start("STEP 5: Video Generation (Kling v2.1)")
            project.status = VideoStatus.CREATING_VIDEO
            
            logger.info(f"🎥 Converting {len(valid_images)} images to video clips...")
            logger.info("🎬 Model: kwaivgi/kling-v2.1")
            logger.info("🚀 PARALLEL processing enabled (4 concurrent)")
            logger.info("⏱️  Each clip: 5 seconds")
            
            video_clips = await video_generator.generate_video_clips(
                images=images,
                script_segments=script.segments,
                project_id=project.id
            )
            
            logger.info(f"✓ Generated {len(video_clips)} video clips")
            
            step5_time = self._log_step_end("STEP 5: Video Generation (Kling v2.1)")
            
            # ============================================
            # STEP 6: Get Background Music (Local Files)
            # ============================================
            self._log_step_start("STEP 6: Background Music (Local)")
            
            logger.info(f"🎵 Finding music for mood: {script.music_mood.value}")
            
            music_path = await music_service.get_background_music(
                mood=script.music_mood,
                project_id=project.id,
                target_duration=video_duration
            )
            project.music_path = music_path
            
            if music_path:
                logger.info(f"✓ Music ready: {Path(music_path).name}")
            else:
                logger.warning("⚠️  No music found (continuing without)")
            
            step6_time = self._log_step_end("STEP 6: Background Music (Local)")
            
            # ============================================
            # STEP 7: Compose Final Video
            # ============================================
            self._log_step_start("STEP 7: Final Composition")
            project.status = VideoStatus.COMPOSITING
            
            logger.info("🎬 Merging video clips...")
            logger.info("🎙️  Adding voiceover (100% volume)...")
            logger.info("🎵 Adding background music (18% volume)...")
            logger.info("📝 Adding cinematic captions (Netflix-style)...")
            logger.info(f"📹 Target: {video_duration}s video with {voiceover_duration:.1f}s voiceover")
            
            # Prepare script segments for captions (include emotional state for music dynamics)
            script_segments = [
                {
                    'narration_text': seg.narration_text,
                    'duration_seconds': seg.duration_seconds,
                    'emotional_state': seg.emotional_state
                }
                for seg in script.segments
            ]
            
            final_video_path = await video_composer.compose_final_video(
                video_clips=video_clips,
                voiceover_path=voiceover_path,
                music_path=music_path,
                project_id=project.id,
                target_duration=video_duration,
                script_segments=script_segments,
                add_captions=True,
                caption_style='cinematic'  # Netflix-style clean captions
            )
            project.final_video_path = final_video_path
            
            step7_time = self._log_step_end("STEP 7: Final Composition")
            
            # ============================================
            # SUCCESS!
            # ============================================
            project.status = VideoStatus.COMPLETED
            
            logger.info("\n" + "="*60)
            logger.info("🎉 VIDEO CREATION SUCCESSFUL!")
            logger.info("="*60)
            logger.info(f"📁 Output: {final_video_path}")
            logger.info(f"📝 Topic: {project.topic}")
            logger.info(f"🆔 Project: {project.id}")
            logger.info(f"🎙️  Voiceover: {voiceover_duration:.1f}s")
            logger.info(f"📹 Video: {video_duration}s")
            logger.info(f"🖼️  Scenes: {num_scenes}")
            
            # Time summary
            logger.info("\n⏱️  STEP TIMES:")
            logger.info(f"  Step 1 (Script):     {step1_time:.1f}s")
            logger.info(f"  Step 2 (Voiceover):  {step2_time:.1f}s")
            logger.info(f"  Step 3 (Calculate):  {step3_time:.1f}s")
            logger.info(f"  Step 4 (Images):     {step4_time:.1f}s")
            logger.info(f"  Step 5 (Videos):     {step5_time:.1f}s")
            logger.info(f"  Step 6 (Music):      {step6_time:.1f}s")
            logger.info(f"  Step 7 (Compose):    {step7_time:.1f}s")
            
            return project
            
        except Exception as e:
            project.status = VideoStatus.FAILED
            project.error_message = str(e)
            logger.error(f"\n❌ PIPELINE FAILED!")
            logger.error(f"Error: {e}")
            logger.exception("Full traceback:")
            raise
    
    def get_project_status(self, project_id: str) -> Optional[VideoProject]:
        """Get status of a project"""
        return self.active_projects.get(project_id)
    
    async def cleanup_temp_files(self, project_id: str):
        """Clean up temporary files"""
        temp_dir = settings.TEMP_DIR / project_id
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            logger.info(f"🧹 Cleaned up temp files for {project_id}")
    
    async def upload_to_youtube(
        self,
        project: VideoProject,
        privacy: str = 'private',
        with_captions: bool = True
    ) -> dict:
        """
        Upload completed video to YouTube
        
        Args:
            project: The completed VideoProject
            privacy: 'private', 'unlisted', or 'public'
            with_captions: Whether to upload captions
        
        Returns:
            Upload result with video_id and URL
        """
        if not project.final_video_path:
            raise ValueError("No video to upload - create video first")
        
        if project.status != VideoStatus.COMPLETED:
            raise ValueError(f"Project not completed. Status: {project.status}")
        
        self._log_step_start("STEP 8: YouTube Upload")
        
        script = project.script
        
        # Generate description
        description = youtube_uploader.generate_description(
            topic=script.title,
            era=script.historical_era or "Historical",
            hook=script.hook,
            tags=[seg.narration_text[:20] for seg in script.segments[:3]]
        )
        
        # Generate tags
        tags = [
            script.title,
            script.historical_era or "History",
            "Indian History",
            "Hindi Story",
            script.music_mood.value
        ]
        
        logger.info(f"📤 Uploading to YouTube...")
        logger.info(f"   📝 Title: {script.title}")
        logger.info(f"   🔒 Privacy: {privacy}")
        
        # Upload video
        result = await youtube_uploader.upload_video(
            video_path=project.final_video_path,
            title=script.title,
            description=description,
            tags=tags,
            category='education',
            privacy=privacy,
            is_short=True,
            language='hi'
        )
        
        if result['success'] and with_captions:
            logger.info("📝 Uploading captions...")
            
            # Generate SRT captions
            segments_data = [
                {'narration_text': seg.narration_text, 'duration_seconds': seg.duration_seconds}
                for seg in script.segments
            ]
            srt_content = youtube_uploader.generate_srt_captions(
                segments_data, 
                script.total_duration
            )
            
            # Upload captions
            caption_result = await youtube_uploader.upload_captions(
                video_id=result['video_id'],
                caption_text=srt_content,
                language='hi',
                name='Hindi'
            )
            result['captions'] = caption_result
        
        self._log_step_end("STEP 8: YouTube Upload")
        
        if result['success']:
            logger.info(f"✅ YouTube upload successful!")
            logger.info(f"🔗 URL: {result['url']}")
            
            # Record in creator metrics for tracking
            creator_metrics.record_video_upload(
                video_id=result['video_id'],
                title=script.title,
                story_lens=script.story_lens.value if hasattr(script, 'story_lens') else 'unknown'
            )
            logger.info(f"📊 Recorded in creator metrics")
        else:
            logger.error(f"❌ YouTube upload failed: {result.get('error')}")
        
        return result
    
    def get_creator_health(self) -> Dict:
        """Get creator brand health report"""
        return creator_metrics.get_health_report()
    
    def set_story_lens(self, lens: StoryLens):
        """Set the current story lens for the channel"""
        trend_researcher.set_story_lens(lens)
        logger.info(f"🎯 Channel story lens set to: {lens.value}")
    
    def get_available_lenses(self) -> list:
        """Get all available story lenses"""
        return trend_researcher.get_all_lenses()


# Singleton instance
pipeline = VideoPipeline()
