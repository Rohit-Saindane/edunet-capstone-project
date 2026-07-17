import sqlite3
import os
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "eduai.db")

def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT NOT NULL,
        topic TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        question_count INTEGER NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        question_type TEXT NOT NULL,
        options TEXT,
        correct_answer TEXT NOT NULL,
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        student_response TEXT NOT NULL,
        is_correct INTEGER NOT NULL,
        marks_obtained REAL NOT NULL,
        total_marks REAL NOT NULL,
        explanation TEXT,
        suggestions TEXT,
        evaluated_at TEXT NOT NULL,
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES quiz_questions(id) ON DELETE CASCADE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weak_topics (
        topic_name TEXT PRIMARY KEY,
        incorrect_count INTEGER DEFAULT 0,
        total_tested INTEGER DEFAULT 0,
        concept_notes TEXT,
        last_updated TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        daily_schedule TEXT NOT NULL,
        weekly_goals TEXT NOT NULL,
        recommended_revision TEXT NOT NULL,
        est_completion_hours REAL NOT NULL,
        is_active INTEGER DEFAULT 1
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def save_quiz(file_name: str, topic: str, difficulty: str, questions: List[Dict[str, Any]]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO quizzes (file_name, topic, difficulty, question_count, created_at) VALUES (?, ?, ?, ?, ?)",
        (file_name, topic, difficulty, len(questions), created_at)
    )
    quiz_id = cursor.lastrowid
    for q in questions:
        options_str = None
        if "options" in q and q["options"]:
            if isinstance(q["options"], list):
                options_str = "||".join(str(o) for o in q["options"])
            else:
                options_str = str(q["options"])
        cursor.execute(
            "INSERT INTO quiz_questions (quiz_id, question_text, question_type, options, correct_answer) VALUES (?, ?, ?, ?, ?)",
            (quiz_id, q["question_text"], q["question_type"], options_str, q["correct_answer"])
        )
    conn.commit()
    conn.close()
    return quiz_id

def get_quizzes() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quizzes ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_quiz_details(quiz_id: int) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
    quiz_row = cursor.fetchone()
    if not quiz_row:
        conn.close()
        return None, []
    cursor.execute("SELECT * FROM quiz_questions WHERE quiz_id = ?", (quiz_id,))
    question_rows = cursor.fetchall()
    conn.close()
    questions = []
    for r in question_rows:
        q_dict = dict(r)
        if q_dict["options"]:
            q_dict["options"] = q_dict["options"].split("||")
        else:
            q_dict["options"] = []
        questions.append(q_dict)
    return dict(quiz_row), questions

def save_student_answers(quiz_id: int, evaluations: List[Dict[str, Any]]) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    evaluated_at = datetime.now().isoformat()
    cursor.execute("SELECT topic FROM quizzes WHERE id = ?", (quiz_id,))
    row = cursor.fetchone()
    topic = row["topic"] if row else "General"
    for eval_item in evaluations:
        cursor.execute(
            """INSERT INTO student_answers 
               (quiz_id, question_id, student_response, is_correct, marks_obtained, total_marks, explanation, suggestions, evaluated_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                quiz_id,
                eval_item["question_id"],
                eval_item["student_response"],
                1 if eval_item["is_correct"] else 0,
                eval_item["marks_obtained"],
                eval_item["total_marks"],
                eval_item["explanation"],
                eval_item.get("suggestions", ""),
                evaluated_at
            )
        )
        is_correct = 1 if eval_item["is_correct"] else 0
        update_weak_topic(cursor, topic, is_correct, eval_item.get("weak_concept_flag", ""))
    conn.commit()
    conn.close()

def update_weak_topic(cursor, topic: str, is_correct: int, concept_notes: str):
    now_str = datetime.now().isoformat()
    cursor.execute("SELECT incorrect_count, total_tested FROM weak_topics WHERE topic_name = ?", (topic,))
    row = cursor.fetchone()
    if row:
        inc_count = row["incorrect_count"] + (1 if is_correct == 0 else 0)
        tot_tested = row["total_tested"] + 1
        cursor.execute(
            "UPDATE weak_topics SET incorrect_count = ?, total_tested = ?, concept_notes = ?, last_updated = ? WHERE topic_name = ?",
            (inc_count, tot_tested, concept_notes if concept_notes else row["concept_notes"], now_str, topic)
        )
    else:
        inc_count = 1 if is_correct == 0 else 0
        cursor.execute(
            "INSERT INTO weak_topics (topic_name, incorrect_count, total_tested, concept_notes, last_updated) VALUES (?, ?, ?, ?, ?)",
            (topic, inc_count, 1, concept_notes, now_str)
        )

def get_weak_topics() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weak_topics WHERE incorrect_count > 0 ORDER BY incorrect_count DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_topics_performance() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weak_topics")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_study_plan(daily_schedule: str, weekly_goals: str, recommended_revision: str, est_completion_hours: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE study_plans SET is_active = 0")
    created_at = datetime.now().isoformat()
    cursor.execute(
        """INSERT INTO study_plans (created_at, daily_schedule, weekly_goals, recommended_revision, est_completion_hours, is_active)
           VALUES (?, ?, ?, ?, ?, 1)""",
        (created_at, daily_schedule, weekly_goals, recommended_revision, est_completion_hours)
    )
    conn.commit()
    conn.close()

def get_active_study_plan() -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM study_plans WHERE is_active = 1 ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_student_evaluation_history() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sa.*, q.topic, q.difficulty, q.file_name, qq.question_text
        FROM student_answers sa
        JOIN quizzes q ON sa.quiz_id = q.id
        JOIN quiz_questions qq ON sa.question_id = qq.id
        ORDER BY sa.evaluated_at ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_setting(key: str, value: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default

def reset_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS quizzes")
    cursor.execute("DROP TABLE IF EXISTS quiz_questions")
    cursor.execute("DROP TABLE IF EXISTS student_answers")
    cursor.execute("DROP TABLE IF EXISTS weak_topics")
    cursor.execute("DROP TABLE IF EXISTS study_plans")
    cursor.execute("DROP TABLE IF EXISTS settings")
    conn.commit()
    conn.close()
    init_db()

init_db()
