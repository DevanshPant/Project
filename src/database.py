"""
Database Management Module
Handle resume database uploads, parsing, and management
"""

import os
import json
import pandas as pd
import streamlit as st
from typing import List, Optional, Tuple
from datetime import datetime
import logging
import sqlite3

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage resume databases and imports."""
    
    def __init__(self, db_folder: str = "data/databases", db_file: str = "data/resumes.db"):
        """
        Initialize database manager.
        
        Args:
            db_folder: Folder for uploaded CSV/Excel files
            db_file: SQLite database file
        """
        self.db_folder = db_folder
        self.db_file = db_file
        self.metadata_file = os.path.join(db_folder, "metadata.json")
        self.ensure_folders_exist()
    
    def ensure_folders_exist(self):
        """Create necessary folders."""
        os.makedirs(self.db_folder, exist_ok=True)
        
        # Initialize metadata file
        if not os.path.exists(self.metadata_file):
            self.save_metadata({})
    
    def save_metadata(self, metadata: dict):
        """Save upload metadata."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
            logger.info("Metadata saved")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def load_metadata(self) -> dict:
        """Load upload metadata."""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def validate_resume_data(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate resume data.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        # Check if DataFrame is empty
        if df.empty:
            return False, "❌ File is empty"
        
        # Check required columns
        required_columns = ['name', 'email', 'phone']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"❌ Missing required columns: {', '.join(missing_columns)}"
        
        # Check for duplicate emails
        if df['email'].duplicated().any():
            return False, "⚠️ Warning: Duplicate emails found"
        
        # Check for empty values in required columns
        for col in required_columns:
            if df[col].isnull().any():
                null_count = df[col].isnull().sum()
                return False, f"❌ Missing values in '{col}' ({null_count} rows)"
        
        return True, "✅ Validation passed"
    
    def insert_resumes(self, df: pd.DataFrame, database_name: str, 
                      description: str = "") -> Tuple[bool, str]:
        """Insert resumes into database."""
        try:
            # Validate data
            is_valid, message = self.validate_resume_data(df)
            if not is_valid and "required columns" in message or "empty" in message:
                return False, message
            
            # Save to CSV
            filename = f"{database_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(self.db_folder, filename)
            df.to_csv(filepath, index=False)
            
            # Update metadata
            metadata = self.load_metadata()
            metadata[database_name] = {
                'filename': filename,
                'filepath': filepath,
                'total_resumes': len(df),
                'columns': list(df.columns),
                'description': description,
                'uploaded_at': datetime.now().isoformat(),
                'size_mb': os.path.getsize(filepath) / (1024 * 1024)
            }
            self.save_metadata(metadata)
            
            logger.info(f"Inserted {len(df)} resumes from {filename}")
            return True, f"✅ Successfully inserted {len(df)} resumes"
        
        except Exception as e:
            logger.error(f"Error inserting resumes: {e}")
            return False, f"❌ Error: {str(e)}"
    
    def load_database(self, database_name: str) -> Optional[pd.DataFrame]:
        """Load resume database."""
        try:
            metadata = self.load_metadata()
            
            if database_name not in metadata:
                return None
            
            filepath = metadata[database_name]['filepath']
            
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                logger.info(f"Loaded database {database_name}")
                return df
            
            return None
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            return None
    
    def get_all_databases(self) -> List[str]:
        """Get list of all databases."""
        metadata = self.load_metadata()
        return list(metadata.keys())
    
    def get_database_info(self, database_name: str) -> Optional[dict]:
        """Get database information."""
        metadata = self.load_metadata()
        return metadata.get(database_name)
    
    def delete_database(self, database_name: str) -> bool:
        """Delete a database."""
        try:
            metadata = self.load_metadata()
            
            if database_name in metadata:
                filepath = metadata[database_name]['filepath']
                
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                del metadata[database_name]
                self.save_metadata(metadata)
                
                logger.info(f"Deleted database {database_name}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error deleting database: {e}")
            return False
    
    def export_database(self, database_name: str, format: str = 'csv') -> Optional[bytes]:
        """Export database to bytes."""
        try:
            df = self.load_database(database_name)
            
            if df is None:
                return None
            
            if format == 'csv':
                return df.to_csv(index=False).encode()
            elif format == 'excel':
                return df.to_excel(index=False).encode()
            
            return None
        except Exception as e:
            logger.error(f"Error exporting database: {e}")
            return None
    
    def get_database_statistics(self, database_name: str) -> Optional[dict]:
        """Get statistics for a database."""
        try:
            df = self.load_database(database_name)
            
            if df is None:
                return None
            
            stats = {
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': list(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum() / 1024 / 1024,  # MB
                'missing_values': df.isnull().sum().to_dict(),
                'duplicates': len(df[df.duplicated()])
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return None
    
    def merge_databases(self, database_names: List[str], 
                       merged_name: str) -> Tuple[bool, str]:
        """Merge multiple databases."""
        try:
            dfs = []
            
            for db_name in database_names:
                df = self.load_database(db_name)
                if df is not None:
                    dfs.append(df)
            
            if not dfs:
                return False, "No databases to merge"
            
            # Merge dataframes
            merged_df = pd.concat(dfs, ignore_index=True)
            
            # Remove duplicates
            merged_df = merged_df.drop_duplicates(subset=['email'], keep='first')
            
            # Insert merged database
            success, message = self.insert_resumes(
                merged_df, 
                merged_name,
                description=f"Merged from: {', '.join(database_names)}"
            )
            
            return success, message
        except Exception as e:
            logger.error(f"Error merging databases: {e}")
            return False, f"Error: {str(e)}"
    
    def search_resume(self, database_name: str, email: str) -> Optional[dict]:
        """Search for resume by email."""
        try:
            df = self.load_database(database_name)
            
            if df is None:
                return None
            
            result = df[df['email'].str.lower() == email.lower()]
            
            if result.empty:
                return None
            
            return result.iloc[0].to_dict()
        except Exception as e:
            logger.error(f"Error searching resume: {e}")
            return None


def display_database_upload():
    """Display database upload interface."""
    
    st.subheader("📤 Upload Resume Database")
    
    col1, col2 = st.columns(2)
    
    with col1:
        database_name = st.text_input(
            "Database Name",
            placeholder="e.g., Finance-Dept-Resumes"
        )
    
    with col2:
        description = st.text_area(
            "Description",
            placeholder="Optional: Add details about this database",
            height=50
        )
    
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=['csv', 'xlsx', 'xls']
    )
    
    if uploaded_file and database_name:
        try:
            # Read file
            if uploaded_file.name.endswith('csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Show preview
            st.markdown("#### 📋 File Preview")
            st.dataframe(df.head(10))
            
            # Show statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Duplicates", len(df[df.duplicated()]))
            with col4:
                st.metric("Missing Values", df.isnull().sum().sum())
            
            # Validate
            db_manager = DatabaseManager()
            is_valid, message = db_manager.validate_resume_data(df)
            st.info(message)
            
            # Insert button
            if st.button("✅ Upload Database"):
                if is_valid or "Warning" in message:
                    success, msg = db_manager.insert_resumes(
                        df, 
                        database_name,
                        description
                    )
                    
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Fix validation errors before uploading")
        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    
    elif uploaded_file and not database_name:
        st.warning("Please enter a database name")


def display_database_management():
    """Display database management interface."""
    
    st.subheader("💾 Database Management")
    
    db_manager = DatabaseManager()
    databases = db_manager.get_all_databases()
    
    if not databases:
        st.info("No databases uploaded yet")
        return
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["View Databases", "Merge Databases", "Search Resume"])
    
    # Tab 1: View Databases
    with tab1:
        st.markdown("### 📊 Uploaded Databases")
        
        for db_name in databases:
            info = db_manager.get_database_info(db_name)
            stats = db_manager.get_database_statistics(db_name)
            
            if info and stats:
                with st.expander(f"**{db_name}** ({stats['row_count']} resumes)", expanded=False):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Resumes", stats['row_count'])
                    with col2:
                        st.metric("Columns", stats['column_count'])
                    with col3:
                        st.metric("Duplicates", stats['duplicates'])
                    with col4:
                        st.metric("Size (MB)", f"{stats['memory_usage']:.2f}")
                    
                    st.markdown(f"**Uploaded:** {info['uploaded_at']}")
                    if info['description']:
                        st.markdown(f"**Description:** {info['description']}")
                    
                    # Button row
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("👁️ Preview", key=f"preview_{db_name}"):
                            df = db_manager.load_database(db_name)
                            st.dataframe(df.head(20))
                    
                    with col2:
                        if st.button("📥 Download", key=f"download_{db_name}"):
                            csv_data = db_manager.export_database(db_name, 'csv')
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name=f"{db_name}.csv",
                                mime="text/csv"
                            )
                    
                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_{db_name}"):
                            if db_manager.delete_database(db_name):
                                st.success("Database deleted")
                                st.rerun()
    
    # Tab 2: Merge Databases
    with tab2:
        st.markdown("### 🔗 Merge Databases")
        
        selected_dbs = st.multiselect(
            "Select databases to merge",
            options=databases,
            min_selections=2
        )
        
        merged_name = st.text_input("Merged database name")
        
        if st.button("✅ Merge"):
            if selected_dbs and merged_name:
                success, msg = db_manager.merge_databases(selected_dbs, merged_name)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    
    # Tab 3: Search Resume
    with tab3:
        st.markdown("### 🔍 Search Resume")
        
        search_db = st.selectbox("Select database", options=databases)
        search_email = st.text_input("Search by email")
        
        if st.button("🔍 Search"):
            if search_email:
                result = db_manager.search_resume(search_db, search_email)
                
                if result:
                    st.success("Resume found!")
                    st.json(result)
                else:
                    st.warning("Resume not found")


if __name__ == "__main__":
    display_database_upload()
    st.markdown("---")
    display_database_management()
