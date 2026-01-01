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
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload", "📋 My Jobs", "ℹ️ About"])
    
    with tab1:
        show_upload_tab()
    
    with tab2:
        show_jobs_tab()
    
    with tab3:
        show_about_tab()

def show_upload_tab():
    """Upload file tab"""
    st.header("📤 Upload Your Data")
    
    st.info("""
    **Supported formats:** CSV, Excel (.xlsx, .xls)  
    **Maximum file size:** 10 MB  
    **Maximum rows:** 10,000 rows
    """)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload your business data file"
    )
    
    if uploaded_file is not None:
        # Show file details
        st.success(f"✅ File selected: **{uploaded_file.name}**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
        with col2:
            st.metric("File Type", uploaded_file.type)
        
        st.divider()
        
        # Upload button
        if st.button("🚀 Upload & Analyze", type="primary", use_container_width=True):
            with st.spinner("Uploading file..."):
                success, message, job_id = upload_file_to_api(uploaded_file)
                
                if success:
                    st.success(f"✅ {message}")
                    st.info(f"**Job ID:** `{job_id}`")
                    st.balloons()
                    
                    # Update user stats
                    st.session_state.user['upload_count'] += 1
                    
                    # Show next steps
                    st.markdown("""
                    ### What's Next?
                    1. Go to **"My Jobs"** tab to see processing status
                    2. Processing usually takes 1-2 minutes
                    3. You'll see charts and insights when complete!
                    """)
                else:
                    st.error(f"❌ {message}")
    else:
        # Example datasets
        st.markdown("### 📊 Don't have data? Try our examples:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📈 Sales Data", use_container_width=True):
                st.info("Example dataset coming soon!")
        
        with col2:
            if st.button("🛒 E-commerce", use_container_width=True):
                st.info("Example dataset coming soon!")
        
        with col3:
            if st.button("📊 Marketing", use_container_width=True):
                st.info("Example dataset coming soon!")

def upload_file_to_api(file):
    """Upload file to API"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        
        response = requests.post(
            f"{API_URL}/api/v1/upload",
            files=files,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return True, data['message'], data['job_id']
        else:
            error = response.json().get('detail', 'Upload failed')
            return False, error, None
            
    except Exception as e:
        return False, str(e), None

def show_jobs_tab():
    """Show user's jobs"""
    st.header("📋 My Processing Jobs")
    
    # Fetch jobs
    jobs = fetch_user_jobs()
    
    if jobs is None:
        st.error("Failed to load jobs")
        return
    
    if len(jobs) == 0:
        st.info("No jobs yet. Upload a file to get started!")
        return
    
    # Display jobs
    for job in jobs:
        with st.expander(f"📄 {job['filename']} - {job['status'].upper()}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Status", job['status'].title())
            
            with col2:
                st.metric("Progress", f"{job['progress']}%")
            
            with col3:
                if job['quality_score']:
                    st.metric("Quality", f"{job['quality_score']}/100")
                else:
                    st.metric("Quality", "N/A")
            
            st.text(f"Created: {job['created_at'][:19]}")
            st.text(f"Job ID: {job['job_id']}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Refresh", key=f"refresh_{job['job_id']}"):
                    st.rerun()
            
            with col2:
                if job['status'] == 'complete':
                    if st.button("📊 View Results", key=f"view_{job['job_id']}"):
                        st.info("Results viewer coming soon!")
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{job['job_id']}"):
                    if delete_job(job['job_id']):
                        st.success("Job deleted!")
                        st.rerun()

def fetch_user_jobs():
    """Fetch user's jobs from API"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(
            f"{API_URL}/api/v1/jobs",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['jobs']
        else:
            return None
            
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def delete_job(job_id: str) -> bool:
    """Delete a job"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.delete(
            f"{API_URL}/api/v1/jobs/{job_id}",
            headers=headers,
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

def show_about_tab():
    """About and development progress"""
    st.header("ℹ️ About This Project")
    
    # Status info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", "🚧 In Development")
    
    with col2:
        st.metric("Version", "1.0.0 MVP")
    
    with col3:
        st.metric("Week", "1/12")
    
    st.divider()
    
    # Progress update
    st.success("✅ **Day 3 Complete:** File upload system working!")
    
    st.info("""
    **Coming Next (Day 4):**
    - Configuration improvements
    - Testing framework
    - Docker deployment setup
    """)
    
    # Development roadmap
    st.subheader("🎯 Development Progress")
    
    with st.expander("✅ Week 1-2: Foundation (Current)", expanded=True):
        st.markdown("""
        - ✅ Project setup
        - ✅ API framework
        - ✅ Database & Authentication
        - ✅ File upload & job tracking
        - 🔄 Configuration & Docker (Day 4-5)
        """)
    
    with st.expander("📋 Week 3-4: Data Cleaning"):
        st.markdown("""
        - Automated data cleaning pipeline
        - Quality scoring
        - Cleaning logs
        - Edge case handling
        """)
    
    with st.expander("📊 Week 5-6: Visualizations & AI"):
        st.markdown("""
        - Chart generation with AutoViz
        - LLM integration (Llama 3.1)
        - Business insights generation
        - Confidence scoring
        """)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center'>
        <p>Built with ❤️ using FastAPI, Streamlit & Llama 3.1</p>
        <p><a href='https://github.com/YOUR_USERNAME/ai-insight-engine'>GitHub</a> | 
        <a href='http://localhost:8000/docs'>API Docs</a></p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application"""
    
    # Check if user is authenticated
    if st.session_state.token and st.session_state.user:
        show_dashboard()
    else:
        show_auth_page()

if __name__ == "__main__":
    main()