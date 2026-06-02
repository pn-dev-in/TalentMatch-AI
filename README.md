# TalentMatch AI 🚀

### Intelligent Resume Screening & Candidate Ranking Platform

TalentMatch AI is an AI-powered recruitment intelligence platform that automates resume screening, candidate ranking, ATS scoring, skill extraction, and job matching using Natural Language Processing (NLP) and Machine Learning.

The system analyzes resumes against job descriptions, extracts relevant skills and qualifications, identifies missing competencies, and generates ATS-style scores to help recruiters make faster and more informed hiring decisions.

Designed as a modern hiring assistant, TalentMatch AI combines traditional information retrieval techniques with semantic AI models to deliver accurate candidate-job matching at scale.

---

## 🌐 Live Demo

**Application:**

https://ai-resume-screening-sym.streamlit.app/

---

# ✨ Features

### 🤖 Intelligent Candidate Matching

Choose between multiple matching approaches:

* TF-IDF Similarity Matching
* BERT Semantic Matching
* Hybrid Ranking System

### 📄 Resume Parsing

Supports:

* PDF Resumes
* DOCX Resumes

Automatically extracts:

* Skills
* Experience
* Education
* Degrees
* Job Titles

### 📊 ATS Scoring Engine

Generates detailed ATS-style scores based on:

* Skill Match
* Experience Match
* Education Relevance
* Resume Completeness

### 🔍 Skill Gap Analysis

Identifies:

* Missing Skills
* Recommended Skills
* Job Fit Improvements

### 📈 Interactive Analytics Dashboard

Provides:

* Candidate Rankings
* ATS Score Breakdown
* Skill Distribution Analysis
* Missing Skill Insights

### 📑 Export Reports

Download:

* CSV Results
* Candidate Reports
* ATS Analysis Summaries

### 🔐 User Authentication

* Login System
* Recruiter Dashboard Access

---

# 🏗️ System Architecture

```text
Resume Upload
      │
      ▼
Document Parsing
(PDF / DOCX)
      │
      ▼
Text Extraction
      │
      ▼
NLP Processing
      │
      ├─────────────► Skill Extraction
      │
      ├─────────────► Experience Detection
      │
      ├─────────────► Education Analysis
      │
      ▼
Candidate Representation
      │
      ▼
TF-IDF / BERT Embeddings
      │
      ▼
Similarity Matching Engine
      │
      ▼
ATS Scoring Engine
      │
      ▼
Candidate Ranking Dashboard
```

---

# 🎯 Key Capabilities

✅ Resume Screening Automation

✅ Candidate Ranking

✅ ATS Compatibility Scoring

✅ Semantic Resume Matching

✅ Skill Gap Analysis

✅ Batch Resume Processing

✅ PDF & DOCX Support

✅ Exportable Reports

---

# 🛠️ Technology Stack

## Frontend

* Streamlit
* Plotly

## Backend

* Python 3.9+

## Natural Language Processing

* spaCy
* NLTK
* Sentence Transformers

## Machine Learning

* Scikit-Learn
* TF-IDF Vectorization
* Cosine Similarity

## Semantic Search

* BERT Embeddings
* FAISS Vector Database

## Document Processing

* PyPDF2
* pdfplumber
* python-docx

## Data Processing

* Pandas
* NumPy

---

# 📂 Project Structure

```text
TalentMatch-AI/

├── app.py
├── requirements.txt
├── data/
├── models/
├── utils/
├── reports/
├── assets/
├── tests/
└── README.md
```

---

# 📊 Business Impact

TalentMatch AI helps organizations:

* Reduce manual resume screening time
* Improve recruiter productivity
* Identify qualified candidates faster
* Standardize hiring decisions
* Detect missing skills automatically
* Process large applicant pools efficiently

---

# 📸 Screenshots

## Login 
<img width="1919" height="1004" alt="Screenshot 2026-05-11 144938" src="https://github.com/user-attachments/assets/4af20170-f5e8-4783-b082-2ad825861e66" />

## Dashboard

<img width="1919" height="1005" alt="Screenshot 2026-05-11 145038" src="https://github.com/user-attachments/assets/deb2985e-de11-42e6-87e9-346b2f124c60" />

## Resume Analysis

<img width="1919" height="1009" alt="Screenshot 2026-05-11 145110" src="https://github.com/user-attachments/assets/d87ff213-6444-4094-b682-4a9b59a240e9" />


## Candidate Ranking

<img width="1919" height="1018" alt="Screenshot 2026-05-11 145123" src="https://github.com/user-attachments/assets/7e691fbb-24aa-45ee-9702-b79e0e6610b0" />


## Personalized Feedback

<img width="1919" height="1012" alt="Screenshot 2026-05-11 145213" src="https://github.com/user-attachments/assets/74fbec67-9437-4462-8800-89ef2c7c0d60" />


## Skill Gap Analysis

<img width="1919" height="1009" alt="Screenshot 2026-05-11 145132" src="https://github.com/user-attachments/assets/b7bb8d8e-2e04-4127-99b8-e8ccdfbc152c" />


---

# 🚀 Local Installation

## Clone Repository

```bash
git clone https://github.com/pn-dev-in/TalentMatch-AI.git

cd TalentMatch-AI
```

## Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Download NLP Resources

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

```bash
python -m spacy download en_core_web_sm
```

## Run Application

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

# 🔑 Demo Credentials

Username:

```text
recruiter
```

Password:

```text
screen2025
```

---

# 📈 Project Highlights

* Supports semantic AI matching using BERT
* Uses FAISS for efficient similarity search
* ATS-style candidate evaluation
* Automated skill extraction
* Candidate ranking system
* Batch resume processing
* Exportable reports
* Cloud deployment ready

---

# 🧪 Testing

Run tests:

```bash
pytest
```

---

# 🚀 Future Roadmap

* LLM-powered resume analysis
* AI interview question generation
* Resume optimization suggestions
* Recruiter collaboration workspace
* Multi-language resume support
* Candidate recommendation engine
* HR analytics dashboard
* Applicant tracking system integration

---

# 🎓 Skills Demonstrated

This project demonstrates practical experience in:

✅ Natural Language Processing

✅ Machine Learning

✅ Semantic Search

✅ Information Retrieval

✅ Resume Parsing

✅ Candidate Ranking Systems

✅ Streamlit Application Development

✅ Data Visualization

✅ Vector Databases (FAISS)

✅ AI Product Development

---

# 👨‍💻 Author

### Pravesh Nandanwar

Computer Science & Engineering

GitHub:
https://github.com/pn-dev-in

LinkedIn:
(Add LinkedIn Profile)

---

# ⭐ Support

If you found this project useful, consider giving it a star on GitHub.

Feedback, suggestions, and contributions are always welcome.
