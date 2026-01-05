#!/usr/bin/env python3
"""
Test script to verify trend research is working
Run this first to ensure real-time data fetching works
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from loguru import logger


async def test_youtube_trending():
    """Test YouTube Trending API (FREE)"""
    logger.info("=" * 50)
    logger.info("Testing YouTube Trending (India)...")
    logger.info("=" * 50)
    
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        logger.warning("⚠️ YOUTUBE_API_KEY not set in .env")
        logger.info("Get FREE key from: https://console.cloud.google.com/")
        logger.info("1. Create project → 2. Enable YouTube Data API v3 → 3. Create API Key")
        return False
    
    try:
        from googleapiclient.discovery import build
        
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode="IN",
            maxResults=10
        )
        response = request.execute()
        
        if response.get('items'):
            logger.info("✅ YouTube API working!")
            logger.info("YouTube Trending in India:")
            for i, item in enumerate(response['items'][:5], 1):
                title = item['snippet']['title'][:50]
                views = int(item['statistics'].get('viewCount', 0))
                logger.info(f"  {i}. {title}... ({views:,} views)")
            return True
        else:
            logger.warning("⚠️ No trending videos returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ YouTube API failed: {e}")
        return False


async def test_google_trends():
    """Test Google Trends fetching"""
    logger.info("\n" + "=" * 50)
    logger.info("Testing Google Trends (India)...")
    logger.info("=" * 50)
    
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl='hi-IN', tz=330)
        trending = pytrends.trending_searches(pn='india')
        trends_list = trending[0].tolist()[:10]
        
        logger.info("✅ Google Trends working!")
        logger.info("Current trending in India:")
        for i, trend in enumerate(trends_list, 1):
            logger.info(f"  {i}. {trend}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Google Trends failed: {e}")
        return False


async def test_news_feeds():
    """Test News RSS feeds"""
    logger.info("\n" + "=" * 50)
    logger.info("Testing News RSS Feeds...")
    logger.info("=" * 50)
    
    try:
        import feedparser
        
        feeds = [
            ("Times of India", "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"),
            ("NDTV", "https://www.ndtv.com/rss/india"),
        ]
        
        for name, url in feeds:
            feed = feedparser.parse(url)
            if feed.entries:
                logger.info(f"✅ {name}: {feed.entries[0].title[:50]}...")
            else:
                logger.warning(f"⚠️ {name}: No entries")
        
        return True
    except Exception as e:
        logger.error(f"❌ News feeds failed: {e}")
        return False


async def test_web_search():
    """Test DuckDuckGo search"""
    logger.info("\n" + "=" * 50)
    logger.info("Testing DuckDuckGo Search...")
    logger.info("=" * 50)
    
    try:
        from duckduckgo_search import DDGS
        
        with DDGS() as ddgs:
            results = list(ddgs.text("trending India today", region='in-en', max_results=3))
            
        if results:
            logger.info("✅ DuckDuckGo working!")
            for r in results:
                logger.info(f"  - {r['title'][:50]}...")
            return True
        else:
            logger.warning("⚠️ No search results")
            return False
            
    except Exception as e:
        logger.error(f"❌ DuckDuckGo failed: {e}")
        return False


async def test_youtube_analyzer():
    """Test YouTube viral pattern analyzer"""
    logger.info("\n" + "=" * 50)
    logger.info("Testing YouTube Viral Analyzer...")
    logger.info("=" * 50)
    
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        logger.warning("⚠️ YOUTUBE_API_KEY not set. Skipping analyzer test.")
        return False
    
    try:
        from app.services.youtube_analyzer import youtube_analyzer
        
        analysis = await youtube_analyzer.analyze_viral_patterns()
        
        if analysis.get('trending_analysis'):
            logger.info("✅ YouTube Analyzer working!")
            logger.info(f"Videos analyzed: {analysis['trending_analysis'].get('total_videos_analyzed', 0)}")
            logger.info(f"Avg views: {analysis['trending_analysis'].get('avg_views', 0):,}")
            logger.info(f"Avg engagement: {analysis['trending_analysis'].get('avg_engagement_rate', 0)}%")
            
            if analysis.get('winning_title_patterns'):
                logger.info(f"Top power words: {', '.join(analysis['winning_title_patterns'].get('common_power_words', [])[:5])}")
            
            return True
        else:
            logger.warning("⚠️ No analysis data returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ YouTube Analyzer failed: {e}")
        return False


async def test_hook_generator():
    """Test viral hook generator"""
    logger.info("\n" + "=" * 50)
    logger.info("Testing Viral Hook Generator...")
    logger.info("=" * 50)
    
    replicate_key = os.getenv('REPLICATE_API_TOKEN')
    if not replicate_key:
        logger.warning("⚠️ REPLICATE_API_TOKEN not set. Skipping hook test.")
        return False
    
    try:
        from app.services.hook_generator import hook_generator
        
        result = await hook_generator.generate_viral_hook(
            topic="Discovery of Fire",
            era="Stone Age",
            mood="dramatic"
        )
        
        logger.info("✅ Hook Generator working!")
        logger.info(f"Best hook: {result['best_hook']}")
        logger.info(f"Alternative hooks: {len(result.get('alternative_hooks', []))}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Hook Generator failed: {e}")
        return False


async def test_full_trend_research():
    """Test full trend research with LLM"""
    logger.info("\n" + "=" * 50)
    logger.info("Testing Full Trend Research (with LLM)...")
    logger.info("=" * 50)
    
    replicate_key = os.getenv('REPLICATE_API_TOKEN')
    if not replicate_key:
        logger.warning("⚠️ REPLICATE_API_TOKEN not set. Skipping LLM test.")
        return False
    
    try:
        from app.services.trend_researcher import trend_researcher
        
        topic = await trend_researcher.get_trending_topic()
        
        logger.info("✅ Full trend research working!")
        logger.info(f"YouTube Trend: {topic.get('youtube_trend', 'N/A')}")
        logger.info(f"Selected Topic: {topic.get('topic')}")
        logger.info(f"Era: {topic.get('era')}")
        logger.info(f"Mood: {topic.get('mood')}")
        logger.info(f"Connection: {topic.get('connection', 'N/A')}")
        logger.info(f"Hook: {topic.get('hook', 'N/A')}")
        logger.info(f"Why Viral: {topic.get('reason', 'N/A')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Full trend research failed: {e}")
        return False


async def main():
    logger.info("🔍 VIRAL CONTENT RESEARCH TEST SUITE")
    logger.info("=" * 50)
    logger.info("Testing all data sources and viral analyzers")
    logger.info("=" * 50 + "\n")
    
    results = {}
    
    # Test YouTube (most important)
    results['youtube_trending'] = await test_youtube_trending()
    
    # Test other sources
    results['google_trends'] = await test_google_trends()
    results['news_feeds'] = await test_news_feeds()
    results['web_search'] = await test_web_search()
    
    # Test YouTube analyzer (advanced)
    results['youtube_analyzer'] = await test_youtube_analyzer()
    
    # Test hook generator
    results['hook_generator'] = await test_hook_generator()
    
    # Test full system (requires Replicate API)
    results['full_research'] = await test_full_trend_research()
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 50)
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{test}: {status}")
    
    # Check critical APIs
    logger.info("\n" + "-" * 50)
    
    if not results['youtube_trending']:
        logger.warning("⚠️ YouTube API not working!")
        logger.info("   Get FREE key: https://console.cloud.google.com/")
        logger.info("   Add to .env: YOUTUBE_API_KEY=your_key")
    
    if not results['full_research']:
        logger.warning("⚠️ LLM not working!")
        logger.info("   Add to .env: REPLICATE_API_TOKEN=your_key")
    
    # Final status
    critical_passed = sum([
        results.get('youtube_trending', False),
        results.get('google_trends', False),
        results.get('youtube_analyzer', False),
    ])
    
    if critical_passed >= 2:
        logger.info("\n🚀 SYSTEM READY! You can create viral videos now.")
        logger.info("   Run: python create_video.py")
    elif critical_passed >= 1:
        logger.info("\n✅ Basic system working. Some features may be limited.")
    else:
        logger.error("\n❌ Critical systems not working. Check API keys.")
    
    return critical_passed >= 1


if __name__ == "__main__":
    asyncio.run(main())
