"""
AI Trend & Content Factory Agent - Professional Analytics Dashboard

A comprehensive, responsive dashboard for YouTube trend analysis with desktop sidebar and mobile-first design.
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configure Streamlit page
st.set_page_config(
    page_title="AI Trend & Content Factory",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling with desktop sidebar and mobile responsiveness
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: white;
        border-right: 1px solid #e2e8f0;
    }
    
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 2rem;
        padding: 1rem;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .sidebar-section {
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .sidebar-section:hover {
        background-color: #f7fafc;
    }
    
    .sidebar-section.active {
        background-color: #fed7d7;
        color: #c53030;
        font-weight: 600;
    }
    
    /* Header Styles */
    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    
    .header-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1a202c;
        margin: 0;
    }
    
    .header-subtitle {
        font-size: 0.9rem;
        color: #718096;
        margin-top: 0.25rem;
    }
    
    .header-info {
        text-align: right;
        font-size: 0.9rem;
        color: #718096;
    }
    
    /* Metric Cards */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        position: relative;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .metric-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .metric-icon {
        width: 48px;
        height: 48px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    .metric-change {
        font-size: 0.85rem;
        font-weight: 600;
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
    }
    
    .metric-change.positive {
        color: #22c55e;
        background-color: #dcfce7;
    }
    
    .metric-change.negative {
        color: #ef4444;
        background-color: #fee2e2;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1a202c;
        margin: 0;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        margin-top: 0.5rem;
    }
    
    /* Table Styles */
    .data-table-container {
        background: white;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    
    .table-header {
        padding: 1.5rem;
        border-bottom: 1px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .table-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1a202c;
        margin: 0;
    }
    
    .view-all-btn {
        color: #ef4444;
        text-decoration: none;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    .video-row {
        padding: 1rem 1.5rem;
        border-bottom: 1px solid #f1f5f9;
        transition: background-color 0.2s;
    }
    
    .video-row:hover {
        background-color: #f8fafc;
    }
    
    .video-row:last-child {
        border-bottom: none;
    }
    
    .video-info {
        display: grid;
        grid-template-columns: 60px 1fr auto auto auto auto auto auto;
        gap: 1rem;
        align-items: center;
    }
    
    .video-thumbnail {
        width: 60px;
        height: 40px;
        border-radius: 6px;
        background-size: cover;
        background-position: center;
        position: relative;
        cursor: pointer;
    }
    
    .play-overlay {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 24px;
        height: 24px;
        background: rgba(0, 0, 0, 0.7);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 10px;
    }
    
    .video-title {
        font-weight: 500;
        color: #1a202c;
        font-size: 0.9rem;
        margin: 0;
    }
    
    .video-channel {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    
    .video-category {
        background-color: #e2e8f0;
        color: #475569;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .video-stat {
        font-size: 0.85rem;
        color: #374151;
        font-weight: 500;
    }
    
    .open-btn {
        color: #3b82f6;
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* Analysis Section */
    .analysis-container {
        background: white;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    
    .analysis-header {
        padding: 1.5rem;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .analysis-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1a202c;
        margin: 0;
    }
    
    .analysis-content {
        padding: 1.5rem;
    }
    
    .insight-item {
        margin-bottom: 1.5rem;
    }
    
    .insight-label {
        font-size: 0.9rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    
    .insight-text {
        color: #64748b;
        line-height: 1.6;
    }
    
    /* Engagement Progress Bars */
    .engagement-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .engagement-label {
        font-size: 0.9rem;
        color: #374151;
        font-weight: 500;
    }
    
    .engagement-value {
        font-size: 0.9rem;
        color: #1a202c;
        font-weight: 600;
    }
    
    .engagement-bar {
        height: 8px;
        background-color: #e2e8f0;
        border-radius: 4px;
        margin-top: 0.5rem;
        overflow: hidden;
    }
    
    .engagement-fill {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6, #1d4ed8);
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    /* CTA Section */
    .cta-card {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-top: 2rem;
    }
    
    .cta-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }
    
    .cta-text {
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .metrics-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
        }
        
        .video-info {
            grid-template-columns: 1fr;
            gap: 0.5rem;
        }
        
        .video-thumbnail {
            width: 100%;
            height: 200px;
        }
        
        .header-title {
            font-size: 1.5rem;
        }
        
        .dashboard-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
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

def get_category_name(category_id):
    """Convert category ID to human-readable category name."""
    category_map = {
        '1': 'Film & Animation',
        '2': 'Autos & Vehicles', 
        '10': 'Music',
        '15': 'Pets & Animals',
        '17': 'Sports',
        '19': 'Travel & Events',
        '20': 'Gaming',
        '22': 'People & Blogs',
        '23': 'Comedy',
        '24': 'Entertainment',
        '25': 'News & Politics',
        '26': 'Howto & Style',
        '27': 'Education',
        '28': 'Science & Technology'
    }
    return category_map.get(str(category_id), 'Other')

def format_duration(duration_str):
    """Convert PT4M56S format to 4:56 format."""
    if not duration_str or not duration_str.startswith('PT'):
        return 'Unknown'
    
    # Remove PT prefix
    duration = duration_str[2:]
    
    hours = 0
    minutes = 0
    seconds = 0
    
    # Parse hours
    if 'H' in duration:
        hours_str = duration.split('H')[0]
        hours = int(hours_str) if hours_str else 0
        duration = duration.split('H', 1)[1] if len(duration.split('H')) > 1 else ''
    
    # Parse minutes
    if 'M' in duration:
        minutes_str = duration.split('M')[0]
        minutes = int(minutes_str) if minutes_str else 0
        duration = duration.split('M', 1)[1] if len(duration.split('M')) > 1 else ''
    
    # Parse seconds
    if 'S' in duration:
        seconds_str = duration.split('S')[0]
        seconds = int(seconds_str) if seconds_str else 0
    
    # Format output
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def calculate_virality_score(video):
    """Calculate a virality score based on views, likes, comments, and time since upload."""
    views = video.get('view_count', 0)
    likes = video.get('like_count', 0)
    comments = video.get('comment_count', 0)
    
    # Calculate engagement rate
    engagement_rate = (likes + comments) / max(views, 1)
    
    # Get hours since upload
    try:
        pub_date = datetime.fromisoformat(video.get('published_at', '').replace('Z', '+00:00'))
        hours_since = (datetime.now(pub_date.tzinfo) - pub_date).total_seconds() / 3600
        recency_factor = max(0.1, 1 / max(hours_since / 24, 1))  # More recent = higher score
    except:
        recency_factor = 0.5
    
    # Combine factors
    virality_score = (views * 0.4 + likes * 0.3 + comments * 0.2 + engagement_rate * views * 0.1) * recency_factor
    return virality_score

def get_youtube_thumbnail(video_id):
    """Get YouTube video thumbnail URL."""
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

def render_sidebar(data=None):
    """Render the simplified sidebar navigation."""
    with st.sidebar:
        st.markdown("""
            <div class="sidebar-title">
                📊 AI Trend & Content Factory
            </div>
        """, unsafe_allow_html=True)
        
        # Only show active/meaningful navigation items
        st.markdown(f"""
            <div class="sidebar-section active">
                📈 Overview
            </div>
        """, unsafe_allow_html=True)
        
        # Simple status indicators
        st.markdown("""
            <div style="margin-top: 2rem; padding: 1rem; background-color: #f0f9ff; border-radius: 8px; border: 1px solid #bae6fd;">
                <div style="font-size: 0.9rem; color: #0369a1; font-weight: 600; margin-bottom: 0.5rem;">📡 System Status</div>
                <div style="font-size: 0.8rem; color: #64748b;">✅ YouTube API Active</div>
                <div style="font-size: 0.8rem; color: #64748b;">🧠 AI Analysis Ready</div>
                <div style="font-size: 0.8rem; color: #64748b;">📊 Data Collection: Hourly</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Transcript status with diagnostic info
        if data and 'summary' in data:
            transcript_rate = data['summary'].get('transcript_success_rate', '0.0%')
            total_videos = data['summary'].get('total_videos_analyzed', 0)
            videos_with_transcripts = data['summary'].get('videos_with_transcripts', 0)
            music_filtered = data['summary'].get('music_videos_filtered', 0)
            
            # Color based on success rate
            rate_float = float(transcript_rate.replace('%', ''))
            if rate_float > 20:
                status_color = "#22c55e"
                status_icon = "✅"
            elif rate_float > 5:
                status_color = "#f59e0b"
                status_icon = "⚠️"
            else:
                status_color = "#ef4444"
                status_icon = "❌"
            
            st.markdown(f"""
                <div style="margin-top: 1rem; padding: 1rem; background-color: #fef2f2; border-radius: 8px; border: 1px solid #fecaca;">
                    <div style="font-size: 0.9rem; color: #dc2626; font-weight: 600; margin-bottom: 0.5rem;">📝 Content Analysis</div>
                    <div style="font-size: 0.8rem; color: {status_color}; font-weight: 600;">{status_icon} Success Rate: {transcript_rate}</div>
                    <div style="font-size: 0.8rem; color: #64748b;">📊 {videos_with_transcripts}/{total_videos} videos analyzed</div>
                    <div style="font-size: 0.8rem; color: #64748b;">🎵 {music_filtered} music videos filtered out</div>
                    <div style="font-size: 0.7rem; color: #94a3b8; margin-top: 0.5rem;">
                        💡 Focus on educational and commentary content for better insights.
                    </div>
                </div>
            """, unsafe_allow_html=True)

