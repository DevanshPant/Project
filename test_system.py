#!/usr/bin/env python
"""
Quick Start Test Script
Demonstrates all key features of the Resume Screening System
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.data_loader import DataLoader
from src.preprocess import TextPreprocessor
from src.feature_extraction import FeatureExtractor, TFIDFFeatureExtractor
from src.matcher import ResumeJobMatcher, CandidateShortlister
from src.utils import DataExporter, compare_tfidf_vs_bert
from main import ResomeScreeningPipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_text_preprocessing():
    """Test NLP preprocessing module."""
    print("\n" + "="*80)
    print("TEST 1: TEXT PREPROCESSING")
    print("="*80)
    
    sample_text = """
    John Doe
    Email: john@example.com | Phone: (555) 123-4567
    
    Senior Software Engineer with 7+ years experience in Python, Java, and Machine Learning.
    Experience with TensorFlow, Scikit-learn, and Data Science platforms.
    """
    
    preprocessor = TextPreprocessor()
    
    print(f"\n📋 ORIGINAL TEXT:\n{sample_text}\n")
    
    processed = preprocessor.preprocess_text(sample_text)
    print(f"🔄 PROCESSED TEXT:\n{processed}\n")
    
    report = preprocessor.get_preprocessing_report(sample_text, processed)
    print(f"📊 STATISTICS:")
    for key, value in report.items():
        print(f"   {key}: {value}")


def test_feature_extraction():
    """Test TF-IDF feature extraction."""
    print("\n" + "="*80)
    print("TEST 2: FEATURE EXTRACTION (TF-IDF)")
    print("="*80)
    
    documents = [
        "python machine learning tensorflow data science",
        "java spring boot backend development microservices",
        "javascript react frontend web development",
        "python machine learning deep learning neural networks",
    ]
    
    extractor = TFIDFFeatureExtractor(max_features=50)
    tfidf_matrix = extractor.fit_transform(documents)
    
    print(f"\n📊 TF-IDF MATRIX SHAPE: {tfidf_matrix.shape}")
    print(f"   Documents: {tfidf_matrix.shape[0]}")
    print(f"   Features: {tfidf_matrix.shape[1]}\n")
    
    print("🏆 TOP FEATURES FOR EACH DOCUMENT:\n")
    for i, doc in enumerate(documents):
        print(f"Document {i}: {doc}")
        top_features = extractor.get_top_features(i, top_n=5)
        for feature, score in top_features:
            print(f"   - {feature}: {score:.4f}")
        print()


def test_resume_matching():
    """Test resume-job matching."""
    print("\n" + "="*80)
    print("TEST 3: RESUME-JOB MATCHING")
    print("="*80)
    
    # Sample resumes
    resumes = [
        "Senior Python Developer with 8 years ML TensorFlow scikit-learn experience",
        "Full stack JavaScript React Node.js Web Developer",
        "Python Data Scientist machine learning deep learning neural networks",
        "Java Backend Engineer microservices Spring Boot",
        "Junior Developer starting career learning programming basics",
    ]
    
    # Job description
    job = "Senior Python ML Engineer with TensorFlow and Scikit-learn expertise"
    
    # Preprocess
    preprocessor = TextPreprocessor()
    processed_resumes = [preprocessor.preprocess_text(r) for r in resumes]
    processed_job = preprocessor.preprocess_text(job)
    
    # Extract features
    extractor = FeatureExtractor()
    all_texts = processed_resumes + [processed_job]
    tfidf_matrix = extractor.tfidf_extractor.fit_transform(all_texts)
    
    resume_features = tfidf_matrix[:-1]
    job_features = tfidf_matrix[-1]
    
    # Match
    matcher = ResumeJobMatcher()
    candidate_info = [{'id': i, 'name': f'Candidate_{i+1}'} for i in range(len(resumes))]
    matches = matcher.match_resumes_to_job(resume_features, job_features, candidate_info, top_n=5)
    
    print(f"\nJob Description: {job}\n")
    print(matcher.get_matches_dataframe().to_string(index=False))
    
    stats = matcher.get_summary_statistics()
    print(f"\n📊 Statistics:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.4f}")
        else:
            print(f"   {key}: {value}")


def test_candidate_shortlisting():
    """Test candidate shortlisting."""
    print("\n" + "="*80)
    print("TEST 4: CANDIDATE SHORTLISTING")
    print("="*80)
    
    # Reuse matches from previous test (simplified)
    class SimpleMatch:
        def __init__(self, id, name, score, rank):
            self.candidate_id = id
            self.candidate_name = name
            self.similarity_score = score
            self.rank = rank
    
    matches = [
        SimpleMatch(0, 'John', 0.92, 1),
        SimpleMatch(1, 'Jane', 0.87, 2),
        SimpleMatch(2, 'Bob', 0.76, 3),
        SimpleMatch(3, 'Alice', 0.54, 4),
        SimpleMatch(4, 'Chris', 0.32, 5),
    ]
    
    shortlister = CandidateShortlister(threshold=0.4)
    shortlist = shortlister.shortlist_candidates(matches, top_n=3)
    
    print(f"\n✂️ SHORTLIST THRESHOLD: 0.4\n")
    print(shortlist.to_string(index=False))
    
    stats = shortlister.get_statistics(matches)
    print(f"\n📊 Statistics:")
    for key, value in stats.items():
        if isinstance(value, (int, float)):
            print(f"   {key}: {value:.2f}" if isinstance(value, float) else f"   {key}: {value}")


def test_export_functionality():
    """Test data export functionality."""
    print("\n" + "="*80)
    print("TEST 5: DATA EXPORT")
    print("="*80)
    
    import pandas as pd
    
    # Sample DataFrame
    data = {
        'Rank': [1, 2, 3],
        'Candidate Name': ['John Doe', 'Jane Smith', 'Bob Wilson'],
        'Similarity Score': [0.92, 0.87, 0.76],
        'Score Percentage': ['92%', '87%', '76%']
    }
    df = pd.DataFrame(data)
    
    exporter = DataExporter('outputs')
    
    print(f"\n📤 EXPORTING TEST DATA:\n")
    print(df.to_string(index=False))
    
    # Export
    csv_path = exporter.export_to_csv(df, 'test_export.csv')
    excel_path = exporter.export_to_excel(df, 'test_export.xlsx')
    json_path = exporter.export_to_json(df.to_dict(orient='records'), 'test_export.json')
    
    print(f"\n✅ EXPORTS COMPLETED:")
    print(f"   CSV: {csv_path}")
    print(f"   Excel: {excel_path}")
    print(f"   JSON: {json_path}")


def test_complete_pipeline():
    """Test complete end-to-end pipeline."""
    print("\n" + "="*80)
    print("TEST 6: COMPLETE PIPELINE")
    print("="*80)
    
    # Sample data
    resumes = [
        """
        Senior Python Engineer
        10+ years software development
        Machine Learning, TensorFlow, Scikit-learn
        Deep Learning, Neural Networks
        """,
        """
        Full Stack JavaScript Developer
        6 years web development
        React, Node.js, MongoDB
        REST APIs, microservices
        """,
        """
        Data Scientist
        5 years analytics
        Python, R, Tableau
        Machine Learning, Statistics
        """
    ]
    
    job_description = """
    Senior ML Engineer
    
    We seek experienced ML engineers with:
    - 8+ years Python development
    - TensorFlow and PyTorch expertise
    - Deep learning experience
    - Production ML systems
    """
    
    # Run pipeline
    pipeline = ResomeScreeningPipeline()
    
    print("\n🚀 RUNNING COMPLETE PIPELINE...\n")
    
    results = pipeline.run_complete_pipeline(
        resumes=resumes,
        job_description=job_description,
        candidate_names=['Python Engineer', 'JS Developer', 'Data Scientist'],
        shortlist_threshold=0.3,
        top_candidates=3,
        export_format='csv'
    )
    
    print("\n✅ PIPELINE COMPLETED!")
    print(f"\n📊 RESULTS:\n{results['shortlist'].to_string(index=False)}")


def test_algorithm_comparison():
    """Display TF-IDF vs BERT comparison."""
    print("\n" + "="*80)
    print("TEST 7: ALGORITHM COMPARISON")
    print("="*80)
    
    print(compare_tfidf_vs_bert())


def run_all_tests():
    """Run all tests."""
    print("\n\n")
    print("🎯" * 40)
    print("RESUME SCREENING SYSTEM - COMPREHENSIVE TEST SUITE")
    print("🎯" * 40)
    
    tests = [
        ("Text Preprocessing", test_text_preprocessing),
        ("Feature Extraction", test_feature_extraction),
        ("Resume Matching", test_resume_matching),
        ("Candidate Shortlisting", test_candidate_shortlisting),
        ("Export Functionality", test_export_functionality),
        ("Complete Pipeline", test_complete_pipeline),
        ("Algorithm Comparison", test_algorithm_comparison),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Error: {str(e)}")
            failed += 1
    
    # Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ PASSED: {passed}/{len(tests)}")
    print(f"❌ FAILED: {failed}/{len(tests)}")
    print("="*80 + "\n")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! System is ready for use.\n")
    else:
        print(f"⚠️ {failed} test(s) failed. Please review errors above.\n")


if __name__ == "__main__":
    run_all_tests()
