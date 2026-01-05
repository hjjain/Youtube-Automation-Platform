"""
API Routes for Video Creation Platform
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import Optional, List
from loguru import logger
from pathlib import Path
from datetime import datetime, timedelta
import os

from app.models.video import VideoRequest, VideoProject, MusicMood
from app.services.pipeline import pipeline
from app.services.video_composer import video_composer
from app.services.voiceover_generator import voiceover_generator
from app.services.trend_researcher import trend_researcher
from app.services.youtube_analyzer import youtube_analyzer
from app.services.hook_generator import hook_generator
from app.core.config import settings

router = APIRouter()


# ============================================
# DASHBOARD ENDPOINTS (for frontend)
# ============================================

@router.get("/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    # Count videos in output directory
    output_dir = settings.OUTPUT_DIR
    total_videos = 0
    videos_today = 0
    today = datetime.now().date()
    
    if output_dir.exists():
        for f in output_dir.glob("*.mp4"):
            total_videos += 1
            # Check if created today
            mtime = datetime.fromtimestamp(f.stat().st_mtime).date()
            if mtime == today:
                videos_today += 1
    
    # Get processing queue count from active_projects
    queue_count = len([p for p in pipeline.active_projects.values() 
                       if hasattr(p, 'status') and p.status.value == 'processing'])
    
    return {
        "total_videos": total_videos,
        "videos_today": videos_today,
        "total_views": 0,  # Would need YouTube API integration
        "queue_count": queue_count,
        "trending_count": 5
    }


@router.get("/videos")
async def get_all_videos(limit: int = Query(default=20, le=100)):
    """Get list of all created videos"""
    videos = []
    output_dir = settings.OUTPUT_DIR
    
    if output_dir.exists():
        # Get all mp4 files sorted by modification time (newest first)
        video_files = sorted(
            output_dir.glob("*.mp4"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:limit]
        
        for f in video_files:
            # Extract project ID from filename (e.g., reel_abc123.mp4 -> abc123)
            filename = f.stem
            project_id = filename.replace("reel_", "").replace("_captioned", "")
            
            # Check if there's a project in memory (active_projects)
            project = pipeline.active_projects.get(project_id)
            
            stat = f.stat()
            videos.append({
                "id": project_id,
                "topic": project.topic if project else filename,
                "status": project.status.value if project else "completed",
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "video_url": f"/output/{f.name}",
                "final_video_path": str(f),
                "duration": None,  # Would need to read video metadata
                "script_title": project.script.title if project and project.script else None,
            })
    
    return videos


@router.post("/videos/create-auto", response_model=dict)
async def create_video_auto(background_tasks: BackgroundTasks):
    """
    Create a new video with AUTO-SELECTED trending topic
    This is the main endpoint for automated video creation
    """
    logger.info("Received auto video creation request")
    
    # Get topic first to return it
    topic_data = await trend_researcher.get_trending_topic()
    
    # Create project synchronously to get ID
    project = VideoProject(topic=topic_data['topic'])
    
    # Run pipeline in background
    background_tasks.add_task(run_auto_pipeline_background, project_id=project.id)
    
    return {
        "message": "Auto video creation started",
        "project_id": project.id,
        "status": "processing",
        "selected_topic": topic_data['topic'],
        "era": topic_data['era'],
        "mood": topic_data['mood'],
        "reason": topic_data.get('reason', ''),
        "event_context": topic_data.get('event_context', '')
    }


@router.post("/videos/create-auto-sync", response_model=dict)
async def create_video_auto_sync():
    """
    Create a video with auto-selected topic (synchronous - waits for completion)
    """
    logger.info("Starting synchronous auto video creation")
    
    try:
        project = await pipeline.create_video_auto()
        
        return {
            "message": "Video created successfully",
            "project_id": project.id,
            "status": project.status.value,
            "topic": project.topic,
            "final_video_path": project.final_video_path,
            "script_segments": len(project.script.segments) if project.script else 0,
            "images_generated": len(project.images)
        }
        
    except Exception as e:
        logger.error(f"Auto video creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/videos/create", response_model=dict)
async def create_video_manual(request: VideoRequest, background_tasks: BackgroundTasks):
    """
    Create a new video with MANUAL topic specification
    Use this only when you want to override auto topic selection
    """
    logger.info(f"Received manual video creation request: {request.topic}")
    
    project = VideoProject(topic=request.topic)
    
    background_tasks.add_task(
        run_manual_pipeline_background,
        request=request,
        project_id=project.id
    )
    
    return {
        "message": "Manual video creation started",
        "project_id": project.id,
        "status": "processing",
        "topic": request.topic,
        "era": request.era
    }


@router.post("/videos/batch", response_model=dict)
async def create_batch_videos(
    count: int = 3,
    delay: int = 60,
    background_tasks: BackgroundTasks = None
):
    """
    Create multiple videos in batch with auto-selected topics
    """
    logger.info(f"Starting batch creation of {count} videos")
    
    background_tasks.add_task(run_batch_pipeline_background, count=count, delay=delay)
    
    return {
        "message": f"Batch creation started for {count} videos",
        "status": "processing",
        "delay_between_videos": delay
    }


@router.get("/topics/trending")
async def get_trending_topic():
    """Get the current trending topic that would be selected"""
    topic_data = await trend_researcher.get_trending_topic()
    return {
        "topic": topic_data['topic'],
        "era": topic_data['era'],
        "mood": topic_data['mood'],
        "hook": topic_data.get('hook', ''),
        "reason": topic_data.get('reason', ''),
        "event_context": topic_data.get('event_context', '')
    }


@router.get("/topics/upcoming")
async def get_upcoming_topics(count: int = 5):
    """Get multiple topic suggestions based on current trends"""
    topics = await trend_researcher.get_multiple_topics(count)
    return {"topics": topics}


@router.get("/topics/raw-trends")
async def get_raw_trends():
    """
    DEBUG: Get raw trends data from all sources
    Shows what YouTube, Google Trends, News, and Web Search return
    """
    trends = await trend_researcher.get_raw_trends()
    return {
        "youtube_trending": trends.get("youtube_trending", []),
        "google_trends": trends.get("google_trends", []),
        "news_headlines": trends.get("news_headlines", []),
        "web_search": trends.get("web_search", []),
        "timestamp": trends.get("timestamp")
    }


@router.get("/topics/youtube-trending")
async def get_youtube_trending():
    """Get YouTube trending videos in India (real-time)"""
    videos = await trend_researcher.get_youtube_trending_only()
    return {
        "count": len(videos),
        "videos": videos
    }


@router.get("/videos/{project_id}/status")
async def get_video_status(project_id: str):
    """Get the status of a video creation project"""
    project = pipeline.get_project_status(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "project_id": project.id,
        "status": project.status.value,
        "topic": project.topic,
        "created_at": project.created_at.isoformat(),
        "final_video_path": project.final_video_path,
        "error_message": project.error_message
    }


@router.get("/music/library")
async def list_music_library():
    """List all available background music files"""
    library = video_composer.list_available_music()
    return {"music_library": library}


@router.get("/voices/available")
async def list_available_voices():
    """List available ElevenLabs voices with recommendations"""
    voices = await voiceover_generator.list_available_voices()
    return {"voices": voices}


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "reel-creator-api"}


# ============================================
# YOUTUBE ANALYZER ENDPOINTS
# ============================================

@router.get("/analyze/viral-patterns")
async def analyze_viral_patterns():
    """
    Analyze current viral patterns on YouTube India
    Returns insights on hooks, titles, keywords, and engagement
    """
    analysis = await youtube_analyzer.analyze_viral_patterns()
    return analysis


@router.get("/analyze/similar-content")
async def find_similar_content(topic: str, max_results: int = 10):
    """Search for viral videos similar to a topic"""
    results = await youtube_analyzer.search_similar_viral_content(topic, max_results)
    return {"topic": topic, "similar_videos": results}


@router.get("/analyze/competitor-channels")
async def analyze_competitors(keywords: str = "history hindi"):
    """Analyze competitor channels for insights"""
    keyword_list = keywords.split(",")
    results = await youtube_analyzer.get_competitor_analysis(keyword_list)
    return {"keywords": keyword_list, "channels": results}


# ============================================
# HOOK GENERATOR ENDPOINTS
# ============================================

@router.post("/hooks/generate")
async def generate_hooks(topic: str, era: str, mood: str = "dramatic"):
    """
    Generate viral hooks for a topic
    Uses YouTube analysis + proven formulas + LLM
    """
    result = await hook_generator.generate_viral_hook(topic, era, mood)
    return result


@router.get("/hooks/formulas")
async def get_hook_formulas():
    """Get all proven hook formula templates"""
    return {"formulas": hook_generator.HOOK_FORMULAS}


# Background task runners
async def run_auto_pipeline_background(project_id: str):
    """Run auto video creation pipeline in background"""
    try:
        await pipeline.create_video_auto()
    except Exception as e:
        logger.error(f"Background auto pipeline failed for {project_id}: {e}")


async def run_manual_pipeline_background(request: VideoRequest, project_id: str):
    """Run manual video creation pipeline in background"""
    try:
        await pipeline.create_video(request)
    except Exception as e:
        logger.error(f"Background manual pipeline failed for {project_id}: {e}")


async def run_batch_pipeline_background(count: int, delay: int):
    """Run batch video creation in background"""
    try:
        await pipeline.batch_create_videos(count=count, delay_between=delay)
    except Exception as e:
        logger.error(f"Batch pipeline failed: {e}")
