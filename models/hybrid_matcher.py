"""
Hybrid Matcher: Combines TF-IDF (lexical) and Sentence-BERT (semantic) scores.
Weighted average with configurable alpha.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional

from models.matcher import BaselineMatcher
from models.semantic_matcher import SemanticMatcher

class HybridMatcher:
    def __init__(self, alpha: float = 0.4, use_faiss: bool = True):
        """
        alpha: weight for TF-IDF score (0 to 1). 
               BERT weight = 1 - alpha.
        Higher alpha gives more importance to keyword matching (TF-IDF).
        Lower alpha favors semantic matching (BERT).
        Default 0.4 is balanced, giving slight edge to semantic.
        """
        self.alpha = alpha
        self.baseline = BaselineMatcher()
        self.semantic = SemanticMatcher(use_faiss=use_faiss)
        self.is_fitted = False
    
    def fit_resumes(self, resume_texts: List[str], resume_names: List[str]):
        """Prepare both matchers with resume texts."""
        # Fit TF-IDF vectorizer and store resume vectors
        self.baseline.fit_transform_resumes(resume_texts)
        # Store resume texts and names for BERT (but SemanticMatcher will fit internally)
        self.resume_texts = resume_texts
        self.resume_names = resume_names
        # Fit semantic matcher (generates embeddings)
        self.semantic.fit_resumes(resume_texts, resume_names)
        self.is_fitted = True
    
    def rank_resumes(self, jd_text: str, top_k: Optional[int] = None) -> pd.DataFrame:
        """
        Rank resumes using hybrid score.
        Returns DataFrame with scores: Hybrid, TF-IDF, BERT.
        """
        if not self.is_fitted:
            raise ValueError("Must call fit_resumes first")
        
        # Get TF-IDF scores
        jd_vec = self.baseline.transform_job_description(jd_text)
        tfidf_scores = self.baseline.compute_scores(jd_vec)  # 0-1 range
        tfidf_percent = (tfidf_scores * 100).round(2)
        
        # Get BERT scores
        # SemanticMatcher.rank_resumes returns full DataFrame; we need raw scores
        # Simpler: compute manually using semantic matcher's internal embeddings
        jd_embedding = self.semantic._get_embeddings([jd_text]).astype(np.float32)
        # Normalize for cosine similarity
        import faiss
        jd_norm = jd_embedding / np.linalg.norm(jd_embedding, axis=1, keepdims=True)
        resume_norm = self.semantic.resume_embeddings / np.linalg.norm(self.semantic.resume_embeddings, axis=1, keepdims=True)
        bert_scores = np.dot(resume_norm, jd_norm.T).flatten()  # cosine similarity
        bert_percent = (bert_scores * 100).round(2)
        
        # Hybrid score: weighted average
        hybrid_scores = self.alpha * tfidf_scores + (1 - self.alpha) * bert_scores
        hybrid_percent = (hybrid_scores * 100).round(2)
        
        # Build results DataFrame
        results = pd.DataFrame({
            'Filename': self.resume_names,
            'Hybrid_Score': hybrid_percent,
            'TFIDF_Score': tfidf_percent,
            'BERT_Score': bert_percent,
            'Text_Preview': [t[:100] + '...' if len(t) > 100 else t for t in self.resume_texts]
        })
        
        # Sort by hybrid score descending
        results = results.sort_values('Hybrid_Score', ascending=False).reset_index(drop=True)
        results.insert(0, 'Rank', range(1, len(results) + 1))
        
        if top_k is not None:
            results = results.head(top_k)
        
        return results
    
    def get_weights(self) -> dict:
        return {'TFIDF_weight': self.alpha, 'BERT_weight': 1 - self.alpha}