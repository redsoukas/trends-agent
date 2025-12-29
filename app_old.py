"""
AI Trend & Content Factory Agent - Modern Streamlit Dashboard

A sleek, mobile-responsive dashboard for YouTube trend analysis.
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configure Streamlit page for mobile-first design
st.set_page_config(
    page_title="AI Trend & Content Factory",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }
    
    /* Header Styles */
    .modern-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        text-align: center;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.9);
        text-align: center;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Overview Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    .metric-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2d3748;
        margin: 0;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #718096;
        margin-top: 0.5rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Section Headers */
    .section-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 2rem 0 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Video Cards */
    .video-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
        margin-bottom: 1rem;
    }
    
    .video-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
    }
    
    .video-thumbnail {
        position: relative;
        width: 100%;
        height: 180px;
        background: linear-gradient(45deg, #667eea, #764ba2);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    
    .play-button {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 60px;
        height: 60px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        color: #667eea;
        transition: transform 0.3s ease;
    }
    
    .video-card:hover .play-button {
        transform: translate(-50%, -50%) scale(1.1);
    }
    
    .video-content {
        padding: 1.5rem;
    }
    
    .video-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2d3748;
        margin: 0 0 0.5rem 0;
        line-height: 1.3;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    .video-channel {
        font-size: 0.9rem;
        color: #718096;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    .video-stats {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.85rem;
        color: #718096;
    }
    
    .stat-item {
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    
    /* Analysis Section */
    .analysis-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 1.5rem;
    }
    
    .analysis-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2d3748;
        margin: 0 0 1rem 0;
    }
    
    .analysis-text {
        color: #4a5568;
        line-height: 1.6;
        font-size: 1rem;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .header-title {
            font-size: 2rem;
        }
        
        .metric-number {
            font-size: 2rem;
        }
        
        .video-thumbnail {
            height: 200px;
        }
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

def load_data():
    """Load the latest trend analysis data."""
    try:
        data_file = Path("data/daily_brief.json")
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        else:
            return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def format_number(num):
    """Format large numbers for display."""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(num)

def get_youtube_thumbnail(video_id):
    """Get YouTube video thumbnail URL."""
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

def render_header():
    """Render the modern header."""
    st.markdown("""
        <div class="modern-header">
            <h1 class="header-title">🚀 AI Trend & Content Factory</h1>
            <p class="header-subtitle">Real-time YouTube trend analysis powered by AI</p>
        </div>
    """, unsafe_allow_html=True)

def render_overview(data):
    """Render the overview metrics section."""
    if not data or 'summary' not in data:
        return
    
    summary = data['summary']
    
    # Calculate metrics
    total_videos = summary.get('total_videos_analyzed', 0)
    transcripts = summary.get('videos_with_transcripts', 0)
    success_rate = summary.get('transcript_success_rate', '0%')
    
    # Calculate total views from videos
    total_views = 0
    if 'trending_videos' in data:
        for video in data['trending_videos']:
            total_views += video.get('view_count', 0)
    
    # Get last updated time
    timestamp = data.get('timestamp', '')
    if timestamp:
        try:
            last_updated = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = last_updated.strftime("%H:%M UTC")
        except:
            time_str = "Recently"
    else:
        time_str = "Recently"
    
    st.markdown(f"""
        <div style="text-align: right; color: rgba(255, 255, 255, 0.8); margin-bottom: 1rem; font-size: 0.9rem;">
            Updated: {time_str}
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{total_videos}</div>
                <div class="metric-label">Videos Analyzed</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{format_number(total_views)}</div>
                <div class="metric-label">Total Views</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{transcripts}</div>
                <div class="metric-label">With Transcripts</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{success_rate.replace('%', '')}<span style="font-size: 1.5rem;">%</span></div>
                <div class="metric-label">Success Rate</div>
            </div>
        """, unsafe_allow_html=True)

def render_video_card(video, index):
    """Render a single video card with preview functionality."""
    video_id = video.get('video_id', '')
    title = video.get('title', 'Unknown Title')
    channel = video.get('channel_title', 'Unknown Channel')
    views = format_number(video.get('view_count', 0))
    likes = format_number(video.get('like_count', 0))
    duration = video.get('duration', 'Unknown')
    
    # Create video card with click to watch
    if st.button(f"▶ {title[:50]}{'...' if len(title) > 50 else ''}", 
                key=f"video_{index}_{video_id}", 
                help=f"Click to watch on YouTube"):
        # Open video in new tab
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        st.markdown(f'<meta http-equiv="refresh" content="0; url={youtube_url}">', 
                   unsafe_allow_html=True)
    
    # Display video info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**{channel}**")
    with col2:
        st.markdown(f"👁 {views}")
    with col3:
        st.markdown(f"👍 {likes}")

def render_trending_videos(data):
    """Render the trending videos section."""
    if not data or 'trending_videos' not in data:
        return
    
    st.markdown("""
        <div class="section-header">
            <h2 class="section-title">🎬 Top Trending Videos</h2>
        </div>
    """, unsafe_allow_html=True)
    
    videos = data['trending_videos'][:10]  # Show top 10 videos
    
    for i, video in enumerate(videos):
        with st.container():
            st.markdown(f"""
                <div class="video-card">
                    <div class="video-thumbnail" style="background-image: url('{get_youtube_thumbnail(video.get('video_id', ''))}'); background-size: cover; background-position: center;">
                        <div class="play-button">▶</div>
                    </div>
                    <div class="video-content">
                        <div class="video-title">{video.get('title', 'Unknown Title')[:80]}{'...' if len(video.get('title', '')) > 80 else ''}</div>
                        <div class="video-channel">{video.get('channel_title', 'Unknown Channel')}</div>
                        <div class="video-stats">
                            <div class="stat-item">
                                <span>👁</span>
                                <span>{format_number(video.get('view_count', 0))}</span>
                            </div>
                            <div class="stat-item">
                                <span>👍</span>
                                <span>{format_number(video.get('like_count', 0))}</span>
                            </div>
                            <div class="stat-item">
                                <span>⏱</span>
                                <span>{video.get('duration', 'Unknown')}</span>
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Button to watch video
            if st.button(f"🎬 Watch Video", key=f"watch_{i}", help="Open in YouTube"):
                youtube_url = f"https://www.youtube.com/watch?v={video.get('video_id', '')}"
                st.markdown(f'[🚀 Open in YouTube]({youtube_url})', unsafe_allow_html=True)
                st.info(f"Video: {video.get('title', 'Unknown')}")
            
            st.markdown("---")

