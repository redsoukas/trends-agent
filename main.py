#!/usr/bin/env python3
"""
AI Trend & Content Factory Agent - Main Entry Point

This script orchestrates the daily content analysis workflow:
1. Fetch trending YouTube data
2. Analyze transcripts
3. Generate AI insights
4. Save to daily_brief.json
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from scouts.youtube_scout import YouTubeScout
from scouts.transcript_scout import TranscriptScout
from brain.agent import ContentAgent


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('trend_agent.log')
        ]
    )
    return logging.getLogger(__name__)


def validate_environment():
    """Validate required environment variables are set."""
    required_vars = ['YOUTUBE_API_KEY', 'OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"Please set these variables before running the agent."
        )


def main():
    """Main execution flow."""
    logger = setup_logging()
    logger.info("🚀 Starting AI Trend & Content Factory Agent")
    
    try:
        # Validate environment
        validate_environment()
        logger.info("✅ Environment validation passed")
        
        # Initialize components
        youtube_scout = YouTubeScout()
        transcript_scout = TranscriptScout()
        content_agent = ContentAgent()
        
        # Step 1: Fetch trending videos
        logger.info("📺 Fetching trending YouTube videos...")
        trending_videos = youtube_scout.get_trending_videos(max_results=10)
        logger.info(f"Found {len(trending_videos)} trending videos")
        
        # Step 2: Get transcripts
        logger.info("📝 Fetching video transcripts...")
        videos_with_transcripts = []
        
        for video in trending_videos:
            try:
                transcript = transcript_scout.get_transcript(video['video_id'])
                if transcript:
                    video['transcript'] = transcript
                    videos_with_transcripts.append(video)
                    logger.info(f"✅ Got transcript for: {video['title'][:50]}...")
            except Exception as e:
                logger.warning(f"⚠️  Failed to get transcript for {video['title'][:50]}: {e}")
                continue
        
        logger.info(f"Got transcripts for {len(videos_with_transcripts)} videos")
        
        # Step 3: Generate AI analysis
        logger.info("🧠 Generating AI content analysis...")
        analysis = content_agent.analyze_trends(videos_with_transcripts)
        
        # Step 4: Prepare final output
        daily_brief = {
            'timestamp': datetime.utcnow().isoformat(),
            'date': datetime.utcnow().strftime('%Y-%m-%d'),
            'summary': {
                'total_videos_analyzed': len(trending_videos),
                'videos_with_transcripts': len(videos_with_transcripts),
                'analysis_generated': analysis is not None
            },
            'trending_videos': trending_videos,
            'videos_with_transcripts': videos_with_transcripts,
            'ai_analysis': analysis
        }
        
        # Step 5: Save results
        output_path = Path('data/daily_brief.json')
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(daily_brief, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved daily brief to {output_path}")
        logger.info("🎉 Agent execution completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent execution failed: {e}")
        raise


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)