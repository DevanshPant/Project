"""
Admin Dashboard Module
Integrated admin interface for system management
"""

import streamlit as st
from datetime import datetime
import logging

# Import the other modules
from keywords import KeywordManager, JobDescriptionManager, display_keyword_management
from database import DatabaseManager, display_database_upload, display_database_management
from system_health import SystemHealthMonitor, display_system_health_check, display_system_tests

logger = logging.getLogger(__name__)


def display_admin_header():
    """Display admin dashboard header."""
    st.markdown("## 👨‍💼 Admin Dashboard")
    st.markdown("Manage keywords, databases, and monitor system health")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        kw_manager = KeywordManager()
        stats = kw_manager.get_statistics()
        st.metric("Keyword Categories", stats['total_categories'])
    
    with col2:
        st.metric("Total Keywords", stats['total_keywords'])
    
    with col3:
        job_manager = JobDescriptionManager()
        jobs = job_manager.get_all_jobs()
        st.metric("Active Jobs", len(jobs))
    
    with col4:
        db_manager = DatabaseManager()
        databases = db_manager.get_all_databases()
        st.metric("Resume Databases", len(databases))
    
    st.markdown("---")


def display_admin_navigation():
    """Display admin navigation."""
    return st.tabs([
        "📊 Dashboard",
        "🔑 Keywords",
        "💼 Job Descriptions",
        "📤 Database Upload",
        "💾 Database Management",
        "🏥 System Health",
        "🧪 System Tests",
        "⚙️ Settings"
    ])


def display_dashboard_tab():
    """Display main dashboard tab."""
    st.subheader("📊 System Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 System Status")
        
        monitor = SystemHealthMonitor()
        report = monitor.run_full_health_check()
        
        modules_ok = all(report['modules'].values())
        dependencies_ok = all(report['dependencies'].values())
        folders_ok = all(report['folders'].values())
        
        status = "✅ Healthy" if (modules_ok and dependencies_ok and folders_ok) else "⚠️ Issues Detected"
        st.write(f"**Status:** {status}")
        st.write(f"**Last Check:** {report['timestamp']}")
        
        # Quick status indicators
        st.metric("Modules OK", sum(1 for v in report['modules'].values() if v))
        st.metric("Dependencies OK", sum(1 for v in report['dependencies'].values() if v))
    
    with col2:
        st.markdown("### 📋 Database Summary")
        
        db_manager = DatabaseManager()
        databases = db_manager.get_all_databases()
        
        st.write(f"**Total Databases:** {len(databases)}")
        
        if databases:
            total_resumes = 0
            for db_name in databases:
                stats = db_manager.get_database_statistics(db_name)
                if stats:
                    total_resumes += stats['row_count']
            
            st.metric("Total Resumes", total_resumes)
    
    st.markdown("---")
    
    # Recent activity
    st.markdown("### 📝 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Run Health Check", use_container_width=True):
            st.session_state.show_health_check = True
    
    with col2:
        if st.button("📊 View Statistics", use_container_width=True):
            st.session_state.show_stats = True
    
    with col3:
        if st.button("🔍 Search Resume", use_container_width=True):
            st.session_state.show_search = True


def display_job_descriptions_tab():
    """Display job descriptions management tab."""
    st.subheader("💼 Job Descriptions")
    
    job_manager = JobDescriptionManager()
    
    col1, col2 = st.columns(2)
    
    # Add new job
    with col1:
        st.markdown("### ➕ Add New Job")
        
        job_id = st.text_input("Job ID")
        job_title = st.text_input("Job Title")
        job_description = st.text_area("Job Description", height=150)
        
        if st.button("✅ Add Job"):
            if job_id and job_title and job_description:
                # Extract keywords
                keywords = job_manager.extract_keywords_from_description(job_description)
                
                success = job_manager.add_job(job_id, job_title, job_description, keywords)
                
                if success:
                    st.success(f"✅ Job '{job_title}' added with {len(keywords)} keywords")
                    st.rerun()
                else:
                    st.error("Job ID already exists")
            else:
                st.warning("Please fill all fields")
    
    # View jobs
    with col2:
        st.markdown("### 📋 View Jobs")
        
        jobs = job_manager.get_all_jobs()
        
        if jobs:
            for job_id, job_info in jobs.items():
                with st.expander(f"**{job_info['title']}** ({job_id})"):
                    st.write(f"**Description:** {job_info['description'][:200]}...")
                    st.write(f"**Keywords:** {', '.join(job_info['keywords'])}")
                    st.write(f"**Created:** {job_info['created_at']}")
                    
                    if st.button("🗑️ Delete", key=f"delete_job_{job_id}"):
                        job_manager.delete_job(job_id)
                        st.success("Job deleted")
                        st.rerun()
        else:
            st.info("No jobs added yet")


def display_settings_tab():
    """Display settings tab."""
    st.subheader("⚙️ Settings")
    
    st.markdown("### System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Keywords Settings")
        
        if st.checkbox("Auto-extract keywords from job descriptions"):
            st.write("✅ Enabled - Keywords will be automatically extracted")
        
        if st.checkbox("Sync keywords with resumes"):
            st.write("✅ Enabled - Resume keywords will be matched against job keywords")
    
    with col2:
        st.markdown("#### Database Settings")
        
        if st.checkbox("Enable duplicate email detection"):
            st.write("✅ Enabled - Duplicate emails will be flagged")
        
        if st.checkbox("Enable data validation"):
            st.write("✅ Enabled - All uploads will be validated")
    
    st.markdown("---")
    
    st.markdown("### User Management")
    
    st.info("User management features will be available in the next update")


def display_admin_panel():
    """Main admin panel function."""
    
    # Check if user is admin
    if 'user_role' not in st.session_state or st.session_state.user_role != 'admin':
        st.error("❌ Admin access required")
        return
    
    # Header
    display_admin_header()
    
    # Navigation tabs
    tabs = display_admin_navigation()
    
    # Dashboard
    with tabs[0]:
        display_dashboard_tab()
    
    # Keywords
    with tabs[1]:
        kw_manager = KeywordManager()
        display_keyword_management(kw_manager)
    
    # Job Descriptions
    with tabs[2]:
        display_job_descriptions_tab()
    
    # Database Upload
    with tabs[3]:
        display_database_upload()
    
    # Database Management
    with tabs[4]:
        display_database_management()
    
    # System Health
    with tabs[5]:
        display_system_health_check()
    
    # System Tests
    with tabs[6]:
        display_system_tests()
    
    # Settings
    with tabs[7]:
        display_settings_tab()


if __name__ == "__main__":
    display_admin_panel()
