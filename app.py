"""
AI Trend & Content Factory Agent - Streamlit Dashboard

This is the main dashboard that displays the daily trend analysis results.
Must be at root level for Streamlit Cloud compatibility.
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
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1e3d59;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ff6b6b;
    }
    .trend-insight {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .video-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_daily_brief():
    """Load the daily brief JSON file."""
    data_path = Path("data/daily_brief.json")
    
    if not data_path.exists():
        return None
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


def format_number(number):
    """Format large numbers for display."""
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)


def display_overview_metrics(data):
    """Display overview metrics in the dashboard."""
    if not data:
        st.warning("No data available")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    summary = data.get('summary', {})
    videos = data.get('trending_videos', [])
    
    # Calculate metrics
    total_views = sum(v.get('view_count', 0) for v in videos)
    total_likes = sum(v.get('like_count', 0) for v in videos)
    avg_engagement = (total_likes / total_views * 100) if total_views > 0 else 0
    
    with col1:
        st.metric(
            "📺 Videos Analyzed", 
            summary.get('total_videos_analyzed', 0)
        )
    
    with col2:
        st.metric(
            "👀 Total Views", 
            format_number(total_views)
        )
    
    with col3:
        st.metric(
            "❤️ Total Likes", 
            format_number(total_likes)
        )
    
    with col4:
        st.metric(
            "📊 Avg Engagement", 
            f"{avg_engagement:.2f}%"
        )


def display_trending_videos(videos):
    """Display trending videos table."""
    if not videos:
        st.warning("No trending videos data available")
        return
    
    # Prepare data for display
    video_data = []
    for video in videos[:15]:  # Show top 15
        video_data.append({
            'Title': video.get('title', 'N/A')[:60] + ('...' if len(video.get('title', '')) > 60 else ''),
            'Channel': video.get('channel_title', 'N/A'),
            'Views': format_number(video.get('view_count', 0)),
            'Likes': format_number(video.get('like_count', 0)),
            'Duration': video.get('duration', 'N/A'),
            'URL': f"https://youtube.com/watch?v={video.get('video_id', '')}"
        })
    
    df = pd.DataFrame(video_data)
    
    # Display as interactive table
    st.subheader("📈 Top Trending Videos")
    
    # Add clickable links
    df_display = df.copy()
    df_display['Link'] = df['URL'].apply(lambda x: f'[▶️ Watch]({x})')
    df_display = df_display.drop('URL', axis=1)
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Link": st.column_config.LinkColumn("Link", width="small")
        }
    )


def display_engagement_chart(videos):
    """Display engagement analysis chart."""
    if not videos:
        return
    
    # Prepare data for visualization
    chart_data = []
    for video in videos[:10]:  # Top 10 for chart clarity
        views = video.get('view_count', 0)
        likes = video.get('like_count', 0)
        engagement_rate = (likes / views * 100) if views > 0 else 0
        
        chart_data.append({
            'Video': video.get('title', 'Unknown')[:30] + '...',
            'Views': views,
            'Likes': likes,
            'Engagement Rate': engagement_rate
        })
    
    df = pd.DataFrame(chart_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Views vs Engagement Rate scatter plot
        fig = px.scatter(
            df, 
            x='Views', 
            y='Engagement Rate',
            hover_data=['Video', 'Likes'],
            title="Views vs Engagement Rate",
            labels={'Engagement Rate': 'Engagement Rate (%)'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top videos by engagement rate
        df_sorted = df.nlargest(8, 'Engagement Rate')
        fig = px.bar(
            df_sorted,
            x='Engagement Rate',
            y='Video',
            orientation='h',
            title="Highest Engagement Videos",
            labels={'Engagement Rate': 'Engagement Rate (%)'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


def display_ai_analysis(analysis):
    """Display AI-generated analysis insights."""
    if not analysis:
        st.warning("No AI analysis available")
        return
    
    st.subheader("🧠 AI Analysis & Insights")
    
    # Create tabs for different analysis sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "🎯 Content Themes", 
        "💡 Predictions", 
        "🎬 Top Videos"
    ])
    
    with tab1:
        # Overall summary
        summary = analysis.get('summary', {})
        if summary:
            st.markdown("### 📈 Trend Summary")
            
            # Display key insights
            for key, value in summary.items():
                if isinstance(value, (str, int, float)):
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
                elif isinstance(value, list):
                    st.markdown(f"**{key.replace('_', ' ').title()}:**")
                    for item in value[:5]:  # Show top 5
                        st.markdown(f"• {item}")
        
        # Engagement insights
        engagement = analysis.get('engagement_insights', {})
        if engagement:
            st.markdown("### 🎯 Engagement Insights")
            for key, value in engagement.items():
                if isinstance(value, (str, int, float)):
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
    
    with tab2:
        # Content themes
        themes = analysis.get('content_themes', {})
        if themes:
            st.markdown("### 🎨 Content Themes & Topics")
            
            for key, value in themes.items():
                if isinstance(value, list):
                    st.markdown(f"**{key.replace('_', ' ').title()}:**")
                    for item in value:
                        st.markdown(f"• {item}")
                elif isinstance(value, (str, int, float)):
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
        else:
            st.info("Content theme analysis not available")
    
    with tab3:
        # Predictions
        predictions = analysis.get('predictions', {})
        if predictions:
            st.markdown("### 🔮 Future Predictions & Recommendations")
            
            for key, value in predictions.items():
                if isinstance(value, list):
                    st.markdown(f"**{key.replace('_', ' ').title()}:**")
                    for item in value:
                        st.markdown(f"• {item}")
                elif isinstance(value, (str, int, float)):
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
        else:
            st.info("Predictions not available")
    
    with tab4:
        # Individual video insights
        video_insights = analysis.get('top_video_insights', [])
        if video_insights:
            st.markdown("### 🎬 Top Video Analysis")
            
            for insight in video_insights:
                with st.expander(f"🎥 {insight.get('title', 'Unknown Video')[:60]}..."):
                    analysis_data = insight.get('analysis', {})
                    for key, value in analysis_data.items():
                        if isinstance(value, list):
                            st.markdown(f"**{key.replace('_', ' ').title()}:**")
                            for item in value:
                                st.markdown(f"• {item}")
                        elif isinstance(value, (str, int, float)):
                            st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
        else:
            st.info("Individual video insights not available")


def display_sidebar_info(data):
    """Display information in the sidebar."""
    st.sidebar.header("📊 Dashboard Info")
    
    if data:
        timestamp = data.get('timestamp')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                st.sidebar.info(f"**Last Updated:** {dt.strftime('%Y-%m-%d %H:%M UTC')}")
            except:
                st.sidebar.info(f"**Last Updated:** {timestamp}")
        
        st.sidebar.info(f"**Analysis Date:** {data.get('date', 'Unknown')}")
        
        # Summary stats
        summary = data.get('summary', {})
        if summary:
            st.sidebar.subheader("📈 Quick Stats")
            st.sidebar.metric("Videos Analyzed", summary.get('total_videos_analyzed', 0))
            st.sidebar.metric("With Transcripts", summary.get('videos_with_transcripts', 0))
            
            if summary.get('analysis_generated'):
                st.sidebar.success("✅ AI Analysis Complete")
            else:
                st.sidebar.warning("⚠️ AI Analysis Incomplete")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 📖 About
    This dashboard displays daily YouTube trend analysis powered by AI.
    
    **Data Sources:**
    - YouTube Data API v3
    - YouTube Transcript API
    - OpenAI GPT-4
    
    **Updates:** Daily at 08:00 UTC
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("🤖 **Powered by AI Trend Agent**")


def main():
    """Main Streamlit app."""
    # Header
    st.markdown('<h1 class="main-header">📈 AI Trend & Content Factory</h1>', unsafe_allow_html=True)
    st.markdown("*Daily YouTube trend analysis powered by artificial intelligence*")
    
    # Load data
    data = load_daily_brief()
    
    if data is None:
        st.error("""
        🚫 **No data available**
        
        The daily analysis hasn't run yet or there was an error loading the data.
        Please check back later or contact the administrator.
        """)
        st.stop()
    
    # Display sidebar
    display_sidebar_info(data)
    
    # Main content
    st.markdown("---")
    
    # Overview metrics
    display_overview_metrics(data)
    
    st.markdown("---")
    
    # Trending videos and charts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_trending_videos(data.get('trending_videos', []))
    
    with col2:
        # Mini stats
        videos_with_transcripts = data.get('videos_with_transcripts', [])
        if videos_with_transcripts:
            st.subheader("📝 Transcript Coverage")
            total_videos = len(data.get('trending_videos', []))
            transcript_count = len(videos_with_transcripts)
            coverage = (transcript_count / total_videos * 100) if total_videos > 0 else 0
            
            st.metric("Coverage", f"{coverage:.1f}%")
            st.progress(coverage / 100)
            
            # Average word count
            word_counts = [v.get('transcript', {}).get('word_count', 0) for v in videos_with_transcripts]
            avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
            st.metric("Avg Words/Video", f"{avg_words:.0f}")
    
    st.markdown("---")
    
    # Engagement analysis
    if data.get('trending_videos'):
        st.subheader("📊 Engagement Analysis")
        display_engagement_chart(data.get('trending_videos', []))
    
    st.markdown("---")
    
    # AI Analysis
    ai_analysis = data.get('ai_analysis')
    if ai_analysis:
        display_ai_analysis(ai_analysis)
    else:
        st.info("🤖 AI analysis will be available after the next update cycle")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>🤖 Generated by AI Trend & Content Factory Agent | 
        📊 Data refreshed daily | 
        ⭐ Powered by OpenAI GPT-4</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()