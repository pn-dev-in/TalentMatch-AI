# 📄 AI-Based Resume Screening & Job Matching System

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-resume-screening-sym.streamlit.app/)

## 📌 Overview

A production-level AI system that automatically screens and ranks resumes against a job description. It uses Natural Language Processing and Machine Learning to provide fair, fast, and data-driven candidate shortlisting.

[Add a screenshot of your app's main screen here]

## ✨ Key Features
*   **🤖 Intelligent Matching**: Choose from **Baseline (TF-IDF)** , **Semantic (BERT+FAISS)** , or a **Hybrid** approach for superior results.
*   **🔍 In-Depth Analysis**: Extracts skills, experience (NER), degrees, and job titles from resumes.
*   **📈 ATS Score & Suggestions**: An ATS breakdown (Skills, Experience, Education, Completeness) plus actionable feedback for each candidate.
*   **🖥️ Interactive Dashboard**: A clean, modern UI featuring skill-radar charts, batch missing-skill analysis, and persistent results.
*   **📑 Export & Reports**: Download results as CSV or a formatted PDF report.
*   **🔐 Mock Authentication**: Basic login to simulate a secure environment.

## 🛠️ Built With
*   **Frontend & Logic**: [Streamlit](https://streamlit.io/)
*   **NLP & ML**: `sentence-transformers`, `spaCy`, `scikit-learn`, `FAISS`, `nltk`
*   **Data Handling**: `PyPDF2`, `pdfplumber`, `python-docx`, `pandas`, `plotly`
*   **Backend**: Python 3.9+

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites
*   Python 3.9+
*   `pip` package manager

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    cd YOUR_REPO_NAME
Set up a virtual environment

bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
Install dependencies

bash
pip install -r requirements.txt
Download required NLTK and spaCy data

bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
python -m spacy download en_core_web_sm
Run the application

bash
streamlit run app.py
Default Login
Username: recruiter

Password: screen2025

📊 Using the Kaggle Dataset
Download the 'Resume Dataset' from Kaggle using:

bash
pip install kaggle
kaggle datasets download snehaanbhawal/resume-dataset
unzip resume-dataset.zip -d data/kaggle_resumes/
For full batch testing, a utility script is included:

bash
python utils/batch_test_kaggle.py
🚢 Deployment
The app is easily deployed on Streamlit Community Cloud or Hugging Face Spaces. Simply link your GitHub repository to the chosen platform.

🤝 Contributing
Contributions are what make the open-source community an amazing place to learn. Any contributions you make are greatly appreciated.

📝 License
Distributed under the MIT License. See LICENSE for more information.

text

---

### 📝 Final Polish for a Perfect Project

1.  **Replace Placeholders**: Before the final push, replace `YOUR_DEPLOYED_APP_LINK` and `YOUR_USERNAME` in the `README.md` with your actual values.
2.  **Add a LICENSE File**: (Optional but recommended) Make your project open-source by creating a simple `LICENSE` file with the MIT license text.
3.  **Final Review**: Go through your checklist to make sure everything is in order.

Let me know if you'd like to adjust the README, or if you run into any issues during the deployment process.
