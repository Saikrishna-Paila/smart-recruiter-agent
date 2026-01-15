<p align="center">
  <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Briefcase.png" alt="Smart Recruiter Logo" width="120"/>
</p>

<h1 align="center">Smart Recruiter Agent</h1>

<p align="center">
  <strong>AI-Powered Multi-Agent Recruitment Platform</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#demo">Demo</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#tech-stack">Tech Stack</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React"/>
  <img src="https://img.shields.io/badge/CrewAI-FF6B6B?style=for-the-badge" alt="CrewAI"/>
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white" alt="Groq"/>
  <img src="https://img.shields.io/badge/TailwindCSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind"/>
  <img src="https://img.shields.io/badge/Resend-000000?style=for-the-badge&logo=resend&logoColor=white" alt="Resend"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License"/>
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome"/>
  <img src="https://img.shields.io/badge/Project-4%20of%2012-blue.svg?style=flat-square" alt="Project 4"/>
</p>

---

## Overview

**Smart Recruiter** is a production-grade, full-stack recruitment platform powered by **CrewAI multi-agent orchestration**. It automates the entire hiring pipeline - from job description optimization to candidate screening, skills matching, and interview question generation.

### Why This Project?

| Traditional Hiring | Smart Recruiter |
|-------------------|-----------------|
| Manual resume screening | AI-powered skill matching |
| Hours per candidate | Seconds per candidate |
| Subjective assessments | Objective scoring (0-100) |
| Generic interview questions | Personalized questions per candidate |
| Manual email follow-ups | Automated candidate notifications |
| Spreadsheet tracking | Real-time dashboard analytics |

---

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Agent AI** | 5 specialized AI agents working together via CrewAI |
| **Resume Parsing** | Extract skills, experience, education from PDF/DOCX |
| **Smart Screening** | AI matches candidates against job requirements |
| **JD Optimizer** | AI enhances job descriptions for better reach |
| **Interview Generator** | Custom technical & behavioral questions |
| **Email Notifications** | Automated assessment emails via Resend |
| **Real-time Dashboard** | Track applicants, scores, and hiring pipeline |
| **Public Apply Portal** | Candidates apply via unique job links |

---

## Demo

<p align="center">
  <img src="assets/dashboard.png" alt="Smart Recruiter Dashboard" width="100%"/>
</p>

<p align="center"><em>Dashboard showing candidate pipeline with AI match scores</em></p>

### AI Screening in Action

```
📄 Resume Uploaded: john_doe_resume.pdf

🤖 Agent 1 - Resume Parser:
   ✓ Extracted: Python, React, AWS, Docker
   ✓ Experience: 5 years at TechCorp
   ✓ Education: MS Computer Science

🤖 Agent 2 - Skill Matcher:
   ✓ Required Skills Match: 8/10
   ✓ Partial Matches: 2 (related experience)
   ✓ Missing: GraphQL

🤖 Agent 3 - Candidate Assessor:
   ✓ Match Score: 78%
   ✓ Recommendation: HIRE
   ✓ Status: Shortlisted

📧 Email sent to candidate with assessment results
```

---

## Architecture

