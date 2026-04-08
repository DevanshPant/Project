"""
Admin and User Authentication Module
Handles login, user management, and session management
"""

import streamlit as st
import pandas as pd
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


# User credentials (in production, use proper database)
ADMIN_CREDENTIALS = {
    "admin@example.com": "admin123",  # Change in production!
}

USER_CREDENTIALS = {
    "recruiter@example.com": "recruiter123",  # Demo credentials
}

SYSTEM_USERS = {
    **ADMIN_CREDENTIALS,
    **USER_CREDENTIALS
}


class AuthenticationManager:
    """Manage user authentication and sessions."""
    
    def __init__(self, session_timeout_minutes: int = 60):
        """
        Initialize authentication manager.
        
        Args:
            session_timeout_minutes: Session timeout duration
        """
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize session state variables."""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_email' not in st.session_state:
            st.session_state.user_email = None
        if 'user_role' not in st.session_state:
            st.session_state.user_role = None
        if 'login_time' not in st.session_state:
            st.session_state.login_time = None
        if 'session_data' not in st.session_state:
            st.session_state.session_data = {}
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash."""
        return self.hash_password(password) == stored_hash
    
    def get_user_role(self, email: str) -> Optional[str]:
        """Determine user role based on email."""
        if email in ADMIN_CREDENTIALS:
            return "admin"
        elif email in USER_CREDENTIALS:
            return "recruiter"
        return None
    
    def authenticate(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate user.
        
        Args:
            email: User email
            password: User password
        
        Returns:
            Tuple: (success, message)
        """
        if email not in SYSTEM_USERS:
            return False, "❌ User not found"
        
        if SYSTEM_USERS[email] != password:
            return False, "❌ Invalid password"
        
        # Set session state
        st.session_state.authenticated = True
        st.session_state.user_email = email
        st.session_state.user_role = self.get_user_role(email)
        st.session_state.login_time = datetime.now()
        
        logger.info(f"User {email} authenticated as {st.session_state.user_role}")
        
        return True, f"✅ Welcome {email}!"
    
    def logout(self):
        """Logout user."""
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.user_role = None
        st.session_state.login_time = None
        logger.info("User logged out")
    
    def is_session_valid(self) -> bool:
        """Check if session is still valid."""
        if not st.session_state.authenticated or not st.session_state.login_time:
            return False
        
        elapsed = datetime.now() - st.session_state.login_time
        return elapsed < self.session_timeout
    
    def is_admin(self) -> bool:
        """Check if current user is admin."""
        return st.session_state.user_role == "admin"
    
    def is_recruiter(self) -> bool:
        """Check if current user is recruiter."""
        return st.session_state.user_role == "recruiter"
    
    def get_current_user(self) -> Optional[str]:
        """Get current authenticated user."""
        return st.session_state.user_email if st.session_state.authenticated else None
    
    def get_user_info(self) -> Dict:
        """Get current user information."""
        return {
            'email': st.session_state.user_email,
            'role': st.session_state.user_role,
            'login_time': st.session_state.login_time,
            'authenticated': st.session_state.authenticated
        }


def login_page(auth_manager: AuthenticationManager):
    """Display login page."""
    
    st.set_page_config(page_title="Resume Screening - Login", layout="centered")
    
    # Custom CSS for login page
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 40px;
        }
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 🎯 Resume Screening System")
        st.markdown("### Sign In to Continue")
        
        st.markdown("---")
        
        # Login form
        with st.form("login_form"):
            email = st.text_input(
                "📧 Email Address",
                placeholder="admin@example.com or recruiter@example.com"
            )
            
            password = st.text_input(
                "🔐 Password",
                type="password",
                placeholder="Enter your password"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                submit_button = st.form_submit_button("🔓 Login", use_container_width=True)
            
            with col2:
                demo_button = st.form_submit_button("📝 Demo Login", use_container_width=True)
            
            if submit_button:
                if not email or not password:
                    st.error("❌ Please enter email and password")
                else:
                    success, message = auth_manager.authenticate(email, password)
                    if success:
                        st.success(message)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(message)
            
            if demo_button:
                # Demo login
                success, message = auth_manager.authenticate(
                    "admin@example.com",
                    "admin123"
                )
                if success:
                    st.success("✅ Demo Admin Login")
                    st.rerun()
        
        st.markdown("---")
        
        # Demo credentials info
        with st.expander("👤 Demo Credentials"):
            st.info("""
            **Admin Account:**
            - Email: `admin@example.com`
            - Password: `admin123`
            
            **Recruiter Account:**
            - Email: `recruiter@example.com`
            - Password: `recruiter123`
            """)
        
        # System info
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: gray; font-size: 12px;">
            <p>🚀 AI-Based Resume Screening System v1.0</p>
            <p>Secure • Fast • Intelligent</p>
        </div>
        """, unsafe_allow_html=True)


def logout_button(auth_manager: AuthenticationManager):
    """Display logout button in sidebar."""
    if auth_manager.is_session_valid():
        user_info = auth_manager.get_user_info()
        
        st.sidebar.markdown("---")
        col1, col2 = st.sidebar.columns([3, 1])
        
        with col1:
            st.sidebar.caption(f"👤 {user_info['email']}")
            st.sidebar.caption(f"🏷️ {user_info['role'].upper()}")
        
        with col2:
            if st.sidebar.button("🚪 Logout"):
                auth_manager.logout()
                st.rerun()


def show_user_header(auth_manager: AuthenticationManager):
    """Show user header with info."""
    if auth_manager.is_session_valid():
        user = auth_manager.get_current_user()
        role = st.session_state.user_role
        
        col1, col2, col3 = st.columns([2, 3, 1])
        
        with col1:
            st.markdown(f"**👤 User:** {user}")
        
        with col2:
            st.markdown(f"**🏷️ Role:** {role.upper()}")
        
        with col3:
            if st.button("🚪 Logout", key="header_logout"):
                auth_manager.logout()
                st.rerun()


if __name__ == "__main__":
    # Test authentication
    auth = AuthenticationManager()
    login_page(auth)
