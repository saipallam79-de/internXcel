from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.internship import Domain
from app.models.module import Module
from app.models.task import Task


CURRICULA = {
    "AI & Machine Learning": [
        "Prerequisite Onboarding",
        "Introduction to AI and Python",
        "Python Mini Project",
        "Data Analysis and Visualization",
        "Machine Learning Fundamentals",
        "AI Tools and Mini Project",
        "Final AI & ML Project",
        "Completion Certificate",
    ],
    "Data Science & Data Analytics": [
        "Prerequisite Onboarding",
        "Python for Data Science",
        "Data Collection and Cleaning",
        "Exploratory Data Analysis",
        "Data Visualization",
        "Statistics and Machine Learning Basics",
        "Data Analytics Final Project",
        "Completion Certificate",
    ],
    "Full Stack Web Development": [
        "Prerequisite Onboarding",
        "HTML and CSS",
        "JavaScript Fundamentals",
        "Frontend Development Project",
        "Backend Development",
        "Database Integration",
        "Full Stack Final Project",
        "Completion Certificate",
    ],
    "Java Development": [
        "Prerequisite Onboarding",
        "Core Java",
        "OOP and Collections",
        "JDBC and Database",
        "Advanced Java",
        "Spring Boot Basics",
        "Java Final Project",
        "Completion Certificate",
    ],
    "Python Development": [
        "Prerequisite Onboarding",
        "Python Fundamentals",
        "Functions and OOP",
        "File Handling and APIs",
        "Libraries and Automation",
        "Python Web/Data Project",
        "Final Python Project",
        "Completion Certificate",
    ],
    "Cloud Computing & DevOps": [
        "Prerequisite Onboarding",
        "Cloud Fundamentals",
        "Linux and Networking",
        "AWS and Cloud Services",
        "Docker and Containers",
        "CI/CD",
        "Infrastructure and Deployment Project",
        "Completion Certificate",
    ],
    "Cybersecurity": [
        "Prerequisite Onboarding",
        "Cybersecurity Fundamentals",
        "Networking Fundamentals",
        "Linux Security",
        "Web Security",
        "Ethical Security Testing Basics",
        "Security Analysis Final Project",
        "Completion Certificate",
    ],
    "UI/UX Design": [
        "Prerequisite Onboarding",
        "Design Fundamentals",
        "User Research",
        "Wireframing",
        "UI Design",
        "Prototyping",
        "Complete UI/UX Case Study",
        "Completion Certificate",
    ],
}


def _module_description(domain_name: str, title: str, number: int) -> tuple[str, str, str, str]:
    if number == 0:
        return (
            "Complete your onboarding requirement before starting the learning path.",
            "Review your personalized offer letter, publish it on LinkedIn, and submit the post URL.",
            "Complete the LinkedIn post and submit a public post URL for review.",
            "LinkedIn post URL",
        )
    if number == len(CURRICULA[domain_name]) - 1:
        return (
            f"Complete and present your {domain_name} internship portfolio.",
            "Deliver a polished final project, explain your decisions, and document outcomes.",
            "Final project repository or case study and a concise project summary.",
            "github_url or live_url or text_response",
        )
    return (
        f"Build practical evidence from the {title} stage of the {domain_name} path.",
        f"Apply the core ideas from {title} in a focused, reviewable piece of work.",
        "A working artifact, supporting notes, and a link or written response for review.",
        "github_url or live_url or text_response",
    )


def ensure_curriculum(db: Session) -> None:
    for domain_name, titles in CURRICULA.items():
        domain = db.scalar(select(Domain).where(Domain.name == domain_name))
        if not domain:
            domain = Domain(name=domain_name, description=f"A practical {domain_name} internship path.", duration=30, status="active")
            db.add(domain)
            db.flush()
        existing = {module.module_number: module for module in db.scalars(select(Module).where(Module.domain_id == domain.id)).all()}
        for number, title in enumerate(titles):
            module = existing.get(number)
            if not module:
                description, objectives, deliverables, prerequisite = _module_description(domain_name, title, number)
                module = Module(
                    domain_id=domain.id,
                    module_number=number,
                    title=title,
                    description=description,
                    learning_objectives=objectives,
                    estimated_duration=2 if number == 0 else 5,
                    prerequisites="None" if number == 0 else titles[number - 1],
                    resources=deliverables,
                    is_locked=number > 0,
                )
                db.add(module)
                db.flush()
            if not db.scalar(select(Task.id).where(Task.module_id == module.id)):
                description, objectives, deliverables, prerequisite = _module_description(domain_name, title, number)
                if number == 0:
                    task_title = "Post Your Internship Offer Letter on LinkedIn"
                    task_description = "Download your personalized offer letter, publish it on LinkedIn, tag InternXcel if configured, and submit the public post URL."
                    instructions = "Open your offer letter, publish it on LinkedIn, copy the post URL, and submit that URL here for review."
                    submission_type = "linkedin_url"
                    required_links = "linkedin_url"
                else:
                    task_title = f"Practical task: {title}"
                    task_description = description
                    instructions = f"{objectives} Submit: {deliverables}"
                    submission_type = "github_url"
                    required_links = prerequisite
                db.add(Task(module_id=module.id, title=task_title, description=task_description, instructions=instructions, submission_type=submission_type, required_links=required_links))
    db.commit()
