"""
Database Management Module
Handle resume databases, user authentication, and match history via SQLite.
"""

import hashlib
import json
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

DEFAULT_USERS = [
    {
        "email": "admin@example.com",
        "password": "admin123",
        "role": "admin"
    },
    {
        "email": "recruiter@example.com",
        "password": "recruiter123",
        "role": "recruiter"
    }
]


class DatabaseManager:
    """Manage resume databases, users, and match history with SQLite."""

    def __init__(self,
                 db_folder: str = "data/databases",
                 db_file: str = "data/resumes.db"):
        self.workspace_root = Path(__file__).resolve().parents[1]
        self.db_folder = self.workspace_root / db_folder
        self.db_file = self.workspace_root / db_file
        self.metadata_file = self.db_folder / "metadata.json"

        self.ensure_folders_exist()
        self.init_db()

    def ensure_folders_exist(self):
        """Create required folders and metadata file."""
        os.makedirs(self.db_folder, exist_ok=True)
        os.makedirs(self.db_file.parent, exist_ok=True)

        if not os.path.exists(self.metadata_file):
            self.save_metadata({})

    def connect(self) -> sqlite3.Connection:
        """Open a SQLite connection with row access by column name."""
        conn = sqlite3.connect(self.db_file, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        """Create the SQLite schema if it does not already exist."""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS resumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    database_name TEXT NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    resume_text TEXT,
                    processed_text TEXT,
                    uploaded_by TEXT,
                    uploaded_at TEXT NOT NULL,
                    description TEXT,
                    source_file TEXT,
                    score REAL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS match_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT,
                    job_description TEXT,
                    candidate_name TEXT,
                    similarity_score REAL,
                    rank INTEGER,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storage."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def seed_demo_users(self):
        """Seed default demo users into the SQLite database."""
        with self.connect() as conn:
            cursor = conn.cursor()
            for user in DEFAULT_USERS:
                existing = cursor.execute(
                    "SELECT id FROM users WHERE email = ?",
                    (user["email"],)
                ).fetchone()

                if existing is None:
                    cursor.execute(
                        "INSERT INTO users (email, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                        (
                            user["email"],
                            self.hash_password(user["password"]),
                            user["role"],
                            datetime.now().isoformat()
                        )
                    )
            conn.commit()

    def add_user(self, email: str, password: str, role: str) -> bool:
        """Add a new user record to the database."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (email, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                    (email, self.hash_password(password), role, datetime.now().isoformat())
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Retrieve a user record by email."""
        with self.connect() as conn:
            cursor = conn.cursor()
            row = cursor.execute(
                "SELECT email, password_hash, role, created_at FROM users WHERE email = ?",
                (email,)
            ).fetchone()
            return dict(row) if row is not None else None

    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Verify user credentials and return the user record."""
        user = self.get_user_by_email(email)
        if user is None:
            return None

        if self.hash_password(password) == user["password_hash"]:
            return user

        return None

    def save_metadata(self, metadata: dict):
        """Save metadata to JSON."""
        try:
            with open(self.metadata_file, "w", encoding="utf-8") as file:
                json.dump(metadata, file, indent=4)
            logger.info("Metadata saved")
        except Exception as exc:
            logger.error(f"Error saving metadata: {exc}")

    def load_metadata(self) -> dict:
        """Load database metadata from JSON."""
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return {}

    def validate_resume_data(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """Validate resume data before inserting into the database."""
        if df.empty:
            return False, "File is empty"

        required_columns = ["name", "email", "phone"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}"

        if df["email"].duplicated().any():
            return False, "?? Warning: Duplicate emails found"

        for col in required_columns:
            if df[col].isnull().any():
                null_count = int(df[col].isnull().sum())
                return False, f"Missing values in '{col}' ({null_count} rows)"

        return True, "Validation passed"

    def _build_resume_text(self, row: pd.Series) -> str:
        text_columns = [
            col for col in row.index if isinstance(row[col], str) and col.lower() not in ["name", "email", "phone"]
        ]
        return " ".join(str(row[col]) for col in text_columns if str(row[col]).strip())

    def insert_resumes(self, df: pd.DataFrame, database_name: str,
                       description: str = "", uploaded_by: str = "system") -> Tuple[bool, str]:
        """Insert resume records into the database and save an archive CSV."""
        try:
            if df.empty:
                return False, "No data to insert"

            if "resume_text" not in df.columns:
                df["resume_text"] = df.apply(self._build_resume_text, axis=1)

            if "processed_text" not in df.columns:
                try:
                    from preprocess import TextPreprocessor
                    preprocessor = TextPreprocessor()
                    df["processed_text"] = df["resume_text"].fillna("").apply(preprocessor.preprocess_text)
                except Exception:
                    df["processed_text"] = df["resume_text"].fillna("")

            is_valid, message = self.validate_resume_data(df)
            if not is_valid and "required columns" in message or "empty" in message:
                return False, message

            filename = f"{database_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = self.db_folder / filename
            df.to_csv(filepath, index=False)

            metadata = self.load_metadata()
            metadata[database_name] = {
                "filename": filename,
                "filepath": str(filepath),
                "total_resumes": int(len(df)),
                "columns": list(df.columns),
                "description": description,
                "uploaded_at": datetime.now().isoformat(),
                "uploaded_by": uploaded_by,
                "size_mb": os.path.getsize(filepath) / (1024 * 1024)
            }
            self.save_metadata(metadata)

            with self.connect() as conn:
                cursor = conn.cursor()
                for _, row in df.iterrows():
                    cursor.execute(
                        "INSERT INTO resumes (database_name, name, email, phone, resume_text, processed_text, uploaded_by, uploaded_at, description, source_file) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            database_name,
                            str(row.get("name", "Unknown")),
                            str(row.get("email", "unknown@example.com")),
                            str(row.get("phone", "0000000000")),
                            str(row.get("resume_text", "")),
                            str(row.get("processed_text", "")),
                            uploaded_by,
                            datetime.now().isoformat(),
                            description,
                            str(row.get("source_file", "upload"))
                        )
                    )
                conn.commit()

            logger.info(f"Inserted {len(df)} resumes into database '{database_name}'")
            return True, f"Successfully inserted {len(df)} resumes into database '{database_name}'"
        except Exception as exc:
            logger.error(f"Error inserting resumes: {exc}")
            return False, f"Error: {exc}"

    def load_database(self, database_name: str) -> Optional[pd.DataFrame]:
        """Load a resume database from SQLite."""
        try:
            with self.connect() as conn:
                query = "SELECT * FROM resumes WHERE database_name = ?"
                df = pd.read_sql_query(query, conn, params=(database_name,))
                if df.empty:
                    return None
                return df
        except Exception as exc:
            logger.error(f"Error loading database: {exc}")
            return None

    def get_all_databases(self) -> List[str]:
        """Return all database names stored in resumes table."""
        with self.connect() as conn:
            cursor = conn.cursor()
            rows = cursor.execute(
                "SELECT DISTINCT database_name FROM resumes ORDER BY database_name"
            ).fetchall()
            return [row[0] for row in rows]

    def get_all_users(self) -> List[Dict]:
        """Return all user records."""
        with self.connect() as conn:
            rows = conn.execute("SELECT email, role, created_at FROM users ORDER BY created_at DESC").fetchall()
            return [dict(row) for row in rows]

    def get_database_info(self, database_name: str) -> Optional[dict]:
        """Return metadata for a database."""
        metadata = self.load_metadata()
        return metadata.get(database_name)

    def delete_database(self, database_name: str) -> bool:
        """Delete all records and metadata for a database."""
        try:
            metadata = self.load_metadata()
            if database_name in metadata:
                filepath = metadata[database_name].get("filepath")
                if filepath and os.path.exists(filepath):
                    os.remove(filepath)
                del metadata[database_name]
                self.save_metadata(metadata)

            with self.connect() as conn:
                conn.execute("DELETE FROM resumes WHERE database_name = ?", (database_name,))
                conn.commit()

            logger.info(f"Deleted database '{database_name}'")
            return True
        except Exception as exc:
            logger.error(f"Error deleting database: {exc}")
            return False

    def export_database(self, database_name: str, format: str = "csv") -> Optional[bytes]:
        """Export resume database to CSV or Excel bytes."""
        df = self.load_database(database_name)
        if df is None:
            return None

        try:
            if format == "csv":
                return df.to_csv(index=False).encode("utf-8")
            elif format == "excel":
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Resumes")
                buffer.seek(0)
                return buffer.read()
        except Exception as exc:
            logger.error(f"Error exporting database: {exc}")
            return None

        return None

    def get_database_statistics(self, database_name: str) -> Optional[dict]:
        """Return statistics for a database."""
        df = self.load_database(database_name)
        if df is None:
            return None

        return {
            "row_count": int(len(df)),
            "column_count": int(len(df.columns)),
            "columns": list(df.columns),
            "memory_usage": float(df.memory_usage(deep=True).sum() / 1024 / 1024),
            "missing_values": df.isnull().sum().to_dict(),
            "duplicates": int(df.duplicated().sum())
        }

    def merge_databases(self, database_names: List[str], merged_name: str) -> Tuple[bool, str]:
        """Merge multiple databases into a new database."""
        try:
            dfs = []
            for name in database_names:
                df = self.load_database(name)
                if df is not None:
                    dfs.append(df)

            if not dfs:
                return False, "No databases to merge"

            merged_df = pd.concat(dfs, ignore_index=True)
            if "email" in merged_df.columns:
                merged_df = merged_df.drop_duplicates(subset=["email"], keep="first")

            return self.insert_resumes(merged_df, merged_name, description=f"Merged from: {', '.join(database_names)}")
        except Exception as exc:
            logger.error(f"Error merging databases: {exc}")
            return False, f"? Error: {exc}"

    def search_resume(self, database_name: str, email: str) -> Optional[dict]:
        """Search for a resume record by email."""
        try:
            with self.connect() as conn:
                query = "SELECT * FROM resumes WHERE database_name = ? AND LOWER(email) = LOWER(?)"
                row = conn.execute(query, (database_name, email)).fetchone()
                return dict(row) if row is not None else None
        except Exception as exc:
            logger.error(f"Error searching resume: {exc}")
            return None

    def insert_match_history(self, user_email: str, job_description: str, matches: List[Dict]) -> Tuple[bool, str]:
        """Save match history entries for a user."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                for match in matches:
                    cursor.execute(
                        "INSERT INTO match_history (user_email, job_description, candidate_name, similarity_score, rank, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            user_email,
                            job_description,
                            match.get("candidate_name") or match.get("Candidate Name"),
                            float(match.get("similarity_score", 0.0)),
                            int(match.get("rank", 0)),
                            datetime.now().isoformat()
                        )
                    )
                conn.commit()
            return True, "Match history saved"
        except Exception as exc:
            logger.error(f"Error saving match history: {exc}")
            return False, f"Error: {exc}"

    def get_match_history(self, user_email: Optional[str] = None) -> List[Dict]:
        """Retrieve saved match history for a user or all users."""
        try:
            with self.connect() as conn:
                if user_email:
                    rows = conn.execute(
                        "SELECT * FROM match_history WHERE LOWER(user_email) = LOWER(?) ORDER BY created_at DESC",
                        (user_email,)
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT * FROM match_history ORDER BY created_at DESC"
                    ).fetchall()
                return [dict(row) for row in rows]
        except Exception as exc:
            logger.error(f"Error loading match history: {exc}")
            return []