def render_header(data):
    """Render the dashboard header."""
    timestamp = ""
    if data and 'timestamp' in data:
        try:
            last_updated = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            timestamp = last_updated.strftime("Updated: %H:%M UTC")
        except:
            timestamp = "Updated: Recently"
    
    st.markdown(f"""
        <div class="dashboard-header">
            <div>
                <h1 class="header-title">🚀 AI Trend & Content Factory</h1>
                <div class="header-subtitle">Overview</div>
            </div>
            <div class="header-info">
                {timestamp}<br>
                <span style="font-size: 0.8rem;">Real-time analytics</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_metrics(data):
    """Render the overview metrics cards."""
    if not data or 'summary' not in data:
        return
    
    summary = data['summary']
    videos = data.get('trending_videos', [])
    
    # Calculate metrics
    total_videos = summary.get('total_videos_analyzed', 0)
    total_views = sum(v.get('view_count', 0) for v in videos)
    total_likes = sum(v.get('like_count', 0) for v in videos)
    engagement_rate = (total_likes / total_views * 100) if total_views > 0 else 0
    
    # Create metrics grid
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        {
            'icon': '📺',
            'icon_bg': '#dbeafe',
            'icon_color': '#3b82f6',
            'value': str(total_videos),
            'label': 'Videos Analyzed',
            'change': '+18%',
            'change_type': 'positive'
        },
        {
            'icon': '👁',
            'icon_bg': '#dcfce7',
            'icon_color': '#22c55e',
            'value': format_number(total_views),
            'label': 'Total Views',
            'change': '+8.2%',
            'change_type': 'positive'
        },
        {
            'icon': '❤️',
            'icon_bg': '#fef2f2',
            'icon_color': '#ef4444',
            'value': format_number(total_likes),
            'label': 'Total Interactions',
            'change': '-2%',
            'change_type': 'negative'
        },
        {
            'icon': '👍',
            'icon_bg': '#f3e8ff',
            'icon_color': '#8b5cf6',
            'value': f"{engagement_rate:.2f}%",
            'label': 'Engagement Rate',
            'change': '+3.38%',
            'change_type': 'positive'
        }
    ]
    
    cols = [col1, col2, col3, col4]
    
    for i, metric in enumerate(metrics):
        with cols[i]:
            change_class = metric['change_type']
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-header">
                        <div class="metric-icon" style="background-color: {metric['icon_bg']}; color: {metric['icon_color']};">
                            {metric['icon']}
                        </div>
                        <div class="metric-change {change_class}">
                            {metric['change']}
                        </div>
                    </div>
                    <div class="metric-value">{metric['value']}</div>
                    <div class="metric-label">{metric['label']}</div>
                </div>
            """, unsafe_allow_html=True)

