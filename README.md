# 🎬 Viral Reel Creator - AI Video Generator for Hindi Historical Shorts

Automated video creation platform that creates **VIRAL Hindi historical reels** using real-time YouTube trend analysis.

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **🔥 YouTube Trend Analysis** | Analyzes 50+ trending videos to learn viral patterns |
| **🎯 Viral Hook Generator** | Creates scroll-stopping hooks using proven formulas |
| **🎬 AI Video Generation** | FLUX images + Ken Burns effects |
| **🎙️ Hindi Voiceover** | ElevenLabs TTS with auto voice selection |
| **📤 YouTube Auto-Upload** | Direct publish to your channel |

## ⚡ Quick Start

```bash
# 1. Setup
git clone https://github.com/hjjain/Youtube-Automation-Platform.git
cd Youtube-Automation-Platform
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Copy env.example to .env and add API keys
cp env.example .env

# 3. Add these API keys to .env
REPLICATE_API_TOKEN=your_key
ELEVENLABS_API_KEY=your_key
YOUTUBE_API_KEY=your_key  # FREE from Google Cloud

# 4. Test everything works
python test_trends.py

# 5. Create your first viral video!
python create_video.py auto
```

## 🎯 CLI Commands

### Create Videos

```bash
# Auto-create one viral video (auto-selects trending topic)
python create_video.py auto

# Create video with specific story lens
python create_video.py auto --lens revenge_and_justice
python create_video.py auto --lens betrayal_and_consequences
python create_video.py auto --lens forgotten_heroes

# Manual topic override
python create_video.py manual --topic "Bhagat Singh" --era "Freedom Struggle"

# Create 3 videos in batch
python create_video.py batch --count 3
```

### View Trending Topics

```bash
# See what's trending right now
python create_video.py topics

# Get raw trend data
python create_video.py trends
```

### 📤 Publish to YouTube

```bash
# Create video AND upload to YouTube (private)
python create_video.py publish

# Create and upload as unlisted
python create_video.py publish --privacy unlisted

# Create and upload as public
python create_video.py publish --privacy public

# Publish with specific story lens
python create_video.py publish --lens revenge_and_justice
```

### YouTube OAuth Setup (One-time)

Before publishing, you need to set up YouTube OAuth:

1. **Go to [Google Cloud Console](https://console.cloud.google.com)**
2. **Create a new project** (or select existing)
3. **Enable YouTube Data API v3**:
   - Go to "APIs & Services" → "Library"
   - Search "YouTube Data API v3" → Enable
4. **Create OAuth Credentials**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Download the JSON file
5. **Save as** `credentials/youtube_oauth.json`
6. **First run**: When you run `publish`, it will open a browser for OAuth consent
7. **Token saved**: After consent, token is saved to `credentials/youtube_token.json`

```bash
# Your credentials folder should look like:
credentials/
├── youtube_oauth.json    # OAuth client (from Google Cloud)
└── youtube_token.json    # Auto-generated after first auth
```

## 🎬 Video Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    VIRAL VIDEO PIPELINE                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1️⃣ TREND RESEARCH                                          │
│     └── YouTube Trending India                               │
│     └── Google Trends (real-time)                           │
│     └── News Headlines (RSS feeds)                          │
│                                                              │
│  2️⃣ TOPIC SELECTION (LLM)                                   │
│     └── Find historical angle for trending topic            │
│     └── Apply story lens (revenge, betrayal, heroes)        │
│                                                              │
│  3️⃣ VIRAL HOOK GENERATION                                   │
│     └── Use proven viral formulas                           │
│     └── Generate 10 hooks, pick the best                    │
│                                                              │
│  4️⃣ SCRIPT GENERATION                                       │
│     └── 40-second viral-optimized Hindi script              │
│     └── Emotional arc for engagement                        │
│                                                              │
│  5️⃣ VOICEOVER FIRST                                         │
│     └── ElevenLabs Hindi voice                              │
│     └── Measure duration for scene timing                   │
│                                                              │
│  6️⃣ AI IMAGE GENERATION                                     │
│     └── FLUX/SDXL historical images                         │
│     └── Number of scenes based on voiceover length          │
│                                                              │
│  7️⃣ VIDEO COMPOSITION                                       │
│     └── Ken Burns zoom/pan effects                          │
│     └── Background music by mood                            │
│     └── Hindi captions                                       │
│     └── 9:16 format for Reels/Shorts                        │
│                                                              │
│  8️⃣ YOUTUBE UPLOAD (Optional)                               │
│     └── Auto-generate title & description                   │
│     └── Add tags and category                               │
│     └── Upload as private/unlisted/public                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🎣 Story Lenses

The system uses these narrative lenses for compelling content:

| Lens | Description |
|------|-------------|
| `revenge_and_justice` | Stories of comeuppance and karma |
| `betrayal_and_consequences` | Trust broken, prices paid |
| `forgotten_heroes` | Unsung champions of history |
| `rise_and_fall` | Power gained and lost |
| `against_all_odds` | Impossible victories |

## 🔑 API Keys Needed

| Service | Cost | Get From |
|---------|------|----------|
| **Replicate** | Pay per use (~$0.01/image) | [replicate.com](https://replicate.com) |
| **ElevenLabs** | Free tier (10k chars/month) | [elevenlabs.io](https://elevenlabs.io) |
| **YouTube Data API** | **FREE** (10k requests/day) | [Google Cloud Console](https://console.cloud.google.com) |

## 📁 Project Structure

```
Youtube-Automation-Platform/
├── app/
│   ├── api/routes.py           # API endpoints
│   ├── main.py                 # FastAPI app
│   └── services/
│       ├── trend_researcher.py     # Real-time trends
│       ├── youtube_analyzer.py     # Viral patterns
│       ├── hook_generator.py       # Hook creation
│       ├── script_generator.py     # Script writing
│       ├── voiceover_generator.py  # ElevenLabs TTS
│       ├── image_generator.py      # FLUX images
│       ├── video_composer.py       # Final video
│       └── youtube_uploader.py     # YouTube upload
├── music/                      # Background music library
│   ├── dramatic/
│   ├── inspiring/
│   ├── suspense/
│   └── emotional/
├── credentials/                # YouTube OAuth (gitignored)
├── output/                     # Generated videos (gitignored)
├── create_video.py             # Main CLI
└── requirements.txt            # Dependencies
```

## 🎨 Background Music

Add royalty-free music to `music/` folder:
- `music/dramatic/` - War, revolution content
- `music/suspense/` - Mystery, secrets
- `music/inspiring/` - Discoveries, achievements
- `music/emotional/` - Sad, nostalgic stories

Download from [YouTube Audio Library](https://studio.youtube.com/channel/UCaudio/music) (FREE).

## 📝 License

MIT License - Use freely for personal and commercial projects.
