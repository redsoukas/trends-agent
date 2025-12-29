"""
Transcript Scout - YouTube Video Transcript Extraction

This module handles fetching transcripts from YouTube videos with comprehensive
error handling, fallback mechanisms, and robust retry logic.
"""

import logging
import time
import re
from typing import Optional, Dict, List
from urllib.parse import urlparse, parse_qs

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter
    from youtube_transcript_api._errors import (
        TranscriptsDisabled, 
        NoTranscriptFound, 
        VideoUnavailable,
        TooManyRequests,
        YouTubeRequestFailed
    )
except ImportError:
    YouTubeTranscriptApi = None
    TextFormatter = None
    TranscriptsDisabled = Exception
    NoTranscriptFound = Exception
    VideoUnavailable = Exception
    TooManyRequests = Exception
    YouTubeRequestFailed = Exception


class TranscriptScout:
    """Handles YouTube transcript extraction with comprehensive error handling."""
    
    def __init__(self):
        """Initialize the Transcript Scout."""
        self.logger = logging.getLogger(__name__)
        self.formatter = TextFormatter() if TextFormatter else None
        
        if YouTubeTranscriptApi is None:
            self.logger.error("❌ youtube-transcript-api not installed. Transcript functionality disabled.")
            self.enabled = False
        else:
            self.logger.info("✅ Transcript Scout initialized successfully")
            self.enabled = True
    
    def get_transcript(self, video_id: str, language_codes: List[str] = None) -> Optional[Dict]:
        """
        Get transcript for a YouTube video with comprehensive error handling.
        
        Args:
            video_id: YouTube video ID
            language_codes: Preferred language codes (default: ['en', 'en-US'])
            
        Returns:
            Dictionary with transcript data or None if unavailable
        """
        if not self.enabled:
            self.logger.warning("⚠️  Transcript API not available")
            return None
        
        if not video_id:
            self.logger.warning("⚠️  Empty video ID provided")
            return None
        
        # Clean video ID (remove any URL components)
        video_id = self._extract_video_id(video_id)
        if not video_id:
            self.logger.warning("⚠️  Invalid video ID format")
            return None
        
        # Default language preferences
        if language_codes is None:
            language_codes = ['en', 'en-US', 'en-GB', 'en-CA']
        
        self.logger.info(f"🎯 Attempting to fetch transcript for video: {video_id}")
        
        # Retry configuration
        max_retries = 3
        base_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                return self._attempt_transcript_fetch(video_id, language_codes, attempt + 1)
                
            except TooManyRequests as e:
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt) * 2  # Longer wait for rate limits
                    self.logger.warning(f"⚠️  Rate limited (attempt {attempt + 1}/{max_retries}). Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    self.logger.error(f"❌ Rate limit exceeded after {max_retries} attempts for video {video_id}")
                    return None
                    
            except (TranscriptsDisabled, NoTranscriptFound) as e:
                # These are permanent failures, no point in retrying
                self.logger.info(f"ℹ️  No transcript available for video {video_id}: {type(e).__name__}")
                return None
                
            except VideoUnavailable as e:
                self.logger.warning(f"⚠️  Video {video_id} unavailable: {e}")
                return None
                
            except YouTubeRequestFailed as e:
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    self.logger.warning(f"⚠️  YouTube request failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    self.logger.error(f"❌ YouTube request failed after {max_retries} attempts for video {video_id}: {e}")
                    return None
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    self.logger.warning(f"⚠️  Unexpected error (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    self.logger.error(f"❌ Failed to fetch transcript for video {video_id} after {max_retries} attempts: {e}")
                    return None
        
        return None
    
    def _attempt_transcript_fetch(self, video_id: str, language_codes: List[str], attempt_num: int) -> Optional[Dict]:
        """
        Single attempt to fetch transcript with detailed error handling.
        
        Args:
            video_id: YouTube video ID
            language_codes: Preferred language codes
            attempt_num: Current attempt number
            
        Returns:
            Transcript data dictionary or raises exception
        """
        try:
            # First, try to get available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to find transcript in preferred languages
            transcript = None
            found_language = None
            
            # First pass: try exact language matches
            for lang_code in language_codes:
                try:
                    transcript = transcript_list.find_transcript([lang_code])
                    found_language = lang_code
                    break
                except NoTranscriptFound:
                    continue
            
            # Second pass: try generated transcripts if no manual ones found
            if transcript is None:
                try:
                    generated_transcripts = [t for t in transcript_list if t.is_generated]
                    if generated_transcripts:
                        # Prefer English generated transcripts
                        for lang_code in language_codes:
                            for t in generated_transcripts:
                                if t.language_code.startswith(lang_code):
                                    transcript = t
                                    found_language = t.language_code
                                    break
                            if transcript:
                                break
                        
                        # If still no match, use first available generated transcript
                        if transcript is None and generated_transcripts:
                            transcript = generated_transcripts[0]
                            found_language = transcript.language_code
                            
                except Exception as e:
                    self.logger.debug(f"Error accessing generated transcripts: {e}")
            
            # Third pass: try any available transcript
            if transcript is None:
                try:
                    available_transcripts = list(transcript_list)
                    if available_transcripts:
                        transcript = available_transcripts[0]
                        found_language = transcript.language_code
                        self.logger.info(f"ℹ️  Using fallback language '{found_language}' for video {video_id}")
                except Exception as e:
                    self.logger.debug(f"Error accessing fallback transcripts: {e}")
            
            if transcript is None:
                raise NoTranscriptFound(f"No transcripts found for video {video_id}")
            
            # Fetch the actual transcript data
            transcript_data = transcript.fetch()
            
            if not transcript_data:
                self.logger.warning(f"⚠️  Empty transcript data for video {video_id}")
                return None
            
            # Format and process the transcript
            formatted_text = self._format_transcript(transcript_data)
            
            result = {
                'video_id': video_id,
                'language': found_language,
                'is_generated': getattr(transcript, 'is_generated', False),
                'is_translatable': getattr(transcript, 'is_translatable', False),
                'text': formatted_text,
                'raw_data': transcript_data[:100],  # Keep first 100 entries for debugging
                'word_count': len(formatted_text.split()) if formatted_text else 0,
                'duration_covered': self._calculate_duration_covered(transcript_data),
                'fetch_timestamp': time.time()
            }
            
            self.logger.info(f"✅ Successfully fetched transcript for video {video_id} "
                           f"(language: {found_language}, {result['word_count']} words)")
            
            return result
            
        except Exception as e:
            # Re-raise to be handled by the retry logic
            raise
    
    def _extract_video_id(self, video_input: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats or return if already an ID.
        
        Args:
            video_input: YouTube URL or video ID
            
        Returns:
            Clean video ID or None if invalid
        """
        if not video_input:
            return None
        
        # If it's already a video ID (11 characters, alphanumeric + underscore + hyphen)
        if len(video_input) == 11 and re.match(r'^[a-zA-Z0-9_-]+$', video_input):
            return video_input
        
        # Extract from various YouTube URL formats
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, video_input)
            if match:
                return match.group(1)
        
        # Try parsing as URL
        try:
            parsed = urlparse(video_input)
            if parsed.hostname in ['youtube.com', 'www.youtube.com']:
                query_params = parse_qs(parsed.query)
                if 'v' in query_params:
                    video_id = query_params['v'][0]
                    if len(video_id) == 11:
                        return video_id
            elif parsed.hostname in ['youtu.be']:
                video_id = parsed.path.lstrip('/')
                if len(video_id) == 11:
                    return video_id
        except Exception:
            pass
        
        return None
    
    def _format_transcript(self, transcript_data: List[Dict]) -> str:
        """
        Format raw transcript data into readable text.
        
        Args:
            transcript_data: Raw transcript entries from API
            
        Returns:
            Formatted transcript text
        """
        if not transcript_data:
            return ""
        
        try:
            if self.formatter:
                return self.formatter.format_transcript(transcript_data)
            else:
                # Fallback formatting
                formatted_parts = []
                for entry in transcript_data:
                    text = entry.get('text', '').strip()
                    if text:
                        # Clean up common transcript artifacts
                        text = re.sub(r'\[.*?\]', '', text)  # Remove [Music], [Applause], etc.
                        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
                        formatted_parts.append(text)
                
                return ' '.join(formatted_parts)
                
        except Exception as e:
            self.logger.warning(f"⚠️  Error formatting transcript: {e}")
            # Emergency fallback
            return ' '.join([entry.get('text', '') for entry in transcript_data if entry.get('text')])
    
    def _calculate_duration_covered(self, transcript_data: List[Dict]) -> float:
        """
        Calculate the duration covered by the transcript.
        
        Args:
            transcript_data: Raw transcript entries
            
        Returns:
            Duration in seconds
        """
        if not transcript_data:
            return 0.0
        
        try:
            start_time = transcript_data[0].get('start', 0)
            last_entry = transcript_data[-1]
            end_time = last_entry.get('start', 0) + last_entry.get('duration', 0)
            return max(0, end_time - start_time)
        except Exception:
            return 0.0
    
    def get_transcript_languages(self, video_id: str) -> List[Dict]:
        """
        Get available transcript languages for a video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List of available language info
        """
        if not self.enabled:
            return []
        
        video_id = self._extract_video_id(video_id)
        if not video_id:
            return []
        
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            languages = []
            
            for transcript in transcript_list:
                languages.append({
                    'language': transcript.language,
                    'language_code': transcript.language_code,
                    'is_generated': getattr(transcript, 'is_generated', False),
                    'is_translatable': getattr(transcript, 'is_translatable', False)
                })
            
            return languages
            
        except Exception as e:
            self.logger.warning(f"⚠️  Could not get transcript languages for video {video_id}: {e}")
            return []
    
    def health_check(self) -> Dict:
        """
        Perform a health check of the transcript service.
        
        Returns:
            Health status dictionary
        """
        return {
            'enabled': self.enabled,
            'api_available': YouTubeTranscriptApi is not None,
            'formatter_available': self.formatter is not None,
            'timestamp': time.time()
        }