import google.generativeai as genai
import json
import re
from typing import List, Dict, Any, Optional

def clean_json_string(text: str) -> str:
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def generate_summary(text: str, api_key: str) -> Dict[str, Any]:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"""
        You are an expert educator under SDG 4 (Quality Education). 
        Analyze the following text and generate structured notes. 
        Your response must be a JSON object with the following keys:
        - "concise_summary": A brief paragraph summarizing the core theme.
        - "bullet_points": A list of 4-6 key takeaways.
        - "key_concepts": A list of dictionaries, where each has "concept" and "definition".
        - "simple_analogy": A simple, creative analogy explaining the core concept so anyone can understand.
        - "important_formulae": A list of mathematical, algorithmic, logical formulas, code definitions, or key rules. If none are present, list general key rules/conclusions.
        - "real_life_example": A concrete, practical real-world application or example of the concepts in action.

        Source Text:
        {text[:8000]}
        
        Format your response EXACTLY as a JSON object. Ensure the output is valid JSON.
        """
        response = model.generate_content(prompt)
        cleaned_response = clean_json_string(response.text)
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Summary generation error: {e}")
        return {
            "concise_summary": "Error generating summary. Please check your API key and try again.",
            "bullet_points": ["Could not load notes due to an API error.", "Verify network connection and API key configuration."],
            "key_concepts": [{"concept": "Error", "definition": str(e)}],
            "simple_analogy": "Error connection failed.",
            "important_formulae": ["Error loading formulas."],
            "real_life_example": "Error loading examples."
        }

def generate_quiz(text: str, topic: str, difficulty: str, mcq_count: int, sa_count: int, tf_count: int, api_key: str) -> List[Dict[str, Any]]:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"""
        You are an expert educational content developer.
        Based on the provided text on the topic "{topic}", generate a quiz.
        
        Difficulty level: {difficulty}
        Number of Multiple Choice (MCQ) questions: {mcq_count}
        Number of Short Answer (SHORT) questions: {sa_count}
        Number of True/False (TF) questions: {tf_count}
        
        Format the output EXACTLY as a JSON list of dictionaries. Do not include any extra introductory text.
        Each question dictionary in the list must have:
        - "question_text": The question string.
        - "question_type": Must be exactly 'MCQ', 'SHORT', or 'TF'.
        - "options": A list of strings (for MCQ only, e.g., ["option A", "option B", "option C", "option D"]). For 'SHORT' or 'TF', set to [].
        - "correct_answer": A string. For MCQ, write the exact matching text of the correct option. For TF, write 'True' or 'False'. For SHORT, write a concise 1-sentence answer containing key terms.

        Source text for the quiz:
        {text[:8000]}
        
        Respond with ONLY the JSON array.
        """
        response = model.generate_content(prompt)
        cleaned_response = clean_json_string(response.text)
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Quiz generation error: {e}")
        return [{
            "question_text": f"Error generating quiz questions: {str(e)}",
            "question_type": "TF",
            "options": [],
            "correct_answer": "False"
        }]

def evaluate_answer(question_text: str, correct_answer: str, question_type: str, student_response: str, api_key: str) -> Dict[str, Any]:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"""
        You are an AI learning evaluator. Grade this student response.
        
        Question: "{question_text}"
        Expected/Model Answer: "{correct_answer}"
        Question Type: {question_type}
        Student Response: "{student_response}"
        
        Evaluate the answer and return a JSON object with:
        - "is_correct": Boolean (true/false). For Short Answers, allow partial correctness (e.g. if key concepts are present, set true).
        - "marks_obtained": Float. Assign marks out of 5.0 (e.g., 5.0 for fully correct, 2.5 for partial, 0.0 for incorrect).
        - "total_marks": 5.0
        - "explanation": Explain any mistakes the student made, or why the answer is correct/incorrect compared to the expected answer. Keep it encouraging!
        - "suggestions": Specific actionable tips on how the student can write a better answer next time.
        - "weak_concept_flag": A specific sub-topic or keyword related to the mistake (e.g., 'Recursion', 'Base Case', 'Time Complexity') if incorrect. If correct, set to "".

        Respond with ONLY the JSON object.
        """
        response = model.generate_content(prompt)
        cleaned_response = clean_json_string(response.text)
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Evaluation error: {e}")
        return {
            "is_correct": False,
            "marks_obtained": 0.0,
            "total_marks": 5.0,
            "explanation": f"Failed to grade answer due to API error: {str(e)}",
            "suggestions": "Try resubmitting.",
            "weak_concept_flag": "Unknown Concept"
        }

def generate_study_plan(weak_topics: List[Dict[str, Any]], api_key: str) -> Dict[str, Any]:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")
        topics_str = "\n".join([f"- {t['topic_name']}: incorrect answers count = {t['incorrect_count']}" for t in weak_topics])
        prompt = f"""
        You are an expert academic advisor. Create a personalized study plan for a student struggling with these topics:
        {topics_str}
        
        Generate a highly structured response in JSON format. The JSON must contain these exact keys:
        - "daily_schedule": A dictionary mapping days (e.g., "Monday", "Tuesday", etc.) to a specific topic and study task.
        - "weekly_goals": A list of 3-5 specific study benchmarks for the week.
        - "recommended_revision": A concise string recommending what resources or conceptual approaches the student should prioritize.
        - "est_completion_hours": A float representing the estimated total study/revision hours required to master these concepts.

        Respond with ONLY the JSON object.
        """
        response = model.generate_content(prompt)
        cleaned_response = clean_json_string(response.text)
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Study plan error: {e}")
        return {
            "daily_schedule": {"Monday": "Review notes", "Wednesday": "Practice problems"},
            "weekly_goals": ["Revise fundamental definitions"],
            "recommended_revision": "Re-read the uploaded study material sections.",
            "est_completion_hours": 4.0
        }

def ask_tutor(query: str, context: str, chat_history: List[Dict[str, str]], persona: str, api_key: str) -> str:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")
        persona_instructions = ""
        if persona == "Simple Words":
            persona_instructions = "Explain using simple words, analogies, and short sentences. Avoid complex jargon."
        elif persona == "Age 10":
            persona_instructions = "Explain like I'm 10 years old. Use a playful, encouraging tone and relate it to childhood concepts like toys, playgrounds, or games."
        elif persona == "Give another example":
            persona_instructions = "Provide 2 fresh, practical real-world examples or metaphors to illustrate the concept clearly."
        else:
            persona_instructions = "Provide a comprehensive, high-quality explanation suitable for a student, focusing on conceptual clarity."
            
        history_str = ""
        for msg in chat_history[-6:]:
            role_label = "Student" if msg["role"] == "user" else "Tutor"
            history_str += f"{role_label}: {msg['content']}\n"
            
        prompt = f"""
        You are a highly supportive and personalized AI tutor, aligned with SDG 4 (Quality Education).
        Use the following uploaded study material context to answer the student's question. If the information isn't in the context, use your general knowledge but mention it is supplementary.
        
        Context:
        {context}
        
        Conversation history:
        {history_str}
        
        Persona/Formatting Constraint:
        {persona_instructions}
        
        Student's Question: "{query}"
        
        Provide a detailed, helpful, and interactive response.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Tutor is currently offline. Error: {str(e)}. Please check your API key."
