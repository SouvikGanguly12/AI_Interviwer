import os
import io
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime

import streamlit as st

from Interview.question_generator import generate_questions
from Interview.answer_evaluator import evaluate_answer
from resume_parser.skill_extractor import skill_extractor
from pdf.pdf_generator import generate_interview_report


st.set_page_config(
    page_title="AI Interview (Streamlit)",
    page_icon="🎙️",
    layout="wide",
)

ROLE_QUESTIONS = {
    "Software Engineer": [
        "Describe a scalable system you designed and how you ensured reliability.",
        "How do you approach debugging a complex production issue?",
        "Explain your experience with version control and code review best practices.",
    ],
    "Data Scientist": [
        "How have you used statistical models to solve a business problem?",
        "Describe a machine learning project where data quality was a challenge.",
        "What metrics do you use to evaluate a predictive model?",
    ],
    "Product Manager": [
        "How do you prioritize features for a product roadmap?",
        "Describe a time you navigated conflicting stakeholder needs.",
        "How do you measure product success after launch?",
    ],
    "UI/UX Designer": [
        "How do you validate a design with users?",
        "Describe your process for creating a user-centered interface.",
        "What are the key accessibility considerations in your designs?",
    ],
    "DevOps Engineer": [
        "How do you implement CI/CD for a distributed application?",
        "Describe your experience with infrastructure as code and monitoring.",
        "How do you respond to an incident in a live environment?",
    ],
    "Quality Assurance Engineer": [
        "How do you design test cases for a critical feature release?",
        "What is your approach to automating regression tests?",
        "How do you handle flaky tests in a CI pipeline?",
    ],
    "Business Analyst": [
        "How do you translate stakeholder requirements into actionable work?",
        "Describe a time you identified a process improvement opportunity.",
        "How do you ensure requirements remain aligned with business goals?",
    ],
    "Sales Manager": [
        "How do you build and motivate a high-performing sales team?",
        "Describe your strategy for closing a large enterprise deal.",
        "How do you track and improve sales pipeline performance?",
    ],
    "Customer Support Specialist": [
        "How do you handle an escalated customer complaint?",
        "Describe a time you turned a dissatisfied customer into a happy one.",
        "What tools and metrics do you use to deliver strong customer support?",
    ],
    "Marketing Manager": [
        "How do you develop a marketing campaign from concept to execution?",
        "Describe a successful digital marketing strategy you implemented.",
        "How do you measure and optimize campaign ROI?",
    ],
    "HR Specialist": [
        "How do you improve employee engagement in a fast-growing team?",
        "Describe your approach to resolving a workplace conflict.",
        "How do you ensure diversity, equity, and inclusion in hiring?",
    ],
    "Finance Analyst": [
        "How do you build financial forecasts and what assumptions do you use?",
        "Describe a time you identified a cost-saving opportunity.",
        "How do you communicate financial insights to non-financial stakeholders?",
    ],
    "Network Engineer": [
        "How do you design a secure and resilient network topology?",
        "Describe your experience troubleshooting network outages.",
        "What tools do you use to monitor network performance?",
    ],
    "Cybersecurity Analyst": [
        "How do you investigate and respond to a security breach?",
        "Describe a security control you implemented to reduce risk.",
        "How do you stay current with emerging cybersecurity threats?",
    ],
    "Content Writer": [
        "How do you craft engaging content for a technical audience?",
        "Describe your process for researching and creating long-form content.",
        "How do you optimize content for readability and SEO?",
    ],
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


@dataclass
class QA:
    question: str
    answer: str
    score: int
    feedback: str
    proper_answer: str


def _save_bytes_to_uploads(upload_dir: str, filename: str, data: bytes) -> str:
    os.makedirs(upload_dir, exist_ok=True)
    safe = "".join(c for c in filename if c.isalnum() or c in (".", "-", "_"))
    path = os.path.join(upload_dir, safe)
    with open(path, "wb") as f:
        f.write(data)
    return path


def _resume_to_text(upload_dir: str, uploaded_file) -> str:
    data = uploaded_file.read()
    resume_path = _save_bytes_to_uploads(upload_dir, uploaded_file.name, data)
    return skill_extractor(resume_path)


def _init_session():
    for k, v in {
        "questions": [],
        "cursor": 0,
        "qas": [],
        "started_at": None,
        "timer_seconds": 0,
        "last_tick": None,
        "answer_text": "",
        "interview_complete": False,
        "show_results": False,
        "interview_started": False,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _tick_timer():
    if st.session_state.get("interview_complete", False) or not st.session_state.get("interview_started", False):
        return

    now = time.time()
    last = st.session_state.get("last_tick")
    if last is None:
        st.session_state["last_tick"] = now
        return

    st.session_state["timer_seconds"] += int(now - last)
    st.session_state["last_tick"] = now


def _start_interview():
    st.session_state["started_at"] = time.time()
    st.session_state["timer_seconds"] = 0
    st.session_state["last_tick"] = time.time()
    st.session_state["interview_started"] = True
    st.session_state["interview_complete"] = False
    st.session_state["show_results"] = False
    st.session_state["answer_text"] = ""


def _format_mmss(seconds: int) -> str:
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"


def _ensure_questions_loaded(questions: List[str]):
    if not questions:
        st.warning("No questions generated from the resume. Try a different resume file.")
        st.session_state["questions"] = []
        st.session_state["cursor"] = 0
        return False

    if not st.session_state.get("questions"):
        st.session_state["questions"] = questions
        st.session_state["cursor"] = 0
        st.session_state["qas"] = []
        st.session_state["interview_started"] = False
    return True


def _current_question() -> Optional[str]:
    idx = st.session_state.get("cursor", 0)
    qs = st.session_state.get("questions", [])
    if idx < len(qs):
        return qs[idx]
    return None


def _progress() -> Dict[str, Any]:
    total = len(st.session_state.get("questions", []))
    asked = len(st.session_state.get("qas", []))
    pct = 0 if total == 0 else int(round((asked / total) * 100))
    avg_score_10 = 0
    if asked:
        avg_score_10 = sum(q.score for q in st.session_state.qas) / asked
    avg_pct = int(round((avg_score_10 / 10) * 100)) if asked else 0
    return {"total": total, "asked": asked, "pct": pct, "avg_pct": avg_pct}


def _render_intro():
    st.title("🎙️ AI Interview (Streamlit Edition)")
    st.caption("Upload a resume → generate skill-based questions → submit answers → get rubric scoring + expected answers.")


def _render_top_summary():
    prog = _progress()
    timer = _format_mmss(st.session_state.get("timer_seconds", 0))

    if prog["total"] > 0 or st.session_state.get("interview_started", False):
        cols = st.columns([1, 1, 1])
        with cols[0]:
            st.metric("Questions", f"{prog['asked']}/{prog['total']}")
        with cols[1]:
            st.metric("Overall Score", f"{prog['avg_pct']}%")
        with cols[2]:
            st.metric("Time", timer)
        st.markdown("---")


def _render_sidebar():
    st.sidebar.header("Interview Progress")

    prog = _progress()

    st.sidebar.metric("Questions", f"{prog['asked']}/{prog['total']}")
    st.sidebar.metric("Overall Score", f"{prog['avg_pct']}%")
    st.sidebar.markdown("---")

    timer = _format_mmss(st.session_state.get("timer_seconds", 0))
    st.sidebar.metric("Time", timer)

    st.sidebar.progress(min(100, prog["pct"]))

    if st.sidebar.button("🧹 Reset session", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


def _submit_current_answer(answer_text: str):
    question = _current_question()
    if not question:
        st.info("Interview complete.")
        return

    with st.spinner("Evaluating answer..."):
        result = evaluate_answer(question, answer_text)

    q = QA(
        question=question,
        answer=answer_text,
        score=int(result.get("score") or 0),
        feedback=result.get("feedback") or "",
        proper_answer=result.get("proper_answer") or "",
    )

    st.session_state.qas.append(q)
    st.session_state.cursor += 1


def _render_results_page():
    st.title("🏆 Interview Results")
    prog = _progress()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Questions", prog['total'])
    with col2:
        st.metric("Answered", prog['asked'])
    with col3:
        st.metric("Overall Score", f"{prog['avg_pct']}%")
    with col4:
        timer = _format_mmss(st.session_state.get("timer_seconds", 0))
        st.metric("Time Taken", timer)

    st.markdown("---")

    if st.session_state.qas:
        scores = [q.score for q in st.session_state.qas]
        st.subheader("Score Distribution")
        st.bar_chart(scores)

    st.markdown("---")

    st.subheader("Detailed Review")
    if st.session_state.qas:
        for i, qa in enumerate(st.session_state.qas, 1):
            with st.container(border=True):
                st.markdown(f"### Question {i}")
                st.info(qa.question)

                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown(f"**Your Score**: {qa.score}/10")
                with col2:
                    score_pct = int((qa.score / 10) * 100)
                    st.markdown(f"**Percentage**: {score_pct}%")

                st.markdown("**Your Answer**")
                st.write(qa.answer if qa.answer else "*[Skipped]*")

                st.markdown("**Feedback**")
                st.write(qa.feedback)

                with st.expander("📖 Expected / Proper Answer"):
                    st.write(qa.proper_answer)

    st.markdown("---")

    st.subheader("Summary Table")
    if st.session_state.qas:
        rows = [
            {
                "#": i,
                "Question": qa.question[:50] + "..." if len(qa.question) > 50 else qa.question,
                "Score": f"{qa.score}/10",
                "Feedback": qa.feedback[:60] + "..." if len(qa.feedback) > 60 else qa.feedback,
            }
            for i, qa in enumerate(st.session_state.qas, 1)
        ]
        st.dataframe(rows, use_container_width=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📥 Download PDF", use_container_width=True):
            pdf_buffer = generate_interview_report(
                st.session_state.qas,
                st.session_state.get("timer_seconds", 0),
                prog['avg_pct'],
            )
            st.download_button(
                label="📄 Download Interview Report",
                data=pdf_buffer,
                file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
    with col2:
        if st.button("🔄 Retake Interview", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
    with col3:
        if st.button("⬅️ Back", use_container_width=True):
            st.session_state["show_results"] = False
            st.rerun()


def _render_chat():
    left, right = st.columns([2, 1])

    with left:
        st.subheader("Interview")
        current_q = _current_question()

        if current_q:
            st.markdown("### Current Question")
            st.info(current_q)

            answer = st.text_area(
                "Your answer",
                value=st.session_state.get("answer_text", ""),
                height=130,
                placeholder="Type your answer (include examples when possible).",
                key="answer_input",
            )

            if st.session_state.get("answer_text") != answer:
                st.session_state.answer_text = answer

            st.markdown("---")
            st.markdown("### Answer Options")

            col_text, col_skip = st.columns(2)
            with col_text:
                if st.button("📝 Send & Evaluate", type="primary", use_container_width=True):
                    if not answer.strip():
                        st.warning("Please enter an answer.")
                    else:
                        _submit_current_answer(answer.strip())
                        st.session_state.answer_text = ""
                        st.rerun()
            with col_skip:
                if st.button("⏭️ Skip question", use_container_width=True):
                    _submit_current_answer(answer_text="")
                    st.rerun()

        st.markdown("---")
        st.markdown("## 📋 Previous Answers")

        if st.session_state.qas:
            with st.expander(f"View all {len(st.session_state.qas)} previous answers"):
                for i, qa in enumerate(st.session_state.qas, 1):
                    st.markdown(f"### Q{i}")
                    st.info(qa.question)
                    st.markdown("**Your answer**")
                    st.write(qa.answer)
                    st.markdown(f"**Score**: {qa.score}/10")
                    st.markdown("**Feedback**")
                    st.write(qa.feedback)
                    with st.expander("Expected / Proper Answer"):
                        st.write(qa.proper_answer)
                    st.divider()
        else:
            st.caption("No previous answers yet.")

    with right:
        st.subheader("Summary")
        prog = _progress()

        st.metric("Asked", f"{prog['asked']}/{prog['total']}")
        st.metric("Overall", f"{prog['avg_pct']}%")

        if st.session_state.qas:
            scores = [q.score for q in st.session_state.qas]
            st.bar_chart(scores)

            with st.expander("Detailed table"):
                rows = [
                    {
                        "#": i,
                        "Question": qa.question,
                        "Score": qa.score,
                        "Feedback": qa.feedback,
                    }
                    for i, qa in enumerate(st.session_state.qas, 1)
                ]
                st.dataframe(rows, use_container_width=True)


def _render_upload_and_generate():
    st.header("1) Upload resume")

    upload_dir = os.path.join("Uploads", "resumes")

    uploaded = st.file_uploader(
        "Upload resume (PDF / TXT / MD)",
        type=["pdf", "txt", "md", "rtf"],
        accept_multiple_files=False,
    )

    colA, colB = st.columns([1, 2])
    with colA:
        max_questions = st.slider("Max questions", min_value=3, max_value=15, value=10, step=1)
    with colB:
        selected_role = st.selectbox(
            "Choose interview role",
            options=list(ROLE_QUESTIONS.keys()),
            index=0,
            help="Select the role for role-specific interview questions.",
        )
        seed = st.text_input("Session label (optional)", value="", help="Affects nothing; helps you identify the session.")

    if uploaded is not None:
        resume_bytes = uploaded.read()
        uploaded2 = io.BytesIO(resume_bytes)
        uploaded2.name = uploaded.name

        import hashlib
        file_hash = hashlib.sha256(resume_bytes).hexdigest()

        if st.session_state.get("last_file_hash") != file_hash:
            st.session_state.last_file_hash = file_hash
            st.session_state.questions = []
            st.session_state.cursor = 0
            st.session_state.qas = []
            st.session_state.timer_seconds = 0
            st.session_state.last_tick = None
            st.session_state["interview_started"] = False
            st.session_state["interview_complete"] = False
            st.session_state["show_results"] = False
            st.session_state["answer_text"] = ""

        if not st.session_state.questions:
            with st.spinner("Extracting text + generating interview questions..."):
                resume_text = _resume_to_text(upload_dir, uploaded2)
                resume_questions = generate_questions(resume_text)

                lower_text = resume_text.lower() if isinstance(resume_text, str) else ""
                projects_found = any(k in lower_text for k in ("project", "projects", "projects:"))
                certs_found = any(k in lower_text for k in ("certificate", "certification", "certified", "certificates"))

                project_questions = []
                if projects_found:
                    project_questions = [
                        "Tell me about one of your projects: its goal, your role, and the outcome.",
                        "What technical challenges did you face in this project and how did you solve them?",
                        "How did you measure the success of this project?",
                    ]

                cert_questions = []
                if certs_found:
                    cert_questions = [
                        "Which certification did you find most valuable and why?",
                        "How did the certification change your approach or skills in practical work?",
                        "Can you describe a topic from your certification where you applied the knowledge in a project?",
                    ]

                role_questions = ROLE_QUESTIONS.get(selected_role, [])
                questions = role_questions + project_questions + cert_questions + resume_questions
                questions = questions[:max_questions]

            ok = _ensure_questions_loaded(questions)
            if not ok:
                return

        st.success(f"Generated {len(st.session_state.questions)} questions.")

        if not st.session_state.get("interview_started", False):
            st.info("Press Start Interview to begin the timer and answer questions.")
            if st.button("▶️ Start Interview", type="primary", use_container_width=True, key="start_interview"):
                _start_interview()
                st.rerun()
        else:
            st.success("Interview started. Answer the questions below.")


def main():
    _init_session()

    current_q = _current_question() if st.session_state.get("questions") else None
    if current_q is None and st.session_state.get("questions") and st.session_state.get("interview_started", False):
        st.session_state["interview_complete"] = True

    _tick_timer()

    _render_sidebar()

    _render_intro()
    _render_top_summary()

    if st.session_state.get("show_results", False) and st.session_state.get("interview_complete", False):
        _render_results_page()
    elif not st.session_state.get("questions") or not st.session_state.get("interview_started", False):
        _render_upload_and_generate()
    else:
        _render_chat()

        st.markdown("---")
        if st.session_state.get("interview_complete", False):
            if st.button("🏁 Go to Results", type="primary", use_container_width=True):
                st.session_state["show_results"] = True
                st.rerun()


if __name__ == "__main__":
    main()

