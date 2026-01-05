"""
YouTube Analyzer Service - VIRAL CONTENT INTELLIGENCE
Analyzes trending videos to learn what makes content go viral
Studies hooks, titles, patterns, and engagement metrics
"""
import re
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import Counter
from loguru import logger

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings


class YouTubeAnalyzerService:
    """
    Deep analysis of YouTube trending content to create viral shorts
    - Analyzes hooks from top videos
    - Studies title patterns
    - Extracts winning keywords/tags
    - Mines comments for content ideas
    """
    
    # Categories relevant for historical/educational content
    RELEVANT_CATEGORIES = {
        "24": "Entertainment",
        "25": "News & Politics", 
        "27": "Education",
        "22": "People & Blogs",
    }
    
    # Hook patterns that work (will be updated dynamically)
    VIRAL_HOOK_PATTERNS = [
        "Kya aapko pata hai...",
        "Yeh kahani aapne kabhi nahi suni...",
        "99% log yeh nahi jaante...",
        "Shocking truth about...",
        "Dekho kya hua jab...",
        "Yeh secret aaj tak chupa tha...",
        "Maine discover kiya...",
        "Ek minute mein samjho...",
    ]
    
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.youtube = None
        self._cache = {}
    
    def _get_client(self):
        """Get or create YouTube API client"""
        if self.youtube is None and self.api_key:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        return self.youtube
    
    async def analyze_viral_patterns(self) -> Dict:
        """
        Comprehensive analysis of what's working on YouTube India
        Returns insights for creating viral content
        """
        logger.info("🔍 Analyzing viral patterns on YouTube India...")
        
        results = {
            "trending_analysis": {},
            "top_hooks": [],
            "winning_title_patterns": [],
            "high_engagement_keywords": [],
            "content_gaps": [],
            "recommended_strategy": {}
        }
        
        # Get trending videos
        trending = await asyncio.to_thread(self._get_trending_with_details)
        
        if not trending:
            logger.warning("Could not fetch trending videos")
            return results
        
        # Analyze various aspects
        results["trending_analysis"] = self._analyze_trending_stats(trending)
        results["top_hooks"] = self._extract_hook_patterns(trending)
        results["winning_title_patterns"] = self._analyze_title_patterns(trending)
        results["high_engagement_keywords"] = self._extract_winning_keywords(trending)
        results["recommended_strategy"] = self._generate_strategy(trending)
        
        return results
    
    def _get_trending_with_details(self) -> List[Dict]:
        """Get trending videos with full details"""
        youtube = self._get_client()
        if not youtube:
            return []
        
        try:
            # Get trending videos
            request = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                chart="mostPopular",
                regionCode="IN",
                maxResults=50
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                snippet = item.get('snippet', {})
                stats = item.get('statistics', {})
                content = item.get('contentDetails', {})
                
                # Calculate engagement rate
                views = int(stats.get('viewCount', 0))
                likes = int(stats.get('likeCount', 0))
                comments = int(stats.get('commentCount', 0))
                
                engagement_rate = 0
                if views > 0:
                    engagement_rate = ((likes + comments) / views) * 100
                
                videos.append({
                    'id': item['id'],
                    'title': snippet.get('title', ''),
                    'channel': snippet.get('channelTitle', ''),
                    'description': snippet.get('description', ''),
                    'tags': snippet.get('tags', []),
                    'category_id': snippet.get('categoryId', ''),
                    'published_at': snippet.get('publishedAt', ''),
                    'duration': content.get('duration', ''),
                    'views': views,
                    'likes': likes,
                    'comments': comments,
                    'engagement_rate': round(engagement_rate, 2),
                    'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', '')
                })
            
            return videos
            
        except Exception as e:
            logger.error(f"Error fetching trending: {e}")
            return []
    
    def _analyze_trending_stats(self, videos: List[Dict]) -> Dict:
        """Analyze statistics of trending videos"""
        if not videos:
            return {}
        
        views = [v['views'] for v in videos]
        engagement = [v['engagement_rate'] for v in videos]
        
        return {
            "total_videos_analyzed": len(videos),
            "avg_views": sum(views) // len(views),
            "max_views": max(views),
            "min_views": min(views),
            "avg_engagement_rate": round(sum(engagement) / len(engagement), 2),
            "top_categories": self._get_top_categories(videos),
            "best_performing": {
                "by_views": videos[0]['title'] if videos else "",
                "by_engagement": max(videos, key=lambda x: x['engagement_rate'])['title'] if videos else ""
            }
        }
    
    def _get_top_categories(self, videos: List[Dict]) -> List[Dict]:
        """Get most common categories in trending"""
        categories = Counter([v['category_id'] for v in videos])
        return [
            {
                "category_id": cat_id,
                "category_name": self.RELEVANT_CATEGORIES.get(cat_id, f"Category {cat_id}"),
                "count": count
            }
            for cat_id, count in categories.most_common(5)
        ]
    
    def _extract_hook_patterns(self, videos: List[Dict]) -> List[Dict]:
        """Extract hook patterns from video titles and descriptions"""
        hooks = []
        
        # Common Hindi hook starters
        hook_indicators = [
            "kya", "kaise", "kyun", "shocking", "secret", "truth",
            "real", "mystery", "unknown", "hidden", "story", "kahani",
            "pata", "jaano", "dekho", "suno", "wow", "omg"
        ]
        
        for video in videos[:20]:  # Top 20 videos
            title = video['title'].lower()
            
            # Check for hook patterns
            for indicator in hook_indicators:
                if indicator in title:
                    hooks.append({
                        "title": video['title'],
                        "hook_type": indicator,
                        "views": video['views'],
                        "engagement": video['engagement_rate']
                    })
                    break
        
        # Sort by engagement
        hooks.sort(key=lambda x: x['engagement'], reverse=True)
        
        return hooks[:10]
    
    def _analyze_title_patterns(self, videos: List[Dict]) -> List[Dict]:
        """Analyze patterns in viral video titles"""
        patterns = []
        
        # Title length analysis
        title_lengths = [len(v['title']) for v in videos]
        avg_length = sum(title_lengths) // len(title_lengths)
        
        # Common words in titles
        all_words = []
        for v in videos:
            words = re.findall(r'\b\w+\b', v['title'].lower())
            all_words.extend(words)
        
        common_words = Counter(all_words).most_common(20)
        
        # Emoji usage
        emoji_count = sum(1 for v in videos if any(ord(c) > 127 for c in v['title']))
        
        # Number usage (listicles)
        number_count = sum(1 for v in videos if any(c.isdigit() for c in v['title']))
        
        return {
            "optimal_title_length": avg_length,
            "common_power_words": [w[0] for w in common_words if len(w[0]) > 3][:10],
            "emoji_usage_percent": round((emoji_count / len(videos)) * 100),
            "number_usage_percent": round((number_count / len(videos)) * 100),
            "top_titles": [
                {"title": v['title'], "views": v['views']}
                for v in sorted(videos, key=lambda x: x['views'], reverse=True)[:5]
            ]
        }
    
    def _extract_winning_keywords(self, videos: List[Dict]) -> List[str]:
        """Extract high-performing keywords from tags"""
        all_tags = []
        
        for video in videos:
            # Weight tags by video performance
            weight = 1
            if video['views'] > 1000000:
                weight = 3
            elif video['views'] > 500000:
                weight = 2
            
            for tag in video.get('tags', []):
                all_tags.extend([tag.lower()] * weight)
        
        # Get most common weighted tags
        tag_counts = Counter(all_tags)
        return [tag for tag, count in tag_counts.most_common(20)]
    
    def _generate_strategy(self, videos: List[Dict]) -> Dict:
        """Generate content strategy based on analysis"""
        
        # Find content gaps (categories with high views but less competition)
        category_performance = {}
        for v in videos:
            cat = v['category_id']
            if cat not in category_performance:
                category_performance[cat] = {'total_views': 0, 'count': 0}
            category_performance[cat]['total_views'] += v['views']
            category_performance[cat]['count'] += 1
        
        # Best time insights (from publish dates)
        recent_viral = [v for v in videos if v['views'] > 500000]
        
        return {
            "recommended_content_type": "Historical/Educational with trending angle",
            "optimal_video_length": "30-60 seconds for Shorts",
            "hook_strategy": "Start with curiosity gap or shocking fact",
            "title_tips": [
                "Keep under 60 characters",
                "Use numbers when possible",
                "Include Hindi keywords",
                "Create curiosity gap"
            ],
            "best_tags_to_use": self._extract_winning_keywords(videos)[:10],
            "engagement_tips": [
                "Ask question in first 3 seconds",
                "Use pattern interrupt",
                "Promise value delivery",
                "Create FOMO"
            ]
        }
    
    async def get_viral_hooks_for_topic(self, topic: str, era: str) -> List[str]:
        """
        Generate viral hooks specifically for a topic
        Uses analysis of what works + topic context
        """
        logger.info(f"Generating viral hooks for: {topic}")
        
        # Get current viral patterns
        analysis = await self.analyze_viral_patterns()
        
        # Hook templates that work for historical content
        hook_templates = [
            f"99% Indians don't know this about {topic}... 😱",
            f"Yeh {era} ki kahani aapne kabhi nahi suni hogi...",
            f"Dekho kya hua tha jab {topic}... 🔥",
            f"School mein yeh nahi padhaya gaya - {topic} ki asli kahani",
            f"Warning: Yeh video dekhne ke baad history change ho jayegi",
            f"Maine {topic} ke baare mein yeh discover kiya aur shocked reh gaya",
            f"Ek minute mein samjho {topic} - yeh secret tha",
            f"Historians hide this about {topic}... but I found out",
            f"POV: You time travel to {era} and witness {topic}",
            f"What they don't tell you about {topic}... 💀",
        ]
        
        return hook_templates
    
    async def search_similar_viral_content(self, topic: str, max_results: int = 10) -> List[Dict]:
        """Search for viral videos similar to our topic"""
        youtube = self._get_client()
        if not youtube:
            return []
        
        try:
            # Search for topic-related videos
            request = youtube.search().list(
                part="snippet",
                q=f"{topic} history India Hindi",
                type="video",
                regionCode="IN",
                relevanceLanguage="hi",
                maxResults=max_results,
                order="viewCount"  # Sort by views
            )
            response = request.execute()
            
            video_ids = [item['id']['videoId'] for item in response.get('items', [])]
            
            if not video_ids:
                return []
            
            # Get video statistics
            stats_request = youtube.videos().list(
                part="statistics,snippet",
                id=','.join(video_ids)
            )
            stats_response = stats_request.execute()
            
            results = []
            for item in stats_response.get('items', []):
                snippet = item.get('snippet', {})
                stats = item.get('statistics', {})
                
                results.append({
                    'title': snippet.get('title', ''),
                    'channel': snippet.get('channelTitle', ''),
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'description': snippet.get('description', '')[:200],
                    'tags': snippet.get('tags', [])[:5]
                })
            
            return sorted(results, key=lambda x: x['views'], reverse=True)
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def get_comment_insights(self, video_id: str, max_comments: int = 50) -> Dict:
        """
        Mine comments to find what audience wants
        Useful for finding content ideas
        """
        youtube = self._get_client()
        if not youtube:
            return {}
        
        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_comments,
                order="relevance"
            )
            response = request.execute()
            
            comments = []
            questions = []
            requests = []
            
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)
                
                # Identify questions (content ideas)
                if '?' in comment:
                    questions.append(comment)
                
                # Identify requests
                request_words = ['please', 'make', 'video', 'banaao', 'banao', 'next']
                if any(word in comment.lower() for word in request_words):
                    requests.append(comment)
            
            return {
                "total_comments": len(comments),
                "questions_asked": questions[:10],
                "content_requests": requests[:10],
                "sentiment": "positive" if len(comments) > 0 else "unknown"
            }
            
        except Exception as e:
            logger.error(f"Comment fetch error: {e}")
            return {}
    
    async def get_competitor_analysis(self, channel_keywords: List[str]) -> List[Dict]:
        """Analyze competitor channels for insights"""
        youtube = self._get_client()
        if not youtube:
            return []
        
        results = []
        
        for keyword in channel_keywords[:3]:  # Limit API calls
            try:
                # Search for channels
                request = youtube.search().list(
                    part="snippet",
                    q=f"{keyword} history Hindi",
                    type="channel",
                    regionCode="IN",
                    maxResults=3
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    results.append({
                        'channel_name': item['snippet']['title'],
                        'description': item['snippet']['description'][:200],
                        'keyword': keyword
                    })
                    
            except Exception as e:
                logger.warning(f"Competitor search error: {e}")
        
        return results


# Singleton instance
youtube_analyzer = YouTubeAnalyzerService()

