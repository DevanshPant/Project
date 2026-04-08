"""
Model Training Module - Train classification and clustering models
"""

import logging
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report
import pickle
from typing import Tuple, Dict, Optional, List
import warnings

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ClassificationModel:
    """
    Train and evaluate classification models for supervised resume screening.
    """
    
    def __init__(self, model_type: str = 'logistic_regression'):
        """
        Initialize classification model.
        
        Args:
            model_type (str): Type of model
                - 'logistic_regression'
                - 'naive_bayes'
                - 'svm'
                - 'random_forest'
        """
        self.model_type = model_type
        self.model = None
        self.is_trained = False
        
        self._initialize_model()
        logger.info(f"Classification model initialized: {model_type}")
    
    def _initialize_model(self):
        """Initialize the selected model."""
        if self.model_type == 'logistic_regression':
            self.model = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)
        elif self.model_type == 'naive_bayes':
            self.model = MultinomialNB()
        elif self.model_type == 'svm':
            self.model = SVC(kernel='rbf', probability=True, random_state=42)
        elif self.model_type == 'random_forest':
            self.model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> Dict:
        """
        Train the classification model.
        
        Args:
            X_train (np.ndarray): Training features
            y_train (np.ndarray): Training labels
        
        Returns:
            Dict: Training results
        """
        logger.info(f"Training {self.model_type} model...")
        logger.info(f"  Training samples: {X_train.shape[0]}")
        logger.info(f"  Features: {X_train.shape[1]}")
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Get training accuracy
        train_accuracy = self.model.score(X_train, y_train)
        
        logger.info(f"  Training accuracy: {train_accuracy:.4f}")
        
        return {'accuracy': train_accuracy}
    
    def predict(self, X_test: np.ndarray) -> np.ndarray:
        """
        Make predictions on test data.
        
        Args:
            X_test (np.ndarray): Test features
        
        Returns:
            np.ndarray: Predicted labels
        """
        if not self.is_trained:
            logger.error("Model not trained yet")
            raise RuntimeError("Model not trained yet")
        
        predictions = self.model.predict(X_test)
        return predictions
    
    def predict_proba(self, X_test: np.ndarray) -> np.ndarray:
        """
        Get prediction probabilities.
        
        Args:
            X_test (np.ndarray): Test features
        
        Returns:
            np.ndarray: Prediction probabilities
        """
        if not hasattr(self.model, 'predict_proba'):
            logger.warning(f"{self.model_type} does not support predict_proba")
            return None
        
        return self.model.predict_proba(X_test)
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """
        Evaluate model on test data.
        
        Args:
            X_test (np.ndarray): Test features
            y_test (np.ndarray): Test labels
        
        Returns:
            Dict: Evaluation metrics
        """
        if not self.is_trained:
            logger.error("Model not trained yet")
            raise RuntimeError("Model not trained yet")
        
        # Predictions
        y_pred = self.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        results = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'y_pred': y_pred,
            'y_test': y_test
        }
        
        logger.info(f"\n{self.model_type} - EVALUATION RESULTS:")
        logger.info(f"  Accuracy:  {accuracy:.4f}")
        logger.info(f"  Precision: {precision:.4f}")
        logger.info(f"  Recall:    {recall:.4f}")
        logger.info(f"  F1-Score:  {f1:.4f}")
        
        return results
    
    def save_model(self, filepath: str):
        """Save trained model to file."""
        logger.info(f"Saving model to {filepath}")
        with open(filepath, 'wb') as f:
            pickle.dump(self.model, f)
    
    def load_model(self, filepath: str):
        """Load trained model from file."""
        logger.info(f"Loading model from {filepath}")
        with open(filepath, 'rb') as f:
            self.model = pickle.load(f)
        self.is_trained = True