def render_ai_insights(data):
    """Render AI analysis insights."""
    if not data or 'analysis' not in data:
        return
    
    st.markdown("""
        <div class="section-header">
            <h2 class="section-title">🧠 AI Insights</h2>
        </div>
    """, unsafe_allow_html=True)
    
    analysis = data['analysis']
    
    # Transcript-based analysis
    if 'transcript_based' in analysis and analysis['transcript_based']:
        transcript_analysis = analysis['transcript_based']
        
        st.markdown("""
            <div class="analysis-card">
                <h3 class="analysis-title">📝 Content Analysis (From Transcripts)</h3>
                <div class="analysis-text">
        """, unsafe_allow_html=True)
        
        if isinstance(transcript_analysis, dict):
            for key, value in transcript_analysis.items():
                if key not in ['raw_data', 'timestamp']:
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
        else:
            st.markdown(str(transcript_analysis))
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Metadata-based analysis  
    if 'metadata_based' in analysis and analysis['metadata_based']:
        metadata_analysis = analysis['metadata_based']
        
        st.markdown("""
            <div class="analysis-card">
                <h3 class="analysis-title">📊 Trend Analysis (From Metadata)</h3>
                <div class="analysis-text">
        """, unsafe_allow_html=True)
        
        if isinstance(metadata_analysis, dict):
            for key, value in metadata_analysis.items():
                if key not in ['metadata_stats', 'raw_data']:
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
        else:
            st.markdown(str(metadata_analysis))
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def main():
    """Main dashboard function."""
    # Render header
    render_header()
    
    # Load data
    data = load_data()
    
    if data is None:
        st.markdown("""
            <div class="analysis-card" style="text-align: center;">
                <h3 style="color: #718096;">📊 Getting Ready...</h3>
                <p style="color: #718096;">
                    No analysis data available yet. The system will generate insights shortly.
                </p>
                <p style="color: #a0aec0; font-size: 0.9rem;">
                    Check back in a few minutes, or trigger the workflow manually from GitHub Actions.
                </p>
            </div>
        """, unsafe_allow_html=True)
        return
    
    # Render overview
    render_overview(data)
    
    # Render trending videos
    render_trending_videos(data)
    
    # Render AI insights
    render_ai_insights(data)
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()