from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from datetime import datetime
import io


def generate_interview_report(qas, timer_seconds, avg_score):
    """
    Generate a PDF report of interview Q&A with answers and corrections.
    
    Args:
        qas: List of QA dataclass objects
        timer_seconds: Total time spent in interview
        avg_score: Average score percentage
        
    Returns:
        BytesIO object containing PDF data
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        alignment=1
    )
    story.append(Paragraph("🏆 Interview Report", title_style))
    
    # Metadata
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    minutes = timer_seconds // 60
    seconds = timer_seconds % 60
    
    meta_style = ParagraphStyle(
        'Meta',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=6
    )
    story.append(Paragraph(f"<b>Report Generated:</b> {timestamp}", meta_style))
    story.append(Paragraph(f"<b>Time Taken:</b> {minutes:02d}:{seconds:02d}", meta_style))
    story.append(Paragraph(f"<b>Overall Score:</b> {avg_score}%", meta_style))
    story.append(Paragraph(f"<b>Total Questions:</b> {len(qas)}", meta_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Q&A Details
    for i, qa in enumerate(qas, 1):
        # Question
        question_style = ParagraphStyle(
            'QuestionStyle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2ca02c'),
            spaceAfter=6,
            spaceBefore=12
        )
        story.append(Paragraph(f"Question {i}", question_style))
        
        # Question text
        normal_style = styles['Normal']
        story.append(Paragraph(qa.question, normal_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Score
        score_pct = int((qa.score / 10) * 100)
        score_style = ParagraphStyle(
            'ScoreStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#d62728'),
            spaceAfter=6
        )
        story.append(Paragraph(f"<b>Score:</b> {qa.score}/10 ({score_pct}%)", score_style))
        
        # Your Answer
        story.append(Paragraph("<b>Your Answer:</b>", ParagraphStyle('Bold', parent=styles['Normal'], fontSize=10)))
        answer_text = qa.answer if qa.answer.strip() else "<i>[Skipped]</i>"
        story.append(Paragraph(answer_text, normal_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Feedback
        story.append(Paragraph("<b>Feedback:</b>", ParagraphStyle('Bold', parent=styles['Normal'], fontSize=10)))
        story.append(Paragraph(qa.feedback, normal_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Proper Answer
        story.append(Paragraph("<b>Expected/Correct Answer:</b>", ParagraphStyle('Bold', parent=styles['Normal'], fontSize=10)))
        story.append(Paragraph(qa.proper_answer, normal_style))
        
        story.append(Spacer(1, 0.2*inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
