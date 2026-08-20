from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph


def create_simple_pdf(path: str, title: str, lines: list[str]) -> str:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas = Canvas(str(output), pagesize=A4)
    canvas.setFillColor(colors.HexColor("#171717"))
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#D9F36A"))
    canvas.rect(0, A4[1] - 0.55 * inch, A4[0], 0.55 * inch, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(0.7 * inch, A4[1] - 0.38 * inch, "INTERNXCEL")
    canvas.setFillColor(colors.HexColor("#FF6B35"))
    canvas.setFont("Helvetica-Bold", 22)
    canvas.drawString(0.7 * inch, A4[1] - 1.25 * inch, title)
    canvas.setStrokeColor(colors.HexColor("#FF6B35"))
    canvas.setLineWidth(2)
    canvas.line(0.7 * inch, A4[1] - 1.45 * inch, A4[0] - 0.7 * inch, A4[1] - 1.45 * inch)
    styles = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=styles["BodyText"], fontName="Helvetica", fontSize=11, leading=18, textColor=colors.HexColor("#333333"), spaceAfter=12)
    story_y = A4[1] - 1.9 * inch
    for line in lines:
        paragraph = Paragraph(line, body)
        _, height = paragraph.wrap(A4[0] - 1.4 * inch, A4[1])
        paragraph.drawOn(canvas, 0.7 * inch, story_y - height)
        story_y -= height + 12
    canvas.setStrokeColor(colors.HexColor("#D9D5CB"))
    canvas.line(0.7 * inch, 1.05 * inch, A4[0] - 0.7 * inch, 1.05 * inch)
    canvas.setFillColor(colors.HexColor("#77736B"))
    canvas.setFont("Helvetica", 9)
    canvas.drawString(0.7 * inch, 0.75 * inch, "Learn. Build. Complete. Get Certified.")
    canvas.drawRightString(A4[0] - 0.7 * inch, 0.75 * inch, "InternXcel · www.internxcel.dev")
    canvas.save()
    return str(output)


def create_offer_letter_pdf(
    path: str,
    student_name: str,
    domain: str,
    intern_id: str,
    start_date: str,
    end_date: str,
    offer_id: str,
    email: str,
) -> str:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas = Canvas(str(output), pagesize=A4)
    width, height = A4
    margin = 0.72 * inch
    dark = colors.HexColor("#241126")
    magenta = colors.HexColor("#9c176b")
    ink = colors.HexColor("#182033")
    muted = colors.HexColor("#5d6473")

    canvas.setFillColor(colors.white)
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.setFillColor(dark)
    canvas.rect(0, height - 0.04 * inch, width, 0.04 * inch, fill=1, stroke=0)
    canvas.setFillColor(magenta)
    canvas.rect(0, height - 1.08 * inch, width, 0.025 * inch, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#f4f0f4"))
    canvas.circle(width - 0.45 * inch, 1.3 * inch, 1.45 * inch, fill=1, stroke=0)

    canvas.setFillColor(dark)
    canvas.setFont("Helvetica-Bold", 26)
    canvas.drawString(margin, height - 0.72 * inch, "Intern")
    canvas.setFillColor(magenta)
    canvas.drawString(margin + 0.92 * inch, height - 0.72 * inch, "Xcel")
    canvas.setFillColor(colors.HexColor("#8f9098"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(margin + 0.02 * inch, height - 0.91 * inch, "Learn. Build. Complete. Get Certified.")

    canvas.setFillColor(ink)
    canvas.setFont("Helvetica", 8)
    contact_x = width - 2.55 * inch
    for index, value in enumerate(["+91 90000 00000", "hello@internxcel.dev", "support@internxcel.dev", "Remote · India"]):
        canvas.drawString(contact_x, height - (0.48 + index * 0.16) * inch, value)

    canvas.setFillColor(muted)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawRightString(width - margin, height - 1.52 * inch, "InternXcel Internship Program")
    canvas.drawRightString(width - margin, height - 1.67 * inch, f"Offer ID: {offer_id}")
    canvas.drawRightString(width - margin, height - 1.82 * inch, f"Issued: {start_date}")

    canvas.setFillColor(ink)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawCentredString(width / 2, height - 2.18 * inch, "INTERNSHIP OFFER LETTER")
    canvas.setStrokeColor(magenta)
    canvas.setLineWidth(1.5)
    canvas.line(margin, height - 2.32 * inch, width - margin, height - 2.32 * inch)

    styles = getSampleStyleSheet()
    body = ParagraphStyle("offer-body", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=14, textColor=ink, alignment=4, spaceAfter=10)
    small = ParagraphStyle("offer-small", parent=body, fontSize=8.2, leading=12, textColor=muted, alignment=0)
    y = height - 2.67 * inch
    story = [
        f"Dear <b>{student_name}</b>,",
        f"We are pleased to offer you the position of <b>{domain} Intern</b> at InternXcel. We are delighted to welcome you to our internship program and look forward to supporting your learning and professional development.",
        "This internship is designed to provide practical industry exposure, hands-on project experience, and an opportunity to enhance your technical and professional skills through structured learning and real-world assignments.",
        f"You are required to log in to the InternXcel Internship Portal using <b>{email}</b> to access your dashboard, complete the assigned modules and tasks, submit your work, and track your internship progress. We encourage you to complete all assigned activities with dedication and maintain professional conduct throughout the program.",
        f"Upon successful completion of all assigned tasks and internship requirements, you will be awarded an Internship Completion Certificate and a Letter of Recommendation. <b>Internship ID:</b> {intern_id} · <b>Duration:</b> {start_date} to {end_date}",
        "We are confident that this internship will be a valuable step in your professional journey and wish you a rewarding learning experience with InternXcel.",
    ]
    for index, text in enumerate(story):
        style = small if index == 0 else body
        paragraph = Paragraph(text, style)
        _, text_height = paragraph.wrap(width - 2 * margin, height)
        paragraph.drawOn(canvas, margin, y - text_height)
        y -= text_height + (8 if index == 0 else 5)

    y = 1.2 * inch
    canvas.setFillColor(ink)
    canvas.setFont("Helvetica", 8.5)
    canvas.drawString(margin, y + 0.42 * inch, "Best Regards,")
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(margin, y + 0.16 * inch, "Program Coordinator")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(muted)
    canvas.drawString(margin, y, "InternXcel Internship Program")
    canvas.setStrokeColor(magenta)
    canvas.line(margin, 0.67 * inch, width - margin, 0.67 * inch)
    canvas.setFillColor(muted)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(margin, 0.43 * inch, "AI & ML  |  Web Development  |  Data Science  |  Cloud & DevOps  |  Cybersecurity  |  UI/UX")
    canvas.drawRightString(width - margin, 0.43 * inch, "internxcel.dev")
    canvas.save()
    return str(output)
