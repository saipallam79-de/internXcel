from app.utils.pdf_generator import create_offer_letter_pdf


def generate_offer_letter(path: str, student_name: str, domain: str, intern_id: str, start_date: str, end_date: str) -> str:
    return create_offer_letter_pdf(path, student_name, domain, intern_id, start_date, end_date, f"INTX-OFFER-{intern_id.replace('/', '-')}", "student@internxcel.dev")


def generate_personalized_offer_letter(path: str, student_name: str, domain: str, intern_id: str, start_date: str, end_date: str, offer_id: str, email: str) -> str:
    return create_offer_letter_pdf(path, student_name, domain, intern_id, start_date, end_date, offer_id, email)
