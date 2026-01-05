# 🎬 Reel Creator - AI VIRAL Video Generator

The **ULTIMATE** automated video creation platform for Hindi historical reels. 
Uses **real-time YouTube trend analysis** to create **VIRAL content**.

## 🚀 What Makes This Different

| Feature | Description |
|---------|-------------|
| **🔥 YouTube Trend Analysis** | Analyzes 50+ trending videos to learn viral patterns |
| **🎯 Viral Hook Generator** | Creates scroll-stopping hooks using proven formulas |
| **📊 Engagement Analytics** | Studies views, likes, comments to find winning patterns |
| **🎬 Similar Content Search** | Finds what's already working for your topic |
| **🧠 LLM-Powered Research** | Connects trending topics to historical content |

## ⚡ Quick Start

```bash
# 1. Setup
cd proj-yt
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Add API keys to .env
REPLICATE_API_TOKEN=your_key
ELEVENLABS_API_KEY=your_key
YOUTUBE_API_KEY=your_key  # FREE from Google Cloud

# 3. Test everything works
python test_trends.py

# 4. Create your first viral video!
python create_video.py
```

## 🎯 How It Creates VIRAL Content

```
┌─────────────────────────────────────────────────────────────┐
│                    VIRAL VIDEO PIPELINE                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1️⃣ YOUTUBE ANALYSIS                                        │
│     └── Analyze 50 trending videos in India                 │
│     └── Extract winning hooks, titles, keywords             │
│     └── Study engagement patterns                           │
│                                                              │
│  2️⃣ TREND RESEARCH                                          │
│     └── Google Trends (real-time)                           │
│     └── News Headlines (RSS feeds)                          │
│     └── Web Search (viral content)                          │
│                                                              │
│  3️⃣ TOPIC SELECTION (LLM)                                   │
│     └── Find historical angle for trending topic            │
│     └── Connect current events to history                   │
│                                                              │
│  4️⃣ HOOK GENERATION                                         │
│     └── Use proven viral formulas                           │
│     └── Study similar viral content                         │
│     └── Generate 10 hooks, pick the best                    │
│                                                              │
│  5️⃣ SCRIPT + IMAGES + VOICEOVER                             │
│     └── Viral-optimized Hindi script                        │
│     └── AI-generated historical images                      │
│     └── Hindi voiceover with best-fit voice                 │
│                                                              │
│  6️⃣ FINAL VIDEO                                             │
│     └── Ken Burns effects                                   │
│     └── Background music by mood                            │
│     └── 9:16 format ready for Reels/Shorts                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 📊 API Endpoints

### Trend Research
| Endpoint | Description |
|----------|-------------|
| `GET /api/topics/youtube-trending` | YouTube trending videos in India |
| `GET /api/topics/trending` | Get auto-selected topic |
| `GET /api/topics/raw-trends` | All trend data (YouTube, Google, News) |

### Viral Analysis
| Endpoint | Description |
|----------|-------------|
| `GET /api/analyze/viral-patterns` | Full YouTube viral analysis |
| `GET /api/analyze/similar-content?topic=xyz` | Find similar viral videos |
| `POST /api/hooks/generate?topic=xyz&era=abc` | Generate viral hooks |
| `GET /api/hooks/formulas` | Get proven hook templates |

### Video Creation
| Endpoint | Description |
|----------|-------------|
| `POST /api/videos/create-auto-sync` | Create video with auto topic |
| `POST /api/videos/batch?count=3` | Create multiple videos |

## 🎣 Hook Formulas (Built-in)

The system uses these **proven viral hook patterns**:

```
CURIOSITY GAP:
- "99% Indians don't know this about {topic}..."
- "Yeh {topic} ki kahani aapne kabhi nahi suni hogi..."

SHOCK VALUE:
- "Warning: Yeh video dekhne ke baad soch badal jayegi"
- "History ki sabse shocking story..."

TIME TRAVEL:
- "POV: Tum {era} mein ho aur {topic} dekh rahe ho"
- "Chalo {era} mein chalte hain... dekho kya ho raha hai"

FOMO:
- "Yeh video delete hone se pehle dekh lo"
- "Sirf intelligent log hi samjhenge"

STORY HOOK:
- "Yeh kahani sunoge toh raat ko neend nahi aayegi"
- "Ek aisi kahani jo history books mein nahi milegi"
```

## 📁 Project Structure

```
proj-yt/
├── app/services/
│   ├── youtube_analyzer.py   ← 🆕 Viral pattern analysis
│   ├── hook_generator.py     ← 🆕 Viral hook creation
│   ├── trend_researcher.py   ← Real-time trend research
│   ├── voice_selector.py     ← Auto voice selection
│   ├── script_generator.py   ← Viral-optimized scripts
│   ├── image_generator.py    ← FLUX/SDXL images
│   ├── video_creator.py      ← Ken Burns effects
│   ├── voiceover_generator.py ← ElevenLabs TTS
│   └── video_composer.py     ← Final composition
├── test_trends.py            ← Test all systems
├── create_video.py           ← CLI (main entry)
└── run_server.py             ← API server
```

## 🔑 API Keys Needed

| Service | Cost | Get From |
|---------|------|----------|
| **Replicate** | Pay per use | [replicate.com](https://replicate.com) |
| **ElevenLabs** | Free tier available | [elevenlabs.io](https://elevenlabs.io) |
| **YouTube Data API** | **FREE** (10k/day) | [Google Cloud Console](https://console.cloud.google.com) |

## 🧪 Testing

```bash
# Test all systems
python test_trends.py

# Output:
# ✅ youtube_trending: PASS
# ✅ google_trends: PASS
# ✅ youtube_analyzer: PASS
# ✅ hook_generator: PASS
# ✅ full_research: PASS
# 🚀 SYSTEM READY! You can create viral videos now.
```

## 📈 Usage Examples

```bash
# Auto-create one viral video
python create_video.py

# Create 3 videos in batch
python create_video.py batch --count 3

# See what's trending right now
python create_video.py topics

# Manual topic override
python create_video.py manual --topic "Bhagat Singh" --era "Freedom Struggle"
```

## 🎨 Background Music

Add royalty-free music to `music/` folder:
- `music/dramatic/` - War, revolution content
- `music/suspense/` - Mystery, secrets
- `music/inspiring/` - Discoveries, achievements

Download from [YouTube Audio Library](https://studio.youtube.com/channel/UCaudio/music) (FREE).

## 🏆 Best Practices

1. **Run in batches** - Create 3+ videos at once for variety
2. **Check trends first** - Use `python create_video.py topics` before creating
3. **Add good music** - Background music significantly improves engagement
4. **Post consistently** - Algorithm favors regular uploads

---

## 🚀 Deployment (Production)

This project has a **frontend dashboard** and **backend API**. Both can be deployed FREE!

### Architecture

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     Vercel      │──────▶│    Railway      │──────▶│   External      │
│   (Frontend)    │ HTTPS │   (Backend)     │       │     APIs        │
│     FREE        │       │     FREE        │       │                 │
│                 │       │  🔐 API Keys    │       │ • Replicate     │
│  Next.js App    │       │  stored here    │       │ • ElevenLabs    │
│                 │       │                 │       │ • YouTube       │
└─────────────────┘       └─────────────────┘       └─────────────────┘
```

### Deploy Backend to Railway (FREE)

1. **Create Railway Account**: Go to [railway.app](https://railway.app)

2. **New Project** → **Deploy from GitHub**

3. **Select this repo**

4. **Add Environment Variables**:
   ```
   REPLICATE_API_TOKEN=your_key
   ELEVENLABS_API_KEY=your_key
   OPENAI_API_KEY=your_key
   YOUTUBE_API_KEY=your_key
   CORS_ORIGINS=https://your-app.vercel.app
   ```

5. **Deploy!** Railway auto-detects Python and uses `nixpacks.toml`

6. **Get your URL**: `https://your-project.up.railway.app`

### Deploy Frontend to Vercel (FREE)

1. **Create Vercel Account**: Go to [vercel.com](https://vercel.com)

2. **Import GitHub Repo**

3. **Set Root Directory**: `frontend`

4. **Add Environment Variable**:
   ```
   NEXT_PUBLIC_API_URL=https://your-project.up.railway.app
   ```

5. **Deploy!**

### Alternative: Render.com (FREE)

1. Go to [render.com](https://render.com)
2. New → Web Service → Connect GitHub
3. It auto-detects `render.yaml` configuration
4. Add environment variables in dashboard
5. Deploy!

### Free Tier Limits

| Service | Free Tier |
|---------|-----------|
| **Railway** | $5 credit/month (~500 hrs) |
| **Render** | 750 hrs/month |
| **Vercel** | Unlimited for hobby |

This is MORE than enough for a portfolio project!

---

## 🎨 Frontend Dashboard

The frontend provides:
- 📊 **Dashboard** - Stats, recent videos, trending topics
- 🎬 **Video Creator** - Real-time pipeline progress
- ⚙️ **Settings** - Caption styles, audio levels
- 📤 **YouTube Upload** - Direct upload to your channel

See `frontend/README.md` for more details.

---

## 📝 License

MIT License - Use freely for personal and commercial projects.
