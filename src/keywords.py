"""
Keyword Management Module
Admin can manage keywords for job descriptions
"""

import json
import os
import pandas as pd
import streamlit as st
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class KeywordManager:
    """Manage job description keywords."""
    
    def __init__(self, keywords_file: str = "data/keywords.json"):
        """
        Initialize keyword manager.
        
        Args:
            keywords_file: Path to keywords storage file
        """
        self.keywords_file = keywords_file
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        """Ensure keywords file exists."""
        os.makedirs(os.path.dirname(self.keywords_file), exist_ok=True)
        
        if not os.path.exists(self.keywords_file):
            default_keywords = {
                "technical_skills": ["Python", "Java", "JavaScript", "SQL", "API"],
                "soft_skills": ["Communication", "Leadership", "Teamwork", "Problem Solving"],
                "certifications": ["AWS", "Azure", "GCP", "Kubernetes", "Docker"],
                "education": ["Bachelor's", "Master's", "PhD", "Bootcamp", "Certification"]
            }
            self.save_keywords(default_keywords)
    
    def load_keywords(self) -> Dict:
        """Load keywords from file."""
        try:
            with open(self.keywords_file, 'r') as f:
                keywords = json.load(f)
            logger.info("Keywords loaded successfully")
            return keywords
        except Exception as e:
            logger.error(f"Error loading keywords: {e}")
            return {}
    
    def save_keywords(self, keywords: Dict):
        """Save keywords to file."""
        try:
            with open(self.keywords_file, 'w') as f:
                json.dump(keywords, f, indent=4)
            logger.info("Keywords saved successfully")
        except Exception as e:
            logger.error(f"Error saving keywords: {e}")
    
    def add_keyword(self, category: str, keyword: str) -> bool:
        """Add a keyword to category."""
        keywords = self.load_keywords()
        
        if category not in keywords:
            keywords[category] = []
        
        if keyword not in keywords[category]:
            keywords[category].append(keyword)
            self.save_keywords(keywords)
            logger.info(f"Added keyword '{keyword}' to category '{category}'")
            return True
        
        return False
    
    def remove_keyword(self, category: str, keyword: str) -> bool:
        """Remove a keyword from category."""
        keywords = self.load_keywords()
        
        if category in keywords and keyword in keywords[category]:
            keywords[category].remove(keyword)
            self.save_keywords(keywords)
            logger.info(f"Removed keyword '{keyword}' from category '{category}'")
            return True
        
        return False
    
    def add_category(self, category: str) -> bool:
        """Add a new category."""
        keywords = self.load_keywords()
        
        if category not in keywords:
            keywords[category] = []
            self.save_keywords(keywords)
            logger.info(f"Added category '{category}'")
            return True
        
        return False
    
    def delete_category(self, category: str) -> bool:
        """Delete a category."""
        keywords = self.load_keywords()
        
        if category in keywords:
            del keywords[category]
            self.save_keywords(keywords)
            logger.info(f"Deleted category '{category}'")
            return True
        
        return False
    
    def get_categories(self) -> List[str]:
        """Get all categories."""
        keywords = self.load_keywords()
        return list(keywords.keys())
    
    def get_keywords_by_category(self, category: str) -> List[str]:
        """Get keywords for category."""
        keywords = self.load_keywords()
        return keywords.get(category, [])
    
    def get_all_keywords(self) -> Dict:
        """Get all keywords."""
        return self.load_keywords()
    
    def search_keyword(self, search_term: str) -> Dict[str, List[str]]:
        """Search keywords across categories."""
        keywords = self.load_keywords()
        results = {}
        
        search_term = search_term.lower()
        
        for category, keyword_list in keywords.items():
            matching = [kw for kw in keyword_list if search_term in kw.lower()]
            if matching:
                results[category] = matching
        
        return results
    
    def export_keywords(self, filepath: str) -> bool:
        """Export keywords to CSV."""
        try:
            keywords = self.load_keywords()
            data = []
            
            for category, keyword_list in keywords.items():
                for keyword in keyword_list:
                    data.append({'Category': category, 'Keyword': keyword})
            
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
            logger.info(f"Keywords exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting keywords: {e}")
            return False
    
    def import_keywords(self, filepath: str) -> bool:
        """Import keywords from CSV."""
        try:
            df = pd.read_csv(filepath)
            keywords = {}
            
            for _, row in df.iterrows():
                category = row['Category']
                keyword = row['Keyword']
                
                if category not in keywords:
                    keywords[category] = []
                
                if keyword not in keywords[category]:
                    keywords[category].append(keyword)
            
            self.save_keywords(keywords)
            logger.info(f"Keywords imported from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error importing keywords: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get keyword statistics."""
        keywords = self.load_keywords()
        
        stats = {
            'total_categories': len(keywords),
            'total_keywords': sum(len(kws) for kws in keywords.values()),
            'categories': {}
        }
        
        for category, keyword_list in keywords.items():
            stats['categories'][category] = len(keyword_list)
        
        return stats


class JobDescriptionManager:
    """Manage job descriptions with keywords."""
    
    def __init__(self, jobs_file: str = "data/job_descriptions.json"):
        """Initialize job description manager."""
        self.jobs_file = jobs_file
        self.keyword_manager = KeywordManager()
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        """Ensure jobs file exists."""
        os.makedirs(os.path.dirname(self.jobs_file), exist_ok=True)
        
        if not os.path.exists(self.jobs_file):
            with open(self.jobs_file, 'w') as f:
                json.dump({}, f)
    
    def load_jobs(self) -> Dict:
        """Load job descriptions."""
        try:
            with open(self.jobs_file, 'r') as f:
                jobs = json.load(f)
            return jobs
        except:
            return {}
    
    def save_jobs(self, jobs: Dict):
        """Save job descriptions."""
        with open(self.jobs_file, 'w') as f:
            json.dump(jobs, f, indent=4)
    
    def add_job(self, job_id: str, title: str, description: str, 
                keywords: List[str] = None) -> bool:
        """Add new job description."""
        jobs = self.load_jobs()
        
        if job_id in jobs:
            return False
        
        jobs[job_id] = {
            'title': title,
            'description': description,
            'keywords': keywords or [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.save_jobs(jobs)
        logger.info(f"Job '{title}' added")
        return True
    
    def update_job(self, job_id: str, title: str = None, 
                   description: str = None, keywords: List[str] = None) -> bool:
        """Update job description."""
        jobs = self.load_jobs()
        
        if job_id not in jobs:
            return False
        
        if title:
            jobs[job_id]['title'] = title
        if description:
            jobs[job_id]['description'] = description
        if keywords is not None:
            jobs[job_id]['keywords'] = keywords
        
        jobs[job_id]['updated_at'] = datetime.now().isoformat()
        
        self.save_jobs(jobs)
        logger.info(f"Job '{job_id}' updated")
        return True
    
    def delete_job(self, job_id: str) -> bool:
        """Delete job description."""
        jobs = self.load_jobs()
        
        if job_id in jobs:
            del jobs[job_id]
            self.save_jobs(jobs)
            logger.info(f"Job '{job_id}' deleted")
            return True
        
        return False
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get specific job description."""
        jobs = self.load_jobs()
        return jobs.get(job_id)
    
    def get_all_jobs(self) -> Dict:
        """Get all job descriptions."""
        return self.load_jobs()
    
    def extract_keywords_from_description(self, description: str) -> List[str]:
        """Extract keywords from description."""
        all_keywords = self.keyword_manager.get_all_keywords()
        extracted = []
        
        description_lower = description.lower()
        
        for category, keyword_list in all_keywords.items():
            for keyword in keyword_list:
                if keyword.lower() in description_lower:
                    extracted.append(keyword)
        
        return list(set(extracted))  # Remove duplicates
    
    def get_jobs_dataframe(self) -> pd.DataFrame:
        """Get jobs as DataFrame."""
        jobs = self.get_all_jobs()
        data = []
        
        for job_id, job_info in jobs.items():
            data.append({
                'Job ID': job_id,
                'Title': job_info['title'],
                'Keywords': ', '.join(job_info['keywords']),
                'Created': job_info['created_at'],
                'Updated': job_info['updated_at']
            })
        
        return pd.DataFrame(data)


def display_keyword_management(keyword_manager: KeywordManager):
    """Display keyword management interface."""
    
    st.subheader("🔑 Keyword Management")
    
    tab1, tab2, tab3 = st.tabs(["View Keywords", "Add Keywords", "Manage Categories"])
    
    # Tab 1: View Keywords
    with tab1:
        st.markdown("### 📊 All Keywords")
        
        keywords = keyword_manager.get_all_keywords()
        
        if keywords:
            # Display statistics
            stats = keyword_manager.get_statistics()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Categories", stats['total_categories'])
            with col2:
                st.metric("Total Keywords", stats['total_keywords'])
            with col3:
                avg_keywords = stats['total_keywords'] / stats['total_categories'] if stats['total_categories'] > 0 else 0
                st.metric("Avg Keywords/Category", f"{avg_keywords:.1f}")
            
            st.markdown("---")
            
            # Display by category
            for category, keyword_list in keywords.items():
                with st.expander(f"**{category}** ({len(keyword_list)} keywords)", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        keywords_text = ", ".join(keyword_list)
                        st.write(keywords_text)
                    
                    with col2:
                        if st.button("📋 Copy", key=f"copy_{category}"):
                            st.write(keywords_text)
        else:
            st.info("No keywords found")
    
    # Tab 2: Add Keywords
    with tab2:
        st.markdown("### ➕ Add Keywords")
        
        category = st.selectbox(
            "Select Category",
            options=keyword_manager.get_categories()
        )
        
        keywords_input = st.text_area(
            "Enter keywords (one per line)",
            height=200,
            placeholder="Python\nJava\nJavaScript"
        )
        
        if st.button("✅ Add Keywords"):
            if keywords_input.strip():
                keywords_list = [kw.strip() for kw in keywords_input.split('\n') if kw.strip()]
                added_count = 0
                
                for keyword in keywords_list:
                    if keyword_manager.add_keyword(category, keyword):
                        added_count += 1
                
                st.success(f"✅ Added {added_count} new keyword(s)")
                st.rerun()
            else:
                st.warning("Please enter keywords")
    
    # Tab 3: Manage Categories
    with tab3:
        st.markdown("### 📁 Manage Categories")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Add New Category")
            new_category = st.text_input("Category name")
            
            if st.button("➕ Add Category"):
                if new_category:
                    if keyword_manager.add_category(new_category):
                        st.success(f"✅ Category '{new_category}' added")
                        st.rerun()
                    else:
                        st.warning("Category already exists")
                else:
                    st.warning("Please enter category name")
        
        with col2:
            st.markdown("#### Delete Category")
            category_to_delete = st.selectbox(
                "Select category to delete",
                options=keyword_manager.get_categories(),
                key="delete_category"
            )
            
            if st.button("🗑️ Delete Category"):
                if keyword_manager.delete_category(category_to_delete):
                    st.success(f"✅ Category deleted")
                    st.rerun()


if __name__ == "__main__":
    km = KeywordManager()
    display_keyword_management(km)
