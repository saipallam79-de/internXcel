# Database design

Users own internships. Each internship references a domain. Domains contain ordered modules, modules contain tasks, and task submissions belong to both a task and student. Offer letters, certificates, and LOR documents reference the internship record so generated PDFs always use database-backed identity data.
