"""
Utility Functions and Export Module
"""

import logging
import os
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataExporter:
    """
    Export screening results to various formats (CSV, Excel, JSON).
    """
    
    def __init__(self, output_dir: str = 'outputs'):
        """
        Initialize data exporter.
        
        Args:
            output_dir (str): Output directory for exported files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"DataExporter initialized with output directory: {output_dir}")
    
    def export_to_csv(self, df: pd.DataFrame, filename: str = None) -> str:
        """
        Export DataFrame to CSV file.
        
        Args:
            df (pd.DataFrame): DataFrame to export
            filename (str): Output filename (auto-generated if None)
        
        Returns:
            str: Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"candidates_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        df.to_csv(filepath, index=False)
        logger.info(f"Exported to CSV: {filepath}")
        
        return filepath
    
    def export_to_excel(self, df: pd.DataFrame, filename: str = None, 
                       include_charts: bool = False) -> str:
        """
        Export DataFrame to Excel file with formatting.
        
        Args:
            df (pd.DataFrame): DataFrame to export
            filename (str): Output filename (auto-generated if None)
            include_charts (bool): Include summary statistics
        
        Returns:
            str: Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"candidates_{timestamp}.xlsx"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Write main data
                df.to_excel(writer, sheet_name='Candidates', index=False)
                
                # Add summary sheet if requested
                if include_charts:
                    summary_df = self._create_summary_sheet(df)
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Format Excel
                workbook = writer.book
                worksheet = writer.sheets['Candidates']
                
                # Auto-adjust column widths
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(col)
                    )
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
            
            logger.info(f"Exported to Excel: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {str(e)}")
            raise
    
    def export_to_json(self, data: Dict, filename: str = None) -> str:
        """
        Export data to JSON file.
        
        Args:
            data (Dict): Data to export
            filename (str): Output filename (auto-generated if None)
        
        Returns:
            str: Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        
        logger.info(f"Exported to JSON: {filepath}")
        return filepath
    
    @staticmethod
    def _create_summary_sheet(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create summary statistics sheet.
        
        Args:
            df (pd.DataFrame): Main results dataframe
        
        Returns:
            pd.DataFrame: Summary statistics
        """
        summary = []
        
        if 'Similarity Score' in df.columns:
            scores = df['Similarity Score']
            summary.append({
                'Metric': 'Total Candidates',
                'Value': len(df)
            })
            summary.append({
                'Metric': 'Average Score',
                'Value': f"{scores.mean():.4f}"
            })
            summary.append({
                'Metric': 'Median Score',
                'Value': f"{scores.median():.4f}"
            })
            summary.append({
                'Metric': 'Max Score',
                'Value': f"{scores.max():.4f}"
            })
            summary.append({
                'Metric': 'Min Score',
                'Value': f"{scores.min():.4f}"
            })
        
        return pd.DataFrame(summary)


class ResultsFormatter:
    """
    Format and display results in various formats.
    """
    
    @staticmethod
    def format_results_table(matches_df: pd.DataFrame) -> str:
        """
        Format results as a table string.
        
        Args:
            matches_df (pd.DataFrame): Matches dataframe
        
        Returns:
            str: Formatted table
        """
        return matches_df.to_string(index=False)
    
    @staticmethod
    def format_candidate_card(candidate: Dict) -> str:
        """
        Format a single candidate as a card.
        
        Args:
            candidate (Dict): Candidate data
        
        Returns:
            str: Formatted card
        """
        card = f"""
        {'='*60}
        Candidate: {candidate.get('Candidate Name', 'N/A')}
        ID: {candidate.get('Candidate ID', 'N/A')}
        Rank: {candidate.get('Rank', 'N/A')}
        Similarity Score: {candidate.get('Similarity Score', 'N/A')}
        Match Type: {candidate.get('Match Type', 'N/A')}
        {'='*60}
        """
        return card
    
    @staticmethod
    def generate_report(shortlist_df: pd.DataFrame, job_description: str, 
                       statistics: Dict) -> str:
        """
        Generate complete screening report.
        
        Args:
            shortlist_df (pd.DataFrame): Shortlisted candidates
            job_description (str): Job description
            statistics (Dict): Screening statistics
        
        Returns:
            str: Formatted report
        """
        report = f"""
{'='*80}
                   RESUME SCREENING & SHORTLISTING REPORT
{'='*80}

SCREENING DATE: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

JOB DESCRIPTION PREVIEW:
{job_description[:200]}...

STATISTICS:
- Total Candidates Processed: {statistics.get('total_candidates', 0)}
- Shortlisted Candidates: {statistics.get('shortlisted_candidates', 0)}
- Shortlist Percentage: {statistics.get('shortlist_percentage', 0):.2f}%
- Average Score (All): {statistics.get('avg_score_all', 0):.4f}
- Average Score (Shortlisted): {statistics.get('avg_score_shortlisted', 0):.4f}

TOP CANDIDATES:
{shortlist_df.to_string(index=False)}

{'='*80}
        """
        return report


class Logger:
    """
    Custom logger for tracking system operations.
    """
    
    def __init__(self, log_file: str = 'resume_screening.log'):
        """Initialize logger."""
        self.log_file = log_file
        self.setup_logger()
    
    def setup_logger(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
    
    def get_logger(self, name: str):
        """Get logger instance."""
        return logging.getLogger(name)


def compare_tfidf_vs_bert():
    """
    Comparison between TF-IDF and BERT approaches.
    
    Returns:
        str: Comparison analysis
    """
    comparison = """
    ==================== TF-IDF vs BERT COMPARISON ====================
    
    TF-IDF (Used in this project):
    ✓ Advantages:
      - Lightweight and fast (O(n*m) complexity)
      - Interpretable (feature importance is clear)
      - Requires less training data
      - Works well for exact term matching
      - Memory efficient
    
    ✗ Disadvantages:
      - Ignores word order and context
      - Can't capture semantic meaning
      - Fixed vocabulary (OOV problem)
      - Performance plateaus with complex documents
    
    BERT (Advanced alternative):
    ✓ Advantages:
      - Understands semantic meaning and context
      - Captures word relationships
      - Pre-trained on massive corpus
      - Handles variations and synonyms better
    
    ✗ Disadvantages:
      - Computationally expensive
      - Requires more resources (GPU/TPU)
      - Larger model size
      - Slower inference time
      - Requires fine-tuning for domain-specific tasks
    
    Recommendation:
    - TF-IDF: For production systems needing speed and efficiency
    - BERT: For research or when budget allows for computation
    
    Hybrid Approach:
    - Use TF-IDF for initial screening (fast filtering)
    - Use BERT for candidates above threshold (accurate ranking)
    =====================================================================
    """
    return comparison


def scalability_analysis():
    """
    Scalability analysis of the system.
    
    Returns:
        str: Scalability considerations
    """
    analysis = """
    ==================== SCALABILITY ANALYSIS ====================
    
    Current System (TF-IDF + Cosine Similarity):
    - Handles: ~10,000 resumes easily
    - Processing time: O(n*m) where n=resumes, m=features
    - Memory usage: Lower (sparse matrices)
    
    Scaling to 100,000+ resumes:
    
    Option 1: Optimize TF-IDF
    ✓ Use sparse matrix operations
    ✓ Implement batch processing
    ✓ Parallelize using multiprocessing
    ✓ Use approximate nearest neighbors (Annoy, Faiss)
    
    Option 2: Add Caching Layer
    ✓ Cache TF-IDF vectors
    ✓ Pre-compute candidate clusters
    ✓ Use Redis for fast retrieval
    
    Option 3: Distributed Computing
    ✓ Spark for distributed TF-IDF computation
    ✓ Elasticsearch for fast similarity search
    ✓ Distributed clustering with Dask
    
    Option 4: Switch to BERT + Vector DB
    ✓ Generate BERT embeddings once
    ✓ Store in vector database (FAISS, Milvus, Weaviate)
    ✓ Use approximate nearest neighbor search
    ✓ Near real-time matching
    
    Recommended Path:
    1. Start: Current TF-IDF + Caching
    2. Scale: Implement batch processing + Annoy
    3. Enterprise: BERT + Vector Database + Distributed backend
    ================================================================
    """
    return analysis


def bias_reduction_strategies():
    """
    Strategies to reduce bias in resume screening.
    
    Returns:
        str: Bias reduction strategies
    """
    strategies = """
    ==================== BIAS REDUCTION IN RESUME SCREENING ====================
    
    Types of Bias:
    
    1. Educational Bias
       - Women/minorities may have non-traditional education paths
       - Solution: Weight experience equally with formal qualifications
    
    2. Name/Demographic Bias
       - Don't use candidate names in scoring (can infer demographics)
       - Solution: Remove names before TF-IDF extraction
    
    3. Gap Bias
       - Career gaps penalize caregivers disproportionately
       - Solution: Normalize timelines or ignore gaps
    
    4. Experience Bias
       - Years of experience alone don't predict performance
       - Solution: Use multiple factors (skills, achievements, growth)
    
    Implementation Strategies:
    
    ✓ Data Pre-processing:
      - Anonymize candidate names
      - Remove demographic information
      - Normalize date formats
    
    ✓ Feature Engineering:
      - Weight skills equally regardless of context
      - Normalize experience years
      - Capture transferable skills
    
    ✓ Model Level:
      - Use fairness-aware learning algorithms
      - Set minimum thresholds avoiding extreme cutoffs
      - Regular bias audits on hiring patterns
    
    ✓ Post-processing:
      - Monitor demographic distribution in matches
      - Enforce diversity in shortlists
      - Regular audits and adjustments
    
    ✓ Human Review:
      - Always have human review final shortlist
      - Transparent scoring criteria
      - Appeal process for candidates
    
    ==================================================================================
    """
    return strategies


def real_world_applicability():
    """
    Real-world applicability and deployment considerations.
    
    Returns:
        str: Applicability details
    """
    applicability = """
    ==================== REAL-WORLD APPLICABILITY ====================
    
    Industries Already Using Similar Systems:
    - Tech/Software: LinkedIn, Indeed, Recruto, Workable
    - Finance: JPMorgan, Goldman Sachs (automated CV screening)
    - Healthcare: CVS, UnitedHealth Group (ATS systems)
    - Consulting: McKinsey, BCG (initial screening automation)
    
    Real-World Challenges & Solutions:
    
    1. Resume Format Variations
       Challenge: PDFs, Word docs, images, plain text
       Solution: Convert all to text, use OCR for images, normalize formatting
    
    2. Multiple Job Descriptions
       Challenge: Same candidate pool for different roles
       Solution: Store pre-computed TF-IDF or embeddings, match dynamically
    
    3. False Negatives
       Challenge: Great candidates filtered out
       Solution: Lower threshold, manual review, multiple passes
    
    4. Compliance & Regulations
       Challenge: GDPR, CCPA, EEOC compliance
       Solution: Data anonymization, audit trails, consent management
    
    5. Language Diversity
       Challenge: Multilingual resumes
       Solution: Language detection + translation or multi-language models
    
    6. Resume Quality vs. Candidate Quality
       Challenge: Good resume ≠ Good candidate
       Solution: Combine with assessments, coding tests, interviews
    
    Integration Points:
    
    - ATS (Applicant Tracking System): Workable, Lever, SmartRecruiters
    - HR Systems: Workday, SAP, BambooHR
    - Email: Automated notifications to HR team
    - Slack/Teams: Notifications to hiring managers
    - Database: Update candidate status in real-time
    
    ROI Benefits:
    
    - 80% reduction in screening time
    - Consistent evaluation across candidates
    - Reduced recruiter burnout
    - Higher quality shortlists
    - Better compliance documentation
    - Faster time-to-hire
    
    =====================================================================
    """
    return applicability


def main():
    """Test utility functions"""
    print("Utility Functions Module")
    print(compare_tfidf_vs_bert())
    print(scalability_analysis())
    print(bias_reduction_strategies())
    print(real_world_applicability())


if __name__ == "__main__":
    main()
