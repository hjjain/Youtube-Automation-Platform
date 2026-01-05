"""
Caption Generator Service
Add burned-in captions/subtitles to videos (TikTok/Reels style)
Supports Hindi (Devanagari) text
"""
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from loguru import logger
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class CaptionSegment:
    """A single caption segment"""
    text: str
    start_time: float  # seconds
    end_time: float    # seconds
    

class CaptionGeneratorService:
    """
    Generate burned-in captions for videos
    Uses FFmpeg for reliable Hindi text rendering
    """
    
    # Caption styling presets
    STYLES = {
        'default': {
            'fontsize': 42,
            'fontcolor': 'white',
            'borderw': 3,
            'bordercolor': 'black',
            'box': 1,
            'boxcolor': 'black@0.6',
            'boxborderw': 10,
        },
        'bold': {
            'fontsize': 48,
            'fontcolor': 'white',
            'borderw': 4,
            'bordercolor': 'black',
            'box': 1,
            'boxcolor': 'black@0.7',
            'boxborderw': 12,
        },
        'minimal': {
            'fontsize': 38,
            'fontcolor': 'white',
            'borderw': 2,
            'bordercolor': 'black',
            'box': 0,
        },
        'highlight': {
            'fontsize': 44,
            'fontcolor': 'yellow',
            'borderw': 3,
            'bordercolor': 'black',
            'box': 1,
            'boxcolor': 'black@0.8',
            'boxborderw': 15,
        },
        # Colorful styles
        'neon_yellow': {
            'fontsize': 46,
            'fontcolor': '#FFFF00',
            'borderw': 4,
            'bordercolor': '#FF6600',
            'shadowcolor': 'black',
            'shadowx': 3,
            'shadowy': 3,
            'box': 0,
        },
        'neon_cyan': {
            'fontsize': 46,
            'fontcolor': '#00FFFF',
            'borderw': 4,
            'bordercolor': '#0066FF',
            'shadowcolor': 'black',
            'shadowx': 3,
            'shadowy': 3,
            'box': 0,
        },
        'fire': {
            'fontsize': 48,
            'fontcolor': '#FF4500',
            'borderw': 4,
            'bordercolor': '#FFD700',
            'shadowcolor': 'black',
            'shadowx': 4,
            'shadowy': 4,
            'box': 0,
        },
        'pink_glow': {
            'fontsize': 46,
            'fontcolor': '#FF69B4',
            'borderw': 4,
            'bordercolor': '#FF1493',
            'shadowcolor': '#8B008B',
            'shadowx': 3,
            'shadowy': 3,
            'box': 0,
        },
        'green_neon': {
            'fontsize': 46,
            'fontcolor': '#00FF00',
            'borderw': 4,
            'bordercolor': '#006400',
            'shadowcolor': 'black',
            'shadowx': 3,
            'shadowy': 3,
            'box': 0,
        },
        'golden': {
            'fontsize': 48,
            'fontcolor': '#FFD700',
            'borderw': 4,
            'bordercolor': '#8B4513',
            'shadowcolor': 'black',
            'shadowx': 4,
            'shadowy': 4,
            'box': 0,
        },
        'tiktok': {
            'fontsize': 50,
            'fontcolor': 'white',
            'borderw': 5,
            'bordercolor': 'black',
            'shadowcolor': '#FF0050',
            'shadowx': 4,
            'shadowy': 4,
            'box': 0,
        },
        'instagram': {
            'fontsize': 46,
            'fontcolor': 'white',
            'borderw': 0,
            'box': 1,
            'boxcolor': '#833AB4@0.85',
            'boxborderw': 15,
        },
        # ===== PREMIUM HINDI STYLES =====
        'royal_saffron': {
            # Indian flag saffron - PERFECT for patriotic/historical content
            'fontsize': 50,
            'fontcolor': '#FF9933',  # Saffron
            'borderw': 5,
            'bordercolor': '#4A2C0A',  # Deep brown
            'shadowcolor': 'black',
            'shadowx': 4,
            'shadowy': 4,
            'box': 0,
        },
        'ancient_gold': {
            # Royal Mughal/Rajput era aesthetic
            'fontsize': 50,
            'fontcolor': '#DAA520',  # Antique gold
            'borderw': 5,
            'bordercolor': '#800000',  # Deep maroon
            'shadowcolor': 'black',
            'shadowx': 5,
            'shadowy': 5,
            'box': 0,
        },
        'cinematic': {
            # Netflix/Amazon Prime style - clean and professional
            'fontsize': 48,
            'fontcolor': 'white',
            'borderw': 6,
            'bordercolor': 'black',
            'shadowcolor': '#333333',
            'shadowx': 2,
            'shadowy': 2,
            'box': 0,
        },
        'electric_cyan': {
            # Modern viral TikTok aesthetic
            'fontsize': 50,
            'fontcolor': '#00FFFF',  # Cyan
            'borderw': 4,
            'bordercolor': '#0080FF',  # Electric blue
            'shadowcolor': '#004080',
            'shadowx': 4,
            'shadowy': 4,
            'box': 0,
        },
        'dramatic_red': {
            # For intense war/battle/dramatic moments
            'fontsize': 50,
            'fontcolor': '#DC143C',  # Crimson red
            'borderw': 5,
            'bordercolor': 'black',
            'shadowcolor': '#8B0000',
            'shadowx': 4,
            'shadowy': 4,
            'box': 0,
        },
        'mystic_purple': {
            # Mysterious, royal purple aesthetic
            'fontsize': 50,
            'fontcolor': '#9B30FF',  # Purple
            'borderw': 4,
            'bordercolor': '#4B0082',  # Indigo
            'shadowcolor': 'black',
            'shadowx': 4,
            'shadowy': 4,
            'box': 0,
        },
        'sunset_orange': {
            # Warm, dramatic sunset vibes
            'fontsize': 50,
            'fontcolor': '#FF6B35',  # Sunset orange
            'borderw': 5,
            'bordercolor': '#C41E3A',  # Cardinal red
            'shadowcolor': 'black',
            'shadowx': 4,
            'shadowy': 4,
            'box': 0,
        },
        'desi_festival': {
            # Vibrant festival colors (Holi/Diwali vibe)
            'fontsize': 52,
            'fontcolor': '#FF1493',  # Deep pink
            'borderw': 5,
            'bordercolor': '#FFD700',  # Gold
            'shadowcolor': '#8B008B',
            'shadowx': 4,
            'shadowy': 4,
            'box': 0,
        },
        'white_premium': {
            # Clean white with soft glow - very readable
            'fontsize': 50,
            'fontcolor': 'white',
            'borderw': 4,
            'bordercolor': '#222222',
            'shadowcolor': '#666666',
            'shadowx': 3,
            'shadowy': 3,
            'box': 0,
        },
        'neon_blue': {
            # Electric neon blue - very vibrant
            'fontsize': 50,
            'fontcolor': '#00BFFF',  # Deep sky blue
            'borderw': 4,
            'bordercolor': '#1E90FF',
            'shadowcolor': '#000080',
            'shadowx': 5,
            'shadowy': 5,
            'box': 0,
        },
    }
    
    def __init__(self):
        # Find a Hindi-supporting font
        self.font_path = self._find_hindi_font()
        
    def _find_hindi_font(self) -> str:
        """Find a font that supports Hindi/Devanagari"""
        # Common Hindi-supporting fonts on macOS/Linux
        font_paths = [
            # macOS
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
            "/System/Library/Fonts/Kohinoor.ttc",
            "/System/Library/Fonts/Supplemental/Kohinoor Devanagari.ttc",
            # Linux
            "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            # Fallback
            "Arial",
        ]
        
        for font in font_paths:
            if os.path.exists(font):
                logger.info(f"📝 Using font: {font}")
                return font
        
        logger.warning("⚠️ No Hindi font found, using default")
        return "Arial"
    
    def create_captions_from_script(
        self,
        segments: List[Dict],
        voiceover_duration: float
    ) -> List[CaptionSegment]:
        """
        Create caption segments from script segments
        
        Args:
            segments: List of {narration_text, duration_seconds}
            voiceover_duration: Total voiceover duration for timing adjustment
        """
        captions = []
        current_time = 0.0
        
        # Calculate timing based on actual voiceover duration
        total_script_duration = sum(seg.get('duration_seconds', 5.0) for seg in segments)
        time_scale = voiceover_duration / total_script_duration if total_script_duration > 0 else 1.0
        
        for seg in segments:
            text = seg.get('narration_text', '')
            duration = seg.get('duration_seconds', 5.0) * time_scale
            
            # Split long text into multiple lines
            text = self._format_caption_text(text)
            
            caption = CaptionSegment(
                text=text,
                start_time=current_time,
                end_time=current_time + duration - 0.1  # Small gap between captions
            )
            captions.append(caption)
            current_time += duration
        
        return captions
    
    def _format_caption_text(self, text: str, max_chars_per_line: int = 35) -> str:
        """Format text for caption display (wrap long lines)"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_chars_per_line:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word) + 1
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Max 3 lines
        if len(lines) > 3:
            lines = lines[:3]
            lines[2] = lines[2][:max_chars_per_line-3] + '...'
        
        return '\n'.join(lines)
    
    async def add_captions_to_video(
        self,
        video_path: str,
        captions: List[CaptionSegment],
        output_path: str,
        style: str = 'default',
        position: str = 'bottom',  # 'top', 'center', 'bottom'
        animate: bool = True  # Add fade-in animation
    ) -> str:
        """
        Add burned-in captions to video using FFmpeg
        
        Args:
            video_path: Input video path
            captions: List of CaptionSegment
            output_path: Output video path
            style: Style preset name
            position: Caption position
            animate: Whether to add fade-in animation
        
        Returns:
            Path to output video with captions
        """
        logger.info(f"📝 Adding captions to video...")
        logger.info(f"   Style: {style}")
        logger.info(f"   Position: {position}")
        logger.info(f"   Segments: {len(captions)}")
        logger.info(f"   Animation: {'fade-in' if animate else 'none'}")
        
        # Get style settings
        style_settings = self.STYLES.get(style, self.STYLES['default'])
        
        # Calculate Y position
        y_positions = {
            'top': 'h*0.1',
            'center': '(h-text_h)/2',
            'bottom': 'h*0.75'
        }
        y_pos = y_positions.get(position, y_positions['bottom'])
        
        # Build FFmpeg drawtext filter
        filter_parts = []
        
        for i, caption in enumerate(captions):
            # Escape special characters for FFmpeg
            escaped_text = self._escape_ffmpeg_text(caption.text)
            
            # Build drawtext filter for this segment
            fade_duration = 0.3  # 300ms fade
            
            # Alpha expression for fade-in effect
            if animate:
                alpha_expr = (
                    f"if(lt(t-{caption.start_time:.2f},{fade_duration}),"
                    f"(t-{caption.start_time:.2f})/{fade_duration},1)"
                )
                alpha_part = f":alpha='{alpha_expr}'"
            else:
                alpha_part = ""
            
            drawtext = (
                f"drawtext="
                f"fontfile='{self.font_path}':"
                f"text='{escaped_text}':"
                f"fontsize={style_settings['fontsize']}:"
                f"fontcolor={style_settings['fontcolor']}:"
                f"x=(w-text_w)/2:"
                f"y={y_pos}:"
                f"enable='between(t,{caption.start_time:.2f},{caption.end_time:.2f})'"
                f"{alpha_part}"
            )
            
            # Add border if specified
            if style_settings.get('borderw', 0) > 0:
                drawtext += (
                    f":borderw={style_settings['borderw']}"
                    f":bordercolor={style_settings.get('bordercolor', 'black')}"
                )
            
            # Add shadow if specified
            if style_settings.get('shadowcolor'):
                drawtext += (
                    f":shadowcolor={style_settings['shadowcolor']}"
                    f":shadowx={style_settings.get('shadowx', 2)}"
                    f":shadowy={style_settings.get('shadowy', 2)}"
                )
            
            # Add box if enabled
            if style_settings.get('box'):
                drawtext += (
                    f":box={style_settings['box']}"
                    f":boxcolor={style_settings['boxcolor']}"
                    f":boxborderw={style_settings['boxborderw']}"
                )
            
            filter_parts.append(drawtext)
        
        # Combine all filters
        filter_complex = ','.join(filter_parts)
        
        # Build FFmpeg command
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output
            '-i', video_path,
            '-vf', filter_complex,
            '-c:a', 'copy',  # Copy audio without re-encoding
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            output_path
        ]
        
        logger.info(f"🎬 Running FFmpeg...")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise Exception(f"FFmpeg failed: {result.stderr[:500]}")
            
            logger.info(f"✅ Captions added: {output_path}")
            return output_path
            
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timed out")
            raise Exception("FFmpeg caption rendering timed out")
    
    def _escape_ffmpeg_text(self, text: str) -> str:
        """Escape special characters for FFmpeg drawtext filter"""
        # FFmpeg drawtext requires escaping of certain characters
        text = text.replace("\\", "\\\\")
        text = text.replace("'", "\\'")
        text = text.replace(":", "\\:")
        text = text.replace("[", "\\[")
        text = text.replace("]", "\\]")
        text = text.replace(",", "\\,")
        text = text.replace(";", "\\;")
        return text
    
    async def add_word_by_word_captions(
        self,
        video_path: str,
        full_text: str,
        start_time: float,
        end_time: float,
        output_path: str,
        style: str = 'highlight'
    ) -> str:
        """
        Add word-by-word highlight captions (karaoke style)
        Each word highlights as it's spoken
        """
        words = full_text.split()
        duration = end_time - start_time
        time_per_word = duration / len(words)
        
        captions = []
        for i, word in enumerate(words):
            word_start = start_time + (i * time_per_word)
            word_end = word_start + time_per_word
            
            # Show all words, highlight current one
            display_text = ' '.join(
                f"[{w}]" if j == i else w 
                for j, w in enumerate(words)
            )
            
            captions.append(CaptionSegment(
                text=display_text,
                start_time=word_start,
                end_time=word_end
            ))
        
        return await self.add_captions_to_video(
            video_path, captions, output_path, style
        )


# Singleton instance
caption_generator = CaptionGeneratorService()
