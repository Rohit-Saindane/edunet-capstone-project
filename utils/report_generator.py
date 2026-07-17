import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_report(output_path: str = "report/report.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path, 
        pagesize=letter,
        rightMargin=54, 
        leftMargin=54, 
        topMargin=40, 
        bottomMargin=40
    )
    styles = getSampleStyleSheet()
    color_primary = colors.HexColor("#1e1b4b")
    color_secondary = colors.HexColor("#4f46e5")
    color_body = colors.HexColor("#334155")
    
    style_title = ParagraphStyle(
        name="DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=color_primary,
        spaceAfter=4,
        alignment=0
    )
    style_subtitle = ParagraphStyle(
        name="DocSub",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=color_secondary,
        spaceAfter=15,
        alignment=0
    )
    style_heading = ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=color_primary,
        spaceBefore=10,
        spaceAfter=4,
        borderColor=color_secondary,
        borderWidth=0.5,
        borderPadding=2,
        keepWithNext=True
    )
    style_body = ParagraphStyle(
        name="DocBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=color_body,
        spaceAfter=8
    )
    
    story = []
    story.append(Paragraph("EduAI: Personalized Learning Assistant", style_title))
    story.append(Paragraph("A Retrieval-Augmented & Adaptive Evaluation System for UN SDG 4 (Quality Education)", style_subtitle))
    
    divider = Table([[""]], colWidths=[504])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 1.5, color_primary),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Abstract", style_heading))
    story.append(Paragraph(
        "Standard digital education tools often function as passive content repositories or generic chatbot interfaces. "
        "These methodologies fail to support students struggling with specific conceptual gaps. "
        "EduAI addresses these limitations by introducing a local database-driven learning companion aligned with UN SDG 4. "
        "By utilizing text parsing, semantic chunk embeddings, and Retrieval-Augmented Generation (RAG) powered by Gemini API, "
        "EduAI enables customized content summarization, adaptive quiz generation, intelligent answers scoring, weak topic detection, "
        "and personalized weekly schedules. Testing shows this method improves response feedback quality and structured learning loops.",
        style_body
    ))
    
    story.append(Paragraph("Objective", style_heading))
    story.append(Paragraph(
        "To build an accessible, cost-effective learning platform that transitions student interaction from passive reading to active, "
        "feedback-guided recall. Specifically, the system aims to automate diagnostic quiz generation, identify conceptual weak spots, "
        "and establish structured revision routines that adapt to individual learning paces.",
        style_body
    ))
    
    story.append(Paragraph("Methodology", style_heading))
    story.append(Paragraph(
        "EduAI is built on a modular Python architecture consisting of five layers: "
        "(1) Ingestion: PDF and TXT text extraction via PyPDF2. "
        "(2) Retrieval (RAG): Segmenting text into 800-character overlapping chunks, indexing with Gemini text embeddings, and searching via cosine similarity. "
        "(3) Adaptive Testing: Generating custom MCQs, short answers, and True/False questions. "
        "(4) Diagnostics: Evaluating responses, assigning numerical marks (0.0 to 5.0), and storing errors in an SQLite database. "
        "(5) Adaptive Planning: Auto-generating a calendar to target weak topics.",
        style_body
    ))
    
    story.append(Paragraph("AI Integration & SDG 4 Impact", style_heading))
    story.append(Paragraph(
        "EduAI directly supports SDG Target 4.3 (equal access to affordable education) and 4.c (teacher training and quality enhancement) by: "
        "providing student-focused, RAG-grounded tutoring that operates like a private, free academic companion; and "
        "offering custom study plans that reduce learning gaps. Visual analytics dashboards present trends in score retention and concept mastery.",
        style_body
    ))
    
    story.append(Paragraph("Results & Conclusion", style_heading))
    story.append(Paragraph(
        "The project successfully implements a complete personalized learning workflow. "
        "Unlike generic LLM chat windows, EduAI retains student context in SQLite, creating a closed-loop learning record. "
        "Future extensions will include sync options with standard Learning Management Systems (LMS) and multi-language summarization. "
        "In conclusion, EduAI demonstrates how generative AI can be structured to support inclusive and high-quality education.",
        style_body
    ))
    
    footer_data = [
        [
            Paragraph("<b>Project:</b> College SDG Exhibition (EduAI)", style_body),
            Paragraph("<b>Target Goal:</b> UN SDG 4 - Quality Education", style_body),
            Paragraph("<b>Tech:</b> Streamlit, SQLite, Gemini API", style_body)
        ]
    ]
    footer_table = Table(footer_data, colWidths=[168, 168, 168])
    footer_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(Spacer(1, 15))
    story.append(footer_table)
    
    doc.build(story)

if __name__ == "__main__":
    generate_report()