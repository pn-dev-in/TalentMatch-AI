"""
ATS Resume Score Breakdown & Feedback Generator.
"""

from typing import List, Dict, Tuple

class ATSScorer:
    def __init__(self):
        # Weights for different components
        self.weights = {
            'skills': 0.40,
            'experience': 0.30,
            'education': 0.20,
            'completeness': 0.10
        }
    
    def compute_skills_score(self, jd_skills: List[str], candidate_skills: List[str]) -> float:
        """Score based on percentage of JD skills found in candidate."""
        if not jd_skills:
            return 100.0
        found = sum(1 for s in jd_skills if s in candidate_skills)
        return (found / len(jd_skills)) * 100
    
    def compute_experience_score(self, candidate_years: int, jd_required_years: int = 0) -> float:
        """Score based on years of experience. Assumes JD expects at least 0 years."""
        if jd_required_years == 0:
            # If no requirement, score based on having any experience
            return 100.0 if candidate_years > 0 else 50.0
        if candidate_years >= jd_required_years:
            return 100.0
        elif candidate_years >= jd_required_years * 0.5:
            return 60.0
        else:
            return 30.0
    
    def compute_education_score(self, candidate_degrees: List[str], jd_requires_degree: bool = True) -> float:
        """Score based on having any degree (simple heuristic)."""
        if not jd_requires_degree:
            return 100.0
        # If JD requires a degree, check if candidate has at least one
        if candidate_degrees:
            return 90.0 if len(candidate_degrees) >= 1 else 70.0
        else:
            return 30.0
    
    def compute_completeness_score(self, resume_text: str) -> float:
        """Simple heuristic: length, presence of common sections."""
        score = 0.0
        text_lower = resume_text.lower()
        # Length check (characters)
        if len(resume_text) > 500:
            score += 40
        elif len(resume_text) > 200:
            score += 20
        else:
            score += 5
        
        # Section presence
        sections = ['experience', 'education', 'skills', 'projects', 'certification']
        found = sum(1 for sec in sections if sec in text_lower)
        score += (found / len(sections)) * 60
        return min(score, 100.0)
    
    def compute_total_score(self, jd_skills: List[str], candidate_skills: List[str],
                            candidate_years: int, candidate_degrees: List[str],
                            resume_text: str, jd_required_years: int = 0,
                            jd_requires_degree: bool = True) -> Dict:
        """Return dict with component scores and weighted total."""
        skills_score = self.compute_skills_score(jd_skills, candidate_skills)
        exp_score = self.compute_experience_score(candidate_years, jd_required_years)
        edu_score = self.compute_education_score(candidate_degrees, jd_requires_degree)
        comp_score = self.compute_completeness_score(resume_text)
        
        total = (skills_score * self.weights['skills'] +
                 exp_score * self.weights['experience'] +
                 edu_score * self.weights['education'] +
                 comp_score * self.weights['completeness'])
        
        return {
            'ATS_Total': round(total, 2),
            'Skills_Score': round(skills_score, 2),
            'Experience_Score': round(exp_score, 2),
            'Education_Score': round(edu_score, 2),
            'Completeness_Score': round(comp_score, 2)
        }
    
    def generate_feedback(self, jd_skills: List[str], candidate_skills: List[str],
                          candidate_years: int, candidate_degrees: List[str],
                          resume_text: str) -> List[str]:
        """Generate actionable feedback tips for the candidate."""
        feedback = []
        
        # Skills feedback
        missing = [s for s in jd_skills if s not in candidate_skills]
        if missing:
            feedback.append(f"❌ Missing required skills: {', '.join(missing[:5])}{'...' if len(missing)>5 else ''}. Consider adding relevant projects or certifications.")
        else:
            feedback.append("✅ All required skills detected.")
        
        # Experience feedback
        if candidate_years == 0:
            feedback.append("⚠ No years of experience found. Add a clear 'Experience' section with dates and roles.")
        elif candidate_years < 2:
            feedback.append("📈 Limited experience (under 2 years). Highlight internships, academic projects, or freelance work.")
        else:
            feedback.append(f"✔ {candidate_years} years of experience detected. Quantify achievements (e.g., 'increased sales by 20%').")
        
        # Education feedback
        if not candidate_degrees:
            feedback.append("🎓 No degree information found. Add your highest degree, university, and graduation year.")
        else:
            feedback.append(f"✔ Education: {', '.join(candidate_degrees)}. Consider adding GPA if >3.0 or relevant coursework.")
        
        # Completeness feedback
        if len(resume_text) < 300:
            feedback.append("📄 Resume is too short (under 300 characters). Expand with detailed descriptions.")
        elif 'github' not in resume_text.lower() and 'linkedin' not in resume_text.lower():
            feedback.append("🔗 Consider adding links to GitHub/LinkedIn to showcase work.")
        
        return feedback