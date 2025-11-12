"""
Main Streamlit Application - Professional Resume Matching System
Clean, professional UI with proper navigation
"""

import streamlit as st
import os
from datetime import datetime

# Import custom modules
from modules.text_extractor import extract_text_from_file, get_files_from_folder
from modules.jd_parser import parse_jd, get_jd_summary
from modules.resume_parser import parse_resume, get_resume_summary
from modules.rubrics_generator import (
    generate_rubrics_from_jd,
    format_rubrics_for_display,
    normalize_weights
)
from modules.evaluator import evaluate_candidate_with_reasoning, rank_candidates
from modules.db_manager import DatabaseManager

# Page Configuration
st.set_page_config(
    page_title="AI Resume Matcher Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Initialize Database Manager
@st.cache_resource
def get_db_manager():
    return DatabaseManager()


db = get_db_manager()

# Custom CSS - Professional Design
st.markdown("""
<style>
    /* Main Header */
    .main-header {
        font-size: 2.2rem;
        font-weight: 600;
        color: #2C3E50;
        margin-bottom: 1.5rem;
        border-bottom: 3px solid #3498DB;
        padding-bottom: 0.5rem;
    }

    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #34495E;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #3498DB;
        padding-left: 0.5rem;
    }

    /* Cards */
    .info-card {
        padding: 1.5rem;
        border-radius: 8px;
        background-color: #F8F9FA;
        border: 1px solid #DEE2E6;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .success-card {
        padding: 1.5rem;
        border-radius: 8px;
        background-color: #D4EDDA;
        border-left: 4px solid #28A745;
        margin: 1rem 0;
    }

    .warning-card {
        padding: 1.5rem;
        border-radius: 8px;
        background-color: #FFF3CD;
        border-left: 4px solid #FFC107;
        margin: 1rem 0;
    }

    /* Stat Box */
    .stat-box {
        background: white;
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 3px solid #3498DB;
    }

    /* Tier Styling */
    .tier-high {
        color: #28A745;
        font-weight: 600;
        background-color: #D4EDDA;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
    }

    .tier-moderate {
        color: #856404;
        font-weight: 600;
        background-color: #FFF3CD;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
    }

    .tier-low {
        color: #721C24;
        font-weight: 600;
        background-color: #F8D7DA;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
    }

    /* Rank Badges */
    .rank-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-right: 0.5rem;
    }

    .rank-1 { background-color: #FFD700; color: #000; }
    .rank-2 { background-color: #C0C0C0; color: #000; }
    .rank-3 { background-color: #CD7F32; color: #fff; }
    .rank-other { background-color: #6C757D; color: #fff; }

    /* Navigation Buttons */
    .stButton button {
        font-weight: 500;
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: #F8F9FA;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'selected_jd_id' not in st.session_state:
    st.session_state.selected_jd_id = None
if 'jd_selected' not in st.session_state:
    st.session_state.jd_selected = False


def reset_navigation():
    """Reset navigation state"""
    st.session_state.selected_jd_id = None
    st.session_state.jd_selected = False


def main():
    st.markdown('<h1 class="main-header">AI-Powered Resume Matching System</h1>', unsafe_allow_html=True)

    # Sidebar Navigation
    with st.sidebar:
        st.header("Navigation")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Home", use_container_width=True):
                st.session_state.current_page = 'home'
                reset_navigation()
                st.rerun()

        with col2:
            if st.button("Back", use_container_width=True):
                if st.session_state.current_page == 'results':
                    st.session_state.current_page = 'resume_matching'
                elif st.session_state.current_page in ['jd_parsing', 'resume_matching']:
                    st.session_state.current_page = 'home'
                st.rerun()

        st.markdown("---")
        st.subheader("System Statistics")

        try:
            total_jds = db.count_all_jds()
            total_resumes = db.count_all_resumes()
            total_results = db.count_all_results()

            st.metric("Total JDs", total_jds)
            st.metric("Total Resumes", total_resumes)
            st.metric("Evaluations", total_results)
        except Exception as e:
            st.error("Error loading statistics")

    # Route to pages
    if st.session_state.current_page == 'home':
        show_home_page()
    elif st.session_state.current_page == 'jd_parsing':
        show_jd_parsing_page()
    elif st.session_state.current_page == 'resume_matching':
        show_resume_matching_page()
    elif st.session_state.current_page == 'results':
        show_results_page()


# ============== HOME PAGE ==============
def show_home_page():
    st.markdown('<h2 class="section-header">Welcome to AI Resume Matcher</h2>', unsafe_allow_html=True)

    st.write("A professional system for intelligent resume screening and candidate evaluation.")

    st.markdown("---")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="info-card">
            <h3 style="color: #2C3E50;">JD Parsing</h3>
            <p style="color: #5D6D7E;">Upload and parse Job Descriptions with AI</p>
            <ul style="color: #5D6D7E;">
                <li>Automatic extraction of requirements</li>
                <li>AI-powered rubrics generation</li>
                <li>Customizable evaluation criteria</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start JD Parsing", use_container_width=True, type="primary"):
            st.session_state.current_page = 'jd_parsing'
            st.rerun()

    with col2:
        st.markdown("""
        <div class="info-card">
            <h3 style="color: #2C3E50;">Resume Matching</h3>
            <p style="color: #5D6D7E;">Match resumes against Job Descriptions</p>
            <ul style="color: #5D6D7E;">
                <li>Select JD for evaluation</li>
                <li>Upload multiple resumes</li>
                <li>AI-driven ranking and analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Resume Matching", use_container_width=True, type="primary"):
            st.session_state.current_page = 'resume_matching'
            reset_navigation()
            st.rerun()

    st.markdown("---")

    # Recent Activity
    st.markdown('<h3 class="section-header">Recent Activity</h3>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Recent JDs**")
        try:
            recent_jds = db.get_recent_jds(5)
            if recent_jds:
                for jd in recent_jds:
                    st.caption(f"• {jd.get('job_title', 'Unknown')} ({jd.get('jd_id')})")
            else:
                st.caption("No JDs uploaded yet")
        except Exception as e:
            st.caption("Error loading JDs")

    with col2:
        st.markdown("**Recent Resumes**")
        try:
            recent_resumes = db.get_recent_resumes(5)
            if recent_resumes:
                for resume in recent_resumes:
                    st.caption(f"• {resume.get('name', 'Unknown')} ({resume.get('resume_id')})")
            else:
                st.caption("No resumes parsed yet")
        except Exception as e:
            st.caption("Error loading resumes")

    with col3:
        st.markdown("**Recent Matches**")
        try:
            recent_results = db.get_recent_results(5)
            if recent_results:
                for result in recent_results:
                    st.caption(f"• {result.get('candidate_name', 'Unknown')} - {result.get('overall_score', 0):.1f}%")
            else:
                st.caption("No matches yet")
        except Exception as e:
            st.caption("Error loading results")


# ============== JD PARSING PAGE ==============
def show_jd_parsing_page():
    st.markdown('<h2 class="section-header">Job Description Parsing</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Upload Job Description")
        jd_file = st.file_uploader(
            "Select JD File (PDF/DOCX)",
            type=['pdf', 'docx', 'doc'],
            key='jd_uploader',
            help="Upload the job description file"
        )

        if jd_file:
            st.success(f"File selected: {jd_file.name}")

    with col2:
        st.subheader("Existing JDs")
        try:
            all_jds = db.get_all_jds()
            if all_jds:
                for jd in all_jds[:5]:
                    with st.expander(f"{jd.get('job_title', 'Unknown')}", expanded=False):
                        st.caption(f"ID: {jd.get('jd_id')}")
                        st.caption(f"Date: {jd.get('timestamp', 'N/A')[:10]}")
            else:
                st.info("No JDs uploaded yet")
        except Exception as e:
            st.error("Error loading JDs")

    st.markdown("---")

    if st.button("Parse JD", type="primary", use_container_width=True, disabled=not jd_file):
        if jd_file:
            with st.spinner("Parsing Job Description..."):
                try:
                    # Extract text
                    jd_text = extract_text_from_file(jd_file)

                    if not jd_text:
                        st.error("Failed to extract text from JD file")
                        return

                    # Parse JD
                    jd_data = parse_jd(jd_text)

                    if not jd_data:
                        st.error("Failed to parse Job Description")
                        return

                    # Save JD
                    jd_id = db.save_jd(jd_data, jd_file.name)

                    st.success(f"Job Description parsed and stored successfully!")
                    st.info(f"JD ID: {jd_id}")

                    # Show JD summary
                    with st.expander("View Parsed JD", expanded=True):
                        st.text(get_jd_summary(jd_data))

                    st.markdown("---")

                    # Auto-generate rubrics
                    st.info("Generating AI rubrics for this JD...")

                    with st.spinner("AI is analyzing JD and generating rubrics..."):
                        rubrics = generate_rubrics_from_jd(jd_data)

                        if rubrics:
                            db.save_rubrics(jd_id, rubrics)
                            st.success("AI rubrics generated successfully!")

                            with st.expander("View Generated Rubrics", expanded=True):
                                st.text(format_rubrics_for_display(rubrics))
                        else:
                            st.error("Failed to generate rubrics")

                except Exception as e:
                    st.error(f"Error during JD parsing: {str(e)}")


# ============== RESUME MATCHING PAGE ==============
def show_resume_matching_page():
    st.markdown('<h2 class="section-header">Resume Matching</h2>', unsafe_allow_html=True)

    # Step 1: Select JD
    if not st.session_state.jd_selected:
        st.subheader("Step 1: Select Job Description")

        try:
            all_jds = db.get_all_jds()

            if not all_jds:
                st.warning("No Job Descriptions found. Please parse a JD first.")
                if st.button("Go to JD Parsing", type="primary"):
                    st.session_state.current_page = 'jd_parsing'
                    st.rerun()
                return

            # Create selection dropdown
            jd_options = {}
            for jd in all_jds:
                jd_title = jd.get('job_title', 'Unknown')
                jd_id = jd.get('jd_id', 'N/A')
                jd_options[f"{jd_title} ({jd_id})"] = jd_id

            selected_jd_name = st.selectbox(
                "Select Job Description:",
                list(jd_options.keys()),
                key='jd_selector'
            )

            if st.button("Confirm JD Selection", type="primary", use_container_width=True):
                st.session_state.selected_jd_id = jd_options[selected_jd_name]
                st.session_state.jd_selected = True
                st.rerun()

        except Exception as e:
            st.error(f"Error loading JDs: {str(e)}")
            return

    # If JD is selected, show next steps
    else:
        jd_id = st.session_state.selected_jd_id

        try:
            jd_data = db.get_jd(jd_id)

            if not jd_data:
                st.error("JD data not found. Please select again.")
                st.session_state.jd_selected = False
                st.rerun()
                return

            # Show selected JD
            st.success(f"Selected JD: {jd_data.get('job_title', 'Unknown')} ({jd_id})")

            if st.button("Change JD Selection", type="secondary"):
                st.session_state.jd_selected = False
                st.rerun()

            st.markdown("---")

            # Display JD Preview
            with st.expander("View Selected JD", expanded=False):
                st.text(get_jd_summary(jd_data))

            st.markdown("---")

            # Step 2: Review/Adjust Rubrics
            st.subheader("Step 2: Review & Adjust Rubrics")

            rubrics = db.get_rubrics(jd_id)

            if not rubrics:
                st.warning("No rubrics found for this JD. Generating now...")
                with st.spinner("Generating AI rubrics..."):
                    try:
                        rubrics = generate_rubrics_from_jd(jd_data)
                        if rubrics:
                            db.save_rubrics(jd_id, rubrics)
                            st.success("Rubrics generated!")
                            st.rerun()
                        else:
                            st.error("Failed to generate rubrics")
                            return
                    except Exception as e:
                        st.error(f"Error generating rubrics: {str(e)}")
                        return

            # Display current rubrics
            with st.expander("View Rubrics Configuration", expanded=False):
                st.text(format_rubrics_for_display(rubrics))

            # Adjustable Weights
            with st.expander("Adjust Evaluation Weights (Optional)", expanded=False):
                st.info("Total must equal 100%")

                weights = rubrics.get('weights', {})

                col1, col2 = st.columns(2)

                with col1:
                    skills_weight = st.slider("Skills Weight (%)", 0, 100, int(weights.get('skills', 25)),
                                              key='skills_slider')
                    tools_weight = st.slider("Tools Weight (%)", 0, 100, int(weights.get('tools', 25)),
                                             key='tools_slider')
                    experience_weight = st.slider("Experience Weight (%)", 0, 100, int(weights.get('experience', 20)),
                                                  key='exp_slider')
                    education_weight = st.slider("Education Weight (%)", 0, 100, int(weights.get('education', 5)),
                                                 key='edu_slider')

                with col2:
                    projects_weight = st.slider("Projects Weight (%)", 0, 100, int(weights.get('projects', 15)),
                                                key='proj_slider')
                    certifications_weight = st.slider("Certifications Weight (%)", 0, 100,
                                                      int(weights.get('certifications', 5)), key='cert_slider')
                    profile_weight = st.slider("Profile Quality Weight (%)", 0, 100,
                                               int(weights.get('profile_quality', 5)), key='prof_slider')

                new_weights = {
                    'skills': skills_weight,
                    'tools': tools_weight,
                    'experience': experience_weight,
                    'education': education_weight,
                    'projects': projects_weight,
                    'certifications': certifications_weight,
                    'profile_quality': profile_weight
                }

                total_weight = sum(new_weights.values())

                if total_weight != 100:
                    st.error(f"Total weight is {total_weight}%. Must equal 100%!")
                else:
                    st.success(f"Total weight = 100%")

                if total_weight == 100 and st.button("Save Rubrics", type="secondary"):
                    try:
                        rubrics['weights'] = new_weights
                        db.save_rubrics(jd_id, rubrics)
                        st.success("Rubrics updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving rubrics: {str(e)}")

            st.markdown("---")

            # Step 3: Upload Resumes
            st.subheader("Step 3: Upload Resumes")

            upload_mode = st.radio(
                "Choose upload mode:",
                ["Upload Files", "Folder Path"],
                horizontal=True
            )

            resume_files = []
            folder_path = None

            if upload_mode == "Upload Files":
                uploaded_files = st.file_uploader(
                    "Upload Resume Files (PDF/DOCX)",
                    type=['pdf', 'docx', 'doc'],
                    accept_multiple_files=True,
                    key='resume_uploader'
                )

                if uploaded_files:
                    resume_files = uploaded_files
                    st.success(f"{len(resume_files)} file(s) selected")
            else:
                folder_path = st.text_input(
                    "Enter folder path containing resumes:",
                    placeholder=r"C:\Users\YourName\Documents\Resumes"
                )

                if folder_path and os.path.exists(folder_path):
                    files = get_files_from_folder(folder_path)
                    st.success(f"Found {len(files)} file(s) in folder")
                elif folder_path:
                    st.error("Folder path does not exist!")

            st.markdown("---")

            # Step 4: Start Matching
            if st.button("Start Matching", type="primary", use_container_width=True):
                if upload_mode == "Upload Files" and not resume_files:
                    st.error("Please upload at least one resume!")
                    return

                if upload_mode == "Folder Path" and not folder_path:
                    st.error("Please enter a valid folder path!")
                    return

                with st.spinner("Processing resumes and evaluating candidates..."):
                    try:
                        # Get resume files
                        if upload_mode == "Folder Path":
                            resume_file_paths = get_files_from_folder(folder_path)
                        else:
                            resume_file_paths = resume_files

                        # Parse and evaluate resumes
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        results = []

                        for idx, resume_file in enumerate(resume_file_paths):
                            status_text.text(f"Processing resume {idx + 1}/{len(resume_file_paths)}...")

                            # Extract text
                            resume_text = extract_text_from_file(resume_file)

                            if resume_text:
                                # Parse resume
                                resume_data = parse_resume(resume_text)

                                if resume_data:
                                    # Save resume
                                    filename = os.path.basename(resume_file) if isinstance(resume_file,
                                                                                           str) else resume_file.name
                                    resume_id = db.save_resume(resume_data, filename)
                                    resume_data['resume_id'] = resume_id

                                    # Evaluate candidate
                                    evaluation = evaluate_candidate_with_reasoning(jd_data, resume_data, rubrics)

                                    result = {
                                        'jd_id': jd_id,
                                        'jd_title': jd_data.get('job_title', 'Unknown'),
                                        'resume_id': resume_id,
                                        'candidate_name': resume_data.get('name', 'Unknown'),
                                        'contact_email': resume_data.get('contact_details', {}).get('email', 'N/A'),
                                        'contact_phone': resume_data.get('contact_details', {}).get('phone', 'N/A'),
                                        'overall_score': evaluation['overall_score'],
                                        'individual_scores': evaluation['individual_scores'],
                                        'weights_applied': evaluation['weights_applied'],
                                        'breakdown': evaluation['breakdown'],
                                        'ai_reasoning': evaluation['ai_reasoning'],
                                        'candidate_tier': evaluation['candidate_tier'],
                                        'strengths': evaluation['strengths'],
                                        'weaknesses': evaluation['weaknesses']
                                    }

                                    results.append(result)

                            progress_bar.progress((idx + 1) / len(resume_file_paths))

                        status_text.empty()
                        progress_bar.empty()

                        if results:
                            # Clear previous results for this JD
                            db.clear_results_for_jd(jd_id)

                            # Rank candidates
                            ranked_results = rank_candidates(results)

                            # Save to database
                            db.save_evaluation_results(ranked_results)

                            st.success(f"Evaluation completed! {len(ranked_results)} candidates ranked.")

                            # Navigate to results
                            if st.button("View Results", type="primary", use_container_width=True):
                                st.session_state.current_page = 'results'
                                st.rerun()
                        else:
                            st.error("Failed to process any resumes")

                    except Exception as e:
                        st.error(f"Error during matching: {str(e)}")

        except Exception as e:
            st.error(f"Error in resume matching: {str(e)}")
            st.session_state.jd_selected = False


# ============== RESULTS PAGE ==============

# ============== RESULTS PAGE ==============
def show_results_page():
    st.markdown('<h2 class="section-header">Evaluation Results</h2>', unsafe_allow_html=True)

    if not st.session_state.selected_jd_id:
        st.warning("No JD selected. Please go to Resume Matching page.")
        if st.button("Go to Resume Matching"):
            st.session_state.current_page = 'resume_matching'
            st.rerun()
        return

    jd_id = st.session_state.selected_jd_id
    jd_data = db.get_jd(jd_id)

    # Get results
    results = db.get_results_for_jd(jd_id)

    if not results:
        st.warning("No evaluation results found for this JD.")
        if st.button("Go Back to Resume Matching"):
            st.session_state.current_page = 'resume_matching'
            st.rerun()
        return

    st.success(f"Showing results for: {jd_data.get('job_title', 'Unknown')} ({jd_id})")
    st.caption(f"Total Candidates: {len(results)}")

    # Statistics
    st.markdown("---")
    st.subheader("Statistics")

    stats = db.get_jd_statistics(jd_id)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Candidates", stats.get('total_candidates', 0))
    col2.metric("Average Score", f"{stats.get('average_score', 0):.1f}%")
    col3.metric("Highest Score", f"{stats.get('highest_score', 0):.1f}%")
    col4.metric("Lowest Score", f"{stats.get('lowest_score', 0):.1f}%")

    st.markdown("---")

    # Tier Distribution
    tier_counts = {'HIGH': 0, 'MODERATE': 0, 'LOW': 0}
    for result in results:
        tier = result.get('candidate_tier', 'MODERATE')
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    col1, col2, col3 = st.columns(3)
    col1.metric("Best Fit", tier_counts['HIGH'])
    col2.metric("Moderate Fit", tier_counts['MODERATE'])
    col3.metric("Low Fit", tier_counts['LOW'])

    st.markdown("---")

    # Display Results
    st.subheader("Ranked Candidates")

    for result in results:
        rank = result.get('rank', 0)
        name = result.get('candidate_name', 'Unknown')
        score = result.get('overall_score', 0)
        tier = result.get('candidate_tier', 'MODERATE')

        # Rank badge HTML
        if rank == 1:
            rank_badge = '<span class="rank-badge rank-1">Rank 1</span>'
        elif rank == 2:
            rank_badge = '<span class="rank-badge rank-2">Rank 2</span>'
        elif rank == 3:
            rank_badge = '<span class="rank-badge rank-3">Rank 3</span>'
        else:
            rank_badge = f'<span class="rank-badge rank-other">Rank {rank}</span>'

        # Tier styling
        if tier == 'HIGH':
            tier_class = "tier-high"
            tier_label = "Best Fit"
        elif tier == 'MODERATE':
            tier_class = "tier-moderate"
            tier_label = "Moderate Fit"
        else:
            tier_class = "tier-low"
            tier_label = "Low Fit"

        with st.expander(f"{name} - {score:.1f}% - {tier_label}", expanded=(rank <= 3)):
            # Header with rank and tier
            st.markdown(f'{rank_badge} <span class="{tier_class}">{tier_label}</span>', unsafe_allow_html=True)

            st.markdown("---")

            # Contact Information
            st.markdown("#### Contact Information")
            col1, col2, col3 = st.columns(3)
            col1.write(f"**Email:** {result.get('contact_email', 'N/A')}")
            col2.write(f"**Phone:** {result.get('contact_phone', 'N/A')}")
            col3.write(f"**Resume ID:** {result.get('resume_id', 'N/A')}")

            st.markdown("---")

            # Overall Score
            st.markdown("#### Overall Score")
            st.progress(score / 100, text=f"{score:.1f}%")

            st.markdown("---")

            # Individual Scores
            st.markdown("#### Individual Scores")
            scores = result.get('individual_scores', {})
            weights = result.get('weights_applied', {})

            for category, score_val in scores.items():
                weight = weights.get(category, 0)
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.progress(score_val / 100, text=f"{category.replace('_', ' ').title()}: {score_val:.1f}%")
                with col2:
                    st.caption(f"Weight: {weight}%")

            st.markdown("---")

            # AI Reasoning
            st.markdown("#### AI Analysis & Recommendation")
            st.info(result.get('ai_reasoning', 'No reasoning available'))

            st.markdown("---")

            # Strengths & Weaknesses
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Strengths")
                strengths = result.get('strengths', [])
                for strength in strengths:
                    st.write(f"• {strength}")

            with col2:
                st.markdown("#### Areas for Improvement")
                weaknesses = result.get('weaknesses', [])
                for weakness in weaknesses:
                    st.write(f"• {weakness}")

            st.markdown("---")
            st.caption(f"Evaluated on: {result.get('timestamp', 'N/A')}")

    # Option to adjust rubrics and re-evaluate
    st.markdown("---")
    st.subheader("Adjust Rubrics & Re-evaluate")

    if st.button("Adjust Rubrics and Test Again", type="secondary", use_container_width=True):
        st.session_state.current_page = 'resume_matching'
        st.rerun()

if __name__ == "__main__":
    main()