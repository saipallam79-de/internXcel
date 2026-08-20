from app.utils.pdf_generator import create_simple_pdf


def generate_certificate(path: str, student_name: str, domain: str, certificate_id: str, intern_id: str, issue_date: str) -> str:
    return create_simple_pdf(path, "CERTIFICATE OF COMPLETION", ["This is to certify that", f"<b><font size=18>{student_name}</font></b>", f"has successfully completed the <b>{domain}</b> internship with InternXcel.", f"<b>Intern ID:</b> {intern_id}<br/><b>Certificate ID:</b> {certificate_id}<br/><b>Issue date:</b> {issue_date}", "Authorized Signature<br/><b>InternXcel</b>"])
