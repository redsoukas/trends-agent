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
        trending_videos_raw = youtube_scout.get_trending_videos(max_results=15)  # Get more to account for filtering
        
        # Filter out music videos (category_id "10")
        trending_videos = []
        music_videos_filtered = 0
        
        for video in trending_videos_raw:
            if video.get('category_id') == '10':  # Music category
                music_videos_filtered += 1
                logger.debug(f"🎵 Filtered music video: {video.get('title', 'Unknown')[:50]}...")
            else:
                trending_videos.append(video)
        
        # Take top 10 after filtering
        trending_videos = trending_videos[:10]
        
        logger.info(f"Found {len(trending_videos)} trending videos (filtered {music_videos_filtered} music videos)")
        
        if len(trending_videos) == 0:
            logger.warning("⚠️ No non-music videos found in trending results")
            return False
        
        # Step 2: Enhanced transcript extraction with filtering
        logger.info("📝 Analyzing videos for transcript potential...")
        
        # Filter videos likely to have transcripts
        high_potential_videos = []
        for video in trending_videos:
            if transcript_scout.has_good_transcript_potential(video):
                high_potential_videos.append(video)
                logger.debug(f"✅ High transcript potential: {video['title'][:50]}...")
            else:
                logger.debug(f"⚠️ Low transcript potential: {video['title'][:50]}...")
        
        logger.info(f"Found {len(high_potential_videos)}/{len(trending_videos)} videos with good transcript potential")
        
        # Get transcripts with enhanced language support
        videos_with_transcripts = []
        videos_without_transcripts = []
        
        for video in high_potential_videos:
            try:
                # Try preferred languages first
                transcript = transcript_scout.get_transcript(video['video_id'])
                
                # If no luck with preferred languages, try any language
                if not transcript:
                    transcript = transcript_scout.get_transcript_any_language(video['video_id'])
                
                if transcript:
                    video['transcript'] = transcript
                    videos_with_transcripts.append(video)
                    logger.info(f"✅ Got transcript ({transcript['language']}): {video['title'][:50]}...")
                else:
                    videos_without_transcripts.append(video)
                    logger.info(f"❌ No transcript available: {video['title'][:50]}...")
                    
            except Exception as e:
                logger.warning(f"⚠️ Error getting transcript for {video['title'][:50]}: {e}")
                videos_without_transcripts.append(video)
                continue
        
        # Include remaining videos for metadata-only analysis
        for video in trending_videos:
            if video not in high_potential_videos:
                videos_without_transcripts.append(video)
        
        logger.info(f"📊 Transcript Results:")
        logger.info(f"  • With transcripts: {len(videos_with_transcripts)} videos")
        logger.info(f"  • Without transcripts: {len(videos_without_transcripts)} videos")
        logger.info(f"  • Success rate: {len(videos_with_transcripts)/len(high_potential_videos)*100:.1f}% (of high-potential videos)")
        
        # Step 3: Enhanced AI analysis with fallback for non-transcript videos
        logger.info("🧠 Generating comprehensive AI analysis...")
        
        # Analyze videos with transcripts
        transcript_analysis = None
        if videos_with_transcripts:
            transcript_analysis = content_agent.analyze_trends(videos_with_transcripts)
        
        # Analyze metadata for all videos
        metadata_analysis = content_agent.analyze_metadata_trends(trending_videos) if hasattr(content_agent, 'analyze_metadata_trends') else None
        
        # Step 4: Prepare comprehensive output
        daily_brief = {
            'timestamp': datetime.utcnow().isoformat(),
            'date': datetime.utcnow().strftime('%Y-%m-%d'),
            'summary': {
                'total_videos_analyzed': len(trending_videos),
                'music_videos_filtered': music_videos_filtered,
                'high_potential_videos': len(high_potential_videos),
                'videos_with_transcripts': len(videos_with_transcripts),
                'videos_without_transcripts': len(videos_without_transcripts),
                'transcript_success_rate': f"{len(videos_with_transcripts)/len(high_potential_videos)*100:.1f}%" if high_potential_videos else "0%",
                'overall_success_rate': f"{len(videos_with_transcripts)/len(trending_videos)*100:.1f}%",
                'analysis_generated': transcript_analysis is not None or metadata_analysis is not None
            },
            'trending_videos': trending_videos,
            'videos_with_transcripts': videos_with_transcripts,
            'videos_without_transcripts': videos_without_transcripts,
            'analysis': {
                'transcript_based': transcript_analysis,
                'metadata_based': metadata_analysis,
                'note': 'Transcript analysis is more detailed, metadata analysis provides broader trends'
            },
            'transcript_insights': {
                'languages_found': list(set([v['transcript']['language'] for v in videos_with_transcripts])),
                'generated_vs_manual': {
                    'generated': len([v for v in videos_with_transcripts if v['transcript'].get('is_generated', False)]),
                    'manual': len([v for v in videos_with_transcripts if not v['transcript'].get('is_generated', True)])
                },
                'average_word_count': sum([v['transcript']['word_count'] for v in videos_with_transcripts]) / len(videos_with_transcripts) if videos_with_transcripts else 0
            }
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