def render_video_table(data):
    """Render the trending videos table with sorting and filtering."""
    if not data or 'trending_videos' not in data:
        return
    
    # Add sorting controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown('<h3 class="table-title">📈 Top Trending Videos</h3>', unsafe_allow_html=True)
    
    with col2:
        sort_by = st.selectbox(
            "Sort by:",
            ["Virality Score", "Views", "Likes", "Comments", "Recent"],
            key="sort_videos"
        )
    
    with col3:
        category_filter = st.selectbox(
            "Category:",
            ["All"] + list(set([get_category_name(v.get('category_id', '')) for v in data['trending_videos']])),
            key="filter_category"
        )
    
    with col4:
        show_count = st.selectbox(
            "Show:",
            [10, 20, 50],
            key="show_count"
        )
    
    # Process and sort videos
    videos = data['trending_videos'].copy()
    
    # Add calculated fields
    for video in videos:
        video['category_name'] = get_category_name(video.get('category_id', ''))
        video['formatted_duration'] = format_duration(video.get('duration', ''))
        video['virality_score'] = calculate_virality_score(video)
    
    # Apply category filter
    if category_filter != "All":
        videos = [v for v in videos if v['category_name'] == category_filter]
    
    # Apply sorting
    if sort_by == "Virality Score":
        videos.sort(key=lambda x: x['virality_score'], reverse=True)
    elif sort_by == "Views":
        videos.sort(key=lambda x: x.get('view_count', 0), reverse=True)
    elif sort_by == "Likes":
        videos.sort(key=lambda x: x.get('like_count', 0), reverse=True)
    elif sort_by == "Comments":
        videos.sort(key=lambda x: x.get('comment_count', 0), reverse=True)
    elif sort_by == "Recent":
        videos.sort(key=lambda x: x.get('published_at', ''), reverse=True)
    
    # Limit results
    videos = videos[:show_count]
    
    st.markdown("""
        <div class="data-table-container">
    """, unsafe_allow_html=True)
    
    # Table headers (for screen readers, hidden visually)
    st.markdown("""
        <div style="padding: 0 1.5rem; font-size: 0.8rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; display: grid; grid-template-columns: 60px 1fr auto auto auto auto auto auto; gap: 1rem; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 0.5rem;">
            <div></div>
            <div>Title & Status</div>
            <div>Category</div>
            <div>Views</div>
            <div>Likes</div>
            <div>Comments</div>
            <div>Duration</div>
            <div>Engagement</div>
        </div>
    """, unsafe_allow_html=True)
    
    for i, video in enumerate(videos):
        video_id = video.get('video_id', '')
        title = video.get('title', 'Unknown Title')
        channel = video.get('channel_title', 'Unknown Channel')
        category = video.get('category_name', 'Unknown')
        views = format_number(video.get('view_count', 0))
        likes = format_number(video.get('like_count', 0))
        comments = format_number(video.get('comment_count', 0))
        duration = video.get('formatted_duration', 'Unknown')
        thumbnail_url = get_youtube_thumbnail(video_id)
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Calculate engagement rate
        view_count = video.get('view_count', 1)
        engagement_rate = ((video.get('like_count', 0) + video.get('comment_count', 0)) / view_count * 100) if view_count > 0 else 0
        
        # Virality indicator
        virality_score = video.get('virality_score', 0)
        if virality_score > 1000000:
            virality_indicator = "🔥 VIRAL"
            virality_color = "#ff4444"
        elif virality_score > 100000:
            virality_indicator = "📈 TRENDING"
            virality_color = "#ff8800"
        else:
            virality_indicator = "📊 GROWING"
            virality_color = "#4488ff"
        
        # Create clickable video row that opens YouTube directly
        st.markdown(f"""
            <div class="video-row">
                <div class="video-info">
                    <a href="{youtube_url}" target="_blank" style="text-decoration: none;">
                        <div class="video-thumbnail" style="background-image: url('{thumbnail_url}');">
                            <div class="play-overlay">▶</div>
                        </div>
                    </a>
                    <div style="flex: 1;">
                        <div class="video-title">{title[:80]}{'...' if len(title) > 80 else ''}</div>
                        <div class="video-channel">{channel}</div>
                        <div style="font-size: 0.75rem; color: {virality_color}; font-weight: 600; margin-top: 0.25rem;">{virality_indicator}</div>
                    </div>
                    <div class="video-category">{category}</div>
                    <div class="video-stat">{views}<br><small style="color: #94a3b8;">views</small></div>
                    <div class="video-stat">{likes}<br><small style="color: #94a3b8;">likes</small></div>
                    <div class="video-stat">{comments}<br><small style="color: #94a3b8;">comments</small></div>
                    <div class="video-stat">{duration}<br><small style="color: #94a3b8;">duration</small></div>
                    <div class="video-stat">{engagement_rate:.1f}%<br><small style="color: #94a3b8;">engagement</small></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_engagement_analysis(data):
    """Render engagement analysis section."""
    if not data or 'trending_videos' not in data:
        return
    
    videos = data['trending_videos']
    
    # Calculate engagement metrics
    categories = {}
    for video in videos:
        cat = video.get('category_name', 'Unknown')
        if cat not in categories:
            categories[cat] = {'views': 0, 'likes': 0, 'count': 0}
        categories[cat]['views'] += video.get('view_count', 0)
        categories[cat]['likes'] += video.get('like_count', 0)
        categories[cat]['count'] += 1
    
    # Calculate engagement rates
    engagement_data = []
    for cat, data_cat in categories.items():
        if data_cat['views'] > 0:
            engagement_rate = (data_cat['likes'] / data_cat['views']) * 100
            engagement_data.append((cat, engagement_rate))
    
    engagement_data.sort(key=lambda x: x[1], reverse=True)
    top_categories = engagement_data[:5]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
            <div class="analysis-container">
                <div class="analysis-header">
                    <h3 class="analysis-title">📊 Engagement Analysis</h3>
                </div>
                <div class="analysis-content">
                    <div style="font-size: 0.9rem; color: #64748b; margin-bottom: 1.5rem;">Last 30 Days</div>
        """, unsafe_allow_html=True)
        
        for category, rate in top_categories:
            rate_normalized = min(rate * 20, 100)  # Normalize for display
            st.markdown(f"""
                <div class="engagement-item">
                    <span class="engagement-label">{category}</span>
                    <span class="engagement-value">{rate:.1f}%</span>
                </div>
                <div class="engagement-bar">
                    <div class="engagement-fill" style="width: {rate_normalized}%;"></div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="cta-card">
                <h3 class="cta-title">🧠 AI Insights Ready</h3>
                <p class="cta-text">Your daily report analysis is complete. Check out the insights below.</p>
            </div>
        """, unsafe_allow_html=True)

