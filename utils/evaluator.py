"""
Evaluation utilities for resume screening system.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple

def precision_at_k(relevant_indices: List[int], ranked_indices: List[int], k: int) -> float:
    """Precision@K: fraction of relevant candidates in top K."""
    top_k = ranked_indices[:k]
    relevant_in_top_k = sum(1 for idx in top_k if idx in relevant_indices)
    return relevant_in_top_k / k if k > 0 else 0.0

def recall_at_k(relevant_indices: List[int], ranked_indices: List[int], k: int) -> float:
    """Recall@K: fraction of all relevant candidates found in top K."""
    top_k = ranked_indices[:k]
    relevant_in_top_k = sum(1 for idx in top_k if idx in relevant_indices)
    total_relevant = len(relevant_indices)
    return relevant_in_top_k / total_relevant if total_relevant > 0 else 0.0

def f1_at_k(relevant_indices: List[int], ranked_indices: List[int], k: int) -> float:
    """F1@K = 2 * (P@K * R@K) / (P@K + R@K)."""
    p = precision_at_k(relevant_indices, ranked_indices, k)
    r = recall_at_k(relevant_indices, ranked_indices, k)
    if p + r == 0:
        return 0.0
    return 2 * (p * r) / (p + r)

def mean_reciprocal_rank(relevant_indices: List[int], ranked_indices: List[int]) -> float:
    """MRR = 1 / rank of first relevant item (0 if none found)."""
    for rank, idx in enumerate(ranked_indices, start=1):
        if idx in relevant_indices:
            return 1.0 / rank
    return 0.0

def evaluate_matcher(matcher_results_df: pd.DataFrame, ground_truth: Dict[str, List[str]]):
    """
    matcher_results_df: columns = ['Rank', 'Filename', 'Match_Score', ...]
    ground_truth: dict mapping job_description_id (or just 'jd') to list of relevant filenames.
    Returns metrics dict.
    """
    # For simplicity, assume single job description and ground truth as list of relevant filenames
    relevant_files = ground_truth.get('relevant_filenames', [])
    # Get ranked filenames from results (order by rank)
    ranked_files = matcher_results_df['Filename'].tolist()
    # Convert filenames to indices for evaluation
    relevant_indices = [i for i, f in enumerate(ranked_files) if f in relevant_files]
    # Find positions of relevant files in the ranked list
    ranked_indices_of_relevant = []
    for i, f in enumerate(ranked_files):
        if f in relevant_files:
            ranked_indices_of_relevant.append(i)
    
    # Calculate metrics at K=5 and K=10 (or use Top-K from settings)
    ks = [5, 10]
    metrics = {}
    for k in ks:
        metrics[f'precision@{k}'] = precision_at_k(ranked_indices_of_relevant, list(range(len(ranked_files))), k)
        metrics[f'recall@{k}'] = recall_at_k(ranked_indices_of_relevant, list(range(len(ranked_files))), k)
        metrics[f'f1@{k}'] = f1_at_k(ranked_indices_of_relevant, list(range(len(ranked_files))), k)
    metrics['mrr'] = mean_reciprocal_rank(ranked_indices_of_relevant, list(range(len(ranked_files))))
    return metrics

def compare_matchers(results_baseline: pd.DataFrame, results_semantic: pd.DataFrame, ground_truth: Dict):
    """Return DataFrame comparing metrics for both matchers."""
    metrics_baseline = evaluate_matcher(results_baseline, ground_truth)
    metrics_semantic = evaluate_matcher(results_semantic, ground_truth)
    comp_df = pd.DataFrame({
        'Metric': list(metrics_baseline.keys()),
        'Baseline (TF-IDF)': [metrics_baseline[m] for m in metrics_baseline],
        'Semantic (BERT+FAISS)': [metrics_semantic[m] for m in metrics_semantic]
    })
    # Format percentages
    for col in ['Baseline (TF-IDF)', 'Semantic (BERT+FAISS)']:
        comp_df[col] = comp_df[col].apply(lambda x: f"{x:.4f}")
    return comp_df