### Multi-Agent System

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           SMART RECRUITER PLATFORM                          │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         REACT FRONTEND                               │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────────┐  │   │
│  │  │ Dashboard│  │ Job Mgmt │  │Candidates│  │   Apply Portal     │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         FASTAPI BACKEND                              │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────────┐  │   │
│  │  │ Jobs API │  │Candidates│  │ Screening│  │   Email Service    │  │   │
│  │  │          │  │   API    │  │    API   │  │     (Resend)       │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      CREWAI AGENT ORCHESTRATION                      │   │
│  │                                                                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │   │
│  │  │ JD Optimizer│  │Resume Parser│  │Skill Matcher│                  │   │
│  │  │   Agent     │  │   Agent     │  │   Agent     │                  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                  │   │
│  │         │                │                │                          │   │
│  │         ▼                ▼                ▼                          │   │
│  │  ┌─────────────┐  ┌─────────────┐                                   │   │
│  │  │  Candidate  │  │  Interview  │                                   │   │
│  │  │  Assessor   │  │  Generator  │                                   │   │
│  │  └─────────────┘  └─────────────┘                                   │   │
│  │                                                                       │   │
│  │         Powered by Groq (Llama 3.3 70B) - Ultra Fast LLM            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         POSTGRESQL DATABASE                          │   │
│  │              Jobs • Candidates • Scores • Assessments                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└────────────────────────────────────────────────────────────────────────────┘
```

### AI Agent Workflow

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         SCREENING CREW WORKFLOW                             │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   CANDIDATE APPLIES                                                          │
│         │                                                                    │
│         ▼                                                                    │
│   ┌─────────────────┐                                                       │
│   │  Resume Parser  │ ──► Extract text, skills, experience, education      │
│   │     Agent       │                                                       │
│   └────────┬────────┘                                                       │
│            │                                                                 │
│            ▼                                                                 │
│   ┌─────────────────┐                                                       │
│   │  Skill Matcher  │ ──► Compare skills vs job requirements               │
│   │     Agent       │     Mark: MATCH | PARTIAL | MISSING                   │
│   └────────┬────────┘                                                       │
│            │                                                                 │
│            ▼                                                                 │
│   ┌─────────────────┐                                                       │
│   │    Candidate    │ ──► Generate match score (0-100)                     │
│   │    Assessor     │     Recommendation: Strong Hire | Hire | Maybe | No  │
│   └────────┬────────┘                                                       │
│            │                                                                 │
│            ▼                                                                 │
│   ┌─────────────────────────────────────────────────────────────┐          │
│   │                     DECISION ENGINE                          │          │
│   │  Score >= 70% ──► SHORTLISTED ──► Email: "Congratulations!" │          │
│   │  Score < 70%  ──► REJECTED    ──► Email: "Thank you..."     │          │
│   └─────────────────────────────────────────────────────────────┘          │
│                                                                              │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

<table>
<tr>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="48" height="48" alt="Python" />
<br><strong>Python</strong>
<br><sub>3.10+</sub>
</td>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" width="48" height="48" alt="FastAPI" />
<br><strong>FastAPI</strong>
<br><sub>Backend API</sub>
</td>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg" width="48" height="48" alt="React" />
<br><strong>React</strong>
<br><sub>Frontend</sub>
</td>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg" width="48" height="48" alt="PostgreSQL" />
<br><strong>PostgreSQL</strong>
<br><sub>Database</sub>
</td>
<td align="center" width="120">
<img src="https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0wIDE4Yy00LjQxIDAtOC0zLjU5LTgtOHMzLjU5LTggOC04IDggMy41OSA4IDgtMy41OSA4LTggOHoiLz48L3N2Zz4=&logoColor=white" width="80" alt="Groq" />
<br><strong>Groq</strong>
<br><sub>LLM Engine</sub>
</td>
</tr>
<tr>
<td align="center" width="120">
<img src="https://img.shields.io/badge/CrewAI-FF6B6B?style=for-the-badge" width="80" alt="CrewAI" />
<br><strong>CrewAI</strong>
<br><sub>Multi-Agent</sub>
</td>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/tailwindcss/tailwindcss-original.svg" width="48" height="48" alt="Tailwind" />
<br><strong>Tailwind</strong>
<br><sub>Styling</sub>
</td>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg" width="48" height="48" alt="TypeScript" />
<br><strong>TypeScript</strong>
<br><sub>Type Safety</sub>
</td>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vite/vite-original.svg" width="48" height="48" alt="Vite" />
<br><strong>Vite</strong>
<br><sub>Build Tool</sub>
</td>
<td align="center" width="120">
<img src="https://img.shields.io/badge/Resend-000000?style=for-the-badge" width="80" alt="Resend" />
<br><strong>Resend</strong>
<br><sub>Email API</sub>
</td>
</tr>
</table>

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI + SQLAlchemy | REST API with async support |
| **Frontend** | React + Vite + TailwindCSS | Modern responsive UI |
| **Database** | PostgreSQL + asyncpg | Async database operations |
| **AI Engine** | CrewAI + Groq (Llama 3.3) | Multi-agent orchestration |
| **Resume Parsing** | PyMuPDF + python-docx | Extract text from PDF/DOCX |
| **Email Service** | Resend API | Automated notifications |
| **State Management** | TanStack Query | Server state caching |

---

## Project Structure

```
04-smart-recruiter-agent/
├── 📁 smart_recruiter/           # Python backend
│   ├── 📁 agents/                # CrewAI agent definitions
│   │   ├── jd_optimizer.py       # Job description optimizer
│   │   ├── resume_parser.py      # Resume parsing agent
│   │   ├── skill_matcher.py      # Skills matching agent
│   │   ├── candidate_assessor.py # Assessment agent
│   │   └── interview_scheduler.py# Interview Q&A agent
│   │
│   ├── 📁 crews/                 # CrewAI crew orchestration
│   │   ├── jd_crew.py            # JD optimization workflow
│   │   ├── screening_crew.py     # Candidate screening workflow
│   │   └── interview_crew.py     # Interview prep workflow
│   │
│   ├── 📁 tools/                 # Agent tools
│   │   ├── resume_parser.py      # PDF/DOCX text extraction
│   │   ├── skill_matcher.py      # Skills comparison tool
│   │   └── interview_tools.py    # Question generation
│   │
│   ├── 📁 api/                   # FastAPI routes
│   │   ├── main.py               # App entry point
│   │   └── routes/
│   │       ├── jobs.py           # Job CRUD endpoints
│   │       ├── candidates.py     # Candidate endpoints
│   │       ├── screening.py      # AI screening endpoints
│   │       └── apply.py          # Public apply endpoint
│   │
│   ├── 📁 database/              # Database layer
│   │   ├── connection.py         # Async PostgreSQL setup
│   │   └── models.py             # SQLAlchemy models
│   │
│   ├── 📁 services/              # External services
│   │   └── email_service.py      # Resend email integration
│   │
│   └── 📁 config/                # Configuration
│       └── settings.py           # Environment settings
│
├── 📁 frontend/                  # React frontend
│   ├── 📁 src/
│   │   ├── 📁 pages/
│   │   │   ├── Dashboard.tsx     # Main dashboard
│   │   │   ├── Jobs.tsx          # Jobs list
│   │   │   ├── JobDetail.tsx     # Job detail + JD optimizer
│   │   │   ├── CandidateDetail.tsx # Candidate profile
│   │   │   └── ApplyForm.tsx     # Public apply page
│   │   │
│   │   ├── 📁 api/
│   │   │   └── client.ts         # API client with axios
│   │   │
│   │   └── App.tsx               # Main app with routing
│   │
│   ├── package.json
│   └── tailwind.config.js
│
├── 📁 data/                      # Uploaded resumes storage
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
├── run.py                        # Development runner
└── README.md                     # This file
```

---

## Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- [Groq API Key](https://console.groq.com/keys) (Free)
- [Resend API Key](https://resend.com/) (Optional, for emails)

### Step 1: Clone Repository

```bash
git clone https://github.com/saikrishnapaila/smart-recruiter-agent.git
cd smart-recruiter-agent
```

### Step 2: Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Database Setup

```bash
# Create PostgreSQL database
createdb smart_recruiter

