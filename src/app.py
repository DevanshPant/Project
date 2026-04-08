"""
Streamlit Web Application for Resume Screening System
Interactive interface for recruiters and HR professionals with role-based access
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
import tempfile
import logging

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import DataLoader
from preprocess import TextPreprocessor
from feature_extraction import FeatureExtractor
from matcher import ResumeJobMatcher, CandidateShortlister
from utils import DataExporter, ResultsFormatter, compare_tfidf_vs_bert, scalability_analysis, bias_reduction_strategies
from auth import AuthenticationManager, login_page, logout_button

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Resume Screening System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 20px;
    }
    .section-header {
        font-size: 24px;
        font-weight: bold;
        margin: 20px 0 10px 0;
        padding: 10px;
        background-color: #f0f0f0;
        border-radius: 5px;
    }
    .metric-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    
    # Authentication check
    auth_manager = AuthenticationManager()
    
    # Check if user is logged in
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        # Show login page
        login_page(auth_manager)
        return
    
    # User is logged in
    st.title("🎯 Resume Screening & Candidate Shortlisting System")
    
    # Sidebar with user info and navigation
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"**Logged in as:** {st.session_state.user_email}")
        st.markdown(f"**Role:** {st.session_state.user_role.upper()}")
        st.markdown("---")
        
        # Logout button
        logout_button()
        
        st.markdown("---")
        
        # Role-based navigation
        if st.session_state.user_role == 'admin':
            # Admin navigation
            st.header("Admin Navigation")
            page = st.radio("Select a Page", [
                "Admin Dashboard",
                "Keywords Management",
                "Database Management",
                "System Health",
                "Documentation"
            ])
        else:
            # Recruiter navigation
            st.header("Recruiter Navigation")
            page = st.radio("Select a Page", [
                "Home",
                "Upload & Process",
                "Job Matching",
                "Results & Export",
                "Analytics",
                "Documentation"
            ])
    
    # Route based on role and page
    if st.session_state.user_role == 'admin':
        # Admin pages
        if page == "Admin Dashboard":
            show_admin_dashboard()
        elif page == "Keywords Management":
            show_keywords_management()
        elif page == "Database Management":
            show_database_management()
        elif page == "System Health":
            show_system_health()
        elif page == "Documentation":
            show_documentation_page()
    else:
        # Recruiter pages
        if page == "Home":
            show_home_page()
        elif page == "Upload & Process":
            show_upload_page()
        elif page == "Job Matching":
            show_matching_page()
        elif page == "Results & Export":
            show_results_page()
        elif page == "Analytics":
            show_analytics_page()
        elif page == "Documentation":
            show_documentation_page()


def show_admin_dashboard():
    """Display admin dashboard."""
    from admin import display_admin_panel
    display_admin_panel()


def show_keywords_management():
    """Display keywords management."""
    from keywords import KeywordManager, display_keyword_management
    kw_manager = KeywordManager()
    display_keyword_management(kw_manager)


def show_database_management():
    """Display database management."""
    from database import display_database_upload, display_database_management
    
    st.header("💾 Database Management")
    
    tab1, tab2 = st.tabs(["Upload Database", "Manage Databases"])
    
    with tab1:
        display_database_upload()
    
    with tab2:
        display_database_management()


def show_system_health():
    """Display system health checks."""
    from system_health import display_system_health_check, display_system_tests
    
    st.header("🏥 System Health & Verification")
    
    tab1, tab2 = st.tabs(["Health Check", "System Tests"])
    
    with tab1:
        display_system_health_check()
    
    with tab2:
        display_system_tests()



def show_home_page():
    """Display home page."""
    
    st.header("Welcome to Resume Screening System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔍 System Features
        
        - **Automated Resume Processing**: Upload resumes and process them automatically
        - **Smart Matching**: Match candidate profiles with job descriptions
        - **Intelligent Ranking**: Rank candidates based on fit and skills
        - **Bulk Shortlisting**: Shortlist top candidates with customizable thresholds
        - **Data Export**: Export results to CSV or Excel
        - **Real-time Analytics**: View matching statistics and insights
        
        ### 🎯 How It Works
        
        1. **Upload Resumes**: Upload multiple resume files (PDF, DOCX, TXT)
        2. **Enter Job Description**: Provide the job description you want to match
        3. **Process**: System extracts features and matches resumes
        4. **Review**: View ranked candidates with match scores
        5. **Export**: Download results in your preferred format
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Technology Stack
        
        **NLP & ML:**
        - NLTK for text preprocessing
        - Scikit-learn for feature extraction (TF-IDF)
        - Cosine similarity for matching
        
        **Data Processing:**
        - Pandas for data manipulation
        - NumPy for numerical computing
        
        **Web Framework:**
        - Streamlit for interactive UI
        
        ### 📈 System Capabilities
        
        - Process up to 10,000+ resumes efficiently
        - Real-time similarity matching
        - Multiple export formats
        - Customizable matching thresholds
        - Comprehensive analytics dashboard
        
        ### ⚙️ Getting Started
        
        1. Click "Upload & Process" to load resumes
        2. Enter job description in "Job Matching"
        3. View results in "Results & Export"
        """)
    
    # Display key metrics
    st.markdown("---")
    st.markdown("### 📌 Quick Information")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Supported Resumes", "10,000+")
    
    with col2:
        st.metric("Processing Speed", "5-10 sec")
    
    with col3:
        st.metric("Accuracy", "~85-92%")
    
    with col4:
        st.metric("Export Formats", "3 types")
    
    # Latest updates
    st.markdown("---")
    st.info("""
    **Latest Updates:**
    - ✅ Added TF-IDF feature extraction
    - ✅ Implemented cosine similarity matching
    - ✅ Excel export with formatting
    - ✅ Real-time analytics dashboard
    """)