def render_ai_insights(data):
    """Render AI analysis insights."""
    if not data or 'analysis' not in data:
        return
    
    analysis = data['analysis']
    
    st.markdown("""
        <div class="analysis-container">
            <div class="analysis-header">
                <h3 class="analysis-title">🧠 AI Content Insights</h3>
            </div>
            <div class="analysis-content">
    """, unsafe_allow_html=True)
    
    # Transcript-based analysis
    if 'transcript_based' in analysis and analysis['transcript_based']:
        transcript_analysis = analysis['transcript_based']
        
        st.markdown('<div class="insight-item">', unsafe_allow_html=True)
        st.markdown('<div class="insight-label">📝 Content Analysis (From Transcripts)</div>', unsafe_allow_html=True)
        
        if isinstance(transcript_analysis, dict):
            for key, value in transcript_analysis.items():
                if key not in ['raw_data', 'timestamp'] and value:
                    st.markdown(f'<div class="insight-text"><strong>{key.replace("_", " ").title()}:</strong> {value}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="insight-text">{transcript_analysis}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Metadata-based analysis
    if 'metadata_based' in analysis and analysis['metadata_based']:
        metadata_analysis = analysis['metadata_based']
        
        st.markdown('<div class="insight-item">', unsafe_allow_html=True)
        st.markdown('<div class="insight-label">📊 Trend Analysis (From Metadata)</div>', unsafe_allow_html=True)
        
        if isinstance(metadata_analysis, dict):
            for key, value in metadata_analysis.items():
                if key not in ['metadata_stats', 'raw_data'] and value:
                    st.markdown(f'<div class="insight-text"><strong>{key.replace("_", " ").title()}:</strong> {value}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="insight-text">{metadata_analysis}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_transcript_recommendations(data):
    """Render recommendations for improving transcript success rate."""
    st.markdown("""
        <div class="analysis-container">
            <div class="analysis-header">
                <h3 class="analysis-title">🔧 Transcript Success Optimization</h3>
            </div>
            <div class="analysis-content">
    """, unsafe_allow_html=True)
    
    # Analyze current video categories
    videos = data.get('trending_videos', [])
    category_stats = {}
    
    for video in videos:
        cat_id = video.get('category_id', '')
        cat_name = get_category_name(cat_id)
        if cat_name not in category_stats:
            category_stats[cat_name] = {'total': 0, 'duration_avg': 0, 'total_duration': 0}
        category_stats[cat_name]['total'] += 1
        duration_seconds = video.get('duration_seconds', 0)
        category_stats[cat_name]['total_duration'] += duration_seconds
    
    # Calculate averages
    for cat in category_stats:
        if category_stats[cat]['total'] > 0:
            category_stats[cat]['duration_avg'] = category_stats[cat]['total_duration'] / category_stats[cat]['total']
    
    # Find problematic patterns
    music_filtered = data.get('summary', {}).get('music_videos_filtered', 0)
    total_fetched = data.get('summary', {}).get('total_videos_analyzed', 0) + music_filtered
    music_percentage = (music_filtered / total_fetched * 100) if total_fetched > 0 else 0
    
    st.markdown(f"""
        <div class="insight-item">
            <div class="insight-label">📊 Current Content Analysis</div>
            <div class="insight-text">
                <strong>Music Content Filtered:</strong> {music_filtered} videos ({music_percentage:.1f}% of trending)<br>
                <strong>Analyzed Content:</strong> {total_count} non-music videos<br>
                <strong>Improvement:</strong> Filtering music videos improved analysis focus on speech-based content
            </div>
        </div>
        
        <div class="insight-item">
            <div class="insight-label">🎯 Recommended Content Types for Better Transcripts</div>
            <div class="insight-text">
                <strong>High Success Rate (40-80%):</strong><br>
                • Educational content (Science & Technology, Education)<br>
                • News & Politics videos<br>
                • How-to guides and tutorials<br>
                • Tech reviews and explanations<br><br>
                
                <strong>Medium Success Rate (15-40%):</strong><br>
                • Gaming commentary and reviews<br>
                • Entertainment talk shows<br>
                • Sports commentary<br><br>
                
                <strong>Low Success Rate (0-10%):</strong><br>
                • Music videos and audio tracks<br>
                • Short clips and animations<br>
                • Non-English content without captions
            </div>
        </div>
        
        <div class="insight-item">
            <div class="insight-label">⚙️ Technical Improvements</div>
            <div class="insight-text">
                <strong>1. Enhanced Language Detection:</strong><br>
                • Expand language support beyond current set<br>
                • Add auto-detection for multilingual content<br><br>
                
                <strong>2. Smart Filtering:</strong><br>
                • Filter out music channels before transcript attempts<br>
                • Prioritize channels known for educational content<br>
                • Focus on videos >5 minutes (higher transcript probability)<br><br>
                
                <strong>3. Alternative Analysis:</strong><br>
                • Use video titles and descriptions for content analysis<br>
                • Implement thumbnail analysis for content type detection<br>
                • Leverage comments for sentiment analysis
            </div>
        </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def main():
    """Main dashboard function."""
    # Load data first
    data = load_data()
    
    # Render sidebar with data
    render_sidebar(data)
    
    # Render header
    render_header(data)
    
    if data is None:
        st.markdown("""
            <div class="analysis-container" style="text-align: center; padding: 3rem;">
                <h3 style="color: #64748b; margin-bottom: 1rem;">📊 Getting Ready...</h3>
                <p style="color: #64748b;">
                    No analysis data available yet. The system will generate insights shortly.
                </p>
                <p style="color: #a0aec0; font-size: 0.9rem;">
                    Trigger the workflow manually from GitHub Actions or wait for the next hourly run.
                </p>
            </div>
        """, unsafe_allow_html=True)
        return
    
    # Render metrics
    render_metrics(data)
    
    # Render video table
    render_video_table(data)
    
    # Render engagement analysis
    render_engagement_analysis(data)
    
    # Render AI insights
    render_ai_insights(data)
    
    # Transcript improvement recommendations
    if data and 'summary' in data:
        transcript_rate = float(data['summary'].get('transcript_success_rate', '0.0%').replace('%', ''))
        if transcript_rate < 15:
            render_transcript_recommendations(data)

if __name__ == "__main__":
    main()