# Or via psql
psql -U postgres -c "CREATE DATABASE smart_recruiter;"
```

### Step 4: Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/smart_recruiter

# Groq LLM (Required)
GROQ_API_KEY=gsk_your_api_key_here

# Resend Email (Optional)
RESEND_API_KEY=re_your_api_key_here
EMAIL_FROM=Smart Recruiter <onboarding@resend.dev>

# Settings
MIN_MATCH_SCORE=70
```

### Step 5: Frontend Setup

```bash
cd frontend
npm install
```

### Step 6: Run Application

```bash
# Terminal 1 - Backend
python run.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

---

## Usage

### 1. Create a Job Posting

1. Navigate to **Jobs** page
2. Click **"Create New Job"**
3. Fill in job details and requirements
4. Click **"Optimize with AI"** to enhance the description
5. Save the job posting

### 2. Share Apply Link

Each job gets a unique public apply link:
```
http://localhost:5173/apply/{job_id}
```

Share this link with candidates to collect applications.

### 3. AI Screening

1. Go to the job's **Candidates** tab
2. Click **"Run AI Screening"**
3. Watch the multi-agent system analyze each resume
4. View match scores and recommendations

### 4. Review Candidates

| Score | Status | Action |
|-------|--------|--------|
| 80-100% | Strong Match | Auto-shortlisted |
| 70-79% | Good Match | Review for shortlist |
| 50-69% | Partial Match | Consider with reservations |
| 0-49% | Poor Match | Auto-rejected |

### 5. Send Notifications

- Click **"Send Assessment Email"** to notify candidates
- Shortlisted candidates receive interview invites
- All candidates get professional, personalized emails

---

## API Endpoints

### Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs` | List all jobs |
| POST | `/api/jobs` | Create new job |
| GET | `/api/jobs/{id}` | Get job details |
| PUT | `/api/jobs/{id}` | Update job |
| DELETE | `/api/jobs/{id}` | Delete job |