def show_upload_page():
    """Display resume upload and processing page."""
    
    st.header("📤 Upload & Process Resumes")
    
    # Sample data option
    use_sample = st.checkbox("Use Sample Data (Demo Mode)")
    
    if use_sample:
        st.info("Using sample resume data for demonstration")
        # Create sample data
        sample_resumes = [
            "Python Expert with 5+ years experience in machine learning and data science. Skills: Python, TensorFlow, Scikit-learn.",
            "Full stack developer with JavaScript, React, Node.js expertise. Strong in web development and responsive design.",
            "Data analyst proficient in SQL, Python, Tableau. Experience with business intelligence and reporting.",
            "Cloud architect with AWS, Azure knowledge. Infrastructure as code, DevOps, containerization.",
            "Project manager with Agile and Scrum certification. Led cross-functional teams to deliver software projects.",
        ]
        
        st.session_state.resumes = sample_resumes
        st.success("✓ Sample resumes loaded")
    else:
        # Manual resume input
        st.subheader("Option 1: Paste Resume Text")
        
        num_resumes = st.number_input("Number of resumes to add", min_value=1, max_value=10, value=1)
        
        resumes = []
        for i in range(num_resumes):
            with st.expander(f"Resume {i+1}"):
                resume_text = st.text_area(
                    f"Paste resume text for candidate {i+1}",
                    height=150,
                    key=f"resume_{i}"
                )
                if resume_text:
                    resumes.append(resume_text)
        
        if resumes:
            st.session_state.resumes = resumes
            st.success(f"✓ {len(resumes)} resume(s) loaded")
    
    # Process resumes
    if st.button("🔄 Process Resumes", key="process_btn"):
        if 'resumes' in st.session_state:
            with st.spinner("Processing resumes..."):
                try:
                    # Preprocess
                    preprocessor = TextPreprocessor()
                    processed_resumes = [
                        preprocessor.preprocess_text(resume) 
                        for resume in st.session_state.resumes
                    ]
                    
                    st.session_state.processed_resumes = processed_resumes
                    
                    # Extract features
                    extractor = FeatureExtractor()
                    resume_features = extractor.tfidf_extractor.fit_transform(processed_resumes)
                    
                    st.session_state.resume_features = resume_features
                    st.session_state.feature_extractor = extractor
                    
                    st.success("✓ Resumes processed successfully!")
                    
                    # Display statistics
                    st.subheader("Processing Statistics")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Resumes Processed", len(processed_resumes))
                    
                    with col2:
                        st.metric("Features Extracted", resume_features.shape[1])
                    
                    with col3:
                        avg_length = np.mean([len(r.split()) for r in processed_resumes])
                        st.metric("Avg Words/Resume", f"{avg_length:.0f}")
                    
                    # Show sample
                    st.subheader("Sample Processed Text")
                    st.text_area(
                        "First 1000 characters of processed resume:",
                        value=processed_resumes[0][:1000],
                        height=100,
                        disabled=True
                    )
                    
                except Exception as e:
                    st.error(f"Error processing resumes: {str(e)}")
        else:
            st.warning("Please load resumes first")


