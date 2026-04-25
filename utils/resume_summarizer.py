"""
Resume Summarizer – Lightweight Template-Based Summary Generation.
No LLM required. Uses extracted NER data and skills.
"""

from typing import Dict, List

class ResumeSummarizer:
    def __init__(self):
        pass
    
    def generate_summary(self, ner_info: Dict, skills: List[str], name_hint: str = "Candidate") -> str:
        """
        Generate a readable summary from NER info and skills.
        
        ner_info: dict with keys: years_experience, degrees, job_titles, universities
        skills: list of extracted skills
        name_hint: optional candidate name (fallback)
        """
        parts = []
        
        # Experience
        exp_years = ner_info.get('years_experience', 0)
        job_titles = ner_info.get('job_titles', [])
        if exp_years > 0 and job_titles:
            parts.append(f"{exp_years} years of experience as {job_titles[0]}")
        elif exp_years > 0:
            parts.append(f"{exp_years} years of professional experience")
        elif job_titles:
            parts.append(f"Experience as {job_titles[0]}")
        
        # Education
        degrees = ner_info.get('degrees', [])
        universities = ner_info.get('universities', [])
        if degrees:
            deg_str = ", ".join(degrees[:2])
            if universities:
                parts.append(f"Holds {deg_str} from {universities[0]}")
            else:
                parts.append(f"Holds {deg_str}")
        elif universities:
            parts.append(f"Studied at {universities[0]}")
        
        # Skills
        if skills:
            top_skills = skills[:5]
            skills_str = ", ".join(top_skills)
            if len(skills) > 5:
                skills_str += f" and {len(skills)-5} more"
            parts.append(f"Skilled in {skills_str}")
        
        # Fallback if nothing extracted
        if not parts:
            return f"{name_hint} – No detailed information extracted. Review resume manually."
        
        # Combine into a single sentence
        summary = f"{name_hint} has " + ", ".join(parts[:-1]) + (", and " + parts[-1] if len(parts) > 1 else parts[0]) + "."
        return summary
    
    def generate_bullet_points(self, ner_info: Dict, skills: List[str]) -> List[str]:
        """Generate bullet points for feedback/suggestions."""
        bullets = []
        
        exp = ner_info.get('years_experience', 0)
        if exp > 0:
            bullets.append(f"✔ Experience: {exp} years")
        else:
            bullets.append("⚠ No clear years of experience found – consider adding explicit years.")
        
        if ner_info.get('degrees'):
            bullets.append("✔ Education: Degree(s) detected.")
        else:
            bullets.append("⚠ No degree information found – add education section.")
        
        if skills:
            bullets.append(f"✔ Key skills: {', '.join(skills[:3])}")
        else:
            bullets.append("⚠ No technical skills detected – list relevant technologies.")
        
        return bullets