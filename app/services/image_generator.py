"""
Image Generation Service - SeeDream 4.5 with VISUAL IDENTITY
Generates SEQUENTIAL images with consistent VISUAL FINGERPRINT
for channel brand recognition in feed.

VISUAL IDENTITY:
- Warm amber + deep shadows
- Low-key cinematic lighting
- Close human perspective (not epic god-view)
- Documentary realism, not fantasy
"""
import httpx
import asyncio
import json
from pathlib import Path
from typing import List, Dict
from loguru import logger

from app.core.config import settings
from app.models.video import VideoScript, GeneratedImage, EmotionalState


class ImageGeneratorService:
    """
    Service to generate SEQUENTIAL images with CONSISTENT VISUAL IDENTITY.
    Uses SeeDream 4.5 with channel-specific visual fingerprint.
    
    Brand consistency > Individual image quality
    Recognizable in feed > Generic "AI epic" look
    """
    
    # VISUAL FINGERPRINT - This makes your videos RECOGNIZABLE
    # Viewers should know it's YOUR video before reading the title
    CHANNEL_VISUAL_STYLE = {
        "color_palette": "warm amber and golden tones with deep shadows, rich earth tones",
        "lighting": "low-key cinematic lighting, dramatic shadows, natural window or torch light",
        "camera": "close intimate human perspective, eye-level, observational documentary style",
        "avoid": "wide fantasy landscapes, epic god-view shots, overly bright, mythic/magical style",
        "texture": "film grain, natural imperfections, documentary aesthetic",
        "focus": "human emotions, faces, hands, eyes - intimate details"
    }
    
    # Emotional state to visual style mapping
    EMOTION_VISUAL_STYLE = {
        EmotionalState.TENSION: {
            "lighting": "dim uncertain lighting, shadows creeping in",
            "composition": "off-center framing, something lurking at edges",
            "mood": "uneasy atmosphere, storm approaching feel"
        },
        EmotionalState.FEAR: {
            "lighting": "harsh single light source, stark shadows",
            "composition": "tight framing, claustrophobic",
            "mood": "danger imminent, vulnerability visible"
        },
        EmotionalState.DECISION: {
            "lighting": "dramatic spotlight effect, clarity emerging from darkness",
            "composition": "centered subject, moment frozen in time",
            "mood": "weight of choice, crossroads feeling"
        },
        EmotionalState.IMPACT: {
            "lighting": "high contrast, aftermath lighting",
            "composition": "wide enough to show consequence, still intimate",
            "mood": "the dust settling, irreversible change"
        },
        EmotionalState.REFLECTION: {
            "lighting": "soft golden hour, contemplative",
            "composition": "breathing room, peaceful framing",
            "mood": "calm after storm, wisdom gained"
        }
    }
    
    # Words to remove from prompts to avoid content filter
    UNSAFE_WORDS = [
        'war', 'battle', 'fight', 'fighting', 'attack', 'attacking', 'kill', 'killing',
        'dead', 'death', 'die', 'dying', 'blood', 'bloody', 'wound', 'wounded',
        'violence', 'violent', 'massacre', 'slaughter', 'murder', 'execution',
        'weapon', 'sword', 'gun', 'rifle', 'cannon', 'spear', 'arrow', 'bomb',
        'explosion', 'exploding', 'burning bodies', 'corpse', 'body', 'bodies',
        'rebellion', 'revolt', 'mutiny', 'siege', 'invasion', 'combat',
        'soldier fighting', 'army attacking', 'troops attacking'
    ]
    
    # Safe replacements for dramatic scenes
    SAFE_REPLACEMENTS = {
        'battle scene': 'dramatic gathering at ancient fort',
        'war scene': 'soldiers standing in formation at sunset',
        'fighting': 'tense confrontation',
        'attack': 'dramatic moment',
        'soldiers attacking': 'soldiers marching',
        'rebellion': 'historic gathering',
        'siege': 'fortified structure',
        'epic wide shot': 'intimate close-up',
        'god view': 'eye-level perspective',
    }
    
    def __init__(self):
        # SeeDream 4.5 model on Replicate
        self.model_url = "https://api.replicate.com/v1/models/bytedance/seedream-4.5/predictions"
        self.api_token = settings.REPLICATE_API_TOKEN
    
    def _sanitize_prompt(self, prompt: str, emotional_state: EmotionalState = EmotionalState.TENSION) -> str:
        """
        Sanitize prompt and apply VISUAL FINGERPRINT for brand consistency.
        Removes violent imagery while adding channel visual identity.
        """
        sanitized = prompt.lower()
        
        # Apply safe replacements first
        for unsafe, safe in self.SAFE_REPLACEMENTS.items():
            sanitized = sanitized.replace(unsafe, safe)
        
        # Remove remaining unsafe words
        for word in self.UNSAFE_WORDS:
            sanitized = sanitized.replace(word, '')
        
        # Clean up extra spaces
        sanitized = ' '.join(sanitized.split())
        
        # Get emotion-specific visual style
        emotion_style = self.EMOTION_VISUAL_STYLE.get(
            emotional_state, 
            self.EMOTION_VISUAL_STYLE[EmotionalState.TENSION]
        )
        
        # Apply VISUAL FINGERPRINT - This is what makes your videos recognizable!
        visual_signature = f"""
{self.CHANNEL_VISUAL_STYLE['color_palette']},
{self.CHANNEL_VISUAL_STYLE['lighting']},
{self.CHANNEL_VISUAL_STYLE['camera']},
{emotion_style['lighting']},
{emotion_style['mood']},
realistic human emotion, documentary cinematic style,
not fantasy, not mythic, not overly epic,
{self.CHANNEL_VISUAL_STYLE['texture']}
"""
        
        # Add visual signature and safety suffix
        safety_suffix = ", peaceful scene, no violence, family friendly, artistic"
        
        return f"{sanitized}, {visual_signature.strip()}{safety_suffix}"
    
    async def generate_images(
        self, 
        script: VideoScript, 
        project_id: str,
        num_images: int = 8
    ) -> List[GeneratedImage]:
        """
        Generate all images in ONE API call using SeeDream 4.5
        Returns list of generated images with local paths
        """
        logger.info(f"🖼️ Generating {num_images} sequential images for project {project_id}")
        
        # Create project temp directory
        project_dir = settings.TEMP_DIR / project_id / "images"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Build the mega-prompt for sequential images
        mega_prompt = self._build_sequential_prompt(script, num_images)
        
        logger.info("📤 Calling SeeDream 4.5 API...")
        logger.info(f"📝 Prompt length: {len(mega_prompt)} chars")
        
        try:
            # Call SeeDream 4.5 API
            image_urls = await self._call_seedream_api(mega_prompt, num_images)
            
            if not image_urls:
                logger.error("❌ No images returned from SeeDream API")
                return []
            
            logger.info(f"✅ Received {len(image_urls)} images from SeeDream")
            
            # Download all images
            images = []
            for i, url in enumerate(image_urls):
                logger.info(f"📥 Downloading image {i+1}/{len(image_urls)}...")
                local_path = await self._download_image(
                    image_url=url,
                    save_path=project_dir / f"segment_{i+1:02d}.png"
                )
                
                images.append(GeneratedImage(
                    segment_number=i + 1,
                    image_url=url,
                    local_path=str(local_path),
                    prompt_used=f"Segment {i+1} of sequential generation"
                ))
                logger.info(f"✅ Image {i+1} saved: {local_path.name}")
            
            return images
            
        except Exception as e:
            logger.error(f"❌ SeeDream image generation failed: {e}")
            raise
    
    def _build_sequential_prompt(self, script: VideoScript, num_images: int) -> str:
        """
        Build a mega-prompt for sequential image generation with VISUAL IDENTITY.
        Each image follows the emotional arc and maintains brand consistency.
        """
        
        # Base rules for visual coherence WITH VISUAL FINGERPRINT
        prompt_parts = [
            f"Generate {num_images} sequential cinematic images as a connected visual story.",
            "",
            f"Scene concept:",
            f"{script.title} - {script.event_description}",
            f"Historical Era: {script.historical_era}",
            "",
            "=== CRITICAL: VISUAL IDENTITY (Brand Fingerprint) ===",
            f"Color palette: {self.CHANNEL_VISUAL_STYLE['color_palette']}",
            f"Lighting style: {self.CHANNEL_VISUAL_STYLE['lighting']}",
            f"Camera perspective: {self.CHANNEL_VISUAL_STYLE['camera']}",
            f"Texture: {self.CHANNEL_VISUAL_STYLE['texture']}",
            f"AVOID: {self.CHANNEL_VISUAL_STYLE['avoid']}",
            "",
            "Global rules for ALL images:",
            "- Same visual style, lighting continuity across all images",
            "- CLOSE HUMAN PERSPECTIVE - not epic wide shots",
            "- Focus on FACES, HANDS, EYES - human emotion",
            "- Documentary realism, historically accurate",
            "- No text, no symbols, no UI elements",
            "- No modern objects or modern humans",
            "- Warm amber tones with deep shadows throughout",
            "- 9:16 vertical format optimized",
            "",
        ]
        
        # Add individual scene descriptions from script segments (SANITIZED with emotion)
        for i, segment in enumerate(script.segments[:num_images], 1):
            if segment.image_prompt:
                # Get emotional state for this segment
                emotion = getattr(segment, 'emotional_state', EmotionalState.TENSION)
                emotion_style = self.EMOTION_VISUAL_STYLE.get(emotion, self.EMOTION_VISUAL_STYLE[EmotionalState.TENSION])
                
                # Sanitize each image prompt with emotional styling
                safe_prompt = self._sanitize_prompt(segment.image_prompt, emotion)
                
                prompt_parts.append(f"Image {i} (Emotion: {emotion.value}):")
                prompt_parts.append(f"Scene: {safe_prompt}")
                prompt_parts.append(f"Mood: {emotion_style['mood']}")
                prompt_parts.append("")
        
        # Add style footer with visual identity emphasis
        prompt_parts.extend([
            "=== Style and Quality ===",
            "Documentary cinematic style, NOT fantasy or mythic",
            f"Historical accuracy for {script.historical_era}",
            "Professional film still quality with film grain texture",
            "Warm amber color grade with deep shadows",
            "Intimate human perspective, emotional storytelling",
            "",
            "IMPORTANT: All images must be peaceful, artistic, family-friendly.",
            "Focus on human emotions, faces, hands - intimate moments.",
            "No violence, no weapons, no conflict imagery.",
            "Show the FEELING, not the action."
        ])
        
        return "\n".join(prompt_parts)
    
    async def _call_seedream_api(self, prompt: str, num_images: int) -> List[str]:
        """Call SeeDream 4.5 API for sequential image generation"""
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "input": {
                "size": "2K",
                "width": 2048,
                "height": 2048,
                "aspect_ratio": "9:16",
                "max_images": num_images,
                "sequential_image_generation": "auto",
                "image_input": [],
                "prompt": prompt
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info("📤 Sending request to SeeDream API...")
            response = await client.post(
                self.model_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code not in [200, 201, 202]:
                logger.error(f"❌ SeeDream API error: {response.status_code}")
                logger.error(f"Response: {response.text[:500]}")
                raise Exception(f"SeeDream API failed with status {response.status_code}")
            
            result = response.json()
            logger.info(f"📋 Prediction ID: {result.get('id', 'unknown')}")
            logger.info(f"📋 Status: {result.get('status', 'unknown')}")
            
            # Get the polling URL
            get_url = result.get("urls", {}).get("get")
            if not get_url:
                get_url = f"https://api.replicate.com/v1/predictions/{result['id']}"
            
            logger.info(f"🔄 Polling for results at: {get_url}")
            
            # Poll for completion
            return await self._poll_for_results(get_url, headers)
    
    async def _poll_for_results(self, url: str, headers: dict, max_attempts: int = 120) -> List[str]:
        """Poll for results when prediction is processing"""
        
        logger.info("⏳ Waiting for image generation (this may take 2-5 minutes)...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(max_attempts):
                await asyncio.sleep(5)  # Wait 5 seconds between polls
                
                response = await client.get(url, headers=headers)
                result = response.json()
                
                status = result.get("status")
                
                # Log progress
                if attempt % 6 == 0:  # Every 30 seconds
                    elapsed = (attempt + 1) * 5
                    logger.info(f"⏳ Still generating... ({elapsed}s elapsed, status: {status})")
                
                if status == "succeeded":
                    logger.info("✅ Image generation completed!")
                    output = result.get("output", [])
                    
                    if isinstance(output, list):
                        logger.info(f"📷 Received {len(output)} image URLs")
                        return output
                    elif isinstance(output, str):
                        return [output]
                    return []
                
                elif status == "failed":
                    error = result.get("error", "")
                    logs = result.get("logs", "No logs available")
                    logger.error(f"❌ SeeDream prediction failed!")
                    logger.error(f"   Error: {error if error else 'No error message'}")
                    logger.error(f"   Logs: {logs[:500] if logs else 'No logs'}")
                    # Check if it's a content filter issue
                    full_result = str(result)
                    if "flagged" in full_result.lower() or "sensitive" in full_result.lower():
                        raise Exception("Content was flagged as sensitive. Try a different topic.")
                    raise Exception(f"SeeDream prediction failed: {error or 'Unknown error - check logs above'}")
                
                elif status == "canceled":
                    logger.error("❌ SeeDream prediction was canceled")
                    raise Exception("SeeDream prediction was canceled")
        
        logger.error("❌ SeeDream prediction timed out after 10 minutes")
        raise Exception("SeeDream prediction timed out")
    
    async def _download_image(self, image_url: str, save_path: Path, max_retries: int = 3) -> Path:
        """Download image from URL with retry logic for resilience"""
        
        for attempt in range(max_retries):
            try:
                # Increased timeout for large image files (2K images can be 1-2MB)
                async with httpx.AsyncClient(timeout=180.0) as client:
                    response = await client.get(image_url)
                    response.raise_for_status()
                    
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                
                return save_path
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # 5s, 10s, 15s
                    logger.warning(f"⚠️ Download attempt {attempt+1} failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"❌ Download failed after {max_retries} attempts: {e}")
                    raise


# Singleton instance
image_generator = ImageGeneratorService()
