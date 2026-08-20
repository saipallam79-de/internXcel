# Project documentation

InternXcel follows a student journey: registration, domain enrollment, offer letter, sequential modules, task submission, review, completion, certificate, and LOR.

The frontend is deliberately framework-free HTML/CSS/JavaScript so it can deploy to Netlify or Vercel as static assets. The backend is a FastAPI service with SQLAlchemy models and JWT-ready authentication.

## Completion rules

A certificate becomes available only when all domain modules, required tasks, and the final project have been approved.
