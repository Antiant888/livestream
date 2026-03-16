"""
Streamlit Web Application

Main Streamlit application for the Gelonghui news analytics dashboard.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import os
import sys

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.database import DatabaseManager
from scraper.models import NewsItem, Hashtag, Stock

# Configure Streamlit page
st.set_page_config(
    page_title="Gelonghui News Analytics",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .news-item {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: white;
    }
    .hashtag-badge {
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        margin: 0.25rem;
        display: inline-block;
    }
    .stock-badge {
        background-color: #fff3e0;
        color: #f57c00;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        margin: 0.25rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


class NewsDashboard:
    """Main news dashboard class"""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'sqlite:///news_data.db')
        self.db_manager = DatabaseManager(self.db_url)
    
    def render_header(self):
        """Render the main header"""
        st.markdown('<div class="main-header">📰 Gelonghui News Analytics Dashboard</div>', unsafe_allow_html=True)
        
        # Last update info
        latest_ts = self.db_manager.get_latest_timestamp()
        if latest_ts:
            last_update = datetime.fromtimestamp(latest_ts)
            st.caption(f"Last update: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.caption("No data available")
    
    def render_sidebar(self):
        """Render sidebar with filters and controls"""
        st.sidebar.header("📊 Filters & Controls")
        
        # Time range selection
        time_range = st.sidebar.selectbox(
            "Time Range",
            options=['1h', '24h', '7d'],
            index=1,
            help="Select time range for data analysis"
        )
        
        # Category filter (placeholder for future implementation)
        category = st.sidebar.selectbox(
            "Category",
            options=['All', 'Financial', 'Technology', 'International'],
            index=0,
            help="Filter by news category"
        )
        
        # Refresh button
        if st.sidebar.button("🔄 Refresh Data", type="primary"):
            st.rerun()
        
        # Statistics section
        st.sidebar.header("📈 Statistics")
        
        # Get counts
        total_news = self.db_manager.get_news_count(time_range)
        top_hashtags = self.db_manager.get_top_hashtags(time_range, 5)
        top_stocks = self.db_manager.get_stock_mentions(time_range, 5)
        
        st.sidebar.metric("Total News Items", total_news)
        st.sidebar.metric("Top Hashtag", top_hashtags[0]['hashtag'] if top_hashtags else "N/A")
        st.sidebar.metric("Most Mentioned Stock", top_stocks[0]['code'] if top_stocks else "N/A")
        
        return time_range, category
    
    def render_metrics(self, time_range):
        """Render key metrics"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_news = self.db_manager.get_news_count(time_range)
            st.metric("📰 Total News", total_news)
        
        with col2:
            top_hashtags = self.db_manager.get_top_hashtags(time_range, 1)
            top_hashtag = top_hashtags[0]['hashtag'] if top_hashtags else "N/A"
            st.metric("🔥 Top Hashtag", top_hashtag)
        
        with col3:
            top_items = self.db_manager.get_top_engaged_items(time_range, 1)
            avg_engagement = sum(item['engagement_score'] for item in top_items) / len(top_items) if top_items else 0
            st.metric("📊 Avg Engagement", f"{avg_engagement:.1f}")
        
        with col4:
            top_stocks = self.db_manager.get_stock_mentions(time_range, 1)
            stock_mentions = top_stocks[0]['mentions'] if top_stocks else 0
            st.metric("📈 Stock Mentions", stock_mentions)
    
    def render_hashtag_analysis(self, time_range):
        """Render hashtag analysis section"""
        st.header("🔥 Hashtag Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Top hashtags chart
            top_hashtags = self.db_manager.get_top_hashtags(time_range, 10)
            
            if top_hashtags:
                df_hashtags = pd.DataFrame(top_hashtags)
                
                fig = px.bar(
                    df_hashtags,
                    x='frequency',
                    y='hashtag',
                    orientation='h',
                    title=f'Top Hashtags ({time_range})',
                    color='frequency',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hashtag data available for the selected time range")
        
        with col2:
            # Hashtag details
            st.subheader("Hashtag Details")
            top_hashtags = self.db_manager.get_top_hashtags(time_range, 5)
            
            for hashtag in top_hashtags:
                st.markdown(f"""
                <div class="hashtag-badge">
                    #{hashtag['hashtag']} - {hashtag['frequency']} mentions
                </div>
                """, unsafe_allow_html=True)
    
    def render_engagement_analysis(self, time_range):
        """Render engagement analysis section"""
        st.header("📊 Engagement Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top engaged items
            top_items = self.db_manager.get_top_engaged_items(time_range, 10)
            
            if top_items:
                df_items = pd.DataFrame(top_items)
                
                fig = px.bar(
                    df_items,
                    x='engagement_score',
                    y='title',
                    orientation='h',
                    title=f'Top Engaged Items ({time_range})',
                    color='engagement_score',
                    color_continuous_scale='Greens'
                )
                fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No engagement data available")
        
        with col2:
            # Engagement metrics breakdown
            st.subheader("Engagement Breakdown")
            
            # Get sample data for breakdown
            sample_items = self.db_manager.get_top_engaged_items(time_range, 5)
            
            if sample_items:
                for item in sample_items:
                    with st.container():
                        st.markdown(f"**{item['title'][:50]}...**")
                        st.write(f"Reads: {item['read_count']:,} | Likes: {item['like_count']:,} | Shares: {item['share_count']:,}")
                        st.progress(item['engagement_score'] / 100)
                        st.divider()
    
    def render_stock_analysis(self, time_range):
        """Render stock analysis section"""
        st.header("📈 Stock Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Stock mentions chart
            stock_mentions = self.db_manager.get_stock_mentions(time_range, 10)
            
            if stock_mentions:
                df_stocks = pd.DataFrame(stock_mentions)
                
                fig = px.pie(
                    df_stocks,
                    values='mentions',
                    names='code',
                    title=f'Stock Mentions Distribution ({time_range})',
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No stock data available")
        
        with col2:
            # Top mentioned stocks
            st.subheader("Top Mentioned Stocks")
            stock_mentions = self.db_manager.get_stock_mentions(time_range, 8)
            
            for stock in stock_mentions:
                st.markdown(f"""
                <div class="stock-badge">
                    {stock['code']} ({stock['market']}) - {stock['mentions']} mentions
                </div>
                """, unsafe_allow_html=True)
    
    def render_news_feed(self, time_range):
        """Render news feed section"""
        st.header("📰 Latest News Feed")
        
        # Get recent news items
        recent_items = self.db_manager.get_top_engaged_items(time_range, 20)
        
        if not recent_items:
            st.info("No news items available")
            return
        
        # Pagination
        items_per_page = 5
        total_pages = (len(recent_items) + items_per_page - 1) // items_per_page
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            page = st.slider("Page", 1, total_pages, 1, key="news_page")
        
        # Display items for current page
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_items = recent_items[start_idx:end_idx]
        
        for item in page_items:
            with st.container():
                st.markdown(f"""
                <div class="news-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4>{item['title'] or 'No title'}</h4>
                        <span style="color: #666; font-size: 0.9rem;">
                            {datetime.fromtimestamp(item['create_timestamp']).strftime('%Y-%m-%d %H:%M')}
                        </span>
                    </div>
                    <p>{item['content'][:200]}...</p>
                    
                    <div style="display: flex; flex-wrap: wrap; margin-top: 0.5rem;">
                        {"".join([f'<span class="hashtag-badge">#{tag}</span>' for tag in item.get('hashtags', [])[:3]])}
                        {"".join([f'<span class="stock-badge">{stock["code"]} ({stock["market"]})</span>' for stock in item.get('stocks', [])[:3]])}
                    </div>
                    
                    <div style="margin-top: 0.5rem; color: #666; font-size: 0.9rem;">
                        Reads: {item['read_count']:,} | Likes: {item['like_count']:,} | Shares: {item['share_count']:,} | Engagement: {item['engagement_score']:.1f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def render_footer(self):
        """Render footer"""
        st.markdown("---")
        st.caption("© 2024 Gelonghui News Analytics. Data sourced from Gelonghui API.")
    
    def run(self):
        """Run the main dashboard"""
        # Render header
        self.render_header()
        
        # Render sidebar and get filters
        time_range, category = self.render_sidebar()
        
        # Render main content
        self.render_metrics(time_range)
        
        st.markdown("---")
        
        self.render_hashtag_analysis(time_range)
        
        st.markdown("---")
        
        self.render_engagement_analysis(time_range)
        
        st.markdown("---")
        
        self.render_stock_analysis(time_range)
        
        st.markdown("---")
        
        self.render_news_feed(time_range)
        
        self.render_footer()


def create_app():
    """Create and return the Streamlit app"""
    return NewsDashboard()


# Run the app if this file is executed directly
if __name__ == "__main__":
    dashboard = NewsDashboard()
    dashboard.run()