import streamlit as st
import os
from utils.theme_manager import inject_theme, load_branding

st.set_page_config(page_title="Exhibition Prep Q&A - EduAI", page_icon="🎓", layout="wide")

inject_theme()
load_branding()

st.markdown("""
<div style='margin-bottom: 20px;'>
    <p style="font-size:18px;font-weight:600;margin:0 0 4px">🎓 Exhibition Prep Q&A Sheet</p>
    <p style="font-size:13px;color:var(--text-secondary);margin:0">A quick reference sheet of technical questions and model answers for internship evaluators.</p>
</div>
""", unsafe_allow_html=True)

qa_pairs = [
    {
        "q": "1. What is the core problem that EduAI addresses, and how does it support UN SDG 4?",
        "a": "Traditional education is often rigid and 'one-size-fits-all'. Private 1-to-1 tutoring is highly effective but financially inaccessible for lower-income students, breaching equitable education values. EduAI democratizes quality tutoring (SDG Target 4.3 & 4.c) by serving as a 24/7 personalized learning assistant. Unlike standard chatbots, it diagnoses conceptual weaknesses using quiz answers, builds dynamic study schedules, and retrieves specific context from uploaded textbooks (RAG) to ensure structured, grounded support."
    },
    {
        "q": "2. Why is a Retrieval-Augmented Generation (RAG) architecture necessary here? Why not just use a standard LLM chatbot?",
        "a": "Generic LLMs are context-blind. They do not know what is inside a student's specific textbook chapter, syllabus, or lecture slides. If a student asks a generic model about a specific course topic, it might hallucinate or reference unrelated online resources. A RAG architecture chunks the student's uploaded textbook, creates vector embeddings, and performs a similarity lookup to feed the exact textbook paragraphs into the LLM context. This guarantees that the tutor's answers are fully grounded in the course material."
    },
    {
        "q": "3. Explain the vector indexing and retrieval flow. What model is used for embeddings?",
        "a": "First, we split the extracted document text into 800-character chunks with a 150-character overlap to retain logical context boundaries. Next, we use Gemini's text embedding model to generate embedding vectors for each chunk. We save this index locally in a JSON file (`uploads/{file}_index.json`). When the user searches or asks the tutor a question, we embed the query and calculate cosine similarity between the query embedding and the chunk embeddings. The top 3 chunks are selected and injected as context."
    },
    {
        "q": "4. What database technology did you use, and what is its schema layout?",
        "a": "We use SQLite, a lightweight SQL database that requires no server setups. The database `database/eduai.db` contains 6 tables:\n- `quizzes`: Stores topic metadata, file origin, and difficulty.\n- `quiz_questions`: Stores questions, types (MCQ, Short Answer, True/False), options, and expected answers.\n- `student_answers`: Stores student responses, LLM grading results, scores (out of 5.0), and suggestions.\n- `weak_topics`: Logs mistakes count and conceptual recommendations per subject.\n- `study_plans`: Holds the generated active daily and weekly study planners.\n- `settings`: Persists configuration settings (like saved API keys)."
    },
    {
        "q": "5. How does the 'Weak Topic Detection' mechanism work under the hood?",
        "a": "When a student submits answers to a quiz, the answers are graded and checked for errors: if the response is incorrect, the AI model is prompted to identify the specific underlying conceptual gap (e.g., 'Recursion Base Case', 'Array Indexing') and return it in a JSON block under `weak_concept_flag`. This flag is captured and saved directly in SQLite. A frequency counter tracks which concepts are failed repeatedly, which then feeds the Study Plan Generator."
    },
    {
        "q": "6. How is the 'Personalized Study Plan' generated from the student's diagnostics?",
        "a": "The planner fetches the flagged records from the `weak_topics` database. We compile a summary list of the topics and their error counts and send them to the Gemini API with a structured prompt. The model processes the concepts and compiles a custom response containing a weekly checklist, an hourly study estimate, and a daily revision calendar. This data is returned as JSON and rendered into Streamlit tables and card elements."
    },
    {
        "q": "7. What fallbacks did you implement to handle environment failures on Windows?",
        "a": "To ensure maximum reliability during the exhibition:\n1. **Vector Store Fallback**: Installing native FAISS or ChromaDB on Windows often fails if C++ compiler dependencies are missing. If the `faiss` library fails to load, the system automatically falls back to a custom, pure-Python/NumPy cosine similarity calculation which works on any environment.\n2. **PDF Parser Fallback**: We implemented extraction fallback; if `pypdf` fails to extract text, the utility automatically tries `pdfplumber` to process the file."
    },
    {
        "q": "8. How did you generate the slideshow and PDF report deliverables programmatically?",
        "a": "We created Python scripts using two popular libraries:\n- `python-pptx` to build `report/presentation.pptx` slide by slide, applying dark slate layouts, custom text positioning, and color schemes.\n- `reportlab` to compile `report/report.pdf` by placing document titles, horizontal dividers, and paragraphs in a single flow, outputting a formal academic layout. Both scripts are linked to buttons in the Settings panel for on-demand creation."
    }
]

for idx, item in enumerate(qa_pairs):
    with st.container(border=True):
        st.markdown(f"#### ❓ {item['q']}")
        st.write("")
        st.markdown(f"💡 **Exhibition Response:**\n\n{item['a']}")
    st.write("")
