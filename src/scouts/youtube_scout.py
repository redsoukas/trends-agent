"""
YouTube Scout - Trending Video Data Collection

This module handles fetching trending videos from YouTube Data API v3.
Includes comprehensive error handling and rate limiting.
"""

import os
import time
import logging
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class YouTubeScout:
    """Handles YouTube API interactions for trending video data."""
    
    def __init__(self):
        """Initialize the YouTube Scout with API credentials."""
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable is required")
        
        try:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
            self.logger.info("✅ YouTube API client initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize YouTube API client: {e}")
            raise
    
    def get_trending_videos(self, 
                          region_code: str = 'US',
                          category_id: str = '0', 
                          max_results: int = 25) -> List[Dict]:
        """
        Fetch trending videos from YouTube.
        
        Args:
            region_code: Country code for trending videos (default: US)
            category_id: Video category ID (0 = all categories)
            max_results: Maximum number of videos to fetch (1-50)
            
        Returns:
            List of video data dictionaries
            
        Raises:
            Exception: If API request fails after retries
        """
        max_results = min(max(1, max_results), 50)  # Clamp to valid range
        
        self.logger.info(f"Fetching {max_results} trending videos for region {region_code}")
        
        request_params = {
            'part': 'id,snippet,statistics,contentDetails',
            'chart': 'mostPopular',
            'regionCode': region_code,
            'maxResults': max_results,
            'videoCategoryId': category_id
        }
        
        # Retry logic for API calls
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                response = self.youtube.videos().list(**request_params).execute()
                
                videos = []
                for item in response.get('items', []):
                    video_data = self._extract_video_data(item)
                    if video_data:
                        videos.append(video_data)
                
                self.logger.info(f"✅ Successfully fetched {len(videos)} trending videos")
                return videos
                
            except HttpError as e:
                error_code = e.resp.status
                error_reason = e.error_details[0].get('reason', 'Unknown') if e.error_details else 'Unknown'
                
                if error_code == 403:
                    if 'quotaExceeded' in str(e) or 'dailyLimitExceeded' in str(e):
                        self.logger.error("❌ YouTube API quota exceeded")
                        raise Exception("YouTube API quota exceeded. Please try again tomorrow.")
                    elif 'keyInvalid' in str(e):
                        self.logger.error("❌ Invalid YouTube API key")
                        raise Exception("Invalid YouTube API key. Please check your credentials.")
                
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(f"⚠️  YouTube API error (attempt {attempt + 1}/{max_retries}): {error_reason}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    self.logger.error(f"❌ YouTube API request failed after {max_retries} attempts: {e}")
                    raise Exception(f"YouTube API error: {error_reason}")
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    self.logger.warning(f"⚠️  Unexpected error (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    self.logger.error(f"❌ Failed to fetch trending videos after {max_retries} attempts: {e}")
                    raise
    
    def _extract_video_data(self, item: Dict) -> Optional[Dict]:
        """
        Extract relevant data from YouTube API response item.
        
        Args:
            item: YouTube API response item
            
        Returns:
            Cleaned video data dictionary or None if extraction fails
        """
        try:
            snippet = item.get('snippet', {})
            statistics = item.get('statistics', {})
            content_details = item.get('contentDetails', {})
            
            # Skip private or deleted videos
            if not snippet.get('title') or snippet.get('title') == 'Private video':
                return None
            
            # Extract duration (convert from ISO 8601 format)
            duration = content_details.get('duration', '')
            duration_seconds = self._parse_duration(duration)
            
            video_data = {
                'video_id': item['id'],
                'title': snippet.get('title', ''),
                'description': snippet.get('description', '')[:1000],  # Truncate long descriptions
                'channel_title': snippet.get('channelTitle', ''),
                'channel_id': snippet.get('channelId', ''),
                'published_at': snippet.get('publishedAt', ''),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'duration': duration,
                'duration_seconds': duration_seconds,
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'category_id': snippet.get('categoryId', ''),
                'tags': snippet.get('tags', [])[:10],  # Limit to first 10 tags
                'url': f"https://www.youtube.com/watch?v={item['id']}"
            }
            
            return video_data
            
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to extract data for video {item.get('id', 'unknown')}: {e}")
            return None
    
    def _parse_duration(self, duration: str) -> int:
        """
        Parse YouTube duration from ISO 8601 format (PT4M13S) to seconds.
        
        Args:
            duration: ISO 8601 duration string
            
        Returns:
            Duration in seconds
        """
        if not duration or not duration.startswith('PT'):
            return 0
        
        try:
            # Remove PT prefix
            duration = duration[2:]
            
            hours = 0
            minutes = 0
            seconds = 0
            
            # Parse hours
            if 'H' in duration:
                hours = int(duration.split('H')[0])
                duration = duration.split('H')[1]
            
            # Parse minutes
            if 'M' in duration:
                minutes = int(duration.split('M')[0])
                duration = duration.split('M')[1]
            
            # Parse seconds
            if 'S' in duration:
                seconds = int(duration.split('S')[0])
            
            return hours * 3600 + minutes * 60 + seconds
            
        except Exception:
            return 0
    
    def get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """
        Get detailed information for specific videos.
        
        Args:
            video_ids: List of YouTube video IDs
            
        Returns:
            List of detailed video data
        """
        if not video_ids:
            return []
        
        # YouTube API allows up to 50 video IDs per request
        video_ids = video_ids[:50]
        
        try:
            response = self.youtube.videos().list(
                part='id,snippet,statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            videos = []
            for item in response.get('items', []):
                video_data = self._extract_video_data(item)
                if video_data:
                    videos.append(video_data)
            
            self.logger.info(f"✅ Successfully fetched details for {len(videos)} videos")
            return videos
            
        except Exception as e:
            self.logger.error(f"❌ Failed to fetch video details: {e}")
            return []