### Candidates

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/candidates/job/{job_id}` | List candidates for job |
| GET | `/api/candidates/{id}` | Get candidate details |
| POST | `/api/candidates/{id}/shortlist` | Shortlist candidate |
| POST | `/api/candidates/{id}/reject` | Reject candidate |
| POST | `/api/candidates/{id}/send-assessment` | Send email |

### AI Screening

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/screening/job/{id}/screen` | Run AI screening |
| POST | `/api/screening/job/{id}/optimize-jd` | Optimize job description |
| POST | `/api/screening/candidate/{id}/rescreen` | Re-screen single candidate |
| POST | `/api/screening/candidate/{id}/generate-questions` | Generate interview Qs |

### Public

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/apply/{job_id}` | Get job details (public) |
| POST | `/api/apply/{job_id}` | Submit application |

---

## AI Agents

### 1. JD Optimizer Agent

Improves job descriptions for clarity and inclusivity.

**Input:** Raw job description
**Output:** Enhanced description with clear requirements

### 2. Resume Parser Agent

Extracts structured data from resumes.

**Detects:** 70+ technical skills including:
- Languages: Python, JavaScript, Java, Go, Rust
- AI/ML: PyTorch, TensorFlow, LangChain, RAG, LLM
- Cloud: AWS, GCP, Azure, Docker, Kubernetes
- Data: SQL, PostgreSQL, MongoDB, Spark

### 3. Skill Matcher Agent

Compares candidate skills against requirements.

**Output:**
- MATCH: Exact skill found
- PARTIAL: Related skill found
- MISSING: Skill not detected

### 4. Candidate Assessor Agent

Generates overall assessment with scoring.

**Scoring Criteria:**
- 90-100: Perfect match, exceeds requirements
- 75-89: Strong match, meets most requirements
- 60-74: Moderate match, some gaps
- 40-59: Weak match, significant gaps
- 0-39: Poor match, doesn't meet key requirements

### 5. Interview Generator Agent

Creates personalized interview questions.

**Question Types:**
- Technical: Based on required skills
- Behavioral: Based on role level
- Experience: Based on their background

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `GROQ_API_KEY` | Groq API key for LLM | Yes |
| `RESEND_API_KEY` | Resend API key for emails | No |
| `EMAIL_FROM` | Sender email address | No |
| `MIN_MATCH_SCORE` | Minimum score for shortlist (default: 70) | No |
| `UPLOAD_DIR` | Resume upload directory | No |

---

## Roadmap

- [x] Multi-agent screening system
- [x] JD optimization
- [x] Email notifications
- [x] Public apply portal
- [ ] Calendar integration for interviews
- [ ] Video interview scheduling
- [ ] Bulk import candidates (CSV)
- [ ] Analytics dashboard
- [ ] Slack/Teams notifications
- [ ] Custom scoring weights
- [ ] Multi-language support

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [CrewAI](https://crewai.com/) - Multi-agent orchestration framework
- [Groq](https://groq.com/) - Ultra-fast LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Resend](https://resend.com/) - Email API for developers
- [TailwindCSS](https://tailwindcss.com/) - Utility-first CSS framework

---

<p align="center">
  <strong>Built with ❤️ by Saikrishna Paila</strong>
</p>

<p align="center">
  <a href="https://github.com/saikrishnapaila">
    <img src="https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github" alt="GitHub"/>
  </a>
  <a href="https://linkedin.com/in/saikrishnapaila">
    <img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin" alt="LinkedIn"/>
  </a>
</p>

---

<p align="center">
  <sub>Part of the <strong>12 AI Projects for 2025</strong> series</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Project_4_of_12-12_AI_Projects_2025-blueviolet?style=flat-square" alt="Project 4 of 12"/>
</p>
