"""
AI Data Insight Engine - Streamlit Frontend
"""
import streamlit as st
import requests
import os

# Page config
st.set_page_config(
    page_title="AI Data Insight Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get API URL from environment
API_URL = os.getenv("API_URL", "http://localhost:8000")

def check_api_health():
    """Check if backend API is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main application"""
    
    # Header
    st.title("📊 AI Data Insight Engine")
    st.markdown("Transform raw business data into actionable insights automatically")
    
    # Sidebar
    with st.sidebar:
        st.header("🚀 Quick Start")
        st.markdown("""
        1. **Upload** your CSV/Excel file
        2. **Wait** for AI to analyze (1-2 min)
        3. **View** insights and charts
        4. **Download** PDF report
        """)
        
        st.divider()
        
        # API Status
        if check_api_health():
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")
            st.info(f"Make sure backend is running at {API_URL}")
    
    # Main content
    st.header("Welcome! 👋")
    
    # Status info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", "🚧 In Development")
    
    with col2:
        st.metric("Version", "1.0.0 MVP")
    
    with col3:
        st.metric("Week", "1/12")
    
    st.divider()
    
    # Coming soon section
    st.subheader("🎯 What's Coming")
    
    with st.expander("✅ Week 1-2: Foundation (Current)", expanded=True):
        st.markdown("""
        - Project setup
        - API framework
        - Basic UI
        - Development environment
        """)
    
    with st.expander("📋 Week 3-4: Data Cleaning"):
        st.markdown("""
        - File upload
        - Automated data cleaning
        - Quality scoring
        - Cleaning logs
        """)
    
    with st.expander("📊 Week 5-6: Visualizations & AI"):
        st.markdown("""
        - Chart generation
        - LLM integration
        - Business insights
        - Confidence scoring
        """)
    
    with st.expander("🎨 Week 7-8: Dashboard"):
        st.markdown("""
        - Results display
        - Interactive UI
        - Chart gallery
        - Insight cards
        """)
    
    with st.expander("📄 Week 9-10: Export & Testing"):
        st.markdown("""
        - PDF generation
        - Quality assurance
        - Performance testing
        - Bug fixes
        """)
    
    with st.expander("🚀 Week 11-12: Launch"):
        st.markdown("""
        - Beta testing
        - Documentation
        - Public launch
        - User feedback
        """)
    
    st.divider()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <p>Built with ❤️ using FastAPI, Streamlit & Llama 3.1</p>
        <p><a href='https://github.com/YOUR_USERNAME/ai-insight-engine'>GitHub</a> | 
        <a href='{API_URL}/docs'>API Docs</a></p>
    </div>
    """.format(API_URL=API_URL), unsafe_allow_html=True)

if __name__ == "__main__":
    main()