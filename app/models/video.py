"""
Data models for the video creation pipeline
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum
from datetime import datetime
import uuid


class VideoStatus(str, Enum):
    """Status of video creation process"""
    PENDING = "pending"
    GENERATING_SCRIPT = "generating_script"
    GENERATING_IMAGES = "generating_images"
    CREATING_VIDEO = "creating_video"
    GENERATING_VOICEOVER = "generating_voiceover"
    COMPOSITING = "compositing"
    COMPLETED = "completed"
    FAILED = "failed"


class MusicMood(str, Enum):
    """Background music mood categories"""
    DRAMATIC = "dramatic"
    SUSPENSE = "suspense"
    INSPIRING = "inspiring"
    EMOTIONAL = "emotional"
    ADVENTURE = "adventure"


class StoryLens(str, Enum):
    """
    POV Engine: Fixed storytelling perspective for channel identity.
    Every story is filtered through ONE of these lenses to build
    a recognizable brand and train the audience.
    """
    POWER = "power_and_control"           # Stories about power dynamics, control, dominance
    FEAR = "fear_to_courage"               # Stories of overcoming fear, bravery moments
    BETRAYAL = "betrayal_and_consequences" # Stories of treachery and its aftermath
    TURNING_POINT = "single_decision_moments"  # One irreversible choice that changed everything
    UNDERRATED = "history_ignored_this"    # Hidden gems, overlooked heroes, forgotten events


class EmotionalState(str, Enum):
    """
    Emotional arc states for each segment.
    Used for visual styling, motion, and music dynamics.
    """
    TENSION = "tension"          # Building unease, uncertainty
    FEAR = "fear"                # Danger, threat, vulnerability
    DECISION = "decision"        # The pivotal choice moment
    IMPACT = "impact"            # Consequence, aftermath, result
    REFLECTION = "reflection"    # Meaning, lesson, lingering thought


class ScriptSegment(BaseModel):
    """A segment of the script with corresponding image prompt"""
    segment_number: int
    narration_text: str  # Hindi narration text
    image_prompt: str  # English prompt for image generation
    duration_seconds: float = 4.0  # Duration for this segment
    emotional_state: EmotionalState = EmotionalState.TENSION  # Emotional arc state for visuals/music


class VideoScript(BaseModel):
    """Complete script for a video"""
    title: str
    hook: str  # Opening hook to grab attention
    segments: List[ScriptSegment]
    total_duration: float
    music_mood: MusicMood = MusicMood.DRAMATIC
    historical_era: str
    event_description: str
    story_lens: StoryLens = StoryLens.TURNING_POINT  # POV lens for consistent storytelling


class GeneratedImage(BaseModel):
    """Generated image data"""
    segment_number: int
    image_url: str
    local_path: Optional[str] = None
    prompt_used: str


class VideoProject(BaseModel):
    """Complete video project data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    topic: str
    status: VideoStatus = VideoStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Generated content
    script: Optional[VideoScript] = None
    images: List[GeneratedImage] = []
    
    # Output paths
    voiceover_path: Optional[str] = None
    base_video_path: Optional[str] = None
    final_video_path: Optional[str] = None
    music_path: Optional[str] = None
    
    # Metadata
    error_message: Optional[str] = None


class VideoRequest(BaseModel):
    """Request to create a new video"""
    topic: str = Field(..., description="Historical event or topic for the video")
    era: str = Field(..., description="Historical era (e.g., 'Stone Age', '1857 Revolution')")
    num_segments: int = Field(default=10, ge=5, le=15)
    target_duration: int = Field(default=40, ge=30, le=60)
    music_mood: MusicMood = MusicMood.DRAMATIC
    story_lens: StoryLens = StoryLens.TURNING_POINT  # POV lens for storytelling
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Discovery of Fire",
                "era": "Stone Age",
                "num_segments": 10,
                "target_duration": 40,
                "music_mood": "dramatic",
                "story_lens": "single_decision_moments"
            }
        }

