"""
NLP Preprocessing Module - Clean and normalize resume text
"""

import re
import string
import logging
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
import pandas as pd
from typing import List, Optional
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

try:
    nltk.data.find('corpora/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TextPreprocessor:
    """
    NLP Text Preprocessing Pipeline for resume text.
    
    Attributes:
        lemmatizer (WordNetLemmatizer): NLTK lemmatizer
        stemmer (PorterStemmer): NLTK stemmer
        stop_words (set): English stop words
    """
    
    def __init__(self, remove_stopwords: bool = True, use_lemmatization: bool = True):
        """
        Initialize TextPreprocessor.
        
        Args:
            remove_stopwords (bool): Whether to remove stopwords
            use_lemmatization (bool): Whether to use lemmatization (vs stemming)
        """
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        self.remove_stopwords = remove_stopwords
        self.use_lemmatization = use_lemmatization
        
        logger.info("TextPreprocessor initialized")
        logger.info(f"  Remove Stopwords: {remove_stopwords}")
        logger.info(f"  Use Lemmatization: {use_lemmatization}")
    
    def to_lowercase(self, text: str) -> str:
        """
        Convert text to lowercase.
        
        Args:
            text (str): Input text
        
        Returns:
            str: Lowercase text
        """
        return text.lower()
    
    def remove_special_characters(self, text: str) -> str:
        """
        Remove special characters, numbers, and extra whitespace.
        Keep alphanumeric characters and spaces.
        
        Args:
            text (str): Input text
        
        Returns:
            str: Text with special characters removed
        """
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text (str): Input text
        
        Returns:
            List[str]: List of tokens
        """
        tokens = word_tokenize(text)
        return tokens
    
    def remove_stopwords_from_tokens(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords from token list.
        
        Args:
            tokens (List[str]): Input tokens
        
        Returns:
            List[str]: Tokens with stopwords removed
        """
        if not self.remove_stopwords:
            return tokens
        
        filtered_tokens = [token for token in tokens if token.lower() not in self.stop_words]
        return filtered_tokens
    
    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """
        Lemmatize tokens using WordNet lemmatizer.
        
        Args:
            tokens (List[str]): Input tokens
        
        Returns:
            List[str]: Lemmatized tokens
        """
        if not self.use_lemmatization:
            return [self.stemmer.stem(token) for token in tokens]
        
        lemmatized = [self.lemmatizer.lemmatize(token) for token in tokens]
        return lemmatized
    
    def preprocess_text(self, text: str) -> str:
        """
        Complete NLP preprocessing pipeline: lowercase -> remove special chars -> 
        tokenize -> remove stopwords -> lemmatize
        
        Args:
            text (str): Raw input text
        
        Returns:
            str: Preprocessed text
        """
        if pd.isna(text) or text is None:
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # Step 1: Lowercase
        text = self.to_lowercase(text)
        
        # Step 2: Remove special characters
        text = self.remove_special_characters(text)
        
        # Step 3: Tokenize
        tokens = self.tokenize(text)
        
        # Step 4: Remove stopwords
        tokens = self.remove_stopwords_from_tokens(tokens)
        
        # Step 5: Lemmatize
        tokens = self.lemmatize_tokens(tokens)
        
        # Step 6: Join back to string
        processed_text = ' '.join(tokens)
        
        return processed_text
    
    def preprocess_dataframe(self, df: pd.DataFrame, text_columns: List[str]) -> pd.DataFrame:
        """
        Preprocess text columns in a DataFrame.
        
        Args:
            df (pd.DataFrame): Input dataframe
            text_columns (List[str]): List of column names to preprocess
        
        Returns:
            pd.DataFrame: Dataframe with preprocessed text
        """
        logger.info(f"Preprocessing {len(text_columns)} text columns...")
        
        df_processed = df.copy()
        
        for col in text_columns:
            if col in df_processed.columns:
                logger.info(f"  Processing column: {col}")
                df_processed[col] = df_processed[col].apply(self.preprocess_text)
        
        logger.info("Text preprocessing completed")
        return df_processed
    
    def get_preprocessing_report(self, original_text: str, processed_text: str) -> dict:
        """
        Generate report showing preprocessing impact.
        
        Args:
            original_text (str): Original text
            processed_text (str): Processed text
        
        Returns:
            dict: Report with statistics
        """
        report = {
            'original_length': len(original_text),
            'processed_length': len(processed_text),
            'original_word_count': len(original_text.split()),
            'processed_word_count': len(processed_text.split()),
            'characters_removed': len(original_text) - len(processed_text),
            'words_removed': len(original_text.split()) - len(processed_text.split())
        }
        return report


class TextNormalizer:
    """
    Additional text normalization utilities.
    """
    
    @staticmethod
    def remove_duplicate_words(text: str) -> str:
        """Remove duplicate consecutive words."""
        words = text.split()
        normalized = []
        for word in words:
            if not normalized or word != normalized[-1]:
                normalized.append(word)
        return ' '.join(normalized)
    
    @staticmethod
    def remove_numbers(text: str) -> str:
        """Remove all numbers from text."""
        return re.sub(r'\d+', '', text)
    
    @staticmethod
    def expand_abbreviations(text: str) -> str:
        """Expand common abbreviations in resumes."""
        expansions = {
            r'\bB\.S\.': 'Bachelor of Science',
            r'\bB\.A\.': 'Bachelor of Arts',
            r'\bM\.S\.': 'Master of Science',
            r'\bM\.A\.': 'Master of Arts',
            r'\bPh\.D\.': 'Philosophy Doctor',
            r'\bEXP\.': 'Experience',
            r'\bDEPT\.': 'Department',
        }
        
        for pattern, expansion in expansions.items():
            text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace: remove leading/trailing and collapse multiple spaces."""
        return ' '.join(text.split())


def main():
    """Test preprocessing functionality"""
    
    # Test text
    sample_resume = """
    John Doe
    Email: john.doe@email.com | Phone: (555) 123-4567
    
    PROFESSIONAL SUMMARY
    Experienced Software Engineer with 5+ years expertise in Python, Java, and C++.
    Strong background in building scalable web applications and microservices.
    
    TECHNICAL SKILLS
    Programming: Python, Java, C++, JavaScript, SQL
    Frameworks: Django, Spring Boot, React.js
    Databases: MySQL, PostgreSQL, MongoDB, Redis
    DevOps: Docker, Kubernetes, Jenkins, AWS
    
    EXPERIENCE
    Senior Software Engineer - Tech Corp (2020-2023)
    - Developed REST APIs using Django and Flask
    - Implemented microservices architecture
    - Led team of 5 engineers
    - Improved performance by 40%
    
    EDUCATION
    B.S. in Computer Science - University (2018)
    
    CERTIFICATIONS
    AWS Solutions Architect Associate (2022)
    """
    
    # Create preprocessor
    preprocessor = TextPreprocessor(remove_stopwords=True, use_lemmatization=True)
    
    # Preprocess text
    print("=" * 80)
    print("ORIGINAL TEXT:")
    print(sample_resume)
    
    processed_text = preprocessor.preprocess_text(sample_resume)
    
    print("\n" + "=" * 80)
    print("PREPROCESSED TEXT:")
    print(processed_text)
    
    # Get report
    report = preprocessor.get_preprocessing_report(sample_resume, processed_text)
    print("\n" + "=" * 80)
    print("PREPROCESSING REPORT:")
    for key, value in report.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
