# app.py
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import io
import base64
import pdf2image
import google.generativeai as genai

from auth import register_user, authenticate_user, init_db
from database import (
    create_job_posting,
    get_job_postings,
    submit_application,
    get_applications,
    update_application_status
)

# Configure Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="RecruitAI - Hiring Platform",
    page_icon="👥",
    layout="wide"
)

# -------------------- Custom CSS --------------------
st.markdown("""
<style>
    body, .stApp {
        background: #F9FAFB;
        font-family: 'Segoe UI', sans-serif;
    }
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease;
    }
    .card:hover {
        transform: scale(1.01);
    }
    .stButton button {
        background-color: #2563EB;
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 0.5rem;
        font-weight: 600;
        transition: background 0.2s ease;
    }
    .stButton button:hover {
        background-color: #1E40AF;
    }
    .status-badge {
        font-weight: bold;
        padding: 0.2rem 0.6rem;
        border-radius: 0.4rem;
        font-size: 0.9rem;
    }
    .status-hired {
        background: #D1FAE5;
        color: #065F46;
    }
    .status-not {
        background: #FECACA;
        color: #7F1D1D;
    }
    .status-pending {
        background: #E5E7EB;
        color: #374151;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- PDF processing --------------------
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            images = pdf2image.convert_from_bytes(
                uploaded_file.read(),
                poppler_path=r"D:\Release-25.07.0-0\poppler-25.07.0\Library\bin"
            )
            first_page = images[0]
            img_byte_arr = io.BytesIO()
            first_page.save(img_byte_arr, format='JPEG')
            return [{"mime_type": "image/jpeg", "data": base64.b64encode(img_byte_arr.getvalue()).decode()}]
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return None
    return None

# -------------------- Gemini AI response --------------------
def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

# -------------------- Main App --------------------
def main():
    # Session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'active_page' not in st.session_state:
        st.session_state.active_page = "Home"

    # ---------- Login/Register ----------
    if not st.session_state.authenticated:
        st.markdown("<h1 style='text-align:center;color:#1E3A8A;'>👥 RecruitAI - Smart Hiring</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔑 Login", "🆕 Register"])

        with tab1:
            st.subheader("Welcome Back!")
            username = st.text_input("👤 Username", key="login_username")
            password = st.text_input("🔒 Password", type="password", key="login_password")
            if st.button("Login"):
                user = authenticate_user(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user_role = user[3]
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")

        with tab2:
            st.subheader("Create an Account")
            new_username = st.text_input("👤 Choose Username", key="reg_username")
            new_password = st.text_input("🔒 Choose Password", type="password", key="reg_password")
            user_role = st.selectbox("🎭 I am a:", ["Candidate", "HR/Recruiter"], key="reg_role")
            if st.button("Create Account"):
                if register_user(new_username, new_password, user_role):
                    st.success("🎉 Account created successfully! Please login.")
                    st.rerun()
                else:
                    st.error("⚠️ Username already exists")
        return

    # ---------- Navbar ----------
    nav_items = []
    if st.session_state.user_role == "Candidate":
        nav_items = ["Home", "Jobs"]
    elif st.session_state.user_role == "HR/Recruiter":
        nav_items = ["Home", "Post Jobs", "Applications", "AI Screening"]

    # Navbar layout
    cols = st.columns([1, 5, 2])  # logo, links, user info

    with cols[0]:
        st.markdown("<h3 style='color:white;background:#1E3A8A;padding:0.4rem 0.8rem; font-size:18px;border-radius:0.5rem;'>RecruitAI</h3>", unsafe_allow_html=True)

    with cols[1]:
        nav_col = st.columns(len(nav_items))
        for i, page in enumerate(nav_items):
            button_style = "background-color:#1E3A8A;color:white;border-radius:0.5rem;padding:0.4rem 1rem;border:none;"
            if page == st.session_state.active_page:
                button_style = "background-color:white;color:#1E3A8A;font-weight:bold;border-radius:0.5rem;padding:0.4rem 1rem;border:2px solid #1E3A8A;"
            if nav_col[i].button(page, key=f"nav_{page}"):
                st.session_state.active_page = page
                st.rerun()

    with cols[2]:
        st.markdown(
            f"<div style='background:#1E3A8A;color:white;padding:0.5rem;border-radius:0.5rem;text-align:center;'>"
            f"{st.session_state.username} | {st.session_state.user_role}</div>",
            unsafe_allow_html=True
        )

    # Sidebar for logout
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.active_page = "Home"
        st.rerun()

    # ---------- Candidate Dashboard ----------
    if st.session_state.user_role == "Candidate":
        if st.session_state.active_page == "Home":
            st.title("👤 Candidate Dashboard")
            st.write("Welcome to RecruitAI! Use the navigation bar to explore jobs.")
        elif st.session_state.active_page == "Jobs":
            st.title("📌 Available Jobs")
            jobs = get_job_postings()

            # Initialize selected_job if not present
            if "selected_job" not in st.session_state:
                st.session_state.selected_job = None

            # Function to redirect to a job page
            def go_to_job(job_id):
                st.session_state.selected_job = job_id
                st.rerun()

            if not jobs:
                st.info("ℹ️ No job positions available yet.")
            else:
                # Show dashboard if no job selected yet
                if st.session_state.selected_job is None:
                    cols = st.columns(2)
                    for i, job in enumerate(jobs):
                        job_id = job[0]
                        company = job[1]
                        role = job[2]
                        department = job[3]
                        requirements = job[4]

                        with cols[i % 2]:
                            st.markdown(f"""
                            <div class="card" style="text-align:center;">
                                <img src="https://via.placeholder.com/100" width="80" style="margin-bottom:0.5rem;"/>
                                <h4>{company}</h4>
                                <p>{role}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            if st.button(f"View {role}", key=f"btn_{job_id}"):
                                go_to_job(job_id)
                else:
                    # Show selected job details and resume upload
                    job = next((j for j in jobs if j[0] == st.session_state.selected_job), None)
                    if job:
                        st.subheader(f"{job[2]} - {job[1]}")
                        st.markdown(f"**Department:** {job[3]}")
                        st.markdown(f"**Requirements:** {job[4]}")

                        uploaded_resume = st.file_uploader(f"📎 Upload Resume for {job[2]}", type=["pdf"], key=f"resume_{job[0]}")
                        if st.button(f"✅ Apply for {job[2]}"):
                            if uploaded_resume:
                                submit_application(st.session_state.user_id, job[0], uploaded_resume)
                                st.success(f"You have successfully applied for {job[2]} at {job[1]}")
                            else:
                                st.error("⚠️ Please upload your resume")
                        
                        if st.button("⬅️ Back to Dashboard"):
                            st.session_state.selected_job = None
                            st.rerun()
                    else:
                        st.warning("⚠️ Job not found. Returning to dashboard.")
                        st.session_state.selected_job = None
                        st.rerun()

    # ---------- HR Dashboard ----------
    elif st.session_state.user_role == "HR/Recruiter":
        if st.session_state.active_page == "Home":
            st.title("👥 HR Recruitment Portal")
            st.write("Welcome to RecruitAI HR Dashboard! Use the navigation bar above.")
        elif st.session_state.active_page == "Post Jobs":
            st.title("📝 Create Job Posting")
            with st.form("job_form"):
                job_title = st.text_input("Job Title")
                company = st.text_input("Company Name")
                department = st.text_input("Department")
                requirements = st.text_area("Job Requirements")
                description = st.text_area("Job Description")
                if st.form_submit_button("✅ Post Job"):
                    create_job_posting(job_title, company, department, requirements, description)
                    st.success("🎉 Job posted successfully!")
        elif st.session_state.active_page == "Applications":
            st.title("📂 Applications")
            applications = get_applications()
            if applications:
                for app in applications:
                    status = app[7] if len(app) > 7 else "Pending"
                    if status == "Hired":
                        badge = "<span class='status-badge status-hired'>Hired</span>"
                    elif status == "Not Hired":
                        badge = "<span class='status-badge status-not'>Not Hired</span>"
                    else:
                        badge = "<span class='status-badge status-pending'>Pending</span>"

                    with st.container():
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown(f"### {app[1]} - {app[2]} {badge}", unsafe_allow_html=True)
                        st.write(f"**Applied on:** {app[3]}")
                        if app[4]:
                            st.download_button("📥 Download Resume", app[4], f"resume_{app[0]}.pdf")
                        else:
                            st.warning("⚠️ No resume available")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Mark as Hired", key=f"hired_{app[0]}"):
                                update_application_status(app[0], "Hired")
                                st.rerun()
                        with col2:
                            if st.button("❌ Mark as Not Hired", key=f"not_hired_{app[0]}"):
                                update_application_status(app[0], "Not Hired")
                                st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("ℹ️ No applications received yet.")
        elif st.session_state.active_page == "AI Screening":
            st.title("🤖 AI-Powered Screening")
            applications = get_applications()
            if applications:
                selected_app = st.selectbox("Select Application", applications, format_func=lambda x: f"{x[1]} - {x[2]}")
                if selected_app and st.button("🚀 Run AI Screening"):
                    st.success("✅ AI Analysis complete! (Mocked output)")
                    st.markdown("""
                    <div class="card">
                        <h4>📊 Evaluation:</h4>
                        - Match Score: 85%  
                        - Strengths: Strong technical skills  
                        - Recommendation: Proceed to interview  
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("ℹ️ No applications to screen yet.")

if __name__ == "__main__":
    main()
