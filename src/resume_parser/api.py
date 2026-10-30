"""FastAPI service: upload a PDF/DOCX resume and get structured fields back.

    uvicorn resume_parser.api:app --reload

Skills come from GPT (``skills_mode: "llm"``) when OPENAI_API_KEY is set, otherwise from
the offline keyword extractor (``skills_mode: "keyword"``). The response always says which.
"""

import tempfile
import time
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from resume_parser.config import settings
from resume_parser.core.framework import ResumeParserFramework
from resume_parser.exceptions import FileParsingError, ResumeParserError, ValidationError

SAMPLES_DIR = Path(__file__).resolve().parents[2] / "samples"
MAX_BYTES = 10 * 1024 * 1024

app = FastAPI(title="Resume Parser API", version="1.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@lru_cache(maxsize=1)
def framework() -> ResumeParserFramework:
    return ResumeParserFramework()


def skills_mode() -> str:
    return getattr(framework().resume_extractor.skills_extractor, "mode", "custom")


def _parse_path(path: Path, filename: str) -> dict:
    fw = framework()
    parser_cls = fw.PARSER_REGISTRY.get(path.suffix.lower())
    started = time.perf_counter()
    try:
        data = fw.parse_resume(path)
        text = parser_cls().parse(path) if parser_cls else ""
    except (ValidationError, FileParsingError) as e:
        raise HTTPException(422, str(e).replace(f"'{path}'", f"'{filename}'").replace(str(path), filename)) from e
    except ResumeParserError as e:
        raise HTTPException(500, str(e).replace(str(path), filename)) from e
    return {
        "filename": filename,
        **data.to_dict(),
        "skills_mode": skills_mode(),
        "parser": parser_cls.__name__ if parser_cls else None,
        "characters": len(text),
        "text_preview": text[:1200],
        "elapsed_ms": round((time.perf_counter() - started) * 1000),
    }


@app.get("/health")
def health():
    return {"status": "ok", "skills_mode": skills_mode(), "llm_enabled": settings.llm_enabled,
            "model": settings.openai_model if settings.llm_enabled else None,
            "formats": sorted(framework().PARSER_REGISTRY)}


@app.get("/api/samples")
def samples():
    return [{"name": p.name, "size": p.stat().st_size}
            for p in sorted(SAMPLES_DIR.glob("*")) if p.suffix.lower() in framework().PARSER_REGISTRY]


@app.post("/api/samples/{name}/parse")
def parse_sample(name: str):
    path = (SAMPLES_DIR / name).resolve()
    if path.parent != SAMPLES_DIR or not path.is_file():
        raise HTTPException(404, "sample not found")
    return _parse_path(path, name)


@app.post("/api/parse")
async def parse_upload(file: UploadFile):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in framework().PARSER_REGISTRY:
        raise HTTPException(415, f"Unsupported file type '{suffix or '?'}'. Use .pdf or .docx")
    body = await file.read()
    if len(body) > MAX_BYTES:
        raise HTTPException(413, "File larger than 10 MB")
    # Uploaded files are parsed from a temp file and never kept.
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / f"upload{suffix}"
        path.write_bytes(body)
        return _parse_path(path, file.filename or path.name)
