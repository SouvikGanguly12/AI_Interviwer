import re
from resume_parser.skill_extractor import skill_extractor

try:
    # These extractors exist in the repo, but may be empty.
    from resume_parser.project_extractor import project_extractor  # type: ignore
except Exception:  # pragma: no cover
    project_extractor = None

try:
    from resume_parser.certificate_extractor import certificate_extractor  # type: ignore
except Exception:  # pragma: no cover
    certificate_extractor = None


question_templates = {
    "skill": {
        "Python": [
            "What are Python decorators?",
            "Explain the difference between a list and a tuple.",
            "What is a generator in Python?",
        ],
        "Machine Learning": [
            "What is overfitting?",
            "Explain the bias-variance tradeoff.",
            "How does linear regression work?",
        ],
        "MongoDB": [
            "What is the difference between SQL and MongoDB?",
            "Explain indexing in MongoDB.",
            "What are aggregation pipelines?",
        ],
        "Django": [
            "Explain Django's MVT architecture.",
            "What is Django ORM?",
            "How do you handle authentication in Django?",
        ],
        "OpenCV": [
            "How does image thresholding work?",
            "Explain face detection using Haar Cascades.",
            "What is the difference between image segmentation and object detection?",
        ],
    },
    "project": [
        "Tell me about one project you built: what was the problem, your approach, and the impact?",
        "What was the hardest technical challenge in your main project, and how did you solve it?",
        "What metrics or results did you achieve in your project (accuracy, performance, latency, etc.)?",
    ],
    "certificate": [
        "Which certificate did you earn and what knowledge did you gain from it?",
        "How did you apply what you learned from a certificate to a real project?",
        "What topics from your certificate are you most confident in, and why?",
    ],
}


def _extract_names(text: str) -> list[str]:
    if not text:
        return []
    # crude extraction: look for bullet-ish lines or headings
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    candidates = []
    for ln in lines:
        if re.search(r"(project|projects|certificate|certification)", ln, re.IGNORECASE):
            continue
        if len(ln) >= 3 and len(ln) <= 80:
            candidates.append(ln)
    return candidates[:5]


def _detect_role(resume_text: str) -> str:
    """Detect developer role from resume keywords.

    Returns:
      - "ml" for ML roles
      - "python" for Python roles

    Heuristic rules (per task request):
      - ML keywords: machine learning, overfitting, model, bias-variance, regression, classification, dataset, neural
      - Python keywords: python, django, flask, decorators, generator, list/tuple
    """
    t = (resume_text or "").lower()

    ml_keywords = [
        "machine learning",
        "overfitting",
        "bias-variance",
        "bias variance",
        "linear regression",
        "regression",
        "classification",
        "neural",
        "neural network",
        "model",
        "feature",
        "dataset",
    ]

    python_keywords = [
        "python",
        "django",
        "flask",
        "decorator",
        "decorators",
        "generator",
        "yield",
        "list",
        "tuple",
    ]

    ml_score = sum(1 for k in ml_keywords if k in t)
    py_score = sum(1 for k in python_keywords if k in t)

    # If tie/weak signals, default to python (safer for general resumes)
    return "ml" if ml_score > py_score else "python"


def _extract_template_skills(resume_text: str) -> list[str]:
    """Return which template skills are present in the resume.

    This maps resume text keywords to the keys used in `question_templates["skill"]`.
    """
    t = (resume_text or "").lower()

    skill_keywords: dict[str, list[str]] = {
        "Python": ["python"],
        "Machine Learning": [
            "machine learning",
            "overfitting",
            "bias-variance",
            "bias variance",
            "linear regression",
            "regression",
            "classification",
            "neural",
            "neural network",
            "dataset",
            "model",
        ],
        "MongoDB": ["mongodb", "mongo"],
        "Django": ["django", "django orm"],
        "OpenCV": ["opencv", "haar cascades", "face detection", "thresholding"],
    }

    matched: list[str] = []
    for skill_name, keywords in skill_keywords.items():
        if any(k in t for k in keywords):
            matched.append(skill_name)

    # Deterministic ordering for UX
    template_order = list(question_templates["skill"].keys())
    matched = [s for s in template_order if s in matched]
    return matched


def generate_questions(resume_text: str):
    """Generate skill + project + certificate questions from resume text."""
    questions: list[str] = []

    role = _detect_role(resume_text)
    extracted_skills = _extract_template_skills(resume_text)


    # Skills: generate for each detected skill template
    for skill_name in extracted_skills:
        questions.extend(question_templates["skill"][skill_name])

    # Backwards-compatible fallback if no skills detected
    if not questions:
        role = _detect_role(resume_text)
        role_skill_names = ["Python"] if role == "python" else ["Machine Learning"]
        for skill_name in role_skill_names:
            if resume_text and re.search(re.escape(skill_name), resume_text, re.IGNORECASE):
                questions.extend(question_templates["skill"][skill_name])

    # Projects/certificates: still generic, but we only keep them if we see relevant markers
    if role == "ml":
        has_project = bool(re.search(r"projects?|machine learning|model|regression|classification|overfitting|bias[- ]variance|neural|dataset", resume_text or "", re.IGNORECASE))
    else:
        has_project = bool(re.search(r"projects?|python|django|flask|mongodb|opencv|face recognition|e-?commerce", resume_text or "", re.IGNORECASE))

    has_cert = bool(re.search(r"certification|certificate|course|training", resume_text or "", re.IGNORECASE))

    if has_project:
        questions.extend(question_templates["project"])
    if has_cert:
        questions.extend(question_templates["certificate"])

    # Fallback: if we have skills extracted but no projects/certs, it's fine.
    # If still empty for some reason, use role-based questions.
    if not questions:
        role = _detect_role(resume_text)
        role_skill_names = ["Python"] if role == "python" else ["Machine Learning"]
        for skill_name in role_skill_names:
            questions.extend(question_templates["skill"][skill_name])
        questions.extend(question_templates["project"])
        if has_cert:
            questions.extend(question_templates["certificate"])

    # Keep reasonable length
    return questions[:10]




# Backwards compatibility: some code calls generator with resume text directly.
# load_resume_questions uses skill_extractor(resume_path) already.





if __name__ == "__main__":
    # Example usage when running this module directly
    resume = """
Skills: Python, Machine Learning, MongoDB
Projects:
E-commerce Website using Django and MongoDB
Face Recognition System using OpenCV
"""

    for i, q in enumerate(generate_questions(resume), 1):
        print(f"{i}. {q}")