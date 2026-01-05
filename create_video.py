#!/usr/bin/env python3
"""
🎬 POV-FIRST CREATOR PIPELINE - CLI
Fully automated video creation with consistent storytelling POV

Usage:
  python create_video.py          # Auto-create one video (POV-first)
  python create_video.py batch    # Create multiple videos
  python create_video.py topics   # Show trending topics
  python create_video.py health   # Show creator brand health
  python create_video.py lens     # Show/set story lens
"""
import asyncio
import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from loguru import logger


async def create_auto(lens_name: str = None):
    """Create video with POV-first auto-selected topic"""
    from app.services.pipeline import pipeline
    from app.models.video import StoryLens
    
    logger.info("🎬 POV-FIRST CREATOR PIPELINE")
    logger.info("=" * 60)
    logger.info("Mode: AUTO (POV-first topic selection)")
    
    # Parse lens if provided
    lens = None
    if lens_name:
        try:
            lens = StoryLens(lens_name)
            logger.info(f"🎯 Story Lens: {lens.value}")
        except ValueError:
            logger.warning(f"Invalid lens '{lens_name}', using default")
    
    logger.info("=" * 60)
    
    project = await pipeline.create_video_auto(lens=lens)
    
    return project.final_video_path


async def create_batch(count: int, delay: int):
    """Create multiple videos"""
    from app.services.pipeline import pipeline
    
    logger.info("🎬 BATCH VIDEO CREATION")
    logger.info(f"Creating {count} videos...")
    
    results = await pipeline.batch_create_videos(count=count, delay_between=delay)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 BATCH SUMMARY")
    logger.info("=" * 60)
    
    for r in results:
        if r['success']:
            logger.info(f"✅ Video {r['video_number']}: {r['topic']}")
        else:
            logger.error(f"❌ Video {r['video_number']}: Failed")
    
    return results


async def show_topics():
    """Show current trending topics with POV lens"""
    from app.services.trend_researcher import trend_researcher
    from app.services.youtube_analyzer import youtube_analyzer
    
    logger.info("📊 POV-FIRST TOPIC RESEARCH")
    logger.info("=" * 60)
    
    # Show current lens
    current_lens = trend_researcher.get_current_lens()
    logger.info(f"\n🎯 Current Story Lens: {current_lens.value}")
    logger.info(f"   POV Ratio: {trend_researcher.POV_RATIO*100:.0f}% POV / {(1-trend_researcher.POV_RATIO)*100:.0f}% Trend")
    
    # Get YouTube trending
    logger.info("\n🎬 YouTube Trending India:")
    trends = await trend_researcher.get_raw_trends()
    
    for i, video in enumerate(trends.get('youtube_trending', [])[:10], 1):
        logger.info(f"  {i}. {video['title'][:50]}...")
        logger.info(f"     Views: {video.get('view_count', 0):,}")
    
    # Get POV-first analyzed topic
    logger.info("\n🎯 POV-First Topic Selection:")
    topic = await trend_researcher.get_trending_topic()
    
    logger.info(f"  Source: {topic.get('source', 'N/A')}")
    logger.info(f"  Story Lens: {topic.get('story_lens', 'N/A')}")
    logger.info(f"  Topic: {topic['topic']}")
    logger.info(f"  Era: {topic['era']}")
    logger.info(f"  Mood: {topic['mood']}")
    logger.info(f"  Hook: {topic.get('hook', 'N/A')}")
    
    return topic


async def show_health():
    """Show creator brand health metrics"""
    from app.services.creator_metrics import creator_metrics
    import json
    
    logger.info("📊 CREATOR BRAND HEALTH")
    logger.info("=" * 60)
    
    report = creator_metrics.get_health_report()
    
    # Summary
    logger.info(f"\n📈 OVERALL GRADE: {report['summary']['overall_grade']}")
    logger.info(f"   Total Videos: {report['summary']['total_videos']}")
    logger.info(f"   Total Views: {report['summary']['total_views']:,}")
    
    # Trust
    logger.info(f"\n🤝 TRUST ({report['trust_metrics']['grade']})")
    logger.info(f"   Retention Rate: {report['trust_metrics']['retention_rate']}")
    logger.info(f"   First 3s Retention: {report['trust_metrics']['first_3s_retention']}")
    logger.info(f"   Story Completion: {report['trust_metrics']['story_completion']}")
    logger.info(f"   → {report['trust_metrics']['interpretation']}")
    
    # Identity
    logger.info(f"\n🎭 IDENTITY ({report['identity_metrics']['grade']})")
    logger.info(f"   Total Subscribers: {report['identity_metrics']['total_subscribers']}")
    logger.info(f"   Growth Rate: {report['identity_metrics']['growth_rate']}")
    logger.info(f"   Most Used Lens: {report['identity_metrics']['most_used_lens']}")
    logger.info(f"   POV Consistency: {report['identity_metrics']['pov_consistency']}")
    logger.info(f"   → {report['identity_metrics']['interpretation']}")
    
    # Engagement
    logger.info(f"\n💬 ENGAGEMENT ({report['engagement_metrics']['grade']})")
    logger.info(f"   Comment Sentiment: {report['engagement_metrics']['comment_sentiment']}")
    logger.info(f"   Repeat Viewer Rate: {report['engagement_metrics']['repeat_viewer_rate']}")
    logger.info(f"   → {report['engagement_metrics']['interpretation']}")
    
    # Recommendations
    logger.info(f"\n💡 RECOMMENDATIONS:")
    for rec in report['recommendations']:
        logger.info(f"   {rec}")
    
    return report


async def manage_lens(action: str, lens_name: str = None):
    """Manage story lens settings"""
    from app.services.trend_researcher import trend_researcher
    from app.models.video import StoryLens
    
    logger.info("🎯 STORY LENS MANAGEMENT")
    logger.info("=" * 60)
    
    if action == "list":
        # Show all available lenses
        logger.info("\n📋 Available Story Lenses:")
        for lens_info in trend_researcher.get_all_lenses():
            current = "← CURRENT" if lens_info['lens'] == trend_researcher.get_current_lens().value else ""
            logger.info(f"  • {lens_info['lens']}: {lens_info['description']} {current}")
    
    elif action == "set" and lens_name:
        # Set new lens
        try:
            new_lens = StoryLens(lens_name)
            trend_researcher.set_story_lens(new_lens)
            logger.info(f"\n✅ Story lens set to: {new_lens.value}")
        except ValueError:
            logger.error(f"\n❌ Invalid lens: {lens_name}")
            logger.info("Use 'python create_video.py lens list' to see available lenses")
    
    elif action == "show":
        # Show current lens
        current = trend_researcher.get_current_lens()
        logger.info(f"\n🎯 Current Story Lens: {current.value}")
        
        # Show pool for this lens
        pool = trend_researcher.HISTORICAL_POOL.get(current, [])
        logger.info(f"\n📚 Curated Topics in Pool ({len(pool)} topics):")
        for i, topic in enumerate(pool[:5], 1):
            logger.info(f"  {i}. {topic['topic'][:60]}...")
            logger.info(f"     Era: {topic['era']}")
    
    else:
        logger.error("Invalid action. Use: list, show, or set --lens <lens_name>")


async def create_manual(topic: str, era: str, num_images: int):
    """Create video with manual topic"""
    from app.services.pipeline import pipeline
    from app.models.video import VideoRequest, MusicMood
    
    logger.info("🎬 MANUAL VIDEO CREATION")
    logger.info(f"Topic: {topic}")
    logger.info(f"Era: {era}")
    
    request = VideoRequest(
        topic=topic,
        era=era,
        num_segments=num_images,
        target_duration=40,
        music_mood=MusicMood.DRAMATIC
    )
    
    project = await pipeline.create_video(request)
    return project.final_video_path


async def upload_video(video_path: str, privacy: str):
    """Upload a video to YouTube"""
    from app.services.youtube_uploader import youtube_uploader
    from app.models.video import VideoScript, ScriptSegment, MusicMood
    
    logger.info("📤 YOUTUBE UPLOAD")
    logger.info("=" * 60)
    logger.info(f"Video: {video_path}")
    logger.info(f"Privacy: {privacy}")
    
    # Get video filename for title
    filename = Path(video_path).stem
    
    result = await youtube_uploader.upload_video(
        video_path=video_path,
        title=f"Historical Story - {filename}",
        description="AI-generated historical content #Shorts #History #India",
        tags=['History', 'India', 'Hindi'],
        privacy=privacy,
        is_short=True
    )
    
    if result['success']:
        logger.info(f"✅ Upload successful!")
        logger.info(f"🔗 URL: {result['url']}")
    else:
        logger.error(f"❌ Upload failed: {result.get('error')}")
    
    return result


