"""
AI-Based Resume Screening System - Enhanced UI
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import os
import tempfile
import matplotlib.pyplot as plt
import yaml
import plotly.graph_objects as go
from datetime import datetime

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Import our modules
from models.resume_parser import ResumeParser
from models.text_preprocessor import TextPreprocessor
from models.matcher import BaselineMatcher
from models.semantic_matcher import SemanticMatcher
from models.hybrid_matcher import HybridMatcher
from utils.resume_summarizer import ResumeSummarizer
from utils.skill_extractor import SkillExtractor
from utils.ats_scorer import ATSScorer
from utils.skill_gap_analyzer import SkillGapAnalyzer
from utils.evaluator import evaluate_matcher
from utils.report_generator import generate_report

# ============================================================================
# PAGE CONFIG & CUSTOM CSS
# ============================================================================
st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container spacing */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    /* Custom header */
    .custom-header {
        background: linear-gradient(90deg, #FF4B4B, #FF8C4B);
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .custom-header h1 {
        color: white;
        margin: 0;
        font-size: 2rem;
    }
    .custom-header p {
        color: #f0f0f0;
        margin: 0.5rem 0 0 0;
    }
    /* Metric cards */
    .metric-card {
        background-color: #262730;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-3px);
    }
    /* Buttons */
    .stButton > button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #FF6B4B;
        transform: scale(1.02);
        box-shadow: 0 2px 8px rgba(255,75,75,0.4);
    }
    /* Expander headers */
    .streamlit-expanderHeader {
        background-color: #1E1E2E;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1.1rem;
    }
    /* Dataframe */
    .dataframe {
        font-size: 0.85rem;
        border-radius: 10px;
        overflow: auto;
    }
    /* Sidebar */
    .css-1d391kg {
        background-color: #1E1E2E;
    }
    /* Success/Warning boxes */
    .stAlert {
        border-radius: 8px;
    }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        background-color: #262730;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4B4B;
        color: white;
    }
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 1px solid #333;
        font-size: 0.8rem;
        color: #aaa;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOGIN / AUTHENTICATION (Mock)
# ============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login_page():
    st.markdown('<div class="custom-header"><h1>🔐 Resume Screening System</h1><p>Please log in to continue</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("#### Demo Access")
        username = st.text_input("Username", placeholder="recruiter")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        if st.button("Login", use_container_width=True):
            if username == "recruiter" and password == "screen2025":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials. Use recruiter / screen2025")
        st.caption("Demo credentials: `recruiter` / `screen2025`")
    st.stop()

if not st.session_state.logged_in:
    login_page()

# ============================================================================
# INIT SESSION STATE
# ============================================================================
if 'screening_results' not in st.session_state:
    st.session_state.screening_results = None
if 'resume_skills_map' not in st.session_state:
    st.session_state.resume_skills_map = None
if 'resume_ner_map' not in st.session_state:
    st.session_state.resume_ner_map = None
if 'resume_summaries' not in st.session_state:
    st.session_state.resume_summaries = None
if 'ats_scores' not in st.session_state:
    st.session_state.ats_scores = None
if 'last_jd_text' not in st.session_state:
    st.session_state.last_jd_text = ""
if 'last_matcher_type' not in st.session_state:
    st.session_state.last_matcher_type = ""
if 'jd_skills' not in st.session_state:
    st.session_state.jd_skills = []

# ============================================================================
# HEADER & SIDEBAR
# ============================================================================
st.markdown('<div class="custom-header"><h1>📄 AI Resume Screener</h1><p>Intelligent candidate ranking & skill analysis</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/resume.png", width=80)
    st.markdown("## ⚙️ Configuration")
    
    matcher_type = st.radio(
        "**Matcher**",
        options=["Baseline (TF-IDF)", "Semantic (BERT+FAISS)", "Hybrid (TF-IDF + BERT)"],
        help="Baseline: keyword only. Semantic: meaning only. Hybrid: best of both.",
        index=2  # default to hybrid
    )
    
    if matcher_type == "Hybrid (TF-IDF + BERT)":
        hybrid_alpha = st.slider(
            "TF-IDF Weight (α)",
            min_value=0.0, max_value=1.0, value=0.4, step=0.05,
            help="Higher = more keyword importance, lower = more semantic meaning."
        )
    else:
        hybrid_alpha = 0.4
    
    top_k = st.slider(
        "**Top candidates**",
        min_value=1, max_value=50, value=config['matching']['top_k_default'],
        help="Number of ranked candidates to display."
    )
    
    st.markdown("---")
    st.info("📌 **Note:** First semantic/hybrid run may take 30s to load the model.")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ============================================================================
# FILE UPLOAD & JOB DESCRIPTION
# ============================================================================
col_left, col_right = st.columns([1, 1], gap="large")
with col_left:
    st.markdown("### 📂 Upload Resumes")
    uploaded_files = st.file_uploader(
        "PDF, DOCX, or TXT",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        key="resume_uploader",
        help="Upload one or more resumes (max 10MB each)."
    )
with col_right:
    st.markdown("### 📝 Job Description")
    jd_text = st.text_area(
        "Paste the job description here",
        height=200,
        placeholder="e.g., We are looking for a Python developer with experience in machine learning and SQL..."
    )

# Process button
process_btn = st.button("🚀 Screen Resumes", type="primary", use_container_width=True)

# ============================================================================
# MAIN PROCESSING (when button clicked)
# ============================================================================
if process_btn:
    if not uploaded_files:
        st.error("❌ Please upload at least one resume file.")
    elif not jd_text.strip():
        st.error("❌ Please enter a job description.")
    else:
        with st.spinner("⏳ Processing resumes... this may take a moment."):
            parser = ResumeParser()
            preprocessor = TextPreprocessor()
            summarizer = ResumeSummarizer()
            skill_extractor = SkillExtractor()
            ats_scorer = ATSScorer()
            
            jd_skills = skill_extractor.extract_required_skills(jd_text)
            st.session_state.jd_skills = jd_skills
            
            resume_texts_cleaned = []
            resume_names = []
            resume_skills = []
            resume_ner = []
            resume_summaries = []
            ats_scores_list = []
            
            progress_bar = st.progress(0)
            for idx, uploaded_file in enumerate(uploaded_files):
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                raw_text, error = parser.parse(tmp_path)
                if raw_text:
                    cleaned, tokens, skills = preprocessor.preprocess(raw_text)
                    ner_info = preprocessor.extract_ner_info(raw_text)
                    summary = summarizer.generate_summary(ner_info, skills, uploaded_file.name)
                    
                    ats_result = ats_scorer.compute_total_score(
                        jd_skills=jd_skills,
                        candidate_skills=skills,
                        candidate_years=ner_info.get('years_experience', 0),
                        candidate_degrees=ner_info.get('degrees', []),
                        resume_text=raw_text,
                        jd_required_years=0,
                        jd_requires_degree=True
                    )
                    ats_scores_list.append(ats_result)
                    resume_summaries.append(summary)
                    resume_texts_cleaned.append(cleaned)
                    resume_names.append(uploaded_file.name)
                    resume_skills.append(skills)
                    resume_ner.append(ner_info)
                else:
                    st.warning(f"⚠️ Could not parse {uploaded_file.name}: {error}")
                
                os.unlink(tmp_path)
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            if not resume_texts_cleaned:
                st.error("No valid resumes could be processed. Check file formats.")
                st.stop()
            
            # Perform matching
            if matcher_type == "Baseline (TF-IDF)":
                matcher = BaselineMatcher()
                results_df = matcher.rank_resumes(resume_texts_cleaned, resume_names, jd_text)
                st.success(f"✅ Baseline matching completed. Processed {len(resume_texts_cleaned)} resumes.")
            elif matcher_type == "Semantic (BERT+FAISS)":
                matcher = SemanticMatcher(use_faiss=True)
                matcher.fit_resumes(resume_texts_cleaned, resume_names)
                results_df = matcher.rank_resumes(jd_text, top_k=None)
                st.success(f"✅ Semantic matching completed. Processed {len(resume_texts_cleaned)} resumes.")
            else:  # Hybrid
                matcher = HybridMatcher(alpha=hybrid_alpha, use_faiss=True)
                matcher.fit_resumes(resume_texts_cleaned, resume_names)
                results_df = matcher.rank_resumes(jd_text, top_k=None)
                st.success(f"✅ Hybrid matching completed (α={hybrid_alpha}). Processed {len(resume_texts_cleaned)} resumes.")
            
            if matcher_type == "Hybrid (TF-IDF + BERT)":
                results_df['Match_Score'] = results_df['Hybrid_Score']
            else:
                results_df['Match_Score'] = results_df['Match_Score']
            
            # Store in session state
            st.session_state.screening_results = results_df
            st.session_state.resume_skills_map = {name: skills for name, skills in zip(resume_names, resume_skills)}
            st.session_state.resume_ner_map = {name: ner for name, ner in zip(resume_names, resume_ner)}
            st.session_state.resume_summaries = resume_summaries
            st.session_state.ats_scores = ats_scores_list
            st.session_state.last_jd_text = jd_text
            st.session_state.last_matcher_type = matcher_type
            
            st.rerun()

# ============================================================================
# DISPLAY RESULTS (if available)
# ============================================================================
if st.session_state.screening_results is not None:
    results_df = st.session_state.screening_results
    resume_skills_map = st.session_state.resume_skills_map
    resume_ner_map = st.session_state.resume_ner_map
    ats_scores = st.session_state.ats_scores
    matcher_type = st.session_state.last_matcher_type
    jd_text = st.session_state.last_jd_text
    
    # Prepare display dataframe
    results_df_display = results_df.head(top_k).copy()
    if ats_scores:
        ats_df = pd.DataFrame(ats_scores)
        for col in ats_df.columns:
            results_df_display[col] = ats_df[col].values[:len(results_df_display)]
    
    if matcher_type == "Hybrid (TF-IDF + BERT)":
        results_df_display['Match_Score'] = results_df_display['Hybrid_Score']
        results_df_display['TF-IDF Score'] = results_df_display['TFIDF_Score']
        results_df_display['BERT Score'] = results_df_display['BERT_Score']
    
    # ========== TOP METRICS ==========
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📄 Total Resumes", len(results_df))
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        score_col = 'Hybrid_Score' if matcher_type == "Hybrid (TF-IDF + BERT)" else 'Match_Score'
        top_score = results_df_display.iloc[0][score_col] if len(results_df_display) > 0 else 0
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🏆 Top Match", f"{top_score:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("⚙️ Matcher", matcher_type)
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        avg_score = results_df_display['Match_Score'].mean() if len(results_df_display) > 0 else 0
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📊 Avg Score", f"{avg_score:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== BAR CHART ==========
    st.subheader("📊 Match Score Distribution (Top Candidates)")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(results_df_display['Filename'], results_df_display['Match_Score'], color='#FF4B4B', edgecolor='white')
    ax.set_xlabel("Match Score (%)", fontsize=12)
    ax.set_title("Ranked by Relevance", fontsize=14)
    ax.invert_yaxis()
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    st.pyplot(fig)
    
    # ========== DETAILED TABLE ==========
    st.subheader("📋 Candidate Details")
    # Add columns
    results_df_display['Detected_Skills'] = results_df_display['Filename'].map(
        lambda f: ", ".join(resume_skills_map.get(f, [])) if resume_skills_map.get(f) else "None"
    )
    results_df_display['Experience (yrs)'] = results_df_display['Filename'].map(
        lambda f: resume_ner_map.get(f, {}).get('years_experience', 0)
    )
    results_df_display['Degrees'] = results_df_display['Filename'].map(
        lambda f: ", ".join(resume_ner_map.get(f, {}).get('degrees', [])) or "None"
    )
    results_df_display['Job Titles'] = results_df_display['Filename'].map(
        lambda f: ", ".join(resume_ner_map.get(f, {}).get('job_titles', [])) or "None"
    )
    results_df_display['Universities'] = results_df_display['Filename'].map(
        lambda f: ", ".join(resume_ner_map.get(f, {}).get('universities', [])) or "None"
    )
    summary_map = dict(zip(st.session_state.resume_skills_map.keys(), st.session_state.resume_summaries))
    results_df_display['Summary'] = results_df_display['Filename'].map(lambda f: summary_map.get(f, ""))
    
    # Select columns to show
    base_cols = ['Rank', 'Filename', 'Match_Score', 'ATS_Total', 'Experience (yrs)', 'Degrees', 'Job Titles', 'Detected_Skills', 'Summary']
    if matcher_type == "Hybrid (TF-IDF + BERT)":
        display_cols = base_cols[:3] + ['TF-IDF Score', 'BERT Score'] + base_cols[3:]
    else:
        display_cols = base_cols
    st.dataframe(results_df_display[display_cols].reset_index(drop=True), use_container_width=True, height=400)
    
    # ========== TABS FOR DEEP ANALYSIS ==========
    tab1, tab2, tab3, tab4 = st.tabs(["📡 Skills Radar", "🔍 Missing Skills", "💡 Personalized Feedback", "📄 Reports"])
    
    with tab1:
        st.subheader("📡 Skills Radar Chart")
        if len(results_df) > 0:
            candidate_names = results_df['Filename'].tolist()
            selected_candidate = st.selectbox("Choose a candidate:", candidate_names, key="radar_select")
            candidate_skills_set = set(s.lower() for s in st.session_state.resume_skills_map.get(selected_candidate, []))
            jd_skills_set = set(s.lower() for s in st.session_state.jd_skills)
            all_skills = sorted(set(jd_skills_set) | candidate_skills_set)
            if all_skills:
                jd_vals = [1 if s in jd_skills_set else 0 for s in all_skills]
                cand_vals = [1 if s in candidate_skills_set else 0 for s in all_skills]
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=jd_vals, theta=all_skills, fill='toself', name='Job Description', line_color='blue'))
                fig.add_trace(go.Scatterpolar(r=cand_vals, theta=all_skills, fill='toself', name=selected_candidate, line_color='orange'))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,1], tickvals=[0,1], ticktext=['Missing','Present'])), height=500)
                st.plotly_chart(fig, use_container_width=True)
                missing = sorted(jd_skills_set - candidate_skills_set)
                if missing:
                    st.warning(f"⚠️ Missing: {', '.join(missing)}")
                else:
                    st.success("✅ Candidate has all required skills!")
            else:
                st.info("No skills detected.")
        else:
            st.info("No candidates to compare.")
    
    with tab2:
        st.subheader("🔍 Missing Skills Analysis (Batch)")
        if st.session_state.jd_skills:
            from utils.skill_gap_analyzer import SkillGapAnalyzer
            analyzer = SkillGapAnalyzer()
            all_candidate_skills = list(st.session_state.resume_skills_map.values())
            gap_summary = analyzer.get_skill_gap_summary(st.session_state.jd_skills, all_candidate_skills)
            if gap_summary:
                st.markdown("**Most frequently missing skills across all candidates:**")
                gap_df = pd.DataFrame(gap_summary.items(), columns=['Skill', 'Missing Count']).head(10)
                st.bar_chart(gap_df.set_index('Skill'))
            with st.expander("📋 Per‑candidate missing skills"):
                for fname, skills in st.session_state.resume_skills_map.items():
                    report = analyzer.generate_missing_skills_report(st.session_state.jd_skills, skills, fname)
                    st.markdown(report)
        else:
            st.info("No JD skills extracted.")
    
    with tab3:
        st.subheader("💡 Personalized Feedback & Suggestions")
        for idx, row in results_df_display.iterrows():
            with st.expander(f"📝 {row['Filename']} – Score: {row.get('ATS_Total', row['Match_Score'])}%"):
                filename = row['Filename']
                candidate_skills = st.session_state.resume_skills_map.get(filename, [])
                ner_info = st.session_state.resume_ner_map.get(filename, {})
                scorer = ATSScorer()
                feedback = scorer.generate_feedback(
                    jd_skills=st.session_state.jd_skills,
                    candidate_skills=candidate_skills,
                    candidate_years=ner_info.get('years_experience', 0),
                    candidate_degrees=ner_info.get('degrees', []),
                    resume_text=row.get('Text_Preview', '')
                )
                for tip in feedback:
                    st.markdown(tip)
                if idx < len(ats_scores):
                    scores = ats_scores[idx]
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Skills", f"{scores['Skills_Score']:.0f}%")
                    c2.metric("Experience", f"{scores['Experience_Score']:.0f}%")
                    c3.metric("Education", f"{scores['Education_Score']:.0f}%")
                    c4.metric("Completeness", f"{scores['Completeness_Score']:.0f}%")
    
    with tab4:
        st.subheader("📄 Export & Reports")
        # Download CSV
        csv = results_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Full Results (CSV)", csv, "resume_screening_results.csv", "text/csv")
        # PDF Report
        if st.button("Generate PDF Report"):
            jd_preview = jd_text[:500] if len(jd_text) > 500 else jd_text
            # Use the display DataFrame which contains all enriched columns
            report_path = generate_report(results_df_display, jd_preview, matcher_type, "screening_report.pdf")
            with open(report_path, "rb") as f:
                st.download_button("📄 Download PDF", f, "screening_report.pdf", "application/pdf")
        # Ground truth evaluation
        st.markdown("**Evaluation with Ground Truth**")
        gt_file = st.file_uploader("Upload ground truth CSV (Filename, Relevant)", type=['csv'], key="gt_eval")
        if gt_file:
            gt_df = pd.read_csv(gt_file)
            relevant_files = gt_df[gt_df['Relevant'] == 1]['Filename'].tolist()
            metrics = evaluate_matcher(results_df, {'relevant_filenames': relevant_files})
            st.dataframe(pd.DataFrame([metrics]).T.rename(columns={0:'Value'}))
    
    # Top resume text expander (optional)
    if len(results_df_display) > 0:
        with st.expander("🔍 View Top Resume Raw Text (Preview)"):
            st.text(results_df_display.iloc[0]['Text_Preview'])
else:
    st.info("👈 Upload resumes, enter a job description, then click 'Screen Resumes'.")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown('<div class="footer">AI-Based Resume Screening System | Built with Streamlit, Sentence-BERT, FAISS</div>', unsafe_allow_html=True)