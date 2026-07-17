# 🎓 EduAI — AI-Powered Personalized Learning Assistant

EduAI is a production-grade, database-driven learning assistant built to align with **United Nations Sustainable Development Goal 4 (SDG 4 - Quality Education)**. By utilizing Retrieval-Augmented Generation (RAG) and local student answer grading telemetry, it closes the educational loop. Unlike basic AI chatbots, EduAI tracks user response histories, analyzes conceptual blindspots, builds dynamic daily schedules, and provides grounded academic assistance.

---

## 🎯 Core Objectives & SDG 4 Impact
*   **Equal Access (SDG Target 4.3):** Democratizes premium private tutoring, making grounded summaries, custom tests, and detailed critiques free.
*   **Skill Enrichment (SDG Target 4.4):** Helps learners master computational, scientific, and quantitative topics through adaptive quizzing and ELI10 (Explain Like I'm 10) analogies.
*   **Teacher Co-Pilot (SDG Target 4.c):** Functions as a student tracking diagnostic, allowing educators to review metrics, conceptual weak points, and auto-generated schedules.

---

## 🛠️ Architecture & Technology Stack
*   **Core Architecture:** Python 3.10+
*   **Web Framework:** Streamlit (Custom Dark SaaS UI Theme)
*   **AI & LLM Orchestrator:** Google Gemini API (`gemini-pro` for summaries, quizzes, and RAG tutoring).
*   **Local Database:** SQLite3 (Persists quizzes, topic progress, settings, study plans).
*   **Vector Search & Embeddings:** Google Generative AI Embeddings (`models/embedding-001`) with NumPy cosine similarity indexing.
*   **Report & Analytics Generators:** `python-pptx` (Slide generation) & `reportlab` (PDF generation).
*   **Analytics Engine:** Pandas & Plotly (for interactive performance and error distribution graphs).
*   **Asset Generator:** `python-pptx` (PowerPoint deck compilers) and `reportlab` (PDF document generator).

---

## 📂 Project Structure & Page Matrix

```
StudyAI/
│
├── app.py                      # Main entrypoint, welcome hub & academic progress dashboard
├── requirements.txt            # System dependencies list
├── README.md                   # Project documentation
│
├── pages/                      # Streamlit Multipage layout
│   ├── 1_Study_Material.py     # File uploader, parser & vector indexing (RAG)
│   ├── 2_AI_Summarizer.py      # Bullet points, key glossary, ELI10, formulae & export options
│   ├── 3_Quiz_Generator.py     # Custom MCQ, Short Answer, TF questions generator
│   ├── 4_AI_Evaluation.py      # Grading window, detailed critiques, and concept flagging
│   ├── 5_Weak_Topics.py        # SQLite-driven conceptual gaps tracker and revision priority
│   ├── 6_Study_Plan.py         # Dynamic daily revision calendar builder based on weak spots
│   ├── 7_AI_Tutor.py           # Grounded tutor chat with selectable personas (Age 10, Simple Words)
│   ├── 8_Progress_Dashboard.py # Analytical score history, topic mastery & mistake distributions
│   ├── 9_SDG_Impact.py         # SDG target descriptions & educational bottleneck analyses
│   ├── 10_Settings.py          # API auth key configs, slide/PDF generator, DB reset controls
│   └── 11_Exhibition_QA.py     # Cheat-sheet prep reference guide for evaluators
│
├── utils/                      # Helper script modules
│   ├── gemini_client.py        # Gemini LLM API calls and structured JSON sanitizers
│   ├── text_extractor.py       # PyPDF & pdfplumber fallback text parsers
│   ├── vector_store.py         # Local NumPy similarity indexing logic
│   ├── slide_generator.py      # pptx exhibition slideshow generator
│   └── report_generator.py     # reportlab academic report generator
│
├── database/                   # DB administration layer
│   ├── db_manager.py           # SQLite tables schema definitions and CRUD functions
│   └── eduai.db                # Active SQL relational database file
│
└── report/                     # Pre-compiled academic deliverables
    ├── presentation.pptx       # Slide deck compiled on-demand
    └── report.pdf              # Academic paper compiled on-demand
```

---

## 🗄️ Relational Database Schema
The system database `database/eduai.db` tracks learning histories across the following tables:
*   `quizzes`: Metadata of generated tests (file source, topic, difficulty, question count).
*   `quiz_questions`: Question details, formats (MCQ, Short Answer, TF), options, and expected responses.
*   `student_answers`: Evaluator grades (0.0 to 5.0), submitted text, conceptual error flags, and feedback logs.
*   `weak_topics`: Aggregate counters of correct/incorrect response tags to identify focus priority.
*   `study_plans`: Active daily and weekly schedules compiled using generative planners.
*   `settings`: Key-value configuration pairs (theme state, saved API key).

---

## 🚀 Installation & Local Setup

### 1. Prerequisites
Ensure you have Python 3.9+ installed.

### 2. Clone the Repository
```bash
git clone https://github.com/Rohit-Saindane/edunet-capstone-project.git
cd edunet-capstone-project
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a file named `.env` in the root directory:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 5. Launch the Web Application
```bash
streamlit run app.py
```

---

## ⚙️ Core Application Workflow

1.  **Authorization:** Input your Gemini API key inside the **Settings** panel (or let it pull automatically from your `.env` configuration).
2.  **Ingestion:** Go to **Study Material** and upload a textbook PDF or notes TXT. Click **Process Document** to extract text, divide it into 800-character overlapping chunks, and build the local vector database.
3.  **Study & Summarize:** Read synthesized notes, formulas, ELI10 analogies, and definitions in the **AI Summarizer**.
4.  **Test:** Generate a custom quiz (MCQ/Short Answer/TF) in the **Quiz Generator** based on your uploaded material.
5.  **Evaluate:** Grade your responses using the **AI Evaluation** engine, which logs errors directly to the SQLite databases.
6.  **Schedule:** Open the **Study Plan** scheduler to translate your diagnostic weak areas into a structured weekly timeline.
7.  **Chat:** Talk to the context-grounded **AI Tutor** to resolve remaining conceptual challenges.
8.  **Export:** Go to **Settings** and click the generator buttons to build your final exhibition presentation slides (`presentation.pptx`) and PDF report (`report.pdf`).
