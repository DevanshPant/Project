"""
Resume Screening System Package
AI-Based Resume Screening & Candidate Shortlisting System

This package provides an end-to-end resume screening solution using NLP and ML.

Main Modules:
- data_loader: Load and preprocess resume datasets
- preprocess: NLP text preprocessing pipeline
- feature_extraction: TF-IDF vectorization
- model: ML model training and evaluation
- matcher: Resume-job matching and ranking
- utils: Utilities for export and formatting
- app: Streamlit web interface

Usage:
    from main import ResomeScreeningPipeline
    
    pipeline = ResomeScreeningPipeline()
    results = pipeline.run_complete_pipeline(
        resumes=['resume1', 'resume2'],
        job_description='Job description'
    )
"""

__version__ = "1.0.0"
__author__ = "AI/ML Team"
__license__ = "MIT"

from src.data_loader import DataLoader
from src.preprocess import TextPreprocessor, TextNormalizer
from src.feature_extraction import FeatureExtractor, TFIDFFeatureExtractor
from src.matcher import ResumeJobMatcher, CandidateShortlister
from src.utils import DataExporter, ResultsFormatter

__all__ = [
    'DataLoader',
    'TextPreprocessor',
    'TextNormalizer',
    'FeatureExtractor',
    'TFIDFFeatureExtractor',
    'ResumeJobMatcher',
    'CandidateShortlister',
    'DataExporter',
    'ResultsFormatter'
]