def show_matching_page():
    """Display job matching page."""
    
    st.header("🔗 Job Matching & Candidate Ranking")
    
    if 'resumes' not in st.session_state or 'processed_resumes' not in st.session_state:
        st.warning("⚠️ Please upload and process resumes first in the 'Upload & Process' page")
        return
    
    # Job description input
    st.subheader("Enter Job Description")
    
    job_description = st.text_area(
        "Paste job description here:",
        height=150,
        placeholder="Senior Python Developer with Machine Learning expertise..."
    )
    
    if not job_description:
        st.info("Please enter a job description to match candidates")
        return
    
    # Matching parameters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.3, 0.05)
    
    with col2:
        top_n = st.number_input("Top N Candidates", min_value=1, max_value=100, value=10)
    
    with col3:
        st.write("")
        st.write("")
        match_button = st.button("🎯 Match Candidates")
    
    if match_button:
        with st.spinner("Matching resumes with job description..."):
            try:
                # Preprocess job description
                preprocessor = TextPreprocessor()
                processed_job = preprocessor.preprocess_text(job_description)
                
                # Extract features for job description
                all_texts = st.session_state.processed_resumes + [processed_job]
                feature_extractor = st.session_state.feature_extractor
                
                # Get job vector
                job_features = feature_extractor.tfidf_extractor.vectorizer.transform([processed_job]).toarray()[0]
                
                # Match candidates
                matcher = ResumeJobMatcher()
                candidate_info = [
                    {'id': i, 'name': f'Candidate {i+1}'} 
                    for i in range(len(st.session_state.resumes))
                ]
                
                matches = matcher.match_resumes_to_job(
                    st.session_state.resume_features,
                    job_features,
                    candidate_info,
                    top_n=top_n
                )
                
                st.session_state.matches = matches
                
                # Display statistics
                st.subheader("📊 Matching Statistics")
                
                stats = matcher.get_summary_statistics()
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Average Score", f"{stats['average_score']:.4f}")
                
                with col2:
                    st.metric("Median Score", f"{stats['median_score']:.4f}")
                
                with col3:
                    st.metric("Max Score", f"{stats['max_score']:.4f}")
                
                with col4:
                    st.metric("Min Score", f"{stats['min_score']:.4f}")
                
                # Display ranked candidates
                st.subheader("👥 Ranked Candidates")
                
                results_df = matcher.get_matches_dataframe()
                st.dataframe(results_df, use_container_width=True)
                
                # Shortlist candidates
                st.subheader("✅ Shortlisted Candidates")
                
                shortlister = CandidateShortlister(threshold=threshold)
                shortlist_df = shortlister.shortlist_candidates(matches, top_n=5)
                
                if not shortlist_df.empty:
                    st.dataframe(shortlist_df, use_container_width=True)
                    st.session_state.shortlist_df = shortlist_df
                else:
                    st.info("No candidates above the selected threshold")
                
            except Exception as e:
                st.error(f"Error in matching: {str(e)}")


