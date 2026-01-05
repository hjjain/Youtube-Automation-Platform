"""
Video Generation Service - Kling v2.1 with EMOTION-BASED MOTION
Converts images to 5-second video clips using Kling v2.1
Motion philosophy: REDUCE motion, INCREASE realism for brand identity

Motion Style:
- Subtle human POV (not epic camera swoops)
- Observational camera (documentary feel)
- Quiet tension (let moments breathe)
"""
import httpx
import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from loguru import logger

from app.core.config import settings
from app.models.video import GeneratedImage, EmotionalState


class VideoGeneratorService:
    """
    Service to convert images to video clips using Kling v2.1
    with EMOTION-BASED MOTION for consistent brand feel.
    
    Motion Philosophy:
    - Less is more - subtle movements create intimacy
    - Human POV, not god-view camera
    - Let emotional moments BREATHE
    """
    
    # EMOTION-BASED MOTION PROMPTS
    # This creates CONSISTENT video feel that viewers recognize
    MOTION_BY_EMOTION = {
        EmotionalState.TENSION: {
            "motion": "very slow handheld movement, uneasy subtle drift",
            "camera": "slightly off-center, uncomfortable framing",
            "speed": "slow deliberate movement, building unease"
        },
        EmotionalState.FEAR: {
            "motion": "minimal shaky handheld, vulnerability feel",
            "camera": "tight framing, claustrophobic slight push",
            "speed": "slow with occasional slight tremor"
        },
        EmotionalState.DECISION: {
            "motion": "slight push-in towards subject, moment frozen",
            "camera": "human eye-level, intimate perspective",
            "speed": "very slow zoom, weight of choice"
        },
        EmotionalState.IMPACT: {
            "motion": "static shot with minimal movement, let moment breathe",
            "camera": "wide enough to see consequence, still intimate",
            "speed": "almost still, aftermath settling"
        },
        EmotionalState.REFLECTION: {
            "motion": "wide calm shot, gentle breathing motion",
            "camera": "peaceful framing, space to think",
            "speed": "slow meditative drift, contemplative"
        }
    }
    
    def __init__(self):
        # Kling v2.1 model on Replicate
        self.model_url = "https://api.replicate.com/v1/models/kwaivgi/kling-v2.1/predictions"
        self.api_token = settings.REPLICATE_API_TOKEN
        self.video_duration = 5  # seconds per clip
        
        # Parallel processing settings
        self.max_concurrent = 4  # Max parallel API calls (avoid rate limits)
    
    async def generate_video_clips(
        self,
        images: List[GeneratedImage],
        script_segments: List,
        project_id: str
    ) -> List[Dict]:
        """
        Generate video clips for each image using Kling v2.1
        Uses PARALLEL processing for faster generation
        Returns list of video clip paths (properly ordered by segment)
        """
        logger.info(f"🎬 Starting PARALLEL video generation for {len(images)} images")
        logger.info(f"🚀 Max concurrent: {self.max_concurrent} videos at once")
        logger.info(f"⏱️  Duration per clip: {self.video_duration}s")
        
        # Create output directory
        project_dir = settings.TEMP_DIR / project_id / "clips"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Filter valid images
        valid_images = [img for img in images if img.image_url and img.image_url.startswith("http")]
        logger.info(f"📊 Valid images for video: {len(valid_images)}/{len(images)}")
        
        if not valid_images:
            logger.error("❌ No valid images found!")
            return []
        
        # Create tasks for parallel execution
        tasks = []
        for i, image in enumerate(valid_images):
            motion_prompt = self._get_motion_prompt(i, len(valid_images), script_segments)
            task = self._generate_single_video_task(
                image=image,
                motion_prompt=motion_prompt,
                segment_number=i + 1,
                project_dir=project_dir
            )
            tasks.append(task)
        
        # Execute in batches to respect rate limits
        all_results = []
        for batch_start in range(0, len(tasks), self.max_concurrent):
            batch_end = min(batch_start + self.max_concurrent, len(tasks))
            batch = tasks[batch_start:batch_end]
            
            logger.info(f"\n{'─'*50}")
            logger.info(f"🎬 Processing batch: clips {batch_start+1}-{batch_end} of {len(tasks)}")
            logger.info(f"{'─'*50}")
            
            # Run batch in parallel
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            
            # Process results
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"❌ Batch error: {result}")
                elif result:
                    all_results.append(result)
        
        # Sort results by segment number to maintain order
        all_results.sort(key=lambda x: x['segment_number'])
        
        logger.info(f"\n{'─'*50}")
        logger.info(f"📊 Video generation complete: {len(all_results)}/{len(valid_images)} clips")
        
        # Verify ordering
        logger.info("📋 Clip order verification:")
        for clip in all_results:
            logger.info(f"   Segment {clip['segment_number']}: {Path(clip['video_path']).name}")
        
        total_duration = len(all_results) * self.video_duration
        logger.info(f"⏱️  Total raw duration: {total_duration}s")
        
        return all_results
    
    async def _generate_single_video_task(
        self,
        image: GeneratedImage,
        motion_prompt: str,
        segment_number: int,
        project_dir: Path
    ) -> Optional[Dict]:
        """
        Task to generate a single video clip
        Returns dict with segment_number for ordering
        """
        logger.info(f"🎥 Starting clip {segment_number}...")
        
        try:
            video_url = await self._generate_single_video(
                image_url=image.image_url,
                motion_prompt=motion_prompt,
                clip_number=segment_number
            )
            
            if video_url:
                # Download video
                video_path = project_dir / f"clip_{segment_number:02d}.mp4"
                await self._download_video(video_url, video_path)
                
                logger.info(f"✅ Clip {segment_number} saved: {video_path.name}")
                
                return {
                    "segment_number": segment_number,
                    "video_path": str(video_path),
                    "video_url": video_url,
                    "duration": self.video_duration
                }
            else:
                logger.error(f"❌ Failed to generate clip {segment_number}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generating clip {segment_number}: {e}")
            return None
    
    def _get_motion_prompt(self, index: int, total: int, segments: List) -> str:
        """
        Generate EMOTION-BASED motion prompt for video generation.
        Uses emotional state from script segment for consistent brand feel.
        """
        
        # Try to get emotional state from segment
        emotional_state = EmotionalState.TENSION  # default
        if segments and index < len(segments):
            segment = segments[index]
            if hasattr(segment, 'emotional_state'):
                emotional_state = segment.emotional_state
        
        # Get emotion-specific motion style
        emotion_motion = self.MOTION_BY_EMOTION.get(
            emotional_state,
            self.MOTION_BY_EMOTION[EmotionalState.TENSION]
        )
        
        # Build motion prompt based on emotional state
        motion_prompt = f"""
{emotion_motion['motion']},
{emotion_motion['camera']},
{emotion_motion['speed']},
natural environmental motion,
subtle ambient movement (fire flicker, dust particles if present),
realistic documentary movement,
NOT epic cinematic swoops,
NOT dramatic camera moves,
human observational perspective
"""
        
        # Position-specific adjustments
        if index == 0:
            motion_prompt += ", slow establishing reveal"
        elif index == total - 1:
            motion_prompt += ", gentle fade feeling, contemplative ending"
        
        return motion_prompt.strip()
    
    async def _generate_single_video(
        self, 
        image_url: str, 
        motion_prompt: str,
        clip_number: int
    ) -> Optional[str]:
        """Generate a single video clip from image using Kling v2.1"""
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "input": {
                "mode": "standard",
                "prompt": motion_prompt,
                "duration": self.video_duration,
                "start_image": image_url,
                "negative_prompt": "blurry, distorted, unnatural motion, glitch, artifacts"
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.model_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code not in [200, 201, 202]:
                logger.error(f"❌ Kling API error for clip {clip_number}: {response.status_code}")
                return None
            
            result = response.json()
            prediction_id = result.get("id", "unknown")
            status = result.get("status", "unknown")
            
            logger.info(f"📋 Clip {clip_number} - Prediction: {prediction_id[:12]}... Status: {status}")
            
            # Check if we need to poll for results
            if status in ["processing", "starting"]:
                get_url = result.get("urls", {}).get("get")
                if not get_url:
                    get_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
                return await self._poll_for_video(get_url, headers, clip_number)
            
            # Direct result
            output = result.get("output")
            if isinstance(output, str):
                return output
            elif isinstance(output, list) and len(output) > 0:
                return output[0]
            
            return None
    
    async def _poll_for_video(
        self, 
        url: str, 
        headers: dict, 
        clip_number: int,
        max_attempts: int = 120
    ) -> Optional[str]:
        """Poll for video generation results"""
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(max_attempts):
                await asyncio.sleep(5)  # Wait 5 seconds between polls
                
                response = await client.get(url, headers=headers)
                result = response.json()
                
                status = result.get("status")
                
                # Log progress every 30 seconds
                if attempt % 6 == 0 and attempt > 0:
                    elapsed = attempt * 5
                    logger.info(f"⏳ Clip {clip_number} generating... ({elapsed}s, status: {status})")
                
                if status == "succeeded":
                    logger.info(f"✅ Clip {clip_number} generation complete!")
                    output = result.get("output")
                    if isinstance(output, str):
                        return output
                    elif isinstance(output, list) and len(output) > 0:
                        return output[0]
                    return None
                
                elif status == "failed":
                    error = result.get("error", "Unknown error")
                    logger.error(f"❌ Clip {clip_number} failed: {error}")
                    return None
                
                elif status == "canceled":
                    logger.error(f"❌ Clip {clip_number} was canceled")
                    return None
        
        logger.error(f"❌ Clip {clip_number} timed out after 10 minutes")
        return None
    
    async def _download_video(self, video_url: str, save_path: Path) -> Path:
        """Download video from URL"""
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(video_url)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
        
        return save_path


# Singleton instance
video_generator = VideoGeneratorService()
