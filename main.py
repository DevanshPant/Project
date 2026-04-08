"""
Main Orchestrator - Complete Resume Screening Pipeline
Coordinates all modules for end-to-end resume screening
"""

import sys
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.data_loader import DataLoader
from src.preprocess import TextPreprocessor
from src.feature_extraction import FeatureExtractor
from src.model import ClassificationModel, ModelComparator, ClusteringModel
from src.matcher import ResumeJobMatcher, CandidateShortlister
from src.utils import DataExporter, ResultsFormatter, Logger, compare_tfidf_vs_bert, scalability_analysis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResomeScreeningPipeline:
    """
    Complete Resume Screening & Shortlisting Pipeline.
    Orchestrates all components for end-to-end processing.
    """
    
    def __init__(self, output_dir: str = "outputs"):
        """
        Initialize pipeline.
        
        Args:
            output_dir (str): Output directory for results
        """
        self.output_dir = output_dir
        self.data_loader = None
        self.preprocessor = TextPreprocessor()
        self.feature_extractor = FeatureExtractor()
        self.matcher = ResumeJobMatcher()
        self.exporter = DataExporter(output_dir)
        
        logger.info("Resume Screening Pipeline initialized")
    
    def load_dataset(self, use_kaggle: bool = False) -> pd.DataFrame:
        """
        Load resume dataset.
        
        Args:
            use_kaggle (bool): If True, download from Kaggle
        
        Returns:
            pd.DataFrame: Loaded dataset
        """
        logger.info("=" * 80)
        logger.info("STEP 1: DATA LOADING")
        logger.info("=" * 80)
        
        self.data_loader = DataLoader()
        
        if use_kaggle:
            self.data_loader.download_dataset()
        
        df = self.data_loader.load_dataset()
        
        # Inspect dataset
        info = self.data_loader.inspect_dataset()
        
        # Handle missing values
        df = self.data_loader.handle_missing_values(strategy='drop')
        
        # Remove duplicates
        df = self.data_loader.remove_duplicates()
        
        logger.info(f"Dataset loaded successfully: {df.shape}")
        
        return df
    
    def preprocess_texts(self, texts: List[str]) -> List[str]:
        """
        Preprocess resume texts.
        
        Args:
            texts (List[str]): Raw resume texts
        
        Returns:
            List[str]: Preprocessed texts
        """
        logger.info("=" * 80)
        logger.info("STEP 2: NLP PREPROCESSING")
        logger.info("=" * 80)
        
        logger.info(f"Preprocessing {len(texts)} documents...")
        
        processed_texts = [self.preprocessor.preprocess_text(text) for text in texts]
        
        logger.info(f"Preprocessing completed. Sample:")
        logger.info(f"  Original: {texts[0][:100]}...")
        logger.info(f"  Processed: {processed_texts[0][:100]}...")
        
        return processed_texts
    
    def extract_features(self, processed_texts: List[str], method: str = 'tfidf') -> np.ndarray:
        """
        Extract features from texts.
        
        Args:
            processed_texts (List[str]): Preprocessed texts
            method (str): Feature extraction method
        
        Returns:
            np.ndarray: Feature matrix
        """
        logger.info("=" * 80)
        logger.info("STEP 3: FEATURE EXTRACTION (TF-IDF)")
        logger.info("=" * 80)
        
        logger.info("Why TF-IDF?")
        logger.info("  - Reflects importance of word in document collection")
        logger.info("  - Reduces impact of common words")
        logger.info("  - Gives high weight to rare meaningful terms")
        logger.info("  - Simple, interpretable, and efficient")
        
        features = self.feature_extractor.extract_features(processed_texts, method=method)
        
        logger.info(f"Feature extraction completed")
        logger.info(f"  Feature matrix shape: {features.shape}")
        logger.info(f"  Features: {features.shape[1]}")
        
        stats = self.feature_extractor.get_summary_statistics()
        logger.info(f"  Sparsity: {stats.get('sparsity', 'N/A'):.4f}")
        
        return features
    
    def train_models(self, features: np.ndarray, labels: Optional[np.ndarray] = None):
        """
        Train classification models (if labels available).
        
        Args:
            features (np.ndarray): Feature matrix
            labels (Optional[np.ndarray]): Target labels
        
        Returns:
            Tuple: (is_supervised, results)
        """
        logger.info("=" * 80)
        logger.info("STEP 4: MODEL TRAINING")
        logger.info("=" * 80)
        
        if labels is not None:
            logger.info("Labeled dataset detected - Training classification models")
            
            from sklearn.model_selection import train_test_split
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, labels, test_size=0.2, random_state=42
            )
            
            # Train and compare models
            comparator = ModelComparator([
                'logistic_regression',
                'naive_bayes',
                'svm',
                'random_forest'
            ])
            
            comparator.train_all_models(X_train, y_train)
            results = comparator.evaluate_all_models(X_test, y_test)
            
            logger.info("Model training completed")
            return True, results
        else:
            logger.info("Unlabeled dataset - Using unsupervised approach (Clustering)")
            
            clustering = ClusteringModel(n_clusters=5)
            labels_pred = clustering.fit(features)
            
            logger.info(f"Clustering completed with {5} clusters")
            return False, labels_pred
    
    def match_candidates(self, resume_features: np.ndarray, 
                        job_description: str,
                        processed_resumes: List[str],
                        candidate_names: Optional[List[str]] = None,
                        top_n: int = 10) -> Tuple[pd.DataFrame, dict]:
        """
        Match resumes with job description.
        
        Args:
            resume_features (np.ndarray): Resume feature vectors
            job_description (str): Job description text
            processed_resumes (List[str]): Preprocessed resume texts
            candidate_names (Optional[List[str]]): Candidate names
            top_n (int): Number of top candidates to return
        
        Returns:
            Tuple: (results_dataframe, statistics)
        """
        logger.info("=" * 80)
        logger.info("STEP 5: RESUME-JOB MATCHING")
        logger.info("=" * 80)
        
        # Preprocess job description
        processed_job = self.preprocessor.preprocess_text(job_description)
        
        # Combine all texts for consistent feature space
        all_texts = processed_resumes + [processed_job]
        
        # Extract features with combined vocabulary
        tfidf_matrix_combined = self.feature_extractor.tfidf_extractor.vectorizer.fit_transform(all_texts).toarray()
        
        resume_features_updated = tfidf_matrix_combined[:-1]
        job_features = tfidf_matrix_combined[-1]
        
        # Create candidate info
        if candidate_names is None:
            candidate_names = [f'Candidate_{i}' for i in range(len(resume_features_updated))]
        
        candidate_info = [
            {'id': i, 'name': name}
            for i, name in enumerate(candidate_names)
        ]
        
        # Match candidates
        matches = self.matcher.match_resumes_to_job(
            resume_features_updated,
            job_features,
            candidate_info,
            top_n=top_n
        )
        
        # Get results
        results_df = self.matcher.get_matches_dataframe()
        stats = self.matcher.get_summary_statistics()
        
        logger.info(f"Matching completed. Results:")
        logger.info(f"\n{results_df.to_string(index=False)}")
        
        return results_df, stats, matches
    
    def shortlist_candidates(self, matches, threshold: float = 0.3, 
                            top_n: int = 5) -> pd.DataFrame:
        """
        Shortlist candidates.
        
        Args:
            matches: List of CandidateMatch objects
            threshold (float): Minimum similarity score
            top_n (int): Maximum candidates to shortlist
        
        Returns:
            pd.DataFrame: Shortlisted candidates
        """
        logger.info("=" * 80)
        logger.info("STEP 6: CANDIDATE SHORTLISTING")
        logger.info("=" * 80)
        
        shortlister = CandidateShortlister(threshold=threshold)
        shortlist_df = shortlister.shortlist_candidates(matches, top_n=top_n)
        
        logger.info(f"Shortlisting completed")
        logger.info(f"\n{shortlist_df.to_string(index=False)}")
        
        return shortlist_df
    
    def export_results(self, results_df: pd.DataFrame, 
                      shortlist_df: pd.DataFrame,
                      export_format: str = 'all') -> dict:
        """
        Export results to files.
        
        Args:
            results_df (pd.DataFrame): All results
            shortlist_df (pd.DataFrame): Shortlisted candidates
            export_format (str): Format to export ('csv', 'excel', 'json', 'all')
        
        Returns:
            dict: Paths to exported files
        """
        logger.info("=" * 80)
        logger.info("STEP 7: OUTPUT GENERATION")
        logger.info("=" * 80)
        
        exported_files = {}
        
        if export_format in ['csv', 'all']:
            csv_path = self.exporter.export_to_csv(shortlist_df, 'shortlisted_candidates.csv')
            exported_files['csv'] = csv_path
        
        if export_format in ['excel', 'all']:
            excel_path = self.exporter.export_to_excel(shortlist_df, 'shortlisted_candidates.xlsx', 
                                                       include_charts=True)
            exported_files['excel'] = excel_path
        
        if export_format in ['json', 'all']:
            json_data = {
                'candidates': shortlist_df.to_dict(orient='records'),
                'export_date': pd.Timestamp.now().isoformat()
            }
            json_path = self.exporter.export_to_json(json_data, 'results.json')
            exported_files['json'] = json_path
        
        logger.info(f"Results exported: {exported_files}")
        return exported_files
    
    def run_complete_pipeline(self, resumes: List[str], job_description: str,
                             candidate_names: Optional[List[str]] = None,
                             shortlist_threshold: float = 0.3,
                             top_candidates: int = 10,
                             export_format: str = 'all'):
        """
        Run complete pipeline end-to-end.
        
        Args:
            resumes (List[str]): List of resume texts
            job_description (str): Job description text
            candidate_names (Optional[List[str]]): Candidate names
            shortlist_threshold (float): Shortlisting threshold
            top_candidates (int): Top N candidates to include
            export_format (str): Export format
        
        Returns:
            dict: Pipeline results
        """
        logger.info("\n" + "=" * 80)
        logger.info("RESUME SCREENING & SHORTLISTING PIPELINE")
        logger.info("=" * 80 + "\n")
        
        try:
            # Step 2: Preprocess
            processed_resumes = self.preprocess_texts(resumes)
            
            # Step 3: Extract features
            resume_features = self.extract_features(processed_resumes)
            
            # Step 5: Match candidates
            results_df, stats, matches = self.match_candidates(
                resume_features,
                job_description,
                processed_resumes,
                candidate_names,
                top_n=top_candidates
            )
            
            # Step 6: Shortlist
            shortlist_df = self.shortlist_candidates(matches, 
                                                    threshold=shortlist_threshold,
                                                    top_n=5)
            
            # Step 7: Export
            exported_files = self.export_results(results_df, shortlist_df, export_format)
            
            logger.info("\n" + "=" * 80)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 80 + "\n")
            
            return {
                'results': results_df,
                'shortlist': shortlist_df,
                'statistics': stats,
                'exported_files': exported_files
            }
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            raise


