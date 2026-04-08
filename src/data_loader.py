"""
Data Loader Module - Load and Preprocess Kaggle Resume Dataset
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import kagglehub
import logging
from typing import Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataLoader:
    """
    Handles loading and basic preprocessing of resume dataset from Kaggle.
    
    Attributes:
        dataset_name (str): Kaggle dataset identifier
        local_path (str): Local path where dataset is stored
        df (pd.DataFrame): Loaded dataset
    """
    
    def __init__(self, dataset_name: str = "snehaanbhawal/resume-dataset"):
        """
        Initialize DataLoader with dataset name.
        
        Args:
            dataset_name (str): Kaggle dataset identifier
        """
        self.dataset_name = dataset_name
        self.local_path = None
        self.df = None
        self.raw_df = None
        
    def download_dataset(self) -> str:
        """
        Download dataset from Kaggle using kagglehub API.
        
        Returns:
            str: Path to downloaded dataset
        """
        try:
            logger.info(f"Downloading dataset: {self.dataset_name}...")
            self.local_path = kagglehub.dataset_download(self.dataset_name)
            logger.info(f"Dataset downloaded successfully at: {self.local_path}")
            return self.local_path
        except Exception as e:
            logger.error(f"Error downloading dataset: {str(e)}")
            raise
    
    def load_dataset(self) -> pd.DataFrame:
        """
        Load dataset from local path into pandas DataFrame.
        Handles multiple file formats (CSV, Excel, etc.)
        
        Returns:
            pd.DataFrame: Loaded dataset
        """
        if self.local_path is None:
            self.download_dataset()
        
        try:
            # Find and load the first CSV or Excel file
            for file in os.listdir(self.local_path):
                if file.endswith('.csv'):
                    file_path = os.path.join(self.local_path, file)
                    logger.info(f"Loading CSV file: {file_path}")
                    self.df = pd.read_csv(file_path)
                    self.raw_df = self.df.copy()
                    logger.info(f"Dataset loaded successfully. Shape: {self.df.shape}")
                    return self.df
                elif file.endswith(('.xlsx', '.xls')):
                    file_path = os.path.join(self.local_path, file)
                    logger.info(f"Loading Excel file: {file_path}")
                    self.df = pd.read_excel(file_path)
                    self.raw_df = self.df.copy()
                    logger.info(f"Dataset loaded successfully. Shape: {self.df.shape}")
                    return self.df
            
            logger.error("No CSV or Excel files found in dataset directory")
            raise FileNotFoundError("No CSV or Excel files found in dataset directory")
            
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            raise
    
    def inspect_dataset(self) -> dict:
        """
        Inspect dataset and return basic statistics.
        
        Returns:
            dict: Dataset information
        """
        if self.df is None:
            self.load_dataset()
        
        info = {
            'shape': self.df.shape,
            'columns': self.df.columns.tolist(),
            'dtypes': self.df.dtypes.to_dict(),
            'missing_values': self.df.isnull().sum().to_dict(),
            'duplicates': self.df.duplicated().sum(),
            'sample_data': self.df.head(5).to_dict()
        }
        
        logger.info(f"Dataset Inspection:")
        logger.info(f"  Shape: {info['shape']}")
        logger.info(f"  Columns: {info['columns']}")
        logger.info(f"  Missing values: {info['missing_values']}")
        logger.info(f"  Duplicates: {info['duplicates']}")
        
        return info
    
    def handle_missing_values(self, strategy: str = 'drop') -> pd.DataFrame:
        """
        Handle missing values in dataset.
        
        Args:
            strategy (str): Strategy to handle missing values
                - 'drop': Remove rows with missing values
                - 'fill_mean': Fill with mean (for numeric)
                - 'fill_mode': Fill with mode (for categorical)
                - 'fill_forward': Forward fill
        
        Returns:
            pd.DataFrame: Cleaned dataset
        """
        logger.info(f"Handling missing values using strategy: {strategy}")
        
        if strategy == 'drop':
            self.df = self.df.dropna()
        elif strategy == 'fill_mean':
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].mean())
        elif strategy == 'fill_mode':
            for col in self.df.columns:
                self.df[col].fillna(self.df[col].mode()[0] if not self.df[col].mode().empty else 'Unknown', 
                                     inplace=True)
        elif strategy == 'fill_forward':
            self.df = self.df.fillna(method='ffill')
        
        logger.info(f"After handling missing values. New shape: {self.df.shape}")
        return self.df
    
    def remove_duplicates(self) -> pd.DataFrame:
        """
        Remove duplicate rows from dataset.
        
        Returns:
            pd.DataFrame: Dataset with duplicates removed
        """
        before_count = len(self.df)
        self.df = self.df.drop_duplicates()
        after_count = len(self.df)
        
        logger.info(f"Removed {before_count - after_count} duplicate rows")
        return self.df
    
    def get_dataset_info(self) -> str:
        """
        Return formatted dataset information.
        
        Returns:
            str: Formatted dataset information
        """
        if self.df is None:
            self.load_dataset()
        
        info_str = f"""
        ==================== DATASET INFORMATION ====================
        Total Records: {len(self.df)}
        Total Columns: {len(self.df.columns)}
        
        Columns: {self.df.columns.tolist()}
        
        Data Types:
        {self.df.dtypes}
        
        Missing Values:
        {self.df.isnull().sum()}
        
        Dataset Sample (First 5 rows):
        {self.df.head()}
        ============================================================
        """
        return info_str
    
    def get_text_columns(self) -> list:
        """
        Identify text columns in dataset.
        
        Returns:
            list: Names of text columns
        """
        if self.df is None:
            self.load_dataset()
        
        text_columns = self.df.select_dtypes(include=['object']).columns.tolist()
        logger.info(f"Identified text columns: {text_columns}")
        return text_columns
    
    def get_label_column(self) -> Optional[str]:
        """
        Identify if dataset has label column (for classification).
        Common label column names: 'Category', 'Label', 'Job_Role', 'Category_Names'
        
        Returns:
            Optional[str]: Name of label column or None
        """
        if self.df is None:
            self.load_dataset()
        
        common_label_names = ['Category', 'Label', 'Job_Role', 'Category_Names', 'class', 'target', 'category']
        
        for col in common_label_names:
            if col in self.df.columns:
                logger.info(f"Identified label column: {col}")
                return col
        
        logger.warning("No standard label column found. Using unsupervised approach.")
        return None


def main():
    """Test data loader functionality"""
    loader = DataLoader()
    
    # Download and load dataset
    loader.download_dataset()
    loader.load_dataset()
    
    # Inspect dataset
    print(loader.get_dataset_info())
    
    # Inspect detailed information
    info = loader.inspect_dataset()
    print(f"\nDetailed Info: {info}")
    
    # Get text and label columns
    text_cols = loader.get_text_columns()
    label_col = loader.get_label_column()
    
    print(f"\nText Columns: {text_cols}")
    print(f"Label Column: {label_col}")


if __name__ == "__main__":
    main()
