"""
Skill Extractor – Extract required skills from job description.
Uses the same skill set as the preprocessor.
"""

import re
from typing import List, Set

# Default skill set (should match or be a superset of TextPreprocessor.DEFAULT_SKILLS)
DEFAULT_SKILLS = {
    "python", "java", "javascript", "sql", "nosql", "mongodb", "postgresql", "mysql",
    "machine learning", "deep learning", "nlp", "computer vision", "pytorch", "tensorflow",
    "keras", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "tableau", "power bi",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github", "gitlab",
    "flask", "django", "fastapi", "streamlit", "react", "angular", "vue",
    "data analysis", "data visualization", "statistics", "probability", "linear algebra",
    "communication", "leadership", "problem solving", "teamwork"
}

class SkillExtractor:
    def __init__(self, skill_set: Set[str] = None):
        self.skill_set = skill_set if skill_set else DEFAULT_SKILLS
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills present in the text from the predefined skill set."""
        text_lower = text.lower()
        found = []
        for skill in self.skill_set:
            # Match whole word/phrase with word boundaries
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.append(skill)
        # Return unique skills in order of appearance
        unique = []
        for s in found:
            if s not in unique:
                unique.append(s)
        return unique
    
    def extract_required_skills(self, job_description: str) -> List[str]:
        """Extract skills that appear to be required from JD (simple extraction)."""
        # For now, just extract all skills from JD
        # Could be enhanced with weighting (e.g., "must have" phrases)
        return self.extract_skills_from_text(job_description)