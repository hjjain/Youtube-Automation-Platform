# 🎬 Autonomous Content Pipeline: Trend-to-Video Engine

> A fully automated system that researches trending topics, generates AI-powered historical content in Hindi, and publishes viral-optimized short-form videos to YouTube.

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [System Architecture](#-system-architecture)
3. [Tech Stack](#-tech-stack)
4. [Pipeline Deep Dive](#-pipeline-deep-dive)
5. [Service Components](#-service-components)
6. [API Endpoints](#-api-endpoints)
7. [Data Models](#-data-models)
8. [Configuration](#-configuration)
9. [Deployment](#-deployment)
10. [Performance Metrics](#-performance-metrics)

---

## 🎯 Project Overview

### What It Does

This platform creates **fully autonomous** Hindi historical content for Instagram Reels and YouTube Shorts. The system:

1. **Researches** real-time trends from YouTube India, Google Trends, and news sources
2. **Identifies** viral historical angles using LLM-powered semantic analysis
3. **Generates** complete video content: script, voiceover, images, and video clips
4. **Composes** final videos with background music, captions, and proper formatting
5. **Publishes** directly to YouTube with SEO-optimized metadata

### Key Differentiators

| Feature | Implementation |
|---------|---------------|
| **Zero-Touch Automation** | End-to-end pipeline from trend detection to YouTube upload |
| **Real-Time Trend Integration** | YouTube Data API + Google Trends + RSS feeds for live signals |
| **Multi-Model AI Pipeline** | 4 AI models orchestrated: GPT-5.2 (script), ElevenLabs (voice), SeeDream (images), Kling (video) |
| **Parallel Processing** | Async/await with 4-way concurrency for GenAI asset generation |
| **Hindi-First Design** | Devanagari script support, Hindi TTS, India-focused trends |

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AUTONOMOUS CONTENT PIPELINE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   TREND     │───▶│   TOPIC     │───▶│   SCRIPT    │───▶│  VOICEOVER  │  │
│  │  RESEARCH   │    │  SELECTION  │    │ GENERATION  │    │ GENERATION  │  │
│  │             │    │             │    │             │    │             │  │
│  │ • YouTube   │    │ • LLM       │    │ • GPT-5.2   │    │ • ElevenLabs│  │
│  │ • Google    │    │   Analysis  │    │ • Hook Gen  │    │ • Hindi TTS │  │
│  │ • RSS News  │    │ • Historical│    │ • Viral     │    │ • Multilingual│ │
│  │ • DuckDuckGo│    │   Mapping   │    │   Patterns  │    │   v2        │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                                                        │          │
│         │                                                        ▼          │
│         │              ┌─────────────────────────────────────────────┐      │
│         │              │           DURATION CALCULATION              │      │
│         │              │  voiceover_duration → num_scenes (6-10)     │      │
│         │              │  video_duration = num_scenes × 5 seconds    │      │
│         │              └─────────────────────────────────────────────┘      │
│         │                                    │                              │
│         ▼                                    ▼                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   IMAGE     │───▶│   VIDEO     │───▶│   VIDEO     │───▶│  YOUTUBE    │  │
│  │ GENERATION  │    │ GENERATION  │    │ COMPOSITION │    │   UPLOAD    │  │
│  │             │    │             │    │             │    │             │  │
│  │ • SeeDream  │    │ • Kling v2.1│    │ • MoviePy   │    │ • OAuth 2.0 │  │
│  │   4.5       │    │ • Parallel  │    │ • FFmpeg    │    │ • Metadata  │  │
│  │ • Sequential│    │   (4-way)   │    │ • Captions  │    │ • Captions  │  │
│  │   Images    │    │ • 5s clips  │    │ • Music     │    │ • SEO Tags  │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Trend Signal ──▶ LLM Analysis ──▶ Script + Hook ──▶ Voiceover (duration) 
     │                                                      │
     │                                              ┌───────┴───────┐
     │                                              │ Calculate:    │
     │                                              │ • num_scenes  │
     │                                              │ • video_dur   │
     │                                              └───────────────┘
     │                                                      │
     ▼                                                      ▼
Image Prompts ──▶ SeeDream 4.5 ──▶ Images ──▶ Kling v2.1 ──▶ Video Clips
                                                                  │
                                                                  ▼
                                              ┌───────────────────────────┐
                                              │ Video Composition:        │
                                              │ • Merge clips            │
                                              │ • Add voiceover (100%)   │
                                              │ • Add music (18%)        │
                                              │ • Burn-in captions       │
                                              │ • Export 9:16 @ 30fps    │
                                              └───────────────────────────┘
                                                                  │
                                                                  ▼
                                                         YouTube Upload
```

---

## 🛠 Tech Stack

### Backend Framework
| Component | Technology | Purpose |
|-----------|------------|---------|
| Web Framework | **FastAPI** | Async REST API with OpenAPI docs |
| Background Tasks | **FastAPI BackgroundTasks** | Non-blocking pipeline execution |
| Async Runtime | **asyncio** | Concurrent I/O operations |
| HTTP Client | **httpx** | Async API calls to external services |

### AI/ML Services
| Service | Provider | Model | Purpose |
|---------|----------|-------|---------|
| LLM | Replicate | `openai/gpt-5.2` | Script generation, trend analysis (with reasoning) |
| Text-to-Speech | ElevenLabs | `eleven_multilingual_v2` | Hindi voiceover |
| Image Generation | Replicate | `bytedance/seedream-4.5` | Sequential image synthesis |
| Video Generation | Replicate | `kwaivgi/kling-v2.1` | Image-to-video conversion |

### Video Processing
| Component | Technology | Purpose |
|-----------|------------|---------|
| Video Editing | **MoviePy v2** | Clip merging, audio mixing |
| Caption Rendering | **FFmpeg** | Burned-in Hindi subtitles |
| Audio Processing | **pydub** | Audio manipulation |
| Image Processing | **Pillow** | Image handling |

### Trend Research
| Source | Library/API | Data Retrieved |
|--------|-------------|----------------|
| YouTube Trending | `google-api-python-client` | Top 50 videos in India |
| Google Trends | `pytrends` | Real-time search trends |
| News Headlines | `feedparser` | TOI, Hindustan Times, Indian Express RSS |
| Web Search | `duckduckgo-search` | Viral content signals |

### YouTube Integration
| Feature | Implementation |
|---------|---------------|
| Authentication | OAuth 2.0 with refresh tokens |
| Video Upload | Resumable upload (1MB chunks) |
| Caption Upload | SRT format, Hindi language |
| Metadata | Auto-generated SEO tags, descriptions |

---

## 🔄 Pipeline Deep Dive

### 7-Stage Video Creation Pipeline

```python
# Execution Order (from pipeline.py)
STEP 1: Script Generation (LLM)      →  5-15 seconds
STEP 2: Voiceover (ElevenLabs)       →  10-30 seconds  
STEP 3: Calculate Video Parameters   →  <1 second
STEP 4: Image Generation (SeeDream)  →  2-5 minutes
STEP 5: Video Generation (Kling)     →  5-10 minutes (parallel)
STEP 6: Background Music (Local)     →  <1 second
STEP 7: Final Composition (MoviePy)  →  30-60 seconds
```

### Stage Details

#### Stage 1: Script Generation
```
Input:  Topic, Era, Mood
Output: VideoScript with 6-10 segments

Process:
1. Generate viral hook using hook_generator
2. Fetch similar viral content from YouTube
3. Build prompt with viral patterns + hook formulas
4. Call GPT-5.2 for script generation (with reasoning)
5. Parse response into structured segments
6. Each segment contains:
   - narration_text (Hindi)
   - image_prompt (English, sanitized)
   - duration_seconds (5s each)
```

#### Stage 2: Voiceover Generation
```
Input:  VideoScript
Output: MP3 audio file, duration in seconds

Process:
1. Concatenate all narration_text with pauses
2. Call ElevenLabs API with:
   - Model: eleven_multilingual_v2
   - Voice: Bunty (FZkK3TvQ0pjyDmT8fzIW)
   - Settings: stability=0.7, style=0.15
3. Save audio to temp/{project_id}/voiceover.mp3
4. Measure actual duration with MoviePy AudioFileClip
```

#### Stage 3: Duration Calculation
```python
def _calculate_video_duration(voiceover_duration: float):
    buffer = 2  # seconds
    target_duration = voiceover_duration + buffer
    video_duration = ceil(target_duration / 5) * 5  # Round to nearest 5
    num_scenes = video_duration // 5
    num_scenes = max(6, min(10, num_scenes))  # Clamp to 6-10
    return video_duration, num_scenes
```

#### Stage 4: Image Generation
```
Input:  Script segments, num_images
Output: List of GeneratedImage with URLs and local paths

Process:
1. Build mega-prompt for sequential generation
2. Sanitize prompts (remove violence, weapons)
3. Call SeeDream 4.5 API:
   - size: 2K (2048x2048)
   - aspect_ratio: 9:16
   - max_images: num_scenes
   - sequential_image_generation: auto
4. Poll for completion (up to 10 minutes)
5. Download all images to temp/{project_id}/images/
```

#### Stage 5: Video Generation (Parallel)
```
Input:  List of images, motion prompts
Output: List of 5-second video clips

Process:
1. Create tasks for each image
2. Execute in batches of 4 (max_concurrent)
3. For each image:
   - Generate motion prompt based on position
   - Call Kling v2.1 API
   - Poll for completion
   - Download video clip
4. Sort results by segment_number
5. Save to temp/{project_id}/clips/
```

#### Stage 6: Background Music
```
Input:  Music mood, target duration
Output: Path to trimmed/looped music file

Process:
1. Look up music/{mood}/ directory
2. Select random track
3. Loop if shorter than target
4. Trim to match video duration
5. Apply 2-second fade out
```

#### Stage 7: Final Composition
```
Input:  Video clips, voiceover, music, captions
Output: Final MP4 at output/reel_{project_id}.mp4

Process:
1. Merge video clips (concatenate_videoclips)
2. Adjust speed if duration mismatch > 3s
3. Mix audio:
   - Voiceover: 100% volume
   - Background music: 18% volume
4. Add burned-in captions via FFmpeg:
   - Style: cinematic (Netflix-style)
   - Position: bottom (75% height)
   - Animation: fade-in (0.3s)
5. Export: 9:16, 30fps, libx264, AAC audio
```

---

## 🧩 Service Components

### 1. Trend Researcher (`trend_researcher.py`)

**Purpose**: Aggregate real-time trend signals from multiple sources

```python
class TrendResearcherService:
    # Data Sources
    NEWS_FEEDS = [
        "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
        "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
        "https://indianexpress.com/feed/",
    ]
    
    # Methods
    async def get_trending_topic() -> Dict
    async def _gather_all_trends() -> Dict
    def _get_youtube_trending_india() -> List[Dict]
    def _get_google_trends_india() -> List[str]
    def _get_news_headlines() -> List[Dict]
    def _search_viral_content() -> List[Dict]
    async def _analyze_trends_with_llm(trends_data: Dict) -> Dict
```

**Output Structure**:
```python
{
    "youtube_trend": "Video title that inspired this",
    "topic": "Historical topic chosen",
    "era": "Historical era",
    "connection": "How it connects to trend",
    "hook": "Hindi hook in Devanagari",
    "mood": "dramatic|suspense|inspiring|emotional|adventure",
    "reason": "Why this will go viral"
}
```

### 2. YouTube Analyzer (`youtube_analyzer.py`)

**Purpose**: Deep analysis of viral patterns on YouTube India

```python
class YouTubeAnalyzerService:
    async def analyze_viral_patterns() -> Dict
    async def search_similar_viral_content(topic: str) -> List[Dict]
    async def get_comment_insights(video_id: str) -> Dict
    async def get_competitor_analysis(keywords: List[str]) -> List[Dict]
```

**Analysis Metrics**:
- Engagement rate: `(likes + comments) / views * 100`
- Hook patterns: curiosity, shock, FOMO indicators
- Title patterns: length, power words, emoji usage
- Winning keywords: weighted by view count

### 3. Hook Generator (`hook_generator.py`)

**Purpose**: Generate scroll-stopping viral hooks using proven formulas

```python
class HookGeneratorService:
    HOOK_FORMULAS = {
        "curiosity_gap": [...],      # "99% Indians don't know..."
        "shock_value": [...],        # "Warning: ये video..."
        "time_travel": [...],        # "POV: तुम 1947 में हो..."
        "fomo": [...],               # "ये video delete होने से पहले..."
        "question_hook": [...],      # "कभी सोचा है..."
        "story_hook": [...],         # "ये कहानी सुनोगे तो..."
        "challenge_belief": [...]    # "जो पढ़ा था वो सब गलत है..."
    }
    
    async def generate_viral_hook(topic, era, mood) -> Dict
```

**Hook Scoring Algorithm**:
```python
score = 0
if len(hook) < 50: score += 10       # Shorter is better
if '?' in hook: score += 8            # Questions create curiosity
if has_emoji: score += 5              # Emojis catch attention
if has_power_word: score += 3         # "secret", "shocking", etc.
if starts_conversational: score += 7  # "देखो", "सुनो"
if has_number: score += 4             # "99%", "5 reasons"
```

### 4. Script Generator (`script_generator.py`)

**Purpose**: Generate complete Hindi scripts with viral optimization

**Prompt Engineering**:
- Complete story arc (hook → context → story → climax → answer → conclusion)
- 80-100 Hindi words total (~40 seconds)
- Each segment: 10-15 words max
- Image prompts: sanitized for content safety

### 5. Image Generator (`image_generator.py`)

**Purpose**: Generate sequential, visually coherent images

**Content Safety**:
```python
UNSAFE_WORDS = [
    'war', 'battle', 'fight', 'weapon', 'sword', 'blood',
    'violence', 'massacre', 'murder', 'explosion'...
]

SAFE_REPLACEMENTS = {
    'battle scene': 'dramatic gathering at ancient fort',
    'soldiers attacking': 'soldiers marching',
    'siege': 'fortified structure'
}
```

### 6. Video Generator (`video_generator.py`)

**Purpose**: Convert images to 5-second video clips with motion

**Parallel Processing**:
```python
max_concurrent = 4  # API rate limit protection

# Execute in parallel batches
for batch_start in range(0, len(tasks), max_concurrent):
    batch = tasks[batch_start:batch_end]
    batch_results = await asyncio.gather(*batch, return_exceptions=True)
```

**Motion Prompts by Position**:
- Opening: "Slow cinematic reveal, gentle camera drift"
- Building: "Subtle zoom in, building tension"
- Climax: "Dynamic but controlled motion, dramatic atmosphere"
- Closing: "Wide static shot, calm ending atmosphere"

### 7. Voiceover Generator (`voiceover_generator.py`)

**Purpose**: Generate Hindi TTS using ElevenLabs

**Voice Configuration**:
```python
VOICE_SETTINGS = {
    "stability": 0.7,          # High for clear pronunciation
    "similarity_boost": 0.75,
    "style": 0.15,             # Low for clarity over expression
    "use_speaker_boost": True
}
```

### 8. Caption Generator (`caption_generator.py`)

**Purpose**: Add burned-in Hindi subtitles with style presets

**Style Presets**:
```python
STYLES = {
    'cinematic': {      # Netflix-style clean
        'fontsize': 48, 'fontcolor': 'white',
        'borderw': 6, 'bordercolor': 'black'
    },
    'royal_saffron': {  # Indian patriotic
        'fontsize': 50, 'fontcolor': '#FF9933',
        'bordercolor': '#4A2C0A'
    },
    'tiktok': {         # Social media style
        'fontsize': 50, 'shadowcolor': '#FF0050'
    },
    # ... 20+ presets
}
```

### 9. Video Composer (`video_composer.py`)

**Purpose**: Merge all assets into final video

**Audio Mixing**:
```python
VOICEOVER_VOLUME = 1.0   # 100% - Primary audio
MUSIC_VOLUME = 0.18      # 18% - Subtle background
```

### 10. YouTube Uploader (`youtube_uploader.py`)

**Purpose**: Automated YouTube publishing with OAuth 2.0

**Quota Management**:
```python
# Daily limit: 10,000 units
VIDEO_UPLOAD_COST = 1600      # units
CAPTION_UPLOAD_COST = 200     # units
VIDEOS_PER_DAY = 5-6          # with captions
```

---

## 🌐 API Endpoints

### Video Creation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/videos/create-auto` | Create video with auto topic (background) |
| POST | `/api/videos/create-auto-sync` | Create video (wait for completion) |
| POST | `/api/videos/create` | Create with manual topic |
| POST | `/api/videos/batch?count=3` | Batch video creation |
| GET | `/api/videos/{project_id}/status` | Check project status |

### Trend Research
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/topics/trending` | Get auto-selected trending topic |
| GET | `/api/topics/upcoming?count=5` | Multiple topic suggestions |
| GET | `/api/topics/youtube-trending` | Raw YouTube trending data |
| GET | `/api/topics/raw-trends` | All trend sources (debug) |

### Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analyze/viral-patterns` | YouTube viral pattern analysis |
| GET | `/api/analyze/similar-content?topic=xyz` | Find similar viral videos |
| GET | `/api/analyze/competitor-channels?keywords=xyz` | Competitor analysis |

### Hook Generation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/hooks/generate?topic=xyz&era=abc` | Generate viral hooks |
| GET | `/api/hooks/formulas` | Get proven hook templates |

### Utilities
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/music/library` | List available background music |
| GET | `/api/voices/available` | List ElevenLabs voices |
| GET | `/api/health` | Health check |

---

## 📊 Data Models

### VideoRequest
```python
class VideoRequest(BaseModel):
    topic: str
    era: str = "Historical India"
    num_segments: int = 8
    target_duration: int = 40
    music_mood: MusicMood = MusicMood.DRAMATIC
```

### VideoScript
```python
class VideoScript(BaseModel):
    title: str
    hook: str
    segments: List[ScriptSegment]
    total_duration: float
    music_mood: MusicMood
    historical_era: Optional[str]
    event_description: Optional[str]
```

### ScriptSegment
```python
class ScriptSegment(BaseModel):
    segment_number: int
    narration_text: str      # Hindi in Devanagari
    image_prompt: str        # English, sanitized
    duration_seconds: float  # Usually 5.0
```

### VideoProject
```python
class VideoProject(BaseModel):
    id: str                  # UUID
    topic: str
    status: VideoStatus
    script: Optional[VideoScript]
    images: List[GeneratedImage]
    voiceover_path: Optional[str]
    music_path: Optional[str]
    final_video_path: Optional[str]
    created_at: datetime
    error_message: Optional[str]
```

### MusicMood (Enum)
```python
class MusicMood(str, Enum):
    DRAMATIC = "dramatic"
    SUSPENSE = "suspense"
    INSPIRING = "inspiring"
    EMOTIONAL = "emotional"
    ADVENTURE = "adventure"
```

---

## ⚙️ Configuration

### Environment Variables
```bash
# Required API Keys
REPLICATE_API_TOKEN=r8_xxxxx          # For GPT-5.2, SeeDream, Kling
ELEVENLABS_API_KEY=xxxxx              # For TTS
YOUTUBE_API_KEY=AIzaxxxxx             # For trend research (FREE)

# Optional
JAMENDO_CLIENT_ID=xxxxx               # For music API (not used currently)
CORS_ORIGINS=http://localhost:3000    # Frontend URL
```

### Application Settings (`config.py`)
```python
# Video Settings
VIDEO_DURATION_SECONDS = 40
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920  # 9:16 aspect ratio
FPS = 30

# Image Generation
IMAGES_PER_VIDEO = 8
IMAGE_MODEL = "bytedance/seedream-4.5"

# Video Generation
VIDEO_MODEL = "kwaivgi/kling-v2.1"
VIDEO_CLIP_DURATION = 5

# LLM
SCRIPT_MODEL = "openai/gpt-5.2"
LLM_REASONING_EFFORT = "medium"  # low, medium, high
LLM_VERBOSITY = "medium"         # low, medium, high

# Paths
OUTPUT_DIR = "./output"
MUSIC_DIR = "./music"
TEMP_DIR = "./temp"
```

---

## 🚀 Deployment

### Local Development
```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp env.example .env
# Edit .env with your API keys

# Run
python run_server.py
# API available at http://localhost:8000
```

### Railway (Backend)
```bash
# Auto-detected via nixpacks.toml
# Set environment variables in Railway dashboard
# Deploy from GitHub
```

### Vercel (Frontend)
```bash
# Root directory: frontend
# Environment: NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
```

---

## 📈 Performance Metrics

### Typical Pipeline Execution
| Stage | Duration | Notes |
|-------|----------|-------|
| Trend Research | 5-10s | API calls + LLM analysis |
| Script Generation | 5-15s | GPT-5.2 inference (with reasoning) |
| Voiceover | 10-30s | ElevenLabs API |
| Image Generation | 2-5 min | SeeDream 4.5 (8-10 images) |
| Video Generation | 5-10 min | Kling v2.1 (parallel 4x) |
| Composition | 30-60s | MoviePy + FFmpeg |
| **Total** | **8-15 min** | Full pipeline |

### API Costs (Approximate)
| Service | Cost per Video | Notes |
|---------|---------------|-------|
| Replicate (GPT-5.2) | ~$0.05 | Script + hooks (with reasoning) |
| Replicate (SeeDream) | ~$0.50 | 8-10 images |
| Replicate (Kling) | ~$2.00 | 8-10 video clips |
| ElevenLabs | ~$0.15 | 40s voiceover |
| YouTube API | FREE | 10k units/day |
| **Total** | **~$2.70** | Per video |

### Output Specifications
| Property | Value |
|----------|-------|
| Resolution | 1080x1920 (9:16) |
| Frame Rate | 30 FPS |
| Codec | H.264 (libx264) |
| Audio | AAC |
| Duration | 35-50 seconds |
| File Size | ~15-30 MB |

---

## 📁 Project Structure

```
proj-yt/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   ├── api/
│   │   └── routes.py              # API endpoint definitions
│   ├── core/
│   │   ├── config.py              # Settings & configuration
│   │   └── logger.py              # Logging setup
│   ├── models/
│   │   └── video.py               # Pydantic data models
│   └── services/
│       ├── pipeline.py            # Main orchestrator (7 stages)
│       ├── trend_researcher.py    # Multi-source trend aggregation
│       ├── youtube_analyzer.py    # Viral pattern analysis
│       ├── hook_generator.py      # Viral hook creation
│       ├── script_generator.py    # LLM script generation
│       ├── image_generator.py     # SeeDream 4.5 integration
│       ├── video_generator.py     # Kling v2.1 with parallel
│       ├── voiceover_generator.py # ElevenLabs TTS
│       ├── caption_generator.py   # FFmpeg burned-in captions
│       ├── video_composer.py      # Final video composition
│       ├── music_service.py       # Background music selection
│       ├── youtube_uploader.py    # OAuth 2.0 upload
│       └── voice_selector.py      # Voice selection logic
├── frontend/                      # Next.js dashboard
├── music/                         # Background music library
│   ├── dramatic/
│   ├── emotional/
│   ├── inspiring/
│   ├── suspense/
│   └── adventure/
├── output/                        # Final rendered videos
├── temp/                          # Working directory per project
├── credentials/                   # YouTube OAuth tokens
├── requirements.txt
├── run_server.py                  # Server entry point
├── create_video.py                # CLI entry point
└── test_trends.py                 # System tests
```

---

## 🔑 Key Technical Decisions

### 1. Voiceover-First Architecture
**Why**: Video duration is determined by voiceover, not the other way around. This ensures natural pacing.

### 2. Parallel Video Generation
**Why**: Kling v2.1 takes 1-2 minutes per clip. Sequential would take 8-16 minutes. Parallel (4x) reduces to 2-4 minutes.

### 3. Content Safety Filters
**Why**: GenAI image models flag violent content. Automatic sanitization prevents API rejections while maintaining dramatic storytelling.

### 4. Caption Burn-in vs SRT
**Why**: Burned-in captions ensure visibility across all platforms without relying on platform caption support.

### 5. Local Music Library
**Why**: Avoids API costs and copyright issues. YouTube Audio Library provides free, royalty-free music.

---

## 📜 License

MIT License - Use freely for personal and commercial projects.

---

*Built with ❤️ for automated content creation*
