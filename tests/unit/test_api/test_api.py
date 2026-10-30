"""API tests against the synthetic samples. Runs offline (keyword skills mode)."""
import pytest
from fastapi.testclient import TestClient

from resume_parser import api


@pytest.fixture(scope="module")
def client():
    return TestClient(api.app)


def test_health_reports_mode(client):
    h = client.get("/health").json()
    assert h["status"] == "ok"
    assert h["skills_mode"] in {"llm", "keyword"}
    assert h["formats"] == [".docx", ".pdf"]


def test_samples_are_listed(client):
    names = {s["name"] for s in client.get("/api/samples").json()}
    assert "alex_rivera_data_engineer.pdf" in names and "morgan_lee_product_designer.docx" in names


@pytest.mark.parametrize("ext", ["pdf", "docx"])
def test_parse_sample(client, ext):
    r = client.post(f"/api/samples/alex_rivera_data_engineer.{ext}/parse")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Alex Rivera"
    assert body["email"] == "alex.rivera@example.com"
    if body["skills_mode"] == "keyword":
        assert {"Python", "Spark", "Kafka", "Docker"} <= set(body["skills"])


def test_upload(client):
    data = (api.SAMPLES_DIR / "samira_haddad_ml_engineer.docx").read_bytes()
    r = client.post("/api/parse", files={"file": ("cv.docx", data)})
    assert r.status_code == 200 and r.json()["email"] == "samira.haddad@example.com"


def test_upload_rejects_bad_type_and_corrupt(client):
    assert client.post("/api/parse", files={"file": ("cv.txt", b"x")}).status_code == 415
    assert client.post("/api/parse", files={"file": ("cv.pdf", b"not a pdf")}).status_code == 422


def test_sample_path_traversal_blocked(client):
    assert client.post("/api/samples/..%2Fpyproject.toml/parse").status_code == 404
