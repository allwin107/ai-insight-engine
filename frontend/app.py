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

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None

def check_api_health():
    """Check if backend API is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def register_user(email, password, full_name):
    """Register a new user"""
    try:
        response = requests.post(
            f"{API_URL}/api/v1/auth/register",
            json={
                "email": email,
                "password": password,
                "full_name": full_name
            }
        )
        if response.status_code == 201:
            data = response.json()
            st.session_state.token = data['access_token']
            st.session_state.user = data['user']
            return True, "Registration successful!"
        else:
            return False, response.json().get('detail', 'Registration failed')
    except Exception as e:
        return False, str(e)

def login_user(email, password):
    """Login user"""
    try:
        response = requests.post(
            f"{API_URL}/api/v1/auth/login",
            json={
                "email": email,
                "password": password
            }
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data['access_token']
            st.session_state.user = data['user']
            return True, "Login successful!"
        else:
            return False, response.json().get('detail', 'Login failed')
    except Exception as e:
        return False, str(e)

def logout_user():
    """Logout user"""
    st.session_state.token = None
    st.session_state.user = None

def show_auth_page():
    """Show login/register page"""
    st.title("📊 AI Data Insight Engine")
    st.markdown("Transform raw business data into actionable insights automatically")
    
    # Check API status
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if check_api_health():
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected - Make sure backend is running")
            return
    
    st.divider()
    
    # Tabs for login and register
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    success, message = login_user(email, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    with tab2:
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            full_name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", help="Min 8 characters")
            password_confirm = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Register", use_container_width=True)
            
            if submit:
                if not email or not password or not password_confirm:
                    st.error("Please fill in all required fields")
                elif password != password_confirm:
                    st.error("Passwords don't match")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    success, message = register_user(email, password, full_name)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

def show_dashboard():
    """Show main dashboard for authenticated users"""
    # Sidebar
    with st.sidebar:
        st.header(f"👤 {st.session_state.user['email']}")
        
        if st.session_state.user.get('full_name'):
            st.write(f"**{st.session_state.user['full_name']}**")
        
        st.divider()
        
        # User stats
        st.metric(
            "Uploads This Month", 
            f"{st.session_state.user['upload_count']}/{st.session_state.user['upload_limit']}"
        )
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
    
    # Main content
    st.title("📊 AI Data Insight Engine")
    
    # Status info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", "🚧 In Development")
    
    with col2:
        st.metric("Version", "1.0.0 MVP")
    
    with col3:
        st.metric("Week", "1/12")
    
    st.divider()
    
    # Coming soon
    st.success("✅ **Day 2 Complete:** Authentication system working!")
    
    st.info("""
    **Coming Next (Day 3):**
    - File upload functionality
    - Processing status tracking
    - Job management
    """)
    
    # Development roadmap
    st.subheader("🎯 Development Progress")
    
    with st.expander("✅ Week 1-2: Foundation (Current)", expanded=True):
        st.markdown("""
        - ✅ Project setup
        - ✅ API framework
        - ✅ Database & Authentication
        - 🔄 File upload (Day 3)
        """)
    
    with st.expander("📋 Week 3-4: Data Cleaning"):
        st.markdown("""
        - File upload
        - Automated data cleaning
        - Quality scoring
        - Cleaning logs
        """)

def main():
    """Main application"""
    
    # Check if user is authenticated
    if st.session_state.token and st.session_state.user:
        show_dashboard()
    else:
        show_auth_page()

if __name__ == "__main__":
    main()