"""Generate the FICTIONAL resume fixtures in tests/test_data/ (PDF + DOCX).

These replace earlier fixtures that contained a real person's resume. Every person,
employer, school, email and phone number here is invented: emails use the reserved
example.com domain and phones use the fictional 555-01xx range.

    uv run python scripts/make_test_fixtures.py
"""

from pathlib import Path

import fitz  # PyMuPDF
from docx import Document

OUT = Path(__file__).resolve().parent.parent / "tests" / "test_data"

SE = {
    "name": "Jordan Blake", "title": "Senior Software Engineer",
    "contact": "jordan.blake@example.com | (555) 010-4410 | Lakeside (fictional)",
    "summary": "Backend engineer with 9 years building distributed systems and developer platforms.",
    "skills": "Python, Go, TypeScript, PostgreSQL, Redis, Kafka, Docker, Kubernetes, AWS, Terraform, GraphQL, CI/CD",
    "jobs": [("Staff Engineer, Bluefin Payments (fictional)", "2020 - Present",
              ["Led a move from a monolith to 14 Go services on Kubernetes.",
               "Cut p99 checkout latency from 900 ms to 220 ms with Redis caching."]),
             ("Software Engineer, Acme Logistics (fictional)", "2015 - 2020",
              ["Built Python and PostgreSQL APIs for route planning.",
               "Introduced GitHub Actions CI and trunk-based development."])],
    "education": "B.Eng. Software Engineering, Example Polytechnic (fictional), 2015",
}
SE2 = {**SE, "name": "Priya Natarajan", "contact": "priya.natarajan@example.com | (555) 010-7732 | Hillview (fictional)",
       "title": "Full-Stack Engineer",
       "skills": "JavaScript, TypeScript, React, Node.js, Python, Django, MySQL, Docker, Azure, Jest",
       "summary": "Full-stack engineer shipping React and Node.js products for six years."}
DS = {
    "name": "Casey Morgan", "title": "Data Scientist",
    "contact": "casey.morgan@example.com | (555) 010-3399 | Brookfield (fictional)",
    "summary": "Data scientist working on forecasting, experimentation and NLP.",
    "skills": "Python, R, SQL, pandas, scikit-learn, PyTorch, TensorFlow, XGBoost, Spark, Tableau, statistics, A/B testing",
    "jobs": [("Senior Data Scientist, Northstar Health (fictional)", "2021 - Present",
              ["Built demand-forecasting models that cut stock-outs 18%.",
               "Ran 30+ A/B tests with a shared experimentation library."]),
             ("Data Analyst, Riverbank Insurance (fictional)", "2017 - 2021",
              ["Automated claims reporting in SQL and Tableau."])],
    "education": "M.Sc. Statistics, Example State University (fictional), 2017",
}


def lines_for(p, repeat_jobs=1):
    out = [p["name"], p["title"], p["contact"], "", "SUMMARY", p["summary"], "", "SKILLS", p["skills"], "", "EXPERIENCE"]
    for i in range(repeat_jobs):
        for role, dates, bullets in p["jobs"]:
            out += [f"{role}  ({dates})" + (f"  [project set {i + 1}]" if repeat_jobs > 1 else "")]
            out += [f"- {b}" for b in bullets]
    out += ["", "EDUCATION", p["education"]]
    return out


def write_pdf(path, lines, lines_per_page=60):
    doc = fitz.open()
    for start in range(0, len(lines), lines_per_page):
        page = doc.new_page()
        y = 50
        for line in lines[start:start + lines_per_page]:
            page.insert_text((50, y), line, fontsize=10)
            y += 12
    doc.save(path)


def write_docx(path, lines, table=None, page_break_every=None):
    d = Document()
    for i, line in enumerate(lines):
        d.add_paragraph(line)
        if page_break_every and i and i % page_break_every == 0:
            d.add_page_break()
    if table:
        t = d.add_table(rows=0, cols=len(table[0]))
        for row in table:
            cells = t.add_row().cells
            for c, v in zip(cells, row):
                c.text = v
    d.save(path)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    se = lines_for(SE)
    write_pdf(OUT / "software_engineer_resume.pdf", se)
    ds = lines_for(DS)
    write_pdf(OUT / "data_scientist_resume.pdf", ds)
    write_docx(OUT / "data_scientist_resume.docx", ds)
    long = lines_for(DS, repeat_jobs=12)  # > 60 lines -> several PDF pages
    write_pdf(OUT / "multi_page_resume.pdf", long)
    write_docx(OUT / "multi_page_resume.docx", long, page_break_every=40)
    table = [["Skill", "Years", "Level"], ["Python", "9", "Expert"], ["Go", "5", "Advanced"], ["Kubernetes", "4", "Advanced"]]
    tl = lines_for(SE) + ["", "SKILLS MATRIX"] + ["  ".join(r) for r in table]
    write_pdf(OUT / "resume_with_tables.pdf", tl)
    write_docx(OUT / "resume_with_tables.docx", lines_for(SE), table=table)
    print("wrote fictional fixtures to", OUT)


if __name__ == "__main__":
    main()