async def create_and_upload(privacy: str = 'private'):
    """Create video and upload to YouTube"""
    from app.services.pipeline import pipeline
    
    logger.info("🎬 CREATE + UPLOAD MODE")
    logger.info("=" * 60)
    
    # Create video
    project = await pipeline.create_video_auto()
    
    # Upload to YouTube
    logger.info("\n📤 Now uploading to YouTube...")
    result = await pipeline.upload_to_youtube(
        project=project,
        privacy=privacy,
        with_captions=True
    )
    
    return result


async def main():
    parser = argparse.ArgumentParser(
        description="🎬 POV-First Creator Pipeline - Automated Hindi Historical Reels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python create_video.py                    # Auto-create one video (POV-first)
  python create_video.py --lens fear_to_courage  # Create with specific lens
  python create_video.py batch -n 3         # Create 3 videos
  python create_video.py topics             # Show trending topics
  python create_video.py health             # Show creator brand health
  python create_video.py lens list          # Show available story lenses
  python create_video.py lens set --lens power_and_control  # Set story lens
  python create_video.py manual -t "1857 Revolution" -e "British Raj"
  python create_video.py upload -f output/reel_xxx.mp4   # Upload existing video
  python create_video.py publish            # Create + upload (private)

STORY LENSES:
  power_and_control       - Stories about power dynamics, dominance
  fear_to_courage         - Stories of overcoming fear, bravery moments
  betrayal_and_consequences - Stories of treachery and its aftermath
  single_decision_moments - One irreversible choice that changed everything
  history_ignored_this    - Hidden gems, forgotten heroes
        """
    )
    
    # Global lens argument
    parser.add_argument("--lens", type=str, help="Story lens override for this video")
    
    subparsers = parser.add_subparsers(dest="mode", help="Mode")
    
    # Auto mode (default)
    auto_parser = subparsers.add_parser("auto", help="Auto-select topic and create video (POV-first)")
    auto_parser.add_argument("--lens", type=str, help="Story lens for this video")
    
    # Batch mode
    batch_parser = subparsers.add_parser("batch", help="Create multiple videos")
    batch_parser.add_argument("-n", "--count", type=int, default=3)
    batch_parser.add_argument("-d", "--delay", type=int, default=60)
    
    # Topics mode
    subparsers.add_parser("topics", help="Show trending topics (POV-first)")
    
    # Health mode (NEW)
    subparsers.add_parser("health", help="Show creator brand health metrics")
    
    # Lens management mode (NEW)
    lens_parser = subparsers.add_parser("lens", help="Manage story lens settings")
    lens_parser.add_argument("action", choices=["list", "show", "set"], help="Action to perform")
    lens_parser.add_argument("--lens", type=str, help="Lens name for 'set' action")
    
    # Manual mode
    manual_parser = subparsers.add_parser("manual", help="Manual topic")
    manual_parser.add_argument("-t", "--topic", required=True)
    manual_parser.add_argument("-e", "--era", required=True)
    manual_parser.add_argument("-i", "--images", type=int, default=8)
    manual_parser.add_argument("--lens", type=str, help="Story lens for this video")
    
    # Upload mode
    upload_parser = subparsers.add_parser("upload", help="Upload existing video to YouTube")
    upload_parser.add_argument("-f", "--file", required=True, help="Video file path")
    upload_parser.add_argument("--public", action="store_true", help="Make video public")
    
    # Publish mode (create + upload)
    publish_parser = subparsers.add_parser("publish", help="Create video and upload to YouTube")
    publish_parser.add_argument("--public", action="store_true", help="Make video public")
    publish_parser.add_argument("--lens", type=str, help="Story lens for this video")
    
    args = parser.parse_args()
    
    try:
        if args.mode == "batch":
            await create_batch(args.count, args.delay)
        elif args.mode == "topics":
            await show_topics()
        elif args.mode == "health":
            await show_health()
        elif args.mode == "lens":
            await manage_lens(args.action, args.lens)
        elif args.mode == "manual":
            await create_manual(args.topic, args.era, args.images)
        elif args.mode == "upload":
            privacy = 'public' if args.public else 'private'
            await upload_video(args.file, privacy)
        elif args.mode == "publish":
            privacy = 'public' if args.public else 'private'
            await create_and_upload(privacy)
        else:
            # Default: auto with optional lens
            lens_name = getattr(args, 'lens', None)
            await create_auto(lens_name)
            
    except KeyboardInterrupt:
        logger.info("\n⛔ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
