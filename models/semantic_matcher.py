"""
Semantic Matcher using Sentence-BERT + FAISS
"""

import numpy as np
import pandas as pd
from typing import List, Optional, Tuple
import os

from utils.logger import setup_logger

logger = setup_logger(__name__)
# Sentence-BERT
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("Install sentence-transformers: pip install sentence-transformers")

# FAISS
try:
    import faiss
except ImportError:
    raise ImportError("Install faiss-cpu: pip install faiss-cpu")

class SemanticMatcher:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', use_faiss: bool = True):
        """
        model_name: Sentence-BERT model
        use_faiss: if True, use FAISS index for fast similarity; else compute manually
        """
        logger.info(f"Loading Sentence-BERT model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        self.use_faiss = use_faiss
        self.index = None
        self.resume_embeddings = None
        self.resume_texts = None
        self.resume_names = None
        self.is_fitted = False
    
    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        # Encode in batches for memory efficiency
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.astype(np.float32)  # FAISS requires float32
    
    def fit_resumes(self, resume_texts: List[str], resume_names: List[str]):
        """Generate embeddings for all resumes and build FAISS index."""
        self.resume_texts = resume_texts
        self.resume_names = resume_names
        self.resume_embeddings = self._get_embeddings(resume_texts)
        
        if self.use_faiss:
            # Build FAISS index (inner product = cosine if vectors normalized)
            self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner Product
            # Normalize embeddings to unit length so IP = cosine similarity
            faiss.normalize_L2(self.resume_embeddings)
            self.index.add(self.resume_embeddings)
        self.is_fitted = True
    
    def rank_resumes(self, jd_text: str, top_k: Optional[int] = None) -> pd.DataFrame:
        """
        Rank resumes against a job description.
        top_k: if None, return all; else return top K matches.
        """
        if not self.is_fitted:
            raise ValueError("Must call fit_resumes first")
        
        # Generate JD embedding
        jd_embedding = self._get_embeddings([jd_text])  # shape (1, dim)
        jd_embedding = jd_embedding.astype(np.float32)
        
        if self.use_faiss and self.index is not None:
            # Normalize JD embedding
            faiss.normalize_L2(jd_embedding)
            if top_k is not None:
                scores, indices = self.index.search(jd_embedding, min(top_k, len(self.resume_texts)))
            else:
                scores, indices = self.index.search(jd_embedding, len(self.resume_texts))
            # scores are cosine similarities (because normalized)
            scores = scores.flatten()
            indices = indices.flatten()
        else:
            # Manual computation (slower for many resumes)
            # Cosine similarity: dot product of normalized vectors
            jd_norm = jd_embedding / np.linalg.norm(jd_embedding, axis=1, keepdims=True)
            resume_norm = self.resume_embeddings / np.linalg.norm(self.resume_embeddings, axis=1, keepdims=True)
            scores = np.dot(resume_norm, jd_norm.T).flatten()
            indices = np.argsort(scores)[::-1]
            scores = scores[indices]
            if top_k is not None:
                indices = indices[:top_k]
                scores = scores[:top_k]
        
        # Build results DataFrame
        match_percentages = (scores * 100).round(2)
        results = []
        for idx, score_perc in zip(indices, match_percentages):
            results.append({
                'Rank': len(results) + 1,
                'Filename': self.resume_names[idx],
                'Match_Score': score_perc,
                'Text_Preview': self.resume_texts[idx][:100] + '...' if len(self.resume_texts[idx]) > 100 else self.resume_texts[idx]
            })
        
        return pd.DataFrame(results)
    
    def save_index(self, index_path: str, embeddings_path: Optional[str] = None):
        """Save FAISS index and optionally embeddings."""
        if self.index is not None:
            faiss.write_index(self.index, index_path)
        if embeddings_path and self.resume_embeddings is not None:
            np.save(embeddings_path, self.resume_embeddings)
    
    def load_index(self, index_path: str, resume_texts: List[str], resume_names: List[str]):
        """Load FAISS index from disk (must match resume order!)."""
        self.index = faiss.read_index(index_path)
        self.resume_texts = resume_texts
        self.resume_names = resume_names
        self.is_fitted = True


# Quick test
if __name__ == "__main__":
    # Dummy data
    resumes = [
        "Python developer with 5 years of experience in Django and SQL",
        "Java backend engineer, skilled in Spring Boot and MongoDB",
        "Data scientist proficient in Python, Machine Learning, and TensorFlow",
        "Frontend developer with React and JavaScript"
    ]
    resume_names = ["resume1.pdf", "resume2.pdf", "resume3.pdf", "resume4.pdf"]
    jd = "We need a Python developer with Django and SQL expertise"
    
    matcher = SemanticMatcher(use_faiss=True)
    matcher.fit_resumes(resumes, resume_names)
    results = matcher.rank_resumes(jd, top_k=3)
    print("Semantic Matching Results (Sentence-BERT + FAISS):")
    print(results.to_string(index=False))
    
    # Compare with baseline
    print("\n" + "="*50)
    print("Note: Semantic should rank 'Python developer' first.")
    print("If 'Data scientist' ranks second, that's fine because Python & ML are semantically close to 'Python developer'.")