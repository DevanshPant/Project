"""
Resume-Job Matching Module - Match resumes with job descriptions
"""

import logging
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class CandidateMatch:
    """Data class for storing matching results."""
    candidate_id: int
    candidate_name: str
    similarity_score: float
    rank: int
    top_matching_skills: List[str]


class ResumeJobMatcher:
    """
    Match resumes with job descriptions using cosine similarity.
    
    Why Cosine Similarity?
    - Measures angle between vectors, not magnitude
    - Works well with sparse TF-IDF vectors
    - Computationally efficient O(n*m)
    - Produces scores between 0-1 (easy to interpret)
    - Robust to document length differences
    """
    
    def __init__(self):
        """Initialize Resume-Job Matcher."""
        self.matches = []
        logger.info("Resume-Job Matcher initialized")
    
    @staticmethod
    def calculate_cosine_similarity(vector1: np.ndarray, vector2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Formula: similarity = (A · B) / (||A|| * ||B||)
        
        Args:
            vector1 (np.ndarray): First vector
            vector2 (np.ndarray): Second vector
        
        Returns:
            float: Similarity score between 0 and 1
        """
        if vector1.shape[0] == 0 or vector2.shape[0] == 0:
            return 0.0
        
        # Reshape 1D arrays for cosine_similarity function
        vector1 = vector1.reshape(1, -1)
        vector2 = vector2.reshape(1, -1)
        
        similarity = cosine_similarity(vector1, vector2)[0][0]
        return float(similarity)
    
    @staticmethod
    def calculate_batch_similarity(resume_vectors: np.ndarray, 
                                  job_vector: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarity between all resumes and a job description.
        More efficient than pairwise calculation.
        
        Args:
            resume_vectors (np.ndarray): Shape (n_resumes, n_features)
            job_vector (np.ndarray): Shape (n_features,) or (1, n_features)
        
        Returns:
            np.ndarray: Similarity scores for each resume
        """
        # Ensure job_vector is 2D
        if job_vector.ndim == 1:
            job_vector = job_vector.reshape(1, -1)
        
        # Calculate similarities for all resumes at once
        similarities = cosine_similarity(resume_vectors, job_vector).flatten()
        
        return similarities
    
    def match_resumes_to_job(self, resume_features: np.ndarray, 
                            job_features_vector: np.ndarray,
                            candidate_info: List[Dict],
                            top_n: int = 10) -> List[CandidateMatch]:
        """
        Match all resumes to job description and rank candidates.
        
        Args:
            resume_features (np.ndarray): TF-IDF vectors for resumes (n_resumes, n_features)
            job_features_vector (np.ndarray): TF-IDF vector for job description (n_features,)
            candidate_info (List[Dict]): List of dicts with 'id' and 'name' keys
            top_n (int): Return top N candidates
        
        Returns:
            List[CandidateMatch]: Ranked list of candidates
        """
        logger.info(f"Matching {len(resume_features)} resumes to job description...")
        
        # Calculate similarity scores for all resumes
        similarity_scores = self.calculate_batch_similarity(resume_features, job_features_vector)
        
        logger.info(f"  Min score: {similarity_scores.min():.4f}")
        logger.info(f"  Max score: {similarity_scores.max():.4f}")
        logger.info(f"  Mean score: {similarity_scores.mean():.4f}")
        
        # Create ranked list
        ranked_candidates = []
        
        # Sort by similarity score (descending)
        sorted_indices = np.argsort(similarity_scores)[::-1]
        
        for rank, idx in enumerate(sorted_indices[:top_n], 1):
            candidate = CandidateMatch(
                candidate_id=candidate_info[idx].get('id', idx),
                candidate_name=candidate_info[idx].get('name', f'Candidate_{idx}'),
                similarity_score=float(similarity_scores[idx]),
                rank=rank,
                top_matching_skills=[]  # Can be filled with feature names
            )
            ranked_candidates.append(candidate)
        
        self.matches = ranked_candidates
        logger.info(f"Matching completed. Top candidate score: {ranked_candidates[0].similarity_score:.4f}")
        
        return ranked_candidates
    
    def get_matches_dataframe(self) -> pd.DataFrame:
        """
        Convert matches to pandas DataFrame.
        
        Returns:
            pd.DataFrame: Matches in tabular format
        """
        data = [
            {
                'Rank': m.rank,
                'Candidate ID': m.candidate_id,
                'Candidate Name': m.candidate_name,
                'Similarity Score': m.similarity_score,
                'Score Percentage': f"{m.similarity_score * 100:.2f}%"
            }
            for m in self.matches
        ]
        
        return pd.DataFrame(data)
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics of matches."""
        if not self.matches:
            return {}
        
        scores = [m.similarity_score for m in self.matches]
        
        stats = {
            'total_candidates_matched': len(self.matches),
            'average_score': float(np.mean(scores)),
            'median_score': float(np.median(scores)),
            'max_score': float(np.max(scores)),
            'min_score': float(np.min(scores)),
            'std_dev': float(np.std(scores))
        }
        
        return stats
    
    @staticmethod
    def get_similarity_interpretation(score: float) -> str:
        """
        Interpret similarity score.
        
        Args:
            score (float): Similarity score between 0 and 1
        
        Returns:
            str: Interpretation of score
        """
        if score >= 0.8:
            return "Excellent Match"
        elif score >= 0.6:
            return "Good Match"
        elif score >= 0.4:
            return "Moderate Match"
        elif score >= 0.2:
            return "Weak Match"
        else:
            return "Poor Match"


class CandidateShortlister:
    """
    Shortlist candidates based on similarity scores and thresholds.
    """
    
    def __init__(self, threshold: float = 0.3):
        """
        Initialize shortlister.
        
        Args:
            threshold (float): Minimum similarity score to include candidate
        """
        self.threshold = threshold
        logger.info(f"CandidateShortlister initialized with threshold: {threshold}")
    
    def shortlist_candidates(self, matches: List[CandidateMatch], 
                            top_n: Optional[int] = None) -> pd.DataFrame:
        """
        Shortlist candidates based on threshold and/or top N.
        
        Args:
            matches (List[CandidateMatch]): List of matched candidates
            top_n (Optional[int]): Return only top N candidates
        
        Returns:
            pd.DataFrame: Shortlisted candidates
        """
        # Filter by threshold
        shortlisted = [m for m in matches if m.similarity_score >= self.threshold]
        
        logger.info(f"Shortlisted {len(shortlisted)} candidates (threshold: {self.threshold})")
        
        # Limit to top N if specified
        if top_n:
            shortlisted = shortlisted[:top_n]
            logger.info(f"Limited to top {top_n} candidates")
        
        # Convert to DataFrame
        data = []
        for candidate in shortlisted:
            data.append({
                'Rank': candidate.rank,
                'Candidate ID': candidate.candidate_id,
                'Candidate Name': candidate.candidate_name,
                'Similarity Score': round(candidate.similarity_score, 4),
                'Match Type': ResumeJobMatcher.get_similarity_interpretation(candidate.similarity_score),
                'Score Percentage': f"{candidate.similarity_score * 100:.2f}%"
            })
        
        df = pd.DataFrame(data)
        return df
    
    def get_statistics(self, matches: List[CandidateMatch]) -> Dict:
        """Get shortlisting statistics."""
        shortlisted = [m for m in matches if m.similarity_score >= self.threshold]
        all_scores = [m.similarity_score for m in matches]
        shortlist_scores = [m.similarity_score for m in shortlisted]
        
        stats = {
            'total_candidates': len(matches),
            'shortlisted_candidates': len(shortlisted),
            'shortlist_percentage': len(shortlisted) / len(matches) * 100,
            'threshold': self.threshold,
            'avg_score_all': float(np.mean(all_scores)),
            'avg_score_shortlisted': float(np.mean(shortlist_scores)) if shortlist_scores else 0
        }
        
        return stats


def main():
    """Test matching functionality"""
    
    logger.info("=" * 80)
    logger.info("RESUME-JOB MATCHING DEMONSTRATION")
    logger.info("=" * 80)
    
    # Create synthetic TF-IDF vectors
    n_resumes = 10
    n_features = 100
    
    # Random resume vectors
    resume_vectors = np.random.rand(n_resumes, n_features)
    
    # Job vector (slightly similar to first resume for demo)
    job_vector = resume_vectors[0] * 0.7 + np.random.rand(n_features) * 0.3
    
    # Create candidate info
    candidate_info = [
        {'id': i, 'name': f'Candidate_{i}'} for i in range(n_resumes)
    ]
    
    # Match resumes
    matcher = ResumeJobMatcher()
    matches = matcher.match_resumes_to_job(
        resume_vectors, 
        job_vector, 
        candidate_info, 
        top_n=5
    )
    
    logger.info("\nMatching Results:")
    logger.info(matcher.get_matches_dataframe().to_string(index=False))
    
    # Get statistics
    stats = matcher.get_summary_statistics()
    logger.info(f"\nStatistics: {stats}")
    
    # Shortlist candidates
    shortlister = CandidateShortlister(threshold=0.3)
    shortlist_df = shortlister.shortlist_candidates(matches, top_n=3)
    
    logger.info("\nShortlisted Candidates:")
    logger.info(shortlist_df.to_string(index=False))


if __name__ == "__main__":
    main()
