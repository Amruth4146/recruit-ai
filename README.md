# Recruit-AI

**Recruit-AI** is a web-based job portal application built with Python and Streamlit. It allows companies to post jobs and candidates to browse and apply for available positions. The platform stores data in SQLite, making it lightweight and easy to deploy.

---

## 🚀 Features

- **Candidate Dashboard**: View all available jobs in a card-style layout.  
- **Job Details Page**: See job requirements, department, and upload resumes to apply.  
- **Company Dashboard**: Post new job openings and manage existing postings.  
- **Secure Authentication**: Register and log in as a candidate or company.  
- **Persistent Storage**: Job postings, candidate data, and resumes stored in SQLite.  

---

## 💻 Tech Stack

- **Frontend & Backend**: Python, Streamlit  
- **Database**: SQLite  
- **Other Libraries**: `pdf2image`, `dotenv`, `google.generativeai`  

---

## 📂 Project Structure

Recruit-AI/
├── app.py
├── auth.py
├── database.py
├── recruitment.db
├── requirements.txt
├── .env
└── pycache/



---
yaml
## ⚡ Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/Amruth4146/recruit-ai.git
cd recruit-ai


to install dependencies 
pip install -r requirements.txt

 return to app 
streamlit run app.py