def show_results_page():
    """Display results and export page."""
    
    st.header("📥 Results & Export")
    
    if 'shortlist_df' not in st.session_state:
        st.info("Please complete job matching first")
        return
    
    shortlist_df = st.session_state.shortlist_df
    
    # Display results
    st.subheader("Shortlisted Candidates")
    st.dataframe(shortlist_df, use_container_width=True)
    
    # Export options
    st.subheader("💾 Export Results")
    
    export_format = st.radio("Select export format:", ["CSV", "Excel", "JSON"])
    
    exporter = DataExporter("outputs")
    
    if export_format == "CSV":
        csv_data = shortlist_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv_data,
            file_name="candidates_shortlist.csv",
            mime="text/csv"
        )
    
    elif export_format == "Excel":
        with st.spinner("Generating Excel file..."):
            try:
                filepath = exporter.export_to_excel(shortlist_df, include_charts=True)
                with open(filepath, 'rb') as f:
                    excel_data = f.read()
                st.download_button(
                    label="📥 Download as Excel",
                    data=excel_data,
                    file_name="candidates_shortlist.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Error generating Excel: {str(e)}")
    
    elif export_format == "JSON":
        json_data = shortlist_df.to_json(orient='records', indent=2)
        st.download_button(
            label="📥 Download as JSON",
            data=json_data,
            file_name="candidates_shortlist.json",
            mime="application/json"
        )


def show_analytics_page():
    """Display analytics dashboard."""
    
    st.header("📊 Analytics & Insights")
    
    if 'matches' not in st.session_state:
        st.info("Please complete job matching first to view analytics")
        return
    
    matches = st.session_state.matches
    
    # Create visualization data
    scores = [m.similarity_score for m in matches]
    
    # Score distribution
    st.subheader("Score Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.bar_chart(pd.DataFrame({
            'Rank': range(1, len(scores)+1),
            'Score': scores
        }).set_index('Rank'))
    
    with col2:
        # Statistics
        st.subheader("Statistics")
        stats_data = {
            'Total Candidates': len(matches),
            'Average Score': f"{np.mean(scores):.4f}",
            'Median Score': f"{np.median(scores):.4f}",
            'Std Dev': f"{np.std(scores):.4f}",
            'Max Score': f"{np.max(scores):.4f}",
            'Min Score': f"{np.min(scores):.4f}"
        }
        
        for key, value in stats_data.items():
            st.metric(key, value)


def show_documentation_page():
    """Display documentation and information."""
    
    st.header("📚 Documentation & Information")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "System Overview",
        "TF-IDF vs BERT",
        "Scalability",
        "Bias Reduction"
    ])
    
    with tab1:
        st.subheader("System Architecture")
        st.markdown("""
        ### Components:
        
        1. **Data Loader**: Loads resume dataset from Kaggle or local files
        2. **Preprocessor**: NLP preprocessing (tokenization, lemmatization, stopword removal)
        3. **Feature Extractor**: TF-IDF vectorization of resume text
        4. **Matcher**: Cosine similarity matching between resumes and job descriptions
        5. **Shortlister**: Candidate ranking and selection based on thresholds
        6. **Exporter**: Results export to multiple formats
        
        ### Data Flow:
        Upload → Preprocess → Extract Features → Match → Rank → Export
        """)
    
    with tab2:
        st.markdown(compare_tfidf_vs_bert())
    
    with tab3:
        st.markdown(scalability_analysis())
    
    with tab4:
        st.markdown(bias_reduction_strategies())


if __name__ == "__main__":
    # Initialize session state
    if 'resumes' not in st.session_state:
        st.session_state.resumes = []
    
    if 'processed_resumes' not in st.session_state:
        st.session_state.processed_resumes = []
    
    if 'matches' not in st.session_state:
        st.session_state.matches = []
    
    # Authentication session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    
    if 'session_time' not in st.session_state:
        st.session_state.session_time = None
    
    main()
