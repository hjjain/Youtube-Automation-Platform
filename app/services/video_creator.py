"""
Video Creation Service
Converts images to video clips with Ken Burns effect and merges them
"""
import os
import random
from pathlib import Path
from typing import List, Tuple
from loguru import logger

from moviepy import (
    ImageClip, 
    concatenate_videoclips, 
    CompositeVideoClip,
    ColorClip
)
import numpy as np
from PIL import Image

from app.core.config import settings
from app.models.video import VideoScript, GeneratedImage


class VideoCreatorService:
    """Service to create videos from generated images"""
    
    def __init__(self):
        self.width = settings.VIDEO_WIDTH
        self.height = settings.VIDEO_HEIGHT
        self.fps = settings.FPS
    
    async def create_base_video(
        self,
        images: List[GeneratedImage],
        script: VideoScript,
        project_id: str
    ) -> str:
        """
        Create base video from images with Ken Burns effect
        Returns path to the created video
        """
        logger.info(f"Creating base video for project {project_id}")
        
        # Filter valid images
        valid_images = [img for img in images if img.local_path and os.path.exists(img.local_path)]
        
        if not valid_images:
            raise ValueError("No valid images found to create video")
        
        # Match images with script segments for duration
        segment_durations = {seg.segment_number: seg.duration_seconds for seg in script.segments}
        
        # Create video clips for each image
        clips = []
        for img in valid_images:
            duration = segment_durations.get(img.segment_number, 4.0)
            clip = self._create_ken_burns_clip(img.local_path, duration)
            clips.append(clip)
        
        # Concatenate all clips
        logger.info(f"Concatenating {len(clips)} clips")
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Output path
        output_dir = settings.TEMP_DIR / project_id
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "base_video.mp4"
        
        # Write video file
        logger.info(f"Writing video to {output_path}")
        final_clip.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio=False,
            preset='ultrafast',  # Fast encoding
            threads=4
        )
        
        # Clean up
        final_clip.close()
        for clip in clips:
            clip.close()
        
        logger.info(f"Base video created: {output_path}")
        return str(output_path)
    
    def _create_ken_burns_clip(self, image_path: str, duration: float) -> ImageClip:
        """
        Create a video clip from an image with Ken Burns effect
        (zoom and pan animation)
        """
        # Load and resize image to fit video dimensions
        img = Image.open(image_path)
        img = self._resize_image_to_fill(img)
        img_array = np.array(img)
        
        # Choose random Ken Burns effect
        effect_type = random.choice(['zoom_in', 'zoom_out', 'pan_left', 'pan_right', 'pan_up', 'pan_down'])
        
        # Create the clip with effect
        clip = self._apply_ken_burns_effect(img_array, duration, effect_type)
        
        return clip
    
    def _resize_image_to_fill(self, img: Image.Image) -> Image.Image:
        """Resize image to fill the video frame (may crop)"""
        target_ratio = self.width / self.height
        img_ratio = img.width / img.height
        
        if img_ratio > target_ratio:
            # Image is wider, fit height
            new_height = self.height
            new_width = int(new_height * img_ratio)
        else:
            # Image is taller, fit width
            new_width = self.width
            new_height = int(new_width / img_ratio)
        
        # Resize with high quality
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return img
    
    def _apply_ken_burns_effect(
        self, 
        img_array: np.ndarray, 
        duration: float, 
        effect_type: str
    ) -> ImageClip:
        """Apply Ken Burns (zoom/pan) effect to image"""
        
        img_h, img_w = img_array.shape[:2]
        
        # Scale factors for zoom
        start_scale = 1.0
        end_scale = 1.15  # 15% zoom
        
        def make_frame(t):
            progress = t / duration
            
            if effect_type == 'zoom_in':
                scale = start_scale + (end_scale - start_scale) * progress
                center_x, center_y = img_w / 2, img_h / 2
            elif effect_type == 'zoom_out':
                scale = end_scale - (end_scale - start_scale) * progress
                center_x, center_y = img_w / 2, img_h / 2
            elif effect_type == 'pan_left':
                scale = 1.1
                center_x = img_w / 2 + (img_w * 0.05) * (1 - progress)
                center_y = img_h / 2
            elif effect_type == 'pan_right':
                scale = 1.1
                center_x = img_w / 2 - (img_w * 0.05) * (1 - progress)
                center_y = img_h / 2
            elif effect_type == 'pan_up':
                scale = 1.1
                center_x = img_w / 2
                center_y = img_h / 2 + (img_h * 0.05) * (1 - progress)
            elif effect_type == 'pan_down':
                scale = 1.1
                center_x = img_w / 2
                center_y = img_h / 2 - (img_h * 0.05) * (1 - progress)
            else:
                scale = 1.0
                center_x, center_y = img_w / 2, img_h / 2
            
            # Calculate crop region
            crop_w = int(self.width / scale)
            crop_h = int(self.height / scale)
            
            # Ensure we don't go out of bounds
            x1 = max(0, min(int(center_x - crop_w / 2), img_w - crop_w))
            y1 = max(0, min(int(center_y - crop_h / 2), img_h - crop_h))
            x2 = x1 + crop_w
            y2 = y1 + crop_h
            
            # Crop and resize
            cropped = img_array[y1:y2, x1:x2]
            
            # Resize to output dimensions
            from PIL import Image
            pil_img = Image.fromarray(cropped)
            pil_img = pil_img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            
            return np.array(pil_img)
        
        # Create clip with the animated frame function
        clip = ImageClip(make_frame, duration=duration)
        clip = clip.set_fps(self.fps)
        
        return clip
    
    def _create_simple_clip(self, image_path: str, duration: float) -> ImageClip:
        """Create a simple static clip (fallback if Ken Burns fails)"""
        img = Image.open(image_path)
        img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        
        clip = ImageClip(np.array(img), duration=duration)
        clip = clip.set_fps(self.fps)
        
        return clip


# Singleton instance
video_creator = VideoCreatorService()

