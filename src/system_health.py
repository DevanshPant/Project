"""
System Health Check Module
Verify system functionality and integrity
"""

import os
import sys
import json
import time
import logging
import streamlit as st
from typing import Dict, List, Tuple
from datetime import datetime
import importlib.util

logger = logging.getLogger(__name__)


class SystemHealthMonitor:
    """Monitor system health and perform diagnostics."""
    
    def __init__(self, src_folder: str = "src", data_folder: str = "data"):
        """Initialize health monitor."""
        self.src_folder = src_folder
        self.data_folder = data_folder
        self.required_modules = [
            'data_loader',
            'preprocess',
            'feature_extraction',
            'model',
            'matcher',
            'utils',
            'auth',
            'keywords',
            'database'
        ]
        self.health_report = {}
    
    def check_module_imports(self) -> Dict[str, bool]:
        """Check if all required modules can be imported."""
        results = {}
        
        for module_name in self.required_modules:
            try:
                module_path = os.path.join(self.src_folder, f"{module_name}.py")
                
                if not os.path.exists(module_path):
                    results[module_name] = False
                    logger.warning(f"Module {module_name} not found")
                    continue
                
                # Try to import
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                results[module_name] = True
                logger.info(f"Module {module_name} imported successfully")
            
            except Exception as e:
                results[module_name] = False
                logger.error(f"Error importing {module_name}: {str(e)}")
        
        return results
    
    def check_data_folders(self) -> Dict[str, bool]:
        """Check if required data folders exist."""
        results = {}
        required_folders = [
            'data',
            'data/databases',
            'outputs',
            'outputs/matches',
            'outputs/reports'
        ]
        
        for folder in required_folders:
            exists = os.path.exists(folder)
            results[folder] = exists
            
            if exists:
                logger.info(f"Folder {folder} exists")
            else:
                logger.warning(f"Folder {folder} not found")
        
        return results
    
    def check_data_files(self) -> Dict[str, Dict]:
        """Check status of data files."""
        results = {}
        
        data_files = {
            'data/keywords.json': 'Keywords storage',
            'data/job_descriptions.json': 'Job descriptions',
            'data/resumes.db': 'Resume database',
            'data/metadata.json': 'Database metadata'
        }
        
        for filepath, description in data_files.items():
            if os.path.exists(filepath):
                size = os.path.getsize(filepath) / 1024  # KB
                modified_time = datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                
                results[filepath] = {
                    'exists': True,
                    'size_kb': round(size, 2),
                    'modified': modified_time,
                    'description': description
                }
                logger.info(f"File {filepath} exists ({size:.2f} KB)")
            else:
                results[filepath] = {
                    'exists': False,
                    'description': description
                }
                logger.warning(f"File {filepath} not found")
        
        return results
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required packages are installed."""
        results = {}
        
        required_packages = [
            'pandas',
            'numpy',
            'sklearn',
            'nltk',
            'streamlit',
            'openpyxl',
            'kagglehub'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                results[package] = True
                logger.info(f"Package {package} is installed")
            except ImportError:
                results[package] = False
                logger.warning(f"Package {package} is not installed")
        
        return results
    
    def check_file_permissions(self) -> Dict[str, bool]:
        """Check read/write permissions."""
        results = {}
        
        test_folders = [
            'data',
            'outputs'
        ]
        
        for folder in test_folders:
            try:
                # Test write permission
                test_file = os.path.join(folder, '.test_write')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                
                results[folder] = True
                logger.info(f"Write permission OK for {folder}")
            except:
                results[folder] = False
                logger.error(f"No write permission for {folder}")
        
        return results
    
    def check_data_integrity(self) -> Dict[str, any]:
        """Check data integrity."""
        results = {
            'keywords_valid': False,
            'jobs_valid': False,
            'databases_valid': False
        }
        
        # Check keywords.json
        try:
            if os.path.exists('data/keywords.json'):
                with open('data/keywords.json', 'r') as f:
                    keywords = json.load(f)
                    results['keywords_valid'] = isinstance(keywords, dict) and len(keywords) > 0
                    logger.info(f"Keywords file valid ({len(keywords)} categories)")
        except:
            logger.error("Keywords file corrupted")
        
        # Check job_descriptions.json
        try:
            if os.path.exists('data/job_descriptions.json'):
                with open('data/job_descriptions.json', 'r') as f:
                    jobs = json.load(f)
                    results['jobs_valid'] = isinstance(jobs, dict)
                    logger.info(f"Jobs file valid ({len(jobs)} jobs)")
        except:
            logger.error("Jobs file corrupted")
        
        # Check databases
        try:
            if os.path.exists('data/metadata.json'):
                with open('data/metadata.json', 'r') as f:
                    metadata = json.load(f)
                    results['databases_valid'] = isinstance(metadata, dict)
                    logger.info(f"Databases metadata valid ({len(metadata)} databases)")
        except:
            logger.error("Databases metadata corrupted")
        
        return results
    
    def check_system_performance(self) -> Dict[str, float]:
        """Check system performance metrics."""
        results = {}
        
        # Test import speed
        start = time.time()
        try:
            import pandas
            import numpy
            from sklearn.feature_extraction.text import TfidfVectorizer
            import nltk
        except:
            pass
        results['import_time_ms'] = (time.time() - start) * 1000
        
        return results
    
    def run_full_health_check(self) -> Dict:
        """Run complete health check."""
        self.health_report = {
            'timestamp': datetime.now().isoformat(),
            'modules': self.check_module_imports(),
            'folders': self.check_data_folders(),
            'files': self.check_data_files(),
            'dependencies': self.check_dependencies(),
            'permissions': self.check_file_permissions(),
            'data_integrity': self.check_data_integrity(),
            'performance': self.check_system_performance()
        }
        
        return self.health_report
    
    def get_health_summary(self) -> str:
        """Get health summary."""
        if not self.health_report:
            return "No health report available"
        
        modules_ok = all(self.health_report['modules'].values())
        folders_ok = all(self.health_report['folders'].values())
        dependencies_ok = all(self.health_report['dependencies'].values())
        permissions_ok = all(self.health_report['permissions'].values())
        
        if modules_ok and folders_ok and dependencies_ok and permissions_ok:
            return "✅ SYSTEM HEALTHY - All checks passed"
        
        issues = []
        if not modules_ok:
            failed = [m for m, ok in self.health_report['modules'].items() if not ok]
            issues.append(f"Failed modules: {', '.join(failed)}")
        if not folders_ok:
            missing = [f for f, ok in self.health_report['folders'].items() if not ok]
            issues.append(f"Missing folders: {', '.join(missing)}")
        if not dependencies_ok:
            missing = [p for p, ok in self.health_report['dependencies'].items() if not ok]
            issues.append(f"Missing packages: {', '.join(missing)}")
        if not permissions_ok:
            denied = [f for f, ok in self.health_report['permissions'].items() if not ok]
            issues.append(f"Permission denied: {', '.join(denied)}")
        
        return "⚠️ SYSTEM ISSUES:\n" + "\n".join([f"• {issue}" for issue in issues])


def display_system_health_check():
    """Display system health check interface."""
    
    st.subheader("🏥 System Health Check")
    
    if st.button("▶️ Run Health Check", use_container_width=True):
        with st.spinner("Checking system health..."):
            monitor = SystemHealthMonitor()
            report = monitor.run_full_health_check()
        
        # Summary
        st.markdown("### 📊 Health Summary")
        summary = monitor.get_health_summary()
        if "HEALTHY" in summary:
            st.success(summary)
        else:
            st.warning(summary)
        
        st.markdown("---")
        
        # Detailed report
        col1, col2, col3 = st.columns(3)
        
        # Modules
        with col1:
            st.markdown("### 📦 Modules")
            modules = report['modules']
            passed = sum(1 for v in modules.values() if v)
            total = len(modules)
            st.metric("Modules OK", f"{passed}/{total}")
            
            for module, ok in modules.items():
                status = "✅" if ok else "❌"
                st.write(f"{status} {module}")
        
        # Dependencies
        with col2:
            st.markdown("### 📚 Dependencies")
            deps = report['dependencies']
            passed = sum(1 for v in deps.values() if v)
            total = len(deps)
            st.metric("Packages OK", f"{passed}/{total}")
            
            for package, ok in deps.items():
                status = "✅" if ok else "❌"
                st.write(f"{status} {package}")
        
        # Folders
        with col3:
            st.markdown("### 📁 Folders")
            folders = report['folders']
            passed = sum(1 for v in folders.values() if v)
            total = len(folders)
            st.metric("Folders OK", f"{passed}/{total}")
            
            for folder, ok in folders.items():
                status = "✅" if ok else "❌"
                st.write(f"{status} {folder}")
        
        st.markdown("---")
        
        # Detailed checks
        with st.expander("📄 **Detailed Report**", expanded=False):
            st.json(report)
        
        # Recommendations
        st.markdown("### 💡 Recommendations")
        
        issues = []
        if not all(report['modules'].values()):
            issues.append("❌ Some modules failed to import - check syntax and dependencies")
        if not all(report['folders'].values()):
            issues.append("⚠️ Missing folders - run setup.py to create them")
        if not all(report['dependencies'].values()):
            issues.append("⚠️ Missing packages - run `pip install -r requirements.txt`")
        if not all(report['permissions'].values()):
            issues.append("❌ Permission issues - check folder access rights")
        
        if issues:
            for issue in issues:
                st.write(issue)
        else:
            st.success("✅ No issues detected. System is ready to use!")


def display_system_tests():
    """Display system tests interface."""
    
    st.subheader("🧪 System Tests")
    
    tabs = st.tabs(["Quick Tests", "Data Tests", "Performance Tests"])
    
    # Quick Tests
    with tabs[0]:
        st.markdown("### ⚡ Quick Tests")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Test Module Imports"):
                monitor = SystemHealthMonitor()
                results = monitor.check_module_imports()
                
                passed = sum(1 for v in results.values() if v)
                total = len(results)
                
                if all(results.values()):
                    st.success(f"All modules imported successfully ({passed}/{total})")
                else:
                    st.warning(f"Some modules failed ({passed}/{total})")
                    for module, ok in results.items():
                        status = "✅" if ok else "❌"
                        st.write(f"{status} {module}")
        
        with col2:
            if st.button("✅ Test Dependencies"):
                monitor = SystemHealthMonitor()
                results = monitor.check_dependencies()
                
                passed = sum(1 for v in results.values() if v)
                total = len(results)
                
                if all(results.values()):
                    st.success(f"All dependencies installed ({passed}/{total})")
                else:
                    st.warning(f"Some packages missing ({passed}/{total})")
                    for package, ok in results.items():
                        status = "✅" if ok else "❌"
                        st.write(f"{status} {package}")
    
    # Data Tests
    with tabs[1]:
        st.markdown("### 📊 Data Tests")
        
        if st.button("✅ Check Data Integrity"):
            monitor = SystemHealthMonitor()
            results = monitor.check_data_integrity()
            
            for check, status in results.items():
                emoji = "✅" if status else "❌"
                st.write(f"{emoji} {check}")
    
    # Performance Tests
    with tabs[2]:
        st.markdown("### ⚡ Performance Tests")
        
        if st.button("⏱️ Measure System Performance"):
            monitor = SystemHealthMonitor()
            perf = monitor.check_system_performance()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Import Time", f"{perf['import_time_ms']:.2f}ms")


if __name__ == "__main__":
    display_system_health_check()
    st.markdown("---")
    display_system_tests()
