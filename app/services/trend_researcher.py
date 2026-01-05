"""
Trend Research Service - POV-FIRST with Strategic Trend Integration
Researches topics through a FIXED STORYTELLING LENS for brand identity,
with optional trend integration for relevance (30% trend-reactive)

POV Engine ensures consistent creator voice and audience training.
"""
import replicate
import asyncio
import random
from datetime import datetime
from typing import List, Dict, Optional
from loguru import logger

# Free trend/search libraries
from pytrends.request import TrendReq
from duckduckgo_search import DDGS
import feedparser

# YouTube Data API
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings
from app.models.video import StoryLens


class TrendResearcherService:
    """
    POV-FIRST Topic Research Service
    
    STRATEGY:
    - 70% POV-driven: Stories from our curated historical pool filtered through current lens
    - 30% trend-reactive: Map current trends to our storytelling POV
    
    This builds BRAND IDENTITY and trains algorithm to find your audience,
    not just chase random viral topics.
    """
    
    # Indian News RSS Feeds (FREE, no API key)
    NEWS_FEEDS = [
        "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
        "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
        "https://indianexpress.com/feed/",
    ]
    
    # YouTube video categories relevant for our content
    YOUTUBE_CATEGORIES = {
        "1": "Film & Animation",
        "2": "Autos & Vehicles",
        "10": "Music",
        "15": "Pets & Animals",
        "17": "Sports",
        "18": "Short Movies",
        "19": "Travel & Events",
        "20": "Gaming",
        "22": "People & Blogs",
        "23": "Comedy",
        "24": "Entertainment",
        "25": "News & Politics",
        "26": "Howto & Style",
        "27": "Education",
        "28": "Science & Technology",
    }
    
    # POV-DRIVEN HISTORICAL TOPIC POOLS
    # Curated stories that fit each lens perfectly
    HISTORICAL_POOL = {
        StoryLens.POWER: [
            {"topic": "The moment Akbar realized his generals feared him more than enemies", "era": "Mughal Empire"},
            {"topic": "When a single betrayal ended the Maratha dream at Panipat", "era": "18th Century"},
            {"topic": "The day Tipu Sultan refused British terms and chose death", "era": "Mysore Kingdom"},
            {"topic": "How Chandragupta Maurya toppled an empire with strategy not armies", "era": "Maurya Empire"},
            {"topic": "The silent coup that made Balban the real power behind the throne", "era": "Delhi Sultanate"},
        ],
        StoryLens.FEAR: [
            {"topic": "The night before Mangal Pandey fired the first shot of 1857", "era": "1857 Revolution"},
            {"topic": "When Bhagat Singh walked into the Assembly knowing there's no escape", "era": "Freedom Struggle"},
            {"topic": "The fisherman who faced Alexander's army and didn't blink", "era": "Ancient India"},
            {"topic": "Rani Lakshmibai's last ride into certain death", "era": "1857 Revolution"},
            {"topic": "The soldier who stayed back alone at Rezang La", "era": "1962 War"},
        ],
        StoryLens.BETRAYAL: [
            {"topic": "Mir Jafar's handshake that sold an empire to the British", "era": "Battle of Plassey"},
            {"topic": "When Prithviraj's own men opened the gates to invaders", "era": "Medieval India"},
            {"topic": "The night Siraj ud-Daulah was betrayed by everyone he trusted", "era": "Bengal Nawabs"},
            {"topic": "How one jealous general destroyed Vijayanagara forever", "era": "Vijayanagara Empire"},
            {"topic": "The prince who killed his father for a throne that crumbled", "era": "Mughal Empire"},
        ],
        StoryLens.TURNING_POINT: [
            {"topic": "The single arrow that changed who ruled India for 700 years", "era": "Tarain Battles"},
            {"topic": "5 minutes of hesitation that cost India the 1962 war", "era": "India-China War"},
            {"topic": "The letter Subhas Chandra Bose chose to ignore", "era": "Freedom Struggle"},
            {"topic": "When Ashoka saw the bodies at Kalinga and became someone else", "era": "Maurya Empire"},
            {"topic": "The moment Gandhi decided salt would break the British", "era": "Freedom Struggle"},
        ],
        StoryLens.UNDERRATED: [
            {"topic": "The woman who led an army before Lakshmibai and history forgot her", "era": "Medieval India"},
            {"topic": "The spy network that actually won us 1971, not soldiers", "era": "Bangladesh Liberation"},
            {"topic": "India's first freedom fighter was not Mangal Pandey", "era": "Colonial India"},
            {"topic": "The scientist India ignored who could have made us a superpower", "era": "Modern India"},
            {"topic": "The tribal king who defeated the British three times and got erased", "era": "Colonial Era"},
        ],
    }
    
    # Current channel lens (can be rotated weekly/monthly for variety)
    # This is the KEY to building recognizable POV
    CURRENT_LENS = StoryLens.TURNING_POINT
    
    # POV vs Trend ratio (70% POV, 30% trend for relevance)
    POV_RATIO = 0.7
    
    def __init__(self):
        self.llm_model = settings.SCRIPT_MODEL
        self.reasoning_effort = settings.LLM_REASONING_EFFORT
        self.verbosity = settings.LLM_VERBOSITY
        self.youtube_api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
        self.youtube_client = None
        self.current_lens = self.CURRENT_LENS
    
    def _get_youtube_client(self):
        """Get or create YouTube API client"""
        if self.youtube_client is None and self.youtube_api_key:
            self.youtube_client = build('youtube', 'v3', developerKey=self.youtube_api_key)
        return self.youtube_client
    
    async def get_trending_topic(self, lens: Optional[StoryLens] = None) -> Dict:
        """
        POV-FIRST Topic Selection
        
        Strategy:
        - 70% of time: Pick from curated historical pool (POV-driven)
        - 30% of time: Map current trends to our storytelling lens (trend-reactive)
        
        This builds BRAND IDENTITY - algorithm learns WHO likes your POV, not just topics.
        """
        current_lens = lens or self.current_lens
        logger.info(f"🎯 POV-FIRST Topic Selection (Lens: {current_lens.value})")
        
        # POV vs Trend decision
        if random.random() < self.POV_RATIO:
            # 70% - POV-DRIVEN from curated pool
            logger.info("📚 Mode: POV-DRIVEN (from curated historical pool)")
            topic = await self._get_pov_driven_topic(current_lens)
        else:
            # 30% - TREND-REACTIVE but mapped to our lens
            logger.info("📈 Mode: TREND-REACTIVE (mapped to our POV)")
            trends_data = await self._gather_all_trends()
            topic = await self._map_trend_to_lens(trends_data, current_lens)
        
        # Add lens to topic data
        topic['story_lens'] = current_lens.value
        
        return topic
    
    async def _get_pov_driven_topic(self, lens: StoryLens) -> Dict:
        """
        Pick a topic from our curated pool that fits the current lens.
        This ensures CONSISTENT storytelling POV.
        """
        pool = self.HISTORICAL_POOL.get(lens, self.HISTORICAL_POOL[StoryLens.TURNING_POINT])
        
        # Random selection from pool
        selected = random.choice(pool)
        
        logger.info(f"📖 Selected from {lens.value} pool: {selected['topic'][:50]}...")
        
        # Generate hook using LLM
        hook = await self._generate_pov_hook(selected['topic'], selected['era'], lens)
        
        return {
            "topic": selected['topic'],
            "era": selected['era'],
            "hook": hook,
            "mood": self._lens_to_mood(lens),
            "reason": f"POV-driven: {lens.value} storytelling",
            "source": "curated_pool"
        }
    
    def _lens_to_mood(self, lens: StoryLens) -> str:
        """Map story lens to music mood"""
        lens_mood_map = {
            StoryLens.POWER: "dramatic",
            StoryLens.FEAR: "suspense",
            StoryLens.BETRAYAL: "emotional",
            StoryLens.TURNING_POINT: "dramatic",
            StoryLens.UNDERRATED: "inspiring",
        }
        return lens_mood_map.get(lens, "dramatic")
    
    async def _generate_pov_hook(self, topic: str, era: str, lens: StoryLens) -> str:
        """Generate a hook that fits the POV lens"""
        
        lens_hook_styles = {
            StoryLens.POWER: "Focus on the moment of power shift, who controlled whom",
            StoryLens.FEAR: "Focus on the fear before the brave act, the human hesitation",
            StoryLens.BETRAYAL: "Focus on trust being broken, the knife in the back",
            StoryLens.TURNING_POINT: "Focus on THE ONE DECISION that changed everything",
            StoryLens.UNDERRATED: "Focus on why this was hidden, who benefited from forgetting",
        }
        
        prompt = f"""You are a master Hindi storyteller for Instagram Reels.
Generate ONE powerful hook for this topic through the {lens.value} lens.

TOPIC: {topic}
ERA: {era}
LENS STYLE: {lens_hook_styles[lens]}

HOOK RULES:
- Write in HINDI DEVANAGARI (हिंदी में)
- Maximum 12-15 words
- NO "99% don't know" - that's spam
- Create CONTRADICTION or TENSION
- Make viewer FEEL, not just curious

GOOD EXAMPLES for this lens:
- "इस पल में, सबसे ताकतवर... सबसे कमज़ोर था"
- "जीत सामने थी... फिर एक फैसले ने सब बदल दिया"
- "जिसपर भरोसा था, वही सबसे बड़ा दुश्मन निकला"

Generate ONE hook (just the hook, nothing else):"""

        try:
            output = replicate.run(
                self.llm_model,
                input={
                    "prompt": prompt,
                    "messages": [],
                    "verbosity": self.verbosity,
                    "reasoning_effort": "low",
                }
            )
            response = output if isinstance(output, str) else "".join(output)
            return response.strip().strip('"')
        except Exception as e:
            logger.error(f"Hook generation failed: {e}")
            return f"ये कहानी आपकी सोच बदल देगी..."
    
    async def _map_trend_to_lens(self, trends_data: Dict, lens: StoryLens) -> Dict:
        """
        Take current trends and find a historical angle that fits our lens.
        This keeps us relevant while maintaining POV consistency.
        """
        # Use existing LLM analysis but with lens constraint
        topic = await self._analyze_trends_with_llm(trends_data, lens)
        topic['source'] = "trend_mapped"
        return topic
    
    async def _gather_all_trends(self) -> Dict:
        """Gather trends from multiple sources including YouTube"""
        
        results = {
            "youtube_trending": [],
            "google_trends": [],
            "news_headlines": [],
            "web_search": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Run all searches concurrently
        try:
            # YouTube Trending (PRIORITY - Most important!)
            youtube_trends = await asyncio.to_thread(self._get_youtube_trending_india)
            results["youtube_trending"] = youtube_trends
            logger.info(f"Found {len(youtube_trends)} YouTube trending videos")
        except Exception as e:
            logger.warning(f"YouTube Trending fetch failed: {e}")
        
        try:
            # Google Trends
            google_trends = await asyncio.to_thread(self._get_google_trends_india)
            results["google_trends"] = google_trends
            logger.info(f"Found {len(google_trends)} Google Trends")
        except Exception as e:
            logger.warning(f"Google Trends fetch failed: {e}")
        
        try:
            # News Headlines
            news = await asyncio.to_thread(self._get_news_headlines)
            results["news_headlines"] = news
            logger.info(f"Found {len(news)} news headlines")
        except Exception as e:
            logger.warning(f"News fetch failed: {e}")
        
        try:
            # Web search for viral content
            web_results = await asyncio.to_thread(self._search_viral_content)
            results["web_search"] = web_results
            logger.info(f"Found {len(web_results)} viral content items")
        except Exception as e:
            logger.warning(f"Web search failed: {e}")
        
        return results
    
    def _get_youtube_trending_india(self) -> List[Dict]:
        """
        Get YouTube Trending videos in India
        Uses YouTube Data API v3 (FREE - 10,000 quota/day)
        """
        youtube = self._get_youtube_client()
        
        if not youtube:
            logger.warning("YouTube API key not configured. Skipping YouTube trends.")
            return []
        
        try:
            # Get most popular videos in India
            request = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode="IN",  # India
                maxResults=25
            )
            response = request.execute()
            
            trending_videos = []
            for item in response.get('items', []):
                snippet = item.get('snippet', {})
                stats = item.get('statistics', {})
                
                trending_videos.append({
                    'title': snippet.get('title', ''),
                    'channel': snippet.get('channelTitle', ''),
                    'category_id': snippet.get('categoryId', ''),
                    'category': self.YOUTUBE_CATEGORIES.get(snippet.get('categoryId', ''), 'Unknown'),
                    'description': snippet.get('description', '')[:200],
                    'view_count': int(stats.get('viewCount', 0)),
                    'tags': snippet.get('tags', [])[:5],
                    'published_at': snippet.get('publishedAt', '')
                })
            
            # Sort by view count
            trending_videos.sort(key=lambda x: x['view_count'], reverse=True)
            
            logger.debug(f"YouTube Trending: {[v['title'][:30] for v in trending_videos[:5]]}")
            return trending_videos
            
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            return []
        except Exception as e:
            logger.error(f"YouTube fetch error: {e}")
            return []
    
    def _get_youtube_trending_by_category(self, category_id: str = "24") -> List[Dict]:
        """Get trending videos in a specific category (default: Entertainment)"""
        youtube = self._get_youtube_client()
        
        if not youtube:
            return []
        
        try:
            request = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode="IN",
                videoCategoryId=category_id,
                maxResults=10
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                snippet = item.get('snippet', {})
                videos.append({
                    'title': snippet.get('title', ''),
                    'channel': snippet.get('channelTitle', ''),
                    'tags': snippet.get('tags', [])[:5]
                })
            
            return videos
            
        except Exception as e:
            logger.error(f"YouTube category fetch error: {e}")
            return []
    
    def _get_google_trends_india(self) -> List[str]:
        """Get real-time trending searches in India from Google Trends"""
        try:
            pytrends = TrendReq(hl='hi-IN', tz=330)  # Hindi, India timezone
            
            # Get trending searches in India
            trending = pytrends.trending_searches(pn='india')
            trends_list = trending[0].tolist()[:20]  # Top 20 trends
            
            logger.debug(f"Google Trends India: {trends_list[:5]}...")
            return trends_list
            
        except Exception as e:
            logger.error(f"Google Trends error: {e}")
            return []
    
    def _get_news_headlines(self) -> List[Dict]:
        """Get current news headlines from Indian sources"""
        headlines = []
        
        for feed_url in self.NEWS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:  # Top 5 from each source
                    headlines.append({
                        "title": entry.get("title", ""),
                        "summary": entry.get("summary", "")[:200] if entry.get("summary") else "",
                        "source": feed.feed.get("title", "Unknown")
                    })
            except Exception as e:
                logger.warning(f"Failed to parse {feed_url}: {e}")
                continue
        
        return headlines[:15]
    
    def _search_viral_content(self) -> List[Dict]:
        """Search for viral/trending content in India"""
        results = []
        
        search_queries = [
            "trending India today viral",
            "breaking news India",
        ]
        
        try:
            with DDGS() as ddgs:
                for query in search_queries:
                    search_results = list(ddgs.text(query, region='in-en', max_results=5))
                    for r in search_results:
                        results.append({
                            "title": r.get("title", ""),
                            "body": r.get("body", "")[:200],
                            "query": query
                        })
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
        
        return results[:10]
    
    async def _analyze_trends_with_llm(self, trends_data: Dict, lens: Optional[StoryLens] = None) -> Dict:
        """Use LLM to analyze trends and pick the best historical topic through our POV lens"""
        
        # Format YouTube trending (PRIORITY)
        youtube_section = ""
        if trends_data.get("youtube_trending"):
            yt_videos = trends_data["youtube_trending"][:10]
            youtube_section = "\n".join([
                f"- {v['title']} ({v['channel']}) - {v['view_count']:,} views - Tags: {', '.join(v.get('tags', [])[:3])}"
                for v in yt_videos
            ])
        
        # Add lens constraint to prompt
        lens_instruction = ""
        if lens:
            lens_descriptions = {
                StoryLens.POWER: "Focus on power dynamics, control, dominance - who held power and lost it",
                StoryLens.FEAR: "Focus on moments of fear becoming courage - the human hesitation before bravery",
                StoryLens.BETRAYAL: "Focus on betrayal and consequences - trust broken, loyalty tested",
                StoryLens.TURNING_POINT: "Focus on THE ONE DECISION that changed everything - irreversible choices",
                StoryLens.UNDERRATED: "Focus on forgotten heroes, ignored events, hidden truth",
            }
            lens_instruction = f"""
⚠️ CRITICAL - STORYTELLING LENS:
Your story MUST be told through this POV: {lens.value.upper()}
{lens_descriptions[lens]}

This is our BRAND IDENTITY. Every story must fit this lens, not just be historically interesting."""
        
        prompt = f"""You are a viral content strategist for Indian Instagram Reels focused on HISTORICAL content.

CURRENT DATE: {datetime.now().strftime('%B %d, %Y')}
{lens_instruction}

=== 🎬 YOUTUBE TRENDING IN INDIA (MOST IMPORTANT!) ===
{youtube_section or 'No data available'}

=== 📈 GOOGLE TRENDS (What Indians are searching) ===
{chr(10).join(f'- {t}' for t in trends_data.get('google_trends', [])[:10]) or 'No data available'}

=== 📰 NEWS HEADLINES ===
{chr(10).join(f'- {h["title"]}' for h in trends_data.get('news_headlines', [])[:8]) or 'No data available'}

=== 🔥 VIRAL CONTENT ===
{chr(10).join(f'- {w["title"]}' for w in trends_data.get('web_search', [])[:5]) or 'No data available'}

YOUR TASK:
Based on these LIVE trends, find a HISTORICAL angle that:
1. Connects to what's trending
2. Fits our storytelling POV/lens perfectly

STRATEGY:
- If a movie/show is trending → Find the real history behind it through our lens
- If a person is trending → Their story filtered through our POV
- If a festival/event → Its origins told through our lens
- Map EVERY trend to our consistent storytelling perspective

RESPOND IN THIS EXACT FORMAT:
YOUTUBE_TREND: [Which YouTube video/topic inspired this]
HISTORICAL_TOPIC: [Your chosen historical topic - MUST fit our lens]
ERA: [Historical era]
CONNECTION: [How it connects to the YouTube trend - one line]
HOOK: [Hindi hook in Devanagari - NO "99% don't know" spam hooks]
MOOD: [dramatic/suspense/inspiring/emotional/adventure]
WHY_VIRAL: [Why this will work right now based on YouTube trends]

IMPORTANT: The hook must create TENSION or CONTRADICTION, not just curiosity bait.
Good: "जीत सामने थी... फिर एक फैसले ने सब बदल दिया"
Bad: "99% लोग नहीं जानते ये कहानी"

Be creative! Find unexpected historical connections through our lens!"""

        try:
            output = replicate.run(
                self.llm_model,
                input={
                    "prompt": prompt,
                    "messages": [],
                    "verbosity": self.verbosity,
                    "reasoning_effort": self.reasoning_effort,
                }
            )
            
            # GPT-5.2 returns string directly, not iterator
            response = output if isinstance(output, str) else "".join(output)
            logger.debug(f"GPT-5.2 Response: {response[:300]}...")
            
            return self._parse_llm_response(response)
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return self._get_fallback_topic(trends_data)
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Parse LLM response into structured topic"""
        
        result = {
            "youtube_trend": "",
            "trending_context": "",
            "topic": "",
            "era": "",
            "connection": "",
            "hook": "",
            "mood": "dramatic",
            "reason": ""
        }
        
        for line in response.strip().split('\n'):
            line = line.strip()
            if line.startswith('YOUTUBE_TREND:'):
                result["youtube_trend"] = line.replace('YOUTUBE_TREND:', '').strip()
                result["trending_context"] = result["youtube_trend"]
            elif line.startswith('HISTORICAL_TOPIC:'):
                result["topic"] = line.replace('HISTORICAL_TOPIC:', '').strip()
            elif line.startswith('ERA:'):
                result["era"] = line.replace('ERA:', '').strip()
            elif line.startswith('CONNECTION:'):
                result["connection"] = line.replace('CONNECTION:', '').strip()
            elif line.startswith('HOOK:'):
                result["hook"] = line.replace('HOOK:', '').strip()
            elif line.startswith('MOOD:'):
                mood = line.replace('MOOD:', '').strip().lower()
                if mood in ['dramatic', 'suspense', 'inspiring', 'emotional', 'adventure']:
                    result["mood"] = mood
            elif line.startswith('WHY_VIRAL:'):
                result["reason"] = line.replace('WHY_VIRAL:', '').strip()
        
        # Validate we got a topic
        if not result["topic"]:
            result["topic"] = "Historical Mystery of India"
            result["era"] = "Ancient India"
        
        return result
    
    def _get_fallback_topic(self, trends_data: Dict) -> Dict:
        """Generate fallback topic if LLM fails"""
        
        # Try to use first YouTube trend
        if trends_data.get("youtube_trending"):
            yt = trends_data["youtube_trending"][0]
            return {
                "youtube_trend": yt['title'],
                "trending_context": yt['title'],
                "topic": f"History connected to {yt['title'][:30]}",
                "era": "Indian History",
                "mood": "dramatic",
                "hook": f"Yeh kahani aapne kabhi nahi suni hogi...",
                "reason": f"Based on YouTube trending: {yt['title'][:30]}"
            }
        
        # Try Google trend
        if trends_data.get("google_trends"):
            trend = trends_data["google_trends"][0]
            return {
                "trending_context": trend,
                "topic": f"History connected to {trend}",
                "era": "Indian History",
                "mood": "dramatic",
                "hook": f"Kya aapko pata hai {trend} ki asli kahani?",
                "reason": "Based on current Google Trend"
            }
        
        # Ultimate fallback
        return {
            "topic": "Unknown Stories of Indian Freedom Struggle",
            "era": "Freedom Struggle",
            "mood": "inspiring",
            "hook": "Yeh kahani aapne kabhi nahi suni hogi...",
            "reason": "Evergreen topic"
        }
    
    async def get_raw_trends(self) -> Dict:
        """Get raw trends data without LLM analysis (for debugging)"""
        return await self._gather_all_trends()
    
    async def get_youtube_trending_only(self) -> List[Dict]:
        """Get only YouTube trending videos (for debugging)"""
        return await asyncio.to_thread(self._get_youtube_trending_india)
    
    async def get_multiple_topics(self, count: int = 5) -> List[Dict]:
        """Get multiple topic suggestions based on current trends"""
        
        trends_data = await self._gather_all_trends()
        topics = []
        
        # Format YouTube trending
        youtube_section = ""
        if trends_data.get("youtube_trending"):
            yt_videos = trends_data["youtube_trending"][:15]
            youtube_section = "\n".join([
                f"- {v['title']} ({v['channel']})"
                for v in yt_videos
            ])
        
        prompt = f"""Based on these YouTube trending videos in India:
{youtube_section}

