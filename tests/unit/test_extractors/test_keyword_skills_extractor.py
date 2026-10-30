from resume_parser.extractors.keyword_skills_extractor import KeywordSkillsExtractor


def test_finds_skills_in_order_with_canonical_names():
    text = "Built APIs with fastapi and postgres. Deployed on k8s via GitHub Actions. Python daily."
    assert KeywordSkillsExtractor().extract(text) == ["FastAPI", "PostgreSQL", "Kubernetes", "GitHub Actions", "Python"]


def test_symbols_and_short_terms():
    ex = KeywordSkillsExtractor()
    assert ex.extract("C++ and C# developer, CI/CD, Node.js") == ["C++", "C#", "CI/CD", "Node.js"]
    # 'go' / 'r' in normal prose must not count as languages
    assert ex.extract("ready to go, r&d team") == []
    assert "Go" in ex.extract("Services in Go and Rust")


def test_no_duplicates():
    assert KeywordSkillsExtractor().extract("AWS, aws, Amazon Web Services") == ["AWS"]