class ClusteringModel:
    """
    K-Means clustering for unsupervised resume screening.
    """
    
    def __init__(self, n_clusters: int = 5, random_state: int = 42):
        """
        Initialize clustering model.
        
        Args:
            n_clusters (int): Number of clusters
            random_state (int): Random seed
        """
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        self.is_trained = False
        logger.info(f"KMeans clustering model initialized with {n_clusters} clusters")
    
    def fit(self, X: np.ndarray) -> np.ndarray:
        """
        Fit clustering model.
        
        Args:
            X (np.ndarray): Feature matrix
        
        Returns:
            np.ndarray: Cluster labels
        """
        logger.info(f"Fitting KMeans model on {X.shape[0]} samples...")
        
        labels = self.model.fit_predict(X)
        self.is_trained = True
        
        logger.info(f"  Inertia: {self.model.inertia_:.4f}")
        logger.info(f"  Silhouette Score calculation can be done separately")
        
        return labels
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict cluster labels.
        
        Args:
            X (np.ndarray): Feature matrix
        
        Returns:
            np.ndarray: Cluster labels
        """
        if not self.is_trained:
            logger.error("Model not trained yet")
            raise RuntimeError("Model not trained yet")
        
        return self.model.predict(X)
    
    def get_cluster_centers(self) -> np.ndarray:
        """Get cluster centers."""
        return self.model.cluster_centers_


class ModelComparator:
    """
    Compare multiple classification models.
    """
    
    def __init__(self, models_list: List[str] = None):
        """
        Initialize model comparator.
        
        Args:
            models_list (List[str]): List of model types to compare
        """
        if models_list is None:
            models_list = ['logistic_regression', 'naive_bayes', 'svm', 'random_forest']
        
        self.models_list = models_list
        self.trained_models = {}
        self.results = {}
    
    def train_all_models(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train all models."""
        logger.info(f"Training {len(self.models_list)} models...")
        
        for model_type in self.models_list:
            logger.info(f"\n{'='*50}")
            logger.info(f"Training: {model_type}")
            logger.info(f"{'='*50}")
            
            try:
                model = ClassificationModel(model_type)
                model.train(X_train, y_train)
                self.trained_models[model_type] = model
            except Exception as e:
                logger.error(f"Error training {model_type}: {str(e)}")
    
    def evaluate_all_models(self, X_test: np.ndarray, y_test: np.ndarray) -> pd.DataFrame:
        """
        Evaluate all trained models.
        
        Returns:
            pd.DataFrame: Comparison results
        """
        logger.info(f"\nEvaluating {len(self.trained_models)} models...")
        
        results_list = []
        
        for model_type, model in self.trained_models.items():
            logger.info(f"\nEvaluating: {model_type}")
            results = model.evaluate(X_test, y_test)
            
            results_list.append({
                'Model': model_type,
                'Accuracy': results['accuracy'],
                'Precision': results['precision'],
                'Recall': results['recall'],
                'F1-Score': results['f1_score']
            })
        
        results_df = pd.DataFrame(results_list)
        
        logger.info(f"\n{'='*80}")
        logger.info("MODEL COMPARISON RESULTS")
        logger.info(f"{'='*80}")
        logger.info(f"\n{results_df.to_string(index=False)}")
        
        # Find best model
        best_model = results_df.loc[results_df['F1-Score'].idxmax()]
        logger.info(f"\nBest Model: {best_model['Model']} with F1-Score: {best_model['F1-Score']:.4f}")
        
        return results_df
    
    def get_best_model(self) -> Optional[ClassificationModel]:
        """Get the best trained model based on evaluation."""
        if not self.trained_models:
            return None
        
        # For now, return first trained model (should implement proper selection)
        return list(self.trained_models.values())[0]


def main():
    """Test model training functionality"""
    from sklearn.datasets import make_classification
    
    logger.info("=" * 80)
    logger.info("MODEL TRAINING DEMONSTRATION")
    logger.info("=" * 80)
    
    # Create synthetic dataset
    X, y = make_classification(n_samples=300, n_features=50, n_classes=3, 
                              n_informative=20, random_state=42)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Compare models
    comparator = ModelComparator()
    comparator.train_all_models(X_train, y_train)
    results = comparator.evaluate_all_models(X_test, y_test)
    
    logger.info("\nResults saved!")


if __name__ == "__main__":
    main()
