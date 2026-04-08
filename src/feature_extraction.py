"""
Feature Extraction Module - Convert text to TF-IDF vectors and other features
"""

import logging
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from typing import Tuple, List, Optional, Dict
import pickle
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TFIDFFeatureExtractor:
    """
    TF-IDF (Term Frequency-Inverse Document Frequency) Feature Extraction.
    
    Why TF-IDF?
    - Reflects how important a word is to a document in a collection of documents
    - Reduces impact of common words across all documents (stopwords)
    - Gives high weight to rare but meaningful terms
    - Simple, interpretable, and computationally efficient
    - Works well for text classification and similarity matching
    
    Attributes:
        vectorizer (TfidfVectorizer): Scikit-learn TF-IDF vectorizer
        feature_names (list): List of feature names (terms)
        tfidf_matrix (sparse matrix): TF-IDF feature matrix
    """
    
    def __init__(self, max_features: int = 5000, max_df: float = 0.95, 
                 min_df: int = 2, ngram_range: Tuple[int, int] = (1, 2)):
        """
        Initialize TF-IDF Feature Extractor.
        
        Args:
            max_features (int): Maximum number of features to extract
            max_df (float): Ignore terms that appear in more than max_df% of documents
            min_df (int): Ignore terms that appear in fewer than min_df documents
            ngram_range (Tuple): Range of n-grams (1,1) = unigrams, (1,2) = unigrams+bigrams
        """
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            max_df=max_df,
            min_df=min_df,
            ngram_range=ngram_range,
            strip_accents='unicode',
            lowercase=True,
            analyzer='word',
            token_pattern=r'\w{1,}',
            stop_words='english'
        )
        
        self.feature_names = None
        self.tfidf_matrix = None
        
        logger.info("TF-IDF Feature Extractor initialized")
        logger.info(f"  Max Features: {max_features}")
        logger.info(f"  Max DF: {max_df}")
        logger.info(f"  Min DF: {min_df}")
        logger.info(f"  N-gram Range: {ngram_range}")
    
    def fit(self, texts: List[str]) -> np.ndarray:
        """
        Fit TF-IDF vectorizer on texts and return feature matrix.
        
        Args:
            texts (List[str]): List of text documents
        
        Returns:
            np.ndarray: TF-IDF feature matrix (dense array)
        """
        logger.info(f"Fitting TF-IDF vectorizer on {len(texts)} documents...")
        
        # Fit and transform
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        self.feature_names = self.vectorizer.get_feature_names_out()
        
        logger.info(f"TF-IDF matrix shape: {self.tfidf_matrix.shape}")
        logger.info(f"  Documents (rows): {self.tfidf_matrix.shape[0]}")
        logger.info(f"  Features (columns): {self.tfidf_matrix.shape[1]}")
        
        return self.tfidf_matrix.toarray()
    
    def transform(self, texts: List[str]) -> np.ndarray:
        """
        Transform texts using fitted vectorizer.
        
        Args:
            texts (List[str]): List of text documents
        
        Returns:
            np.ndarray: TF-IDF feature matrix (dense array)
        """
        logger.info(f"Transforming {len(texts)} documents...")
        matrix = self.vectorizer.transform(texts)
        logger.info(f"Transformed matrix shape: {matrix.shape}")
        return matrix.toarray()
    
    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """
        Fit and transform in one step.
        
        Args:
            texts (List[str]): List of text documents
        
        Returns:
            np.ndarray: TF-IDF feature matrix (dense array)
        """
        return self.fit(texts)
    
    def get_feature_names(self) -> List[str]:
        """
        Get list of feature names (terms).
        
        Returns:
            List[str]: List of terms
        """
        return list(self.feature_names) if self.feature_names is not None else []
    
    def get_top_features(self, doc_index: int = 0, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Get top N features for a specific document.
        
        Args:
            doc_index (int): Document index in the matrix
            top_n (int): Number of top features to return
        
        Returns:
            List[Tuple[str, float]]: List of (feature_name, tfidf_score) tuples
        """
        if self.tfidf_matrix is None:
            logger.error("TF-IDF matrix not fitted yet")
            return []
        
        if doc_index >= self.tfidf_matrix.shape[0]:
            logger.error(f"Document index {doc_index} out of range")
            return []
        
        # Get TF-IDF scores for document
        doc_tfidf = self.tfidf_matrix[doc_index].toarray().flatten()
        
        # Get top indices
        top_indices = np.argsort(doc_tfidf)[-top_n:][::-1]
        
        # Create result list
        top_features = [(self.feature_names[i], doc_tfidf[i]) for i in top_indices if doc_tfidf[i] > 0]
        
        return top_features
    
    def save_vectorizer(self, filepath: str):
        """Save fitted vectorizer to file."""
        logger.info(f"Saving vectorizer to {filepath}")
        with open(filepath, 'wb') as f:
            pickle.dump(self.vectorizer, f)
    
    def load_vectorizer(self, filepath: str):
        """Load vectorizer from file."""
        logger.info(f"Loading vectorizer from {filepath}")
        with open(filepath, 'rb') as f:
            self.vectorizer = pickle.load(f)
        self.feature_names = self.vectorizer.get_feature_names_out()


class FeatureExtractor:
    """
    Main Feature Extraction handler combining multiple extraction methods.
    """
    
    def __init__(self):
        """Initialize Feature Extractor."""
        self.tfidf_extractor = TFIDFFeatureExtractor()
        self.logger = logger
    
    def extract_features(self, texts: List[str], method: str = 'tfidf') -> np.ndarray:
        """
        Extract features using specified method.
        
        Args:
            texts (List[str]): List of text documents
            method (str): Feature extraction method ('tfidf')
        
        Returns:
            np.ndarray: Feature matrix
        """
        if method == 'tfidf':
            return self.tfidf_extractor.fit_transform(texts)
        else:
            self.logger.error(f"Unknown feature extraction method: {method}")
            raise ValueError(f"Unknown method: {method}")
    
    def extract_resume_and_job_features(self, resumes: List[str], 
                                       job_description: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract features for resumes and job description.
        Important: Fit on combined texts to ensure same feature space.
        
        Args:
            resumes (List[str]): List of resume texts
            job_description (str): Job description text
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: (resume_features, job_features)
        """
        self.logger.info("Extracting features for resumes and job description...")
        
        # Combine all texts for fitting to ensure same feature space
        all_texts = resumes + [job_description]
        
        # Fit on all texts
        tfidf_matrix = self.tfidf_extractor.fit_transform(all_texts)
        
        # Separate resume and job features
        resume_features = tfidf_matrix[:len(resumes)]
        job_features = tfidf_matrix[-1:][0]  # Last one is job description
        
        self.logger.info(f"Resume features shape: {resume_features.shape}")
        self.logger.info(f"Job features shape: {job_features.shape}")
        
        return resume_features, job_features
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics of extracted features."""
        if self.tfidf_extractor.tfidf_matrix is None:
            return {}
        
        matrix = self.tfidf_extractor.tfidf_matrix.toarray()
        
        stats = {
            'total_documents': matrix.shape[0],
            'total_features': matrix.shape[1],
            'sparsity': 1 - (np.count_nonzero(matrix) / matrix.size),
            'mean_tfidf': float(np.mean(matrix)),
            'max_tfidf': float(np.max(matrix)),
            'min_tfidf': float(np.min(matrix))
        }
        
        return stats


def demonstrate_tfidf_extraction():
    """Demonstrate TF-IDF feature extraction."""
    
    logger.info("=" * 80)
    logger.info("TF-IDF FEATURE EXTRACTION DEMONSTRATION")
    logger.info("=" * 80)
    
    # Sample documents
    documents = [
        "machine learning is fascinating field",
        "deep learning uses neural networks",
        "natural language processing with machine learning",
        "data science and machine learning applications",
    ]
    
    # Create and fit TF-IDF extractor
    extractor = TFIDFFeatureExtractor(max_features=20)
    tfidf_matrix = extractor.fit_transform(documents)
    
    logger.info(f"\nDocuments processed: {len(documents)}")
    logger.info(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
    
    logger.info("\nTOP 5 FEATURES FOR EACH DOCUMENT:")
    for i, (doc, tfidf_scores) in enumerate(zip(documents, tfidf_matrix)):
        logger.info(f"\nDocument {i}: {doc}")
        top_features = extractor.get_top_features(i, top_n=5)
        for feature, score in top_features:
            logger.info(f"  {feature}: {score:.4f}")
    
    logger.info("\nAll extracted features:")
    logger.info(extractor.get_feature_names())


if __name__ == "__main__":
    demonstrate_tfidf_extraction()
