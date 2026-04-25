"""
Skill Gap Analyzer – Detailed missing skills detection.
"""

from typing import List, Dict, Set
from collections import Counter

class SkillGapAnalyzer:
    def __init__(self):
        # Optional: categorize skills (can be extended)
        self.tech_skills = {
            "python", "java", "sql", "aws", "docker", "kubernetes",
            "tensorflow", "pytorch", "react", "angular", "django"
        }
        self.soft_skills = {
            "communication", "leadership", "teamwork", "problem solving"
        }
    
    def get_missing_skills(self, jd_skills: List[str], candidate_skills: List[str]) -> List[str]:
        """Return list of skills in JD but not in candidate."""
        return list(set(jd_skills) - set(candidate_skills))
    
    def get_missing_skills_with_categories(self, jd_skills: List[str], candidate_skills: List[str]) -> Dict:
        """Return missing skills categorized by type."""
        missing = set(jd_skills) - set(candidate_skills)
        categorized = {
            "technical": [s for s in missing if s in self.tech_skills],
            "soft": [s for s in missing if s in self.soft_skills],
            "other": [s for s in missing if s not in self.tech_skills and s not in self.soft_skills]
        }
        # Sort each category
        for k in categorized:
            categorized[k].sort()
        return categorized
    
    def get_skill_gap_summary(self, jd_skills: List[str], all_candidates_skills: List[List[str]]) -> Dict:
        """
        For a batch of candidates, find which JD skills are most frequently missing.
        Returns dict with skill -> count of candidates missing it.
        """
        jd_set = set(jd_skills)
        missing_counter = Counter()
        for cand_skills in all_candidates_skills:
            cand_set = set(cand_skills)
            missing = jd_set - cand_set
            missing_counter.update(missing)
        # Convert to dict sorted by frequency descending
        return dict(missing_counter.most_common())
    
    def generate_missing_skills_report(self, jd_skills: List[str], candidate_skills: List[str], candidate_name: str) -> str:
        """Generate a human-readable report of missing skills."""
        missing = self.get_missing_skills(jd_skills, candidate_skills)
        if not missing:
            return f"✅ {candidate_name} has all required skills!"
        
        categorized = self.get_missing_skills_with_categories(jd_skills, candidate_skills)
        report = f"⚠️ **{candidate_name} missing {len(missing)} skills:**\n"
        if categorized['technical']:
            report += f"- Technical: {', '.join(categorized['technical'])}\n"
        if categorized['soft']:
            report += f"- Soft skills: {', '.join(categorized['soft'])}\n"
        if categorized['other']:
            report += f"- Other: {', '.join(categorized['other'])}\n"
        return report