from resume_parser.skill_extractor import skill_extractor
from .question_generator import generate_questions

questions = []
current_question = 0

# Simple session-less flow (kept for now to avoid breaking routes)
# NOTE: This app currently uses module globals; upgrading to per-session
# state would require storing questions in Flask session or a server cache.

def load_resume_questions(resume_path):
    global questions, current_question
    resume_text = skill_extractor(resume_path)
    questions = generate_questions(resume_text)
    current_question = 0
    return questions

def get_next_question():
    global current_question
    
    if current_question < len(questions):
        q = questions[current_question]
        current_question += 1
        return q
    return None