"""
TF-IDF + Cosine Similarity Matcher (Baseline)
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple, Optional
from utils.logger import setup_logger
logger = setup_logger(__name__)

class BaselineMatcher:
    def __init__(self, max_features: int = 5000, ngram_range: tuple = (1, 2)):
        """
        max_features: limit vocabulary size (helps performance)
        ngram_range: (1,2) includes unigrams and bigrams
        """
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            stop_words='english',  # extra stopword removal
            lowercase=True
        )
        self.is_fitted = False
    
    def fit_transform_resumes(self, resume_texts: List[str]) -> np.ndarray:
        """Fit vectorizer on resumes and transform them to TF-IDF matrix."""
        self.resume_vectors = self.vectorizer.fit_transform(resume_texts)
        self.is_fitted = True
        return self.resume_vectors
    
    def transform_job_description(self, jd_text: str) -> np.ndarray:
        """Transform job description using the already-fitted vectorizer."""
        if not self.is_fitted:
            raise ValueError("Must call fit_transform_resumes first")
        return self.vectorizer.transform([jd_text])
    
    def compute_scores(self, jd_vector: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between JD and each resume."""
        # cosine_similarity returns (1, n_resumes) matrix, flatten to 1D
        scores = cosine_similarity(jd_vector, self.resume_vectors).flatten()
        return scores
    
    def rank_resumes(self, resume_texts: List[str], resume_names: List[str], 
                     jd_text: str) -> pd.DataFrame:
        """
        Full pipeline: vectorize, score, rank.
        Returns DataFrame with columns: Rank, Filename, Match_Score, Text_Preview
        """
        # Fit on resumes and get vectors
        self.fit_transform_resumes(resume_texts)
        
        # Transform JD
        jd_vec = self.transform_job_description(jd_text)
        
        # Compute scores (0 to 1)
        scores = self.compute_scores(jd_vec)
        
        # Convert to percentage
        percentages = (scores * 100).round(2)
        
        # Create results DataFrame
        results = pd.DataFrame({
            'Filename': resume_names,
            'Match_Score': percentages,
            'Text_Preview': [t[:100] + '...' if len(t) > 100 else t for t in resume_texts]
        })
        
        # Sort by score descending
        results = results.sort_values('Match_Score', ascending=False).reset_index(drop=True)
        results.insert(0, 'Rank', range(1, len(results) + 1))
        
        return results

# For quick testing
if __name__ == "__main__":
    # Dummy resumes
    resumes = [
        "Python developer with 5 years of experience in Django and SQL",
        "Java backend engineer, skilled in Spring Boot and MongoDB",
        "Data scientist proficient in Python, Machine Learning, and TensorFlow",
        "Frontend developer with React and JavaScript"
    ]
    resume_names = ["resume1.pdf", "resume2.pdf", "resume3.pdf", "resume4.pdf"]
    
    # Job description
    jd = "We are hiring a Python developer with expertise in Django and SQL"
    
    # Initialize matcher
    matcher = BaselineMatcher()
    results_df = matcher.rank_resumes(resumes, resume_names, jd)
    
    print("Baseline Matching Results (TF-IDF + Cosine):")
    print(results_df.to_string(index=False))