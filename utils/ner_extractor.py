"""
NER Extractor for Experience, Education, Titles, and Universities.
Uses spaCy's en_core_web_sm model.
"""

import re
import spacy
from typing import Dict, List, Tuple, Optional

# Load spaCy model (download if not present)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

class NERExtractor:
    def __init__(self):
        # Predefined lists for degree detection
        self.degrees = {
            "bachelor", "b.s", "b.sc", "b.a", "b.tech", "b.e", "b.b.a",
            "master", "m.s", "m.sc", "m.a", "m.tech", "m.e", "m.b.a",
            "phd", "doctorate", "associate", "diploma", "certification"
        }
        # Common job titles (can be expanded)
        self.job_titles = {
            "engineer", "developer", "scientist", "analyst", "manager", "director",
            "architect", "consultant", "specialist", "coordinator", "administrator",
            "data scientist", "machine learning engineer", "software engineer",
            "product manager", "project manager", "business analyst", "data analyst"
        }
    
    def extract_experience_years(self, text: str) -> int:
        """Extract number of years of experience from text."""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s+of\s+experience',
            r'(\d+)\+?\s*(?:years?|yrs?)\s+experience',
            r'experience\s+of\s+(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*\+\s*years?',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Also find any standalone numbers with year context
        matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', text, re.IGNORECASE)
        if matches:
            return max(int(m) for m in matches)
        return 0
    
    def extract_degrees(self, text: str) -> List[str]:
        """Extract degree names from text."""
        text_lower = text.lower()
        found = []
        for deg in self.degrees:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(deg) + r'\b'
            if re.search(pattern, text_lower):
                # Capitalize nicely for display
                found.append(deg.title())
        # Remove duplicates while preserving order
        return list(dict.fromkeys(found))
    
    def extract_universities(self, text: str) -> List[str]:
        """Extract university names using spaCy NER (ORG) and heuristics."""
        doc = nlp(text[:10000])  # limit to first 10k chars for performance
        universities = set()
        
        for ent in doc.ents:
            if ent.label_ == "ORG":
                # Additional heuristics: contains 'university', 'college', 'institute'
                ent_text = ent.text.lower()
                if any(keyword in ent_text for keyword in ["university", "college", "institute", "school"]):
                    universities.add(ent.text.strip())
        
        # Also look for common patterns with "University of X" or "X University"
        patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+University',
            r'University\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for m in matches:
                universities.add(m.strip())
        
        return list(universities)[:3]  # limit to top 3
    
    def extract_job_titles(self, text: str) -> List[str]:
        """Extract job titles from text (based on keyword matching and nearby lines)."""
        # Look for titles near words like "experience as", "worked as", "position"
        title_patterns = [
            r'(?:experience as|worked as|position as|role as|job title)\s+([A-Za-z\s]+?)(?:\.|,|\n|$)',
            r'(?:Current|Previous)\s+([A-Za-z\s]+?)(?:\s+at|\s+for|\s+with|\.|\n)'
        ]
        found_titles = set()
        for pattern in title_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                cleaned = m.strip().title()
                if len(cleaned) > 2:
                    found_titles.add(cleaned)
        
        # Also search for known job titles in text
        for title in self.job_titles:
            if re.search(r'\b' + re.escape(title) + r'\b', text.lower()):
                found_titles.add(title.title())
        
        return list(found_titles)[:3]
    
    def extract_all(self, text: str) -> Dict:
        """Run all extractors and return a dictionary."""
        return {
            'years_experience': self.extract_experience_years(text),
            'degrees': self.extract_degrees(text),
            'universities': self.extract_universities(text),
            'job_titles': self.extract_job_titles(text)
        }