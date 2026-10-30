"""Offline skills extractor: dictionary matching, no API key needed.

Used automatically when OPENAI_API_KEY is not configured so the framework (and the
local web app) still works. It only finds skills from a fixed vocabulary, so recall is
lower than the GPT extractor, and results are labelled ``keyword`` in the API.
"""

import re
from typing import List

from resume_parser.config import settings
from resume_parser.extractors.base import FieldExtractor

# Canonical spelling -> extra aliases (matched case-insensitively on word boundaries)
VOCABULARY: dict[str, list[str]] = {
    # languages
    "Python": [], "Java": [], "JavaScript": ["JS"], "TypeScript": ["TS"], "Go": ["Golang"],
    "Rust": [], "C++": [], "C#": [], "Scala": [], "Kotlin": [], "Swift": [], "Ruby": [],
    "PHP": [], "R": [], "SQL": [], "Bash": ["Shell scripting"],
    # frameworks / libs
    "React": ["React.js", "ReactJS"], "Angular": [], "Vue": ["Vue.js"], "Node.js": ["NodeJS"],
    "Django": [], "Flask": [], "FastAPI": [], "Spring Boot": ["Spring"], "Express": [],
    "Next.js": [], "pandas": [], "NumPy": [], "scikit-learn": ["sklearn"], "TensorFlow": [],
    "PyTorch": [], "Keras": [], "Spark": ["PySpark", "Apache Spark"], "Airflow": ["Apache Airflow"],
    "dbt": [], "Kafka": ["Apache Kafka"], "LangChain": [], "Hugging Face": ["HuggingFace"],
    # data / ml
    "Machine Learning": ["ML"], "Deep Learning": [], "NLP": ["Natural Language Processing"],
    "Computer Vision": [], "Data Analysis": [], "Data Visualization": [], "Statistics": [],
    "A/B Testing": [], "Tableau": [], "Power BI": [], "Excel": [], "LLMs": ["LLM", "Large Language Models"],
    # cloud / infra
    "AWS": ["Amazon Web Services"], "Azure": ["Microsoft Azure"], "GCP": ["Google Cloud"],
    "Docker": [], "Kubernetes": ["K8s"], "Terraform": [], "Ansible": [], "Linux": [],
    "CI/CD": [], "GitHub Actions": [], "Jenkins": [], "Git": [], "Microservices": [],
    "REST APIs": ["REST", "RESTful"], "GraphQL": [],
    # databases
    "PostgreSQL": ["Postgres"], "MySQL": [], "MongoDB": [], "Redis": [], "Snowflake": [],
    "BigQuery": [], "Elasticsearch": [], "DynamoDB": [], "Cassandra": [],
    # practices / soft
    "Agile": [], "Scrum": [], "TDD": ["Test-Driven Development"], "Project Management": [],
    "Team Leadership": ["Leadership"], "Mentoring": [], "Communication": [],
    "Stakeholder Management": [], "Product Management": [], "UX Design": ["UX"], "Figma": [],
}


def _pattern(term: str) -> re.Pattern:
    # word boundaries that also work for terms like C++, C#, Node.js, CI/CD
    return re.compile(r"(?<![\w+#])" + re.escape(term) + r"(?![\w+#])", re.IGNORECASE)


_COMPILED = [(canon, [_pattern(t) for t in [canon, *aliases]]) for canon, aliases in VOCABULARY.items()]
# Very short / ambiguous names are only accepted when written exactly (case-sensitive)
_CASE_SENSITIVE = {"Go", "R", "TS", "JS", "ML", "UX", "Spring", "Express", "REST"}


class KeywordSkillsExtractor(FieldExtractor):
    """Find skills from a fixed vocabulary. Deterministic, offline, no LLM."""

    mode = "keyword"

    def extract(self, text: str) -> List[str]:
        self._validate_text_input(text)
        found: list[tuple[int, str]] = []
        for canon, patterns in _COMPILED:
            terms = [canon, *VOCABULARY[canon]]
            for term, pat in zip(terms, patterns):
                if term in _CASE_SENSITIVE:
                    m = re.search(r"(?<![\w+#])" + re.escape(term) + r"(?![\w+#])", text)
                else:
                    m = pat.search(text)
                if m:
                    found.append((m.start(), canon))
                    break
        found.sort()
        return [canon for _, canon in found][: settings.max_skills_returned]