def run_demo():
    """Run demonstration with sample resumes."""
    
    logger.info("LAUNCHING RESUME SCREENING SYSTEM DEMONSTRATION")
    
    # Sample resumes
    resumes = [
        """
        John Doe
        Senior Software Engineer
        Email: john@example.com | Phone: (555) 123-4567
        
        SUMMARY
        Experienced software engineer with 7+ years in Python and machine learning.
        
        SKILLS
        Python, Java, C++, Machine Learning, TensorFlow, Scikit-learn, Data Science
        
        EXPERIENCE
        Senior Engineer at TechCorp (2020-Present)
        - Developed ML models for recommendation systems
        - Led team of 5 engineers
        - Improved system performance by 40%
        
        EDUCATION
        B.S. Computer Science - University (2016)
        """,
        
        """
        Jane Smith
        Data Science Manager
        Email: jane@example.com | Phone: (555) 234-5678
        
        SUMMARY
        Data science professional with 6+ years experience in analytics and BI.
        
        SKILLS
        Python, SQL, Tableau, Power BI, Excel, Business Intelligence, Analytics
        
        EXPERIENCE
        Data Science Lead at DataCorp (2019-Present)
        - Built analytical dashboards
        - Managed data pipelines
        
        EDUCATION
        M.S. Statistics - University (2018)
        """,
        
        """
        Bob Wilson
        Full Stack Developer
        Email: bob@example.com | Phone: (555) 345-6789
        
        SUMMARY
        Web developer with expertise in JavaScript and React.
        
        SKILLS
        JavaScript, React, Node.js, CSS, HTML, MongoDB, Express
        
        EXPERIENCE
        Frontend Developer at WebInc (2018-Present)
        - Built responsive web applications
        - Collaborated with design team
        
        EDUCATION
        Bootcamp Certification - Code Academy (2017)
        """
    ]
    
    # Job description
    job_description = """
    Senior Python Machine Learning Engineer
    
    We are seeking a Senior Python Engineer with expertise in Machine Learning 
    and Data Science. The ideal candidate will have:
    
    Requirements:
    - 5+ years of Python programming experience
    - Strong background in machine learning and deep learning
    - Experience with TensorFlow, Scikit-learn, or similar frameworks
    - Proficiency in data science and statistics
    - Bachelor's degree in Computer Science or related field
    
    Responsibilities:
    - Develop and deploy machine learning models
    - Write clean, maintainable Python code
    - Collaborate with data scientists and engineers
    - Optimize model performance and scalability
    
    Nice to have:
    - Experience with distributed computing
    - Knowledge of cloud platforms (AWS, GCP)
    - Published research or contributions to open source
    """
    
    # Run pipeline
    pipeline = ResomeScreeningPipeline()
    
    results = pipeline.run_complete_pipeline(
        resumes=resumes,
        job_description=job_description,
        candidate_names=['John Doe', 'Jane Smith', 'Bob Wilson'],
        shortlist_threshold=0.3,
        top_candidates=3,
        export_format='all'
    )
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("FINAL SUMMARY")
    logger.info("=" * 80)
    logger.info(f"\nShortlisted Candidates:\n{results['shortlist'].to_string(index=False)}")
    logger.info(f"\nStatistics: {results['statistics']}")
    logger.info(f"\nExported Files: {results['exported_files']}")


if __name__ == "__main__":
    run_demo()
