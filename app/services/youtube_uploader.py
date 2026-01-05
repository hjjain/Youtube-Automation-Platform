"""
YouTube Uploader Service
Upload Shorts directly to YouTube with metadata and captions
Uses YouTube Data API v3 (FREE - 10,000 units/day)
"""
import os
import json
import httplib2
from pathlib import Path
from typing import Optional, Dict, List
from loguru import logger
from datetime import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from app.core.config import settings


class YouTubeUploaderService:
    """
    Upload videos to YouTube with full metadata
    
    Quota costs:
    - Video upload: 1,600 units
    - Caption upload: 200 units
    - Daily limit: 10,000 units (~5-6 videos/day with captions)
    """
    
    # OAuth scopes needed for uploading and captions
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube',
        'https://www.googleapis.com/auth/youtube.force-ssl'  # Required for captions
    ]
    
    # Video categories
    CATEGORIES = {
        'film': '1',
        'autos': '2',
        'music': '10',
        'pets': '15',
        'sports': '17',
        'travel': '19',
        'gaming': '20',
        'people': '22',
        'comedy': '23',
        'entertainment': '24',
        'news': '25',
        'howto': '26',
        'education': '27',
        'science': '28',
        'nonprofit': '29'
    }
    
    def __init__(self):
        self.credentials_file = Path("credentials/youtube_oauth.json")
        self.token_file = Path("credentials/youtube_token.json")
        self.youtube = None
        
    def _get_authenticated_service(self):
        """Get authenticated YouTube service"""
        creds = None
        
        # Check for existing token
        if self.token_file.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_file), self.SCOPES)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("🔄 Refreshing YouTube credentials...")
                creds.refresh(Request())
            else:
                if not self.credentials_file.exists():
                    raise FileNotFoundError(
                        f"OAuth credentials not found at {self.credentials_file}\n"
                        "Please download from Google Cloud Console:\n"
                        "1. Go to console.cloud.google.com\n"
                        "2. APIs & Services → Credentials\n"
                        "3. Create OAuth 2.0 Client ID (Desktop app)\n"
                        "4. Download JSON and save as credentials/youtube_oauth.json"
                    )
                
                logger.info("🔐 Starting YouTube OAuth flow...")
                logger.info("📱 A browser window will open for authentication")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file), 
                    self.SCOPES
                )
                creds = flow.run_local_server(port=8080)
            
            # Save credentials for future use
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
            logger.info("✅ YouTube credentials saved")
        
        return build('youtube', 'v3', credentials=creds)
    
    async def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str] = None,
        category: str = 'entertainment',
        privacy: str = 'private',  # private, unlisted, public
        is_short: bool = True,
        language: str = 'hi',  # Hindi
        scheduled_time: Optional[datetime] = None
    ) -> Dict:
        """
        Upload a video to YouTube
        
        Args:
            video_path: Path to the video file
            title: Video title (max 100 chars)
            description: Video description (max 5000 bytes)
            tags: List of tags/keywords
            category: Video category
            privacy: Privacy status (private/unlisted/public)
            is_short: Whether this is a YouTube Short
            language: Default language
            scheduled_time: When to publish (for scheduled uploads)
        
        Returns:
            Dict with video_id and upload status
        """
        logger.info(f"📤 Uploading video to YouTube: {title[:50]}...")
        
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Get authenticated service
        if not self.youtube:
            self.youtube = self._get_authenticated_service()
        
        # Prepare title for Shorts
        if is_short and not title.startswith('#'):
            title = f"{title} #Shorts"
        
        # Truncate title if needed
        if len(title) > 100:
            title = title[:97] + "..."
        
        # Prepare tags
        if tags is None:
            tags = []
        if is_short:
            tags = ['Shorts', 'Short', 'YouTubeShorts'] + tags
        
        # Add Hindi/India tags
        tags.extend(['Hindi', 'India', 'Indian History', 'हिंदी'])
        tags = list(set(tags))[:500]  # Max 500 chars total
        
        # Build request body
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': self.CATEGORIES.get(category, '24'),
                'defaultLanguage': language,
                'defaultAudioLanguage': language
            },
            'status': {
                'privacyStatus': privacy,
                'selfDeclaredMadeForKids': False,
                'license': 'youtube',  # Standard YouTube license
            }
        }
        
        # Add scheduled publish time if provided
        if scheduled_time and privacy == 'private':
            body['status']['publishAt'] = scheduled_time.isoformat() + 'Z'
        
        # Create media upload
        media = MediaFileUpload(
            video_path,
            mimetype='video/mp4',
            resumable=True,
            chunksize=1024*1024  # 1MB chunks
        )
        
        try:
            # Execute upload
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = None
            logger.info("⏳ Uploading... (this may take a minute)")
            
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"📊 Upload progress: {progress}%")
            
            video_id = response['id']
            logger.info(f"✅ Video uploaded successfully!")
            logger.info(f"🎬 Video ID: {video_id}")
            logger.info(f"🔗 URL: https://youtube.com/shorts/{video_id}")
            
            return {
                'success': True,
                'video_id': video_id,
                'url': f"https://youtube.com/shorts/{video_id}",
                'title': title,
                'privacy': privacy
            }
            
        except HttpError as e:
            error_content = json.loads(e.content.decode('utf-8'))
            error_reason = error_content.get('error', {}).get('errors', [{}])[0].get('reason', 'unknown')
            logger.error(f"❌ YouTube upload failed: {error_reason}")
            logger.error(f"   Details: {error_content}")
            
            return {
                'success': False,
                'error': error_reason,
                'details': str(error_content)
            }
    
    async def upload_captions(
        self,
        video_id: str,
        caption_text: str,
        language: str = 'hi',
        name: str = 'Hindi'
    ) -> Dict:
        """
        Upload captions/subtitles for a video
        
        Args:
            video_id: YouTube video ID
            caption_text: Caption content (SRT format)
            language: Language code
            name: Caption track name
        """
        logger.info(f"📝 Uploading captions for video: {video_id}")
        
        if not self.youtube:
            self.youtube = self._get_authenticated_service()
        
        # Save caption to temp file
        caption_file = Path(f"temp/captions_{video_id}.srt")
        caption_file.parent.mkdir(parents=True, exist_ok=True)
        caption_file.write_text(caption_text, encoding='utf-8')
        
        try:
            request = self.youtube.captions().insert(
                part='snippet',
                body={
                    'snippet': {
                        'videoId': video_id,
                        'language': language,
                        'name': name,
                        'isDraft': False
                    }
                },
                media_body=MediaFileUpload(str(caption_file), mimetype='text/plain')
            )
            
            response = request.execute()
            logger.info(f"✅ Captions uploaded: {response['id']}")
            
            # Clean up
            caption_file.unlink()
            
            return {
                'success': True,
                'caption_id': response['id']
            }
            
        except HttpError as e:
            logger.error(f"❌ Caption upload failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_srt_captions(
        self, 
        segments: List[Dict],
        total_duration: float
    ) -> str:
        """
        Generate SRT format captions from script segments
        
        Args:
            segments: List of {narration_text, duration_seconds}
            total_duration: Total video duration
        """
        srt_lines = []
        current_time = 0.0
        
        for i, seg in enumerate(segments, 1):
            text = seg.get('narration_text', '')
            duration = seg.get('duration_seconds', 5.0)
            
            start_time = current_time
            end_time = current_time + duration
            
            # Format timestamps
            start_str = self._format_srt_time(start_time)
            end_str = self._format_srt_time(end_time)
            
            srt_lines.append(f"{i}")
            srt_lines.append(f"{start_str} --> {end_str}")
            srt_lines.append(text)
            srt_lines.append("")
            
            current_time = end_time
        
        return "\n".join(srt_lines)
    
    def _format_srt_time(self, seconds: float) -> str:
        """Format seconds to SRT timestamp format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def generate_description(
        self,
        topic: str,
        era: str,
        hook: str,
        tags: List[str] = None
    ) -> str:
        """Generate optimized YouTube description"""
        
        hashtags = '#Shorts #History #India #Hindi #हिंदी'
        if tags:
            hashtags += ' ' + ' '.join([f'#{t.replace(" ", "")}' for t in tags[:10]])
        
        description = f"""{hook}

📚 आज की कहानी: {topic}
🕰️ समय: {era}

─────────────────────────
🔔 Subscribe करें और Bell icon दबाएं!
👍 Like करें अगर आपको पसंद आया
💬 Comment में बताएं आपको कौन सी कहानी चाहिए

─────────────────────────
{hashtags}

© AI-generated historical content for educational purposes
"""
        return description
    
    async def check_quota(self) -> Dict:
        """Check remaining API quota (approximate)"""
        # Note: YouTube API doesn't have a direct quota check endpoint
        # This is informational only
        return {
            'daily_limit': 10000,
            'video_upload_cost': 1600,
            'caption_upload_cost': 200,
            'videos_per_day': 6,
            'videos_with_captions_per_day': 5,
            'note': 'Actual quota usage depends on your Google Cloud project'
        }


# Singleton instance
youtube_uploader = YouTubeUploaderService()
