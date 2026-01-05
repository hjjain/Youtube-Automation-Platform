"""
Creator Metrics Service - TRUST-BUILDING ANALYTICS
Tracks metrics that indicate creator brand growth, not just virality.

PHILOSOPHY:
Views alone will mislead you. These metrics indicate:
- Trust (repeat viewers)
- Identity (subscriber gain per video)
- Long-term viability (comment sentiment, retention)
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from loguru import logger

from app.core.config import settings


@dataclass
class VideoMetrics:
    """Metrics for a single video"""
    video_id: str
    title: str
    story_lens: str
    uploaded_at: datetime
    
    # Basic metrics
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    
    # TRUST metrics (what actually matters for creators)
    avg_view_duration_seconds: float = 0.0
    avg_view_percentage: float = 0.0
    first_3s_retention: float = 0.0  # Critical: if they leave in 3s, hook failed
    
    # IDENTITY metrics (brand building)
    subscriber_gain: int = 0
    subscriber_loss: int = 0
    net_subscriber_change: int = 0
    
    # ENGAGEMENT metrics (community building)
    comment_sentiment_score: float = 0.0  # -1 to 1
    repeat_viewer_percentage: float = 0.0
    unique_viewers: int = 0
    returning_viewers: int = 0
    
    # Content performance
    hook_effectiveness: float = 0.0  # Based on first 3s retention
    story_completion_rate: float = 0.0  # How many watched to end
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['uploaded_at'] = self.uploaded_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'VideoMetrics':
        """Create from dictionary"""
        data['uploaded_at'] = datetime.fromisoformat(data['uploaded_at'])
        return cls(**data)


@dataclass 
class CreatorHealth:
    """Overall creator brand health metrics"""
    calculated_at: datetime
    
    # Overall performance
    total_videos: int = 0
    total_views: int = 0
    avg_views_per_video: float = 0.0
    
    # TRUST indicators
    overall_retention_rate: float = 0.0
    avg_first_3s_retention: float = 0.0
    avg_story_completion: float = 0.0
    
    # IDENTITY indicators
    total_subscribers: int = 0
    subscriber_growth_rate: float = 0.0  # % growth per week
    avg_subscriber_gain_per_video: float = 0.0
    
    # ENGAGEMENT indicators
    avg_comment_sentiment: float = 0.0
    repeat_viewer_rate: float = 0.0
    community_engagement_score: float = 0.0
    
    # Content consistency (POV alignment)
    most_used_lens: str = ""
    lens_distribution: Dict[str, int] = None
    consistent_pov_score: float = 0.0  # Higher = more consistent brand
    
    # Health grades
    trust_grade: str = ""  # A, B, C, D, F
    identity_grade: str = ""
    engagement_grade: str = ""
    overall_grade: str = ""
    
    def __post_init__(self):
        if self.lens_distribution is None:
            self.lens_distribution = {}


class CreatorMetricsService:
    """
    Service to track and analyze creator metrics that matter for
    long-term brand building, not just viral hits.
    
    Key metrics:
    1. Trust: Do people watch your whole video? Do they come back?
    2. Identity: Are you gaining subscribers? Is your lens consistent?
    3. Engagement: What do comments say? Is there a community forming?
    """
    
    # Metric file storage
    METRICS_FILE = "creator_metrics.json"
    
    # Thresholds for grades
    GRADE_THRESHOLDS = {
        'A': 0.8,
        'B': 0.6,
        'C': 0.4,
        'D': 0.2,
        'F': 0.0
    }
    
    def __init__(self):
        self.metrics_path = settings.OUTPUT_DIR / self.METRICS_FILE
        self.video_metrics: Dict[str, VideoMetrics] = {}
        self._load_metrics()
    
    def _load_metrics(self):
        """Load existing metrics from file"""
        if self.metrics_path.exists():
            try:
                with open(self.metrics_path, 'r') as f:
                    data = json.load(f)
                    for video_id, metrics_data in data.get('videos', {}).items():
                        self.video_metrics[video_id] = VideoMetrics.from_dict(metrics_data)
                logger.info(f"📊 Loaded metrics for {len(self.video_metrics)} videos")
            except Exception as e:
                logger.error(f"Failed to load metrics: {e}")
    
    def _save_metrics(self):
        """Save metrics to file"""
        try:
            data = {
                'videos': {
                    video_id: metrics.to_dict() 
                    for video_id, metrics in self.video_metrics.items()
                },
                'last_updated': datetime.now().isoformat()
            }
            self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.metrics_path, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def record_video_upload(
        self, 
        video_id: str, 
        title: str, 
        story_lens: str
    ) -> VideoMetrics:
        """Record a new video upload"""
        metrics = VideoMetrics(
            video_id=video_id,
            title=title,
            story_lens=story_lens,
            uploaded_at=datetime.now()
        )
        self.video_metrics[video_id] = metrics
        self._save_metrics()
        logger.info(f"📹 Recorded upload: {title[:30]}... (Lens: {story_lens})")
        return metrics
    
    def update_video_metrics(
        self,
        video_id: str,
        views: int = None,
        likes: int = None,
        comments: int = None,
        avg_view_duration: float = None,
        avg_view_percentage: float = None,
        first_3s_retention: float = None,
        subscriber_gain: int = None,
        subscriber_loss: int = None,
        comment_sentiment: float = None,
        unique_viewers: int = None,
        returning_viewers: int = None
    ) -> Optional[VideoMetrics]:
        """Update metrics for a video (call with YouTube Analytics data)"""
        
        if video_id not in self.video_metrics:
            logger.warning(f"Video {video_id} not found in metrics")
            return None
        
        metrics = self.video_metrics[video_id]
        
        # Update provided metrics
        if views is not None:
            metrics.views = views
        if likes is not None:
            metrics.likes = likes
        if comments is not None:
            metrics.comments = comments
        if avg_view_duration is not None:
            metrics.avg_view_duration_seconds = avg_view_duration
        if avg_view_percentage is not None:
            metrics.avg_view_percentage = avg_view_percentage
        if first_3s_retention is not None:
            metrics.first_3s_retention = first_3s_retention
            metrics.hook_effectiveness = first_3s_retention
        if subscriber_gain is not None:
            metrics.subscriber_gain = subscriber_gain
        if subscriber_loss is not None:
            metrics.subscriber_loss = subscriber_loss
        if subscriber_gain is not None or subscriber_loss is not None:
            metrics.net_subscriber_change = metrics.subscriber_gain - metrics.subscriber_loss
        if comment_sentiment is not None:
            metrics.comment_sentiment_score = comment_sentiment
        if unique_viewers is not None:
            metrics.unique_viewers = unique_viewers
        if returning_viewers is not None:
            metrics.returning_viewers = returning_viewers
            if unique_viewers and unique_viewers > 0:
                metrics.repeat_viewer_percentage = (returning_viewers / unique_viewers) * 100
        
        self._save_metrics()
        return metrics
    
    def calculate_creator_health(self) -> CreatorHealth:
        """
        Calculate overall creator brand health.
        This is the REAL metric of success, not just views.
        """
        health = CreatorHealth(calculated_at=datetime.now())
        
        if not self.video_metrics:
            return health
        
        videos = list(self.video_metrics.values())
        health.total_videos = len(videos)
        
        # Basic aggregates
        health.total_views = sum(v.views for v in videos)
        health.avg_views_per_video = health.total_views / health.total_videos
        
        # TRUST metrics
        retention_rates = [v.avg_view_percentage for v in videos if v.avg_view_percentage > 0]
        if retention_rates:
            health.overall_retention_rate = sum(retention_rates) / len(retention_rates)
        
        first_3s = [v.first_3s_retention for v in videos if v.first_3s_retention > 0]
        if first_3s:
            health.avg_first_3s_retention = sum(first_3s) / len(first_3s)
        
        completion = [v.story_completion_rate for v in videos if v.story_completion_rate > 0]
        if completion:
            health.avg_story_completion = sum(completion) / len(completion)
        
        # IDENTITY metrics
        total_sub_gain = sum(v.subscriber_gain for v in videos)
        total_sub_loss = sum(v.subscriber_loss for v in videos)
        health.total_subscribers = total_sub_gain - total_sub_loss
        health.avg_subscriber_gain_per_video = total_sub_gain / health.total_videos
        
        # Calculate growth rate (last 7 days vs previous 7 days)
        health.subscriber_growth_rate = self._calculate_growth_rate(videos)
        
        # ENGAGEMENT metrics
        sentiments = [v.comment_sentiment_score for v in videos if v.comment_sentiment_score != 0]
        if sentiments:
            health.avg_comment_sentiment = sum(sentiments) / len(sentiments)
        
        repeat_rates = [v.repeat_viewer_percentage for v in videos if v.repeat_viewer_percentage > 0]
        if repeat_rates:
            health.repeat_viewer_rate = sum(repeat_rates) / len(repeat_rates)
        
        # Community engagement (weighted score of likes, comments, shares per view)
        engagement_scores = []
        for v in videos:
            if v.views > 0:
                engagement = ((v.likes * 1) + (v.comments * 2) + (v.shares * 3)) / v.views
                engagement_scores.append(engagement)
        if engagement_scores:
            health.community_engagement_score = sum(engagement_scores) / len(engagement_scores)
        
        # POV consistency
        lens_counts = {}
        for v in videos:
            lens_counts[v.story_lens] = lens_counts.get(v.story_lens, 0) + 1
        health.lens_distribution = lens_counts
        
        if lens_counts:
            health.most_used_lens = max(lens_counts, key=lens_counts.get)
            # Consistency score: % of videos using most common lens
            health.consistent_pov_score = lens_counts[health.most_used_lens] / health.total_videos
        
        # Calculate grades
        health.trust_grade = self._grade_metric(health.overall_retention_rate / 100)
        health.identity_grade = self._grade_metric(
            min(1.0, health.avg_subscriber_gain_per_video / 100)  # 100 subs/video = A
        )
        health.engagement_grade = self._grade_metric(
            min(1.0, health.community_engagement_score * 10)  # 0.1 engagement = A
        )
        
        # Overall grade (weighted average)
        grades = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'F': 0}
        overall_score = (
            grades.get(health.trust_grade, 0) * 0.4 +
            grades.get(health.identity_grade, 0) * 0.35 +
            grades.get(health.engagement_grade, 0) * 0.25
        )
        health.overall_grade = self._score_to_grade(overall_score / 4)
        
        return health
    
    def _calculate_growth_rate(self, videos: List[VideoMetrics]) -> float:
        """Calculate week-over-week subscriber growth rate"""
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)
        
        recent = [v for v in videos if v.uploaded_at >= week_ago]
        previous = [v for v in videos if two_weeks_ago <= v.uploaded_at < week_ago]
        
        recent_subs = sum(v.net_subscriber_change for v in recent)
        previous_subs = sum(v.net_subscriber_change for v in previous)
        
        if previous_subs > 0:
            return ((recent_subs - previous_subs) / previous_subs) * 100
        return 0.0
    
    def _grade_metric(self, value: float) -> str:
        """Convert 0-1 value to letter grade"""
        for grade, threshold in self.GRADE_THRESHOLDS.items():
            if value >= threshold:
                return grade
        return 'F'
    
    def _score_to_grade(self, score: float) -> str:
        """Convert 0-1 score to letter grade"""
        return self._grade_metric(score)
    
    def get_health_report(self) -> Dict:
        """Get a formatted health report for the creator"""
        health = self.calculate_creator_health()
        
        report = {
            "calculated_at": health.calculated_at.isoformat(),
            "summary": {
                "overall_grade": health.overall_grade,
                "total_videos": health.total_videos,
                "total_views": health.total_views,
            },
            "trust_metrics": {
                "grade": health.trust_grade,
                "retention_rate": f"{health.overall_retention_rate:.1f}%",
                "first_3s_retention": f"{health.avg_first_3s_retention:.1f}%",
                "story_completion": f"{health.avg_story_completion:.1f}%",
                "interpretation": self._interpret_trust(health.trust_grade)
            },
            "identity_metrics": {
                "grade": health.identity_grade,
                "total_subscribers": health.total_subscribers,
                "growth_rate": f"{health.subscriber_growth_rate:.1f}%",
                "avg_subs_per_video": f"{health.avg_subscriber_gain_per_video:.1f}",
                "most_used_lens": health.most_used_lens,
                "pov_consistency": f"{health.consistent_pov_score*100:.1f}%",
                "interpretation": self._interpret_identity(health.identity_grade)
            },
            "engagement_metrics": {
                "grade": health.engagement_grade,
                "comment_sentiment": f"{health.avg_comment_sentiment:.2f}",
                "repeat_viewer_rate": f"{health.repeat_viewer_rate:.1f}%",
                "community_score": f"{health.community_engagement_score:.3f}",
                "interpretation": self._interpret_engagement(health.engagement_grade)
            },
            "recommendations": self._get_recommendations(health)
        }
        
        return report
    
    def _interpret_trust(self, grade: str) -> str:
        """Interpret trust grade"""
        interpretations = {
            'A': "Excellent! Viewers trust your content and watch to completion.",
            'B': "Good retention. Your hooks are working and stories deliver.",
            'C': "Average. Some viewers leaving early. Check your hook-to-story alignment.",
            'D': "Concern. Many leaving before story payoff. Review your structure.",
            'F': "Critical. Viewers not staying. Major hook/story disconnect."
        }
        return interpretations.get(grade, "No data yet")
    
    def _interpret_identity(self, grade: str) -> str:
        """Interpret identity grade"""
        interpretations = {
            'A': "Strong brand! Viewers are subscribing consistently.",
            'B': "Building identity. Subscriber growth is healthy.",
            'C': "Moderate growth. Consider more POV consistency.",
            'D': "Slow growth. Your brand may feel inconsistent to viewers.",
            'F': "Brand not connecting. Review your storytelling POV."
        }
        return interpretations.get(grade, "No data yet")
    
    def _interpret_engagement(self, grade: str) -> str:
        """Interpret engagement grade"""
        interpretations = {
            'A': "Thriving community! Viewers are engaged and returning.",
            'B': "Good engagement. Community forming around your content.",
            'C': "Average engagement. Consider more community-building content.",
            'D': "Low engagement. Viewers watching but not interacting.",
            'F': "No community yet. Focus on trust-building first."
        }
        return interpretations.get(grade, "No data yet")
    
    def _get_recommendations(self, health: CreatorHealth) -> List[str]:
        """Get actionable recommendations based on health metrics"""
        recommendations = []
        
        # Trust recommendations
        if health.avg_first_3s_retention < 60:
            recommendations.append(
                "🎯 First 3s retention is low. Your hooks need work. "
                "Use more contradiction hooks, less curiosity bait."
            )
        if health.avg_story_completion < 50:
            recommendations.append(
                "📖 Story completion is low. Make sure you ANSWER "
                "the questions your hooks raise. No cliffhangers without payoff."
            )
        
        # Identity recommendations
        if health.consistent_pov_score < 0.6:
            recommendations.append(
                "🎭 POV inconsistency detected. Stick to ONE story lens "
                f"(currently most used: {health.most_used_lens}). "
                "This trains the algorithm to find your audience."
            )
        if health.avg_subscriber_gain_per_video < 10:
            recommendations.append(
                "👤 Low subscriber gain. Your content may be forgettable. "
                "Focus on consistent visual identity and storytelling POV."
            )
        
        # Engagement recommendations
        if health.avg_comment_sentiment < 0:
            recommendations.append(
                "💬 Negative comment sentiment. Review your hooks for "
                "misleading promises. Trust = matching expectations."
            )
        if health.repeat_viewer_rate < 20:
            recommendations.append(
                "🔁 Few repeat viewers. Your content isn't building habit. "
                "Consider series/sequels and consistent posting schedule."
            )
        
        if not recommendations:
            recommendations.append(
                "✅ Great work! Keep creating with your current POV. "
                "Consistency is key to long-term success."
            )
        
        return recommendations
    
    def get_video_performance(self, video_id: str) -> Optional[Dict]:
        """Get detailed performance for a specific video"""
        if video_id not in self.video_metrics:
            return None
        
        metrics = self.video_metrics[video_id]
        
        return {
            "video_id": video_id,
            "title": metrics.title,
            "story_lens": metrics.story_lens,
            "uploaded_at": metrics.uploaded_at.isoformat(),
            "performance": {
                "views": metrics.views,
                "likes": metrics.likes,
                "comments": metrics.comments,
                "like_ratio": f"{(metrics.likes/metrics.views*100) if metrics.views > 0 else 0:.1f}%"
            },
            "trust_indicators": {
                "avg_view_duration": f"{metrics.avg_view_duration_seconds:.1f}s",
                "avg_view_percentage": f"{metrics.avg_view_percentage:.1f}%",
                "first_3s_retention": f"{metrics.first_3s_retention:.1f}%",
                "hook_effectiveness": "Good" if metrics.first_3s_retention > 70 else "Needs work"
            },
            "identity_impact": {
                "subscriber_gain": metrics.subscriber_gain,
                "subscriber_loss": metrics.subscriber_loss,
                "net_impact": metrics.net_subscriber_change
            },
            "engagement": {
                "comment_sentiment": metrics.comment_sentiment_score,
                "repeat_viewers": f"{metrics.repeat_viewer_percentage:.1f}%"
            }
        }
    
    def compare_lenses(self) -> Dict:
        """Compare performance across different story lenses"""
        lens_performance = {}
        
        for video_id, metrics in self.video_metrics.items():
            lens = metrics.story_lens
            if lens not in lens_performance:
                lens_performance[lens] = {
                    "videos": 0,
                    "total_views": 0,
                    "avg_retention": [],
                    "avg_subs": [],
                    "avg_sentiment": []
                }
            
            lens_performance[lens]["videos"] += 1
            lens_performance[lens]["total_views"] += metrics.views
            if metrics.avg_view_percentage > 0:
                lens_performance[lens]["avg_retention"].append(metrics.avg_view_percentage)
            lens_performance[lens]["avg_subs"].append(metrics.net_subscriber_change)
            if metrics.comment_sentiment_score != 0:
                lens_performance[lens]["avg_sentiment"].append(metrics.comment_sentiment_score)
        
        # Calculate averages
        comparison = {}
        for lens, data in lens_performance.items():
            comparison[lens] = {
                "videos": data["videos"],
                "avg_views": data["total_views"] / data["videos"] if data["videos"] > 0 else 0,
                "avg_retention": sum(data["avg_retention"]) / len(data["avg_retention"]) if data["avg_retention"] else 0,
                "avg_subs_impact": sum(data["avg_subs"]) / len(data["avg_subs"]) if data["avg_subs"] else 0,
                "avg_sentiment": sum(data["avg_sentiment"]) / len(data["avg_sentiment"]) if data["avg_sentiment"] else 0
            }
        
        # Find best performing lens
        if comparison:
            best_lens = max(
                comparison.keys(),
                key=lambda l: comparison[l]["avg_retention"] * 0.4 + 
                             comparison[l]["avg_subs_impact"] * 0.4 +
                             (comparison[l]["avg_sentiment"] + 1) * 0.2
            )
            comparison["recommendation"] = f"Best performing lens: {best_lens}"
        
        return comparison


# Singleton instance
creator_metrics = CreatorMetricsService()