def display_database_upload():
    """Display database upload interface."""
    st.subheader("Upload Resume Database")
    
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
            if uploaded_file.name.endswith('csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.markdown("#### File Preview")
            st.dataframe(df.head(10))
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Duplicates", len(df[df.duplicated()]))
            with col4:
                st.metric("Missing Values", int(df.isnull().sum().sum()))
            
            db_manager = DatabaseManager()
            is_valid, message = db_manager.validate_resume_data(df)
            st.info(message)
            
            if st.button("Upload Database"):
                if is_valid or "Warning" in message:
                    success, msg = db_manager.insert_resumes(
                        df,
                        database_name,
                        description,
                        uploaded_by=st.session_state.get('user_email', 'system')
                    )
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Fix validation errors before uploading")
        except Exception as exc:
            st.error(f"Error reading file: {exc}")
    elif uploaded_file and not database_name:
        st.warning("Please enter a database name")


def display_database_management():
    """Display database management interface."""
    st.subheader("Database Management")
    
    db_manager = DatabaseManager()
    databases = db_manager.get_all_databases()
    
    if not databases:
        st.info("No databases uploaded yet")
        return
    
    tab1, tab2, tab3 = st.tabs(["View Databases", "Merge Databases", "Search Resume"])
    
    with tab1:
        st.markdown("### ?? Uploaded Databases")
        
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
                    if info.get('description'):
                        st.markdown(f"**Description:** {info['description']}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("??? Preview", key=f"preview_{db_name}"):
                            df = db_manager.load_database(db_name)
                            st.dataframe(df.head(20))
                    
                    with col2:
                        if st.button("?? Download", key=f"download_{db_name}"):
                            csv_data = db_manager.export_database(db_name, 'csv')
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name=f"{db_name}.csv",
                                mime="text/csv"
                            )
                    
                    with col3:
                        if st.button("??? Delete", key=f"delete_{db_name}"):
                            if db_manager.delete_database(db_name):
                                st.success("Database deleted")
                                st.rerun()
    
    with tab2:
        st.markdown("### ?? Merge Databases")
        
        selected_dbs = st.multiselect(
            "Select databases to merge",
            options=databases,
            min_selections=2
        )
        
        merged_name = st.text_input("Merged database name")
        
        if st.button("? Merge"):
            if selected_dbs and merged_name:
                success, msg = db_manager.merge_databases(selected_dbs, merged_name)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    
    with tab3:
        st.markdown("### ?? Search Resume")
        
        search_db = st.selectbox("Select database", options=databases)
        search_email = st.text_input("Search by email")
        
        if st.button("?? Search"):
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
