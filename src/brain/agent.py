"""
Content Agent - AI-Powered Trend Analysis

This module handles AI-powered analysis of trending content using OpenAI GPT-4.
Generates insights, summaries, and trend predictions from YouTube data.
"""

import os
import json
import logging
import time
from typing import List, Dict, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class ContentAgent:
    """AI-powered content analysis agent using OpenAI GPT-4."""
    
    def __init__(self):
        """Initialize the Content Agent with OpenAI credentials."""
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        if OpenAI is None:
            raise ImportError("openai package is required. Install with: pip install openai")
        
        try:
            self.client = OpenAI(api_key=self.api_key)
            self.logger.info("✅ OpenAI client initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize OpenAI client: {e}")
            raise
        
        # Model configuration
        self.model = "gpt-4o"
        self.max_tokens = 4000
        self.temperature = 0.7
    
    def analyze_metadata_trends(self, videos: List[Dict]) -> Optional[Dict]:
        \"\"\"
        Analyze trends using only video metadata (for videos without transcripts).
        
        Args:
            videos: List of video data dictionaries
            
        Returns:
            Dictionary with metadata-based trend analysis
        \"\"\"
        if not videos:
            self.logger.warning(\"No videos provided for metadata analysis\")
            return None
        
        self.logger.info(f\"🔍 Analyzing metadata trends for {len(videos)} videos\")
        
        try:
            # Prepare metadata for analysis
            metadata = self._prepare_metadata_analysis(videos)
            
            prompt = f\"\"\"
            Analyze YouTube trending patterns using ONLY metadata (no transcripts available):
            
            OVERVIEW:
            • Total Videos: {metadata['total_videos']}
            • Total Views: {metadata['total_views']:,}
            • Average Engagement: {metadata['avg_engagement_rate']:.2f}%
            • Categories: {', '.join(metadata['top_categories'])}
            
            VIDEO TITLES:
            {chr(10).join(f'• {title}' for title in metadata['titles'][:15])}
            
            TOP CHANNELS:
            {chr(10).join(f'• {channel} ({count} videos)' for channel, count in metadata['top_channels'][:10])}
            
            CATEGORIES BREAKDOWN:
            {chr(10).join(f'• {cat}: {count} videos' for cat, count in metadata['category_counts'][:10])}
            
            Based on this metadata, analyze:
            
            1. **CONTENT TRENDS** - What topics/themes are trending based on titles?
            2. **CREATOR PATTERNS** - Which types of channels are dominating?
            3. **AUDIENCE PREFERENCES** - What content formats are popular?
            4. **ENGAGEMENT INSIGHTS** - What drives views and interaction?
            5. **MARKET OPPORTUNITIES** - Gaps or emerging niches to explore?
            
            Provide insights in JSON format with specific, actionable findings.
            Focus on what can be determined from titles, channels, and metadata patterns.
            \"\"\"
            
            response = self._call_openai(prompt, \"Metadata trend analysis\")
            
            if response:
                # Add metadata statistics to the response
                response['metadata_stats'] = {
                    'analysis_method': 'metadata_only',
                    'data_sources': ['titles', 'channels', 'categories', 'engagement_metrics'],
                    'videos_analyzed': len(videos),
                    'top_categories': metadata['top_categories'][:5],
                    'top_channels': dict(metadata['top_channels'][:5]),
                    'avg_views_per_video': metadata['total_views'] // len(videos) if videos else 0
                }
            
            return response
            
        except Exception as e:
            self.logger.error(f\"❌ Failed to generate metadata analysis: {e}\")
            return None
    
    def _prepare_metadata_analysis(self, videos: List[Dict]) -> Dict:
        \"\"\"
        Prepare metadata for analysis.
        
        Args:
            videos: List of video data
            
        Returns:
            Processed metadata dictionary
        \"\"\"
        from collections import Counter
        
        # Basic metrics
        total_views = sum(video.get('view_count', 0) for video in videos)
        total_likes = sum(video.get('like_count', 0) for video in videos)
        
        # Extract and count categories
        categories = [video.get('category_name', 'Unknown') for video in videos]
        category_counts = Counter(categories).most_common()
        
        # Extract and count channels
        channels = [video.get('channel_title', 'Unknown') for video in videos]
        channel_counts = Counter(channels).most_common()
        
        # Extract titles
        titles = [video.get('title', '') for video in videos]
        
        return {
            'total_videos': len(videos),
            'total_views': total_views,
            'total_likes': total_likes,
            'avg_engagement_rate': (total_likes / total_views * 100) if total_views > 0 else 0,
            'titles': titles,
            'top_categories': [cat for cat, _ in category_counts],
            'category_counts': category_counts,
            'top_channels': channel_counts,
            'durations': [video.get('duration_seconds', 0) for video in videos]
        }
    
    def analyze_trends(self, videos_with_transcripts: List[Dict]) -> Optional[Dict]:
        """
        Generate comprehensive AI analysis of trending content.
        
        Args:
            videos_with_transcripts: List of video data with transcript information
            
        Returns:
            Dictionary containing AI analysis and insights
        """
        if not videos_with_transcripts:
            self.logger.warning("⚠️  No videos with transcripts provided for analysis")
            return None
        
        self.logger.info(f"🧠 Analyzing {len(videos_with_transcripts)} videos with AI")
        
        try:
            # Prepare data for analysis
            analysis_data = self._prepare_analysis_data(videos_with_transcripts)
            
            # Generate different types of analysis
            analyses = {}
            
            # 1. Overall trend analysis
            analyses['trend_summary'] = self._analyze_overall_trends(analysis_data)
            
            # 2. Content themes analysis
            analyses['content_themes'] = self._analyze_content_themes(analysis_data)
            
            # 3. Audience engagement insights
            analyses['engagement_insights'] = self._analyze_engagement_patterns(analysis_data)
            
            # 4. Predictions and recommendations
            analyses['predictions'] = self._generate_predictions(analysis_data)
            
            # 5. Individual video insights
            analyses['video_insights'] = self._analyze_individual_videos(videos_with_transcripts[:5])  # Top 5
            
            # Compile final analysis
            final_analysis = {
                'analysis_timestamp': time.time(),
                'videos_analyzed': len(videos_with_transcripts),
                'model_used': self.model,
                'summary': analyses.get('trend_summary', {}),
                'content_themes': analyses.get('content_themes', {}),
                'engagement_insights': analyses.get('engagement_insights', {}),
                'predictions': analyses.get('predictions', {}),
                'top_video_insights': analyses.get('video_insights', [])
            }
            
            self.logger.info("✅ AI analysis completed successfully")
            return final_analysis
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate AI analysis: {e}")
            return None
    
    def _prepare_analysis_data(self, videos: List[Dict]) -> Dict:
        """Prepare video data for AI analysis."""
        total_views = sum(video.get('view_count', 0) for video in videos)
        total_likes = sum(video.get('like_count', 0) for video in videos)
        total_comments = sum(video.get('comment_count', 0) for video in videos)
        
        # Extract key information
        titles = [video.get('title', '') for video in videos]
        channels = [video.get('channel_title', '') for video in videos]
        descriptions = [video.get('description', '')[:500] for video in videos]  # First 500 chars
        transcripts = [video.get('transcript', {}).get('text', '')[:2000] for video in videos]  # First 2000 chars
        
        return {
            'total_videos': len(videos),
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'avg_engagement_rate': (total_likes / total_views * 100) if total_views > 0 else 0,
            'titles': titles,
            'channels': channels,
            'descriptions': descriptions,
            'transcripts': transcripts,
            'categories': [video.get('category_id', '') for video in videos],
            'durations': [video.get('duration_seconds', 0) for video in videos]
        }
    
    def _analyze_overall_trends(self, data: Dict) -> Dict:
        """Generate overall trend analysis."""
        prompt = f"""
        Analyze the following trending YouTube data and provide insights on current content trends:

        Total Videos: {data['total_videos']}
        Total Views: {data['total_views']:,}
        Average Engagement Rate: {data['avg_engagement_rate']:.2f}%

        Video Titles:
        {chr(10).join(f"• {title}" for title in data['titles'][:10])}

        Top Channels:
        {chr(10).join(f"• {channel}" for channel in set(data['channels']))}

        Please provide a comprehensive trend analysis including:
        1. Main content themes and topics
        2. Popular content formats
        3. Audience interests and preferences
        4. Notable patterns in engagement
        5. Current cultural or social trends reflected

        Format as JSON with clear categories.
        """
        
        return self._call_openai(prompt, "Overall trend analysis")
    
    def _analyze_content_themes(self, data: Dict) -> Dict:
        """Analyze content themes and topics."""
        prompt = f"""
        Analyze the content themes from these trending videos:

        Descriptions (first 500 chars each):
        {chr(10).join(f"• {desc}" for desc in data['descriptions'] if desc)}

        Transcripts (excerpts):
        {chr(10).join(f"• {transcript[:500]}..." for transcript in data['transcripts'] if transcript)}

        Identify:
        1. Top 5 content themes/topics
        2. Emotional tone and sentiment
        3. Target audience demographics
        4. Content purpose (entertainment, education, news, etc.)
        5. Recurring keywords and phrases

        Format as JSON with detailed breakdown.
        """
        
        return self._call_openai(prompt, "Content themes analysis")
    
    def _analyze_engagement_patterns(self, data: Dict) -> Dict:
        """Analyze engagement patterns and metrics."""
        avg_duration = sum(data['durations']) / len(data['durations']) if data['durations'] else 0
        
        prompt = f"""
        Analyze engagement patterns from this data:

        Total Videos: {data['total_videos']}
        Total Views: {data['total_views']:,}
        Total Likes: {data['total_likes']:,}
        Total Comments: {data['total_comments']:,}
        Average Duration: {avg_duration:.0f} seconds
        Average Engagement Rate: {data['avg_engagement_rate']:.2f}%

        Video Titles (to understand content types):
        {chr(10).join(data['titles'][:8])}

        Provide insights on:
        1. What drives high engagement
        2. Optimal content duration patterns
        3. Title and thumbnail strategies
        4. Audience behavior patterns
        5. Content timing and release patterns

        Format as JSON with actionable insights.
        """
        
        return self._call_openai(prompt, "Engagement patterns analysis")
    
    def _generate_predictions(self, data: Dict) -> Dict:
        """Generate predictions and recommendations."""
        prompt = f"""
        Based on current trending data, make predictions about future content trends:

        Current Top Themes: {', '.join(set(data['titles']))}
        Current Popular Channels: {', '.join(list(set(data['channels']))[:5])}
        Average Engagement Rate: {data['avg_engagement_rate']:.2f}%

        Predict and recommend:
        1. Emerging content trends (next 30 days)
        2. Content formats likely to gain popularity
        3. Topics/themes to watch
        4. Optimal content strategies for creators
        5. Potential viral content characteristics
        6. Seasonal or event-driven opportunities

        Format as JSON with specific, actionable predictions.
        """
        
        return self._call_openai(prompt, "Predictions and recommendations")
    
    def _analyze_individual_videos(self, videos: List[Dict]) -> List[Dict]:
        """Generate insights for individual top-performing videos."""
        insights = []
        
        for video in videos:
            if not video.get('transcript'):
                continue
            
            prompt = f"""
            Analyze this specific trending video:

            Title: {video.get('title', 'N/A')}
            Channel: {video.get('channel_title', 'N/A')}
            Views: {video.get('view_count', 0):,}
            Likes: {video.get('like_count', 0):,}
            Comments: {video.get('comment_count', 0):,}
            Duration: {video.get('duration', 'N/A')}

            Transcript (first 1000 chars):
            {video.get('transcript', {}).get('text', '')[:1000]}

            Provide specific insights:
            1. Why this content is trending
            2. Key success factors
            3. Target audience appeal
            4. Content structure and style
            5. Viral elements or hooks

            Format as JSON with specific analysis.
            """
            
            analysis = self._call_openai(prompt, f"Individual video analysis: {video.get('title', 'Unknown')[:50]}")
            if analysis:
                insights.append({
                    'video_id': video.get('video_id'),
                    'title': video.get('title'),
                    'analysis': analysis
                })
        
        return insights
    
    def _call_openai(self, prompt: str, analysis_type: str) -> Dict:
        """
        Make a call to OpenAI API with error handling and retries.
        
        Args:
            prompt: The prompt to send to OpenAI
            analysis_type: Type of analysis for logging
            
        Returns:
            Parsed JSON response or empty dict on failure
        """
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"🤖 Generating {analysis_type} (attempt {attempt + 1})")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert content strategist and trend analyst. "
                                     "Provide detailed, actionable insights in valid JSON format. "
                                     "Be specific, data-driven, and focus on practical insights."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                
                # Try to parse as JSON
                try:
                    result = json.loads(content)
                    self.logger.info(f"✅ Successfully generated {analysis_type}")
                    return result
                except json.JSONDecodeError as e:
                    self.logger.warning(f"⚠️  Invalid JSON in OpenAI response for {analysis_type}: {e}")
                    # Return the raw content wrapped in a dict
                    return {"raw_response": content, "error": "Invalid JSON format"}
                
            except Exception as e:
                if "rate_limit" in str(e).lower():
                    if attempt < max_retries - 1:
                        wait_time = base_delay * (2 ** attempt) * 5  # Longer wait for rate limits
                        self.logger.warning(f"⚠️  Rate limited for {analysis_type} (attempt {attempt + 1}). Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    self.logger.warning(f"⚠️  Error in {analysis_type} (attempt {attempt + 1}): {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    self.logger.error(f"❌ Failed to generate {analysis_type} after {max_retries} attempts: {e}")
        
        return {}
    
    def health_check(self) -> Dict:
        """
        Perform a health check of the AI service.
        
        Returns:
            Health status dictionary
        """
        try:
            # Simple test request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Respond with 'healthy'"}],
                max_tokens=10,
                temperature=0
            )
            
            is_healthy = "healthy" in response.choices[0].message.content.lower()
            
            return {
                'service': 'openai',
                'model': self.model,
                'healthy': is_healthy,
                'timestamp': time.time(),
                'api_key_set': bool(self.api_key)
            }
            
        except Exception as e:
            return {
                'service': 'openai',
                'model': self.model,
                'healthy': False,
                'error': str(e),
                'timestamp': time.time(),
                'api_key_set': bool(self.api_key)
            }