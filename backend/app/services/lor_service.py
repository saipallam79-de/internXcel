from app.utils.pdf_generator import create_simple_pdf


def generate_lor(path: str, student_name: str, domain: str, intern_id: str, duration: int, skills: str) -> str:
    return create_simple_pdf(path, "LETTER OF RECOMMENDATION", ["To whom it may concern,", f"This letter is to recommend <b>{student_name}</b>, who successfully completed the <b>{domain}</b> internship with InternXcel.", f"During this {duration}-day internship, {student_name} demonstrated commitment to structured learning, practical problem solving, and professional communication.", f"Skills demonstrated: {skills}.", f"Intern ID: {intern_id}<br/><br/>Authorized Signatory<br/><b>InternXcel Internship Program</b>"])