And these Google trends:
{chr(10).join(f'- {t}' for t in trends_data.get('google_trends', [])[:10])}

Suggest {count} different HISTORICAL video topics that connect to these trends.
For each, provide:
TOPIC: [Historical topic]
ERA: [Era]
TREND: [Which YouTube video/trend it connects to]
MOOD: [dramatic/suspense/inspiring/emotional/adventure]

Separate each topic with ---"""

        try:
            output = replicate.run(
                self.llm_model,
                input={
                    "prompt": prompt,
                    "messages": [],
                    "verbosity": self.verbosity,
                    "reasoning_effort": self.reasoning_effort,
                }
            )
            
            # GPT-5.2 returns string directly, not iterator
            response = output if isinstance(output, str) else "".join(output)
            
            # Parse multiple topics
            topic_blocks = response.split('---')
            for block in topic_blocks:
                topic_data = {}
                for line in block.strip().split('\n'):
                    if line.startswith('TOPIC:'):
                        topic_data['topic'] = line.replace('TOPIC:', '').strip()
                    elif line.startswith('ERA:'):
                        topic_data['era'] = line.replace('ERA:', '').strip()
                    elif line.startswith('TREND:'):
                        topic_data['trend_connection'] = line.replace('TREND:', '').strip()
                    elif line.startswith('MOOD:'):
                        topic_data['mood'] = line.replace('MOOD:', '').strip().lower()
                
                if topic_data.get('topic'):
                    topics.append(topic_data)
            
        except Exception as e:
            logger.error(f"Multiple topics generation failed: {e}")
        
        return topics[:count]
    
    # ============================================
    # POV ENGINE MANAGEMENT
    # ============================================
    
    def set_story_lens(self, lens: StoryLens):
        """
        Set the current storytelling lens for the channel.
        Recommended: Change weekly/monthly for variety while maintaining identity.
        """
        self.current_lens = lens
        logger.info(f"🎯 Story lens updated to: {lens.value}")
    
    def get_current_lens(self) -> StoryLens:
        """Get the current storytelling lens"""
        return self.current_lens
    
    def get_all_lenses(self) -> List[Dict]:
        """Get all available story lenses with descriptions"""
        descriptions = {
            StoryLens.POWER: "Stories about power dynamics, control, dominance",
            StoryLens.FEAR: "Stories of overcoming fear, bravery moments", 
            StoryLens.BETRAYAL: "Stories of treachery and its aftermath",
            StoryLens.TURNING_POINT: "One irreversible choice that changed everything",
            StoryLens.UNDERRATED: "Hidden gems, overlooked heroes, forgotten events",
        }
        return [
            {"lens": lens.value, "description": descriptions[lens]}
            for lens in StoryLens
        ]
    
    def add_to_historical_pool(self, lens: StoryLens, topic: str, era: str):
        """Add a new topic to the historical pool for a lens"""
        if lens in self.HISTORICAL_POOL:
            self.HISTORICAL_POOL[lens].append({"topic": topic, "era": era})
            logger.info(f"Added to {lens.value} pool: {topic[:50]}...")
    
    def set_pov_ratio(self, ratio: float):
        """
        Set the POV vs Trend ratio.
        Recommended: 0.7 (70% POV, 30% trend) for brand building
        """
        if 0 <= ratio <= 1:
            self.POV_RATIO = ratio
            logger.info(f"POV ratio updated to: {ratio*100:.0f}% POV, {(1-ratio)*100:.0f}% trend")


# Singleton instance
trend_researcher = TrendResearcherService()
