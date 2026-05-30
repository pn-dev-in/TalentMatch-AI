# At the top of text_preprocessor.py
import spacy

# Load model (will be installed via requirements.txt)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback: try to download (shouldn't happen if in requirements.txt)
    import subprocess
    subprocess.check_call(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List, Tuple, Optional

from utils.logger import setup_logger
logger = setup_logger(__name__)
from utils.ner_extractor import NERExtractor
# Optional spaCy (more accurate, but heavier)
try:
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    USE_SPACY = True
except:
    USE_SPACY = False
    # Fallback to NLTK tokenizer
    from nltk.tokenize import word_tokenize

# Download NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Predefined skill set (expandable)
DEFAULT_SKILLS = {
    "python", "java", "javascript", "sql", "nosql", "mongodb", "postgresql", "mysql",
    "machine learning", "deep learning", "nlp", "computer vision", "pytorch", "tensorflow",
    "keras", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "tableau", "power bi",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github", "gitlab",
    "flask", "django", "fastapi", "streamlit", "react", "angular", "vue",
    "data analysis", "data visualization", "statistics", "probability", "linear algebra",
    "communication", "leadership", "problem solving", "teamwork"
}

class TextPreprocessor:
    def __init__(self, skill_set: set = None):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.skill_set = skill_set if skill_set else DEFAULT_SKILLS
        # Add common resume noise words
        self.stop_words.update(["experience", "year", "years", "skill", "skills", 
                                "work", "job", "role", "company", "candidate",
                                "resume", "cv", "applicant", "position"])
        self.ner = NERExtractor() 

    def clean_text(self, text: str) -> str:
        """Basic cleaning: lowercase, remove special chars, numbers, extra spaces."""
        text = text.lower()
        # Remove punctuation and special characters (keep letters and spaces)
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        if USE_SPACY:
            doc = nlp(text)
            tokens = [token.text for token in doc if not token.is_punct and not token.is_space]
        else:
            tokens = word_tokenize(text)
            # Remove punctuation tokens
            tokens = [t for t in tokens if t.isalpha()]
        return tokens

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords."""
        return [t for t in tokens if t not in self.stop_words]

    def lemmatize(self, tokens: List[str]) -> List[str]:
        """Lemmatize each token."""
        return [self.lemmatizer.lemmatize(t) for t in tokens]

    def extract_skills(self, text: str) -> List[str]:
        """Extract skill keywords from text (case-insensitive, whole word matching)."""
        text_lower = text.lower()
        found_skills = set()
        for skill in self.skill_set:
            # Use word boundary regex to match whole words/phrases
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        # Also check for multi-word skills without boundaries issue
        # (the above handles phrases like "machine learning" as whole)
        return sorted(found_skills)
    
    def extract_ner_info(self, raw_text: str) -> dict:
        """Extract experience, degrees, universities, job titles."""
        try:
            return self.ner.extract_all(raw_text)
        except Exception as e:
            logger.warning(f"NER extraction failed: {str(e)}")
        return {}

    def preprocess(self, raw_text: str) -> Tuple[str, List[str], List[str]]:
        """
        Main pipeline.
        Returns: (cleaned_text_string, list_of_tokens, list_of_found_skills)
        """
        if not raw_text or not isinstance(raw_text, str):
            return "", [], []
        
        # Step 1: Basic clean
        cleaned = self.clean_text(raw_text)
        
        # Step 2: Tokenize
        tokens = self.tokenize(cleaned)
        
        # Step 3: Remove stopwords
        tokens_no_stop = self.remove_stopwords(tokens)
        
        # Step 4: Lemmatize
        tokens_lemmatized = self.lemmatize(tokens_no_stop)
        
        # Step 5: Extract skills (from original raw text for better phrase detection)
        skills = self.extract_skills(raw_text)
        
        # Return cleaned string (space-joined tokens) for vectorization
        cleaned_string = " ".join(tokens_lemmatized)
        
        return cleaned_string, tokens_lemmatized, skills


# Quick test (run from project root)
if __name__ == "__main__":
    sample_text = """
    John Doe is a Python Developer with 5 years of experience in Machine Learning and SQL.
    He has worked on deep learning projects using TensorFlow and PyTorch.
    """
    preprocessor = TextPreprocessor()
    cleaned, tokens, skills = preprocessor.preprocess(sample_text)
    print("Cleaned string:", cleaned[:200], "...")
    print("Skills found:", skills)