# Business case: Resume Parser

**Name, email and skills as JSON, from any PDF or Word resume.**

## Who buys this

The buyer is the operations lead at a recruiting agency or the HR-tech lead at an employer with high application volume. The users are recruiters who need clean candidate records, and developers integrating with an applicant-tracking system.

## The problem and what it costs

Resumes arrive in many layouts and formats, and someone has to copy the basics into the tracking system. Parsing those fields is routine, but tools that *rank* or *screen* candidates are regulated in some places. New York City's Local Law 144, for example, requires a bias audit before an employer uses an automated employment decision tool ([NYC DCWP](https://www.nyc.gov/site/dca/about/automated-employment-decision-tools.page)). This repo extracts fields and makes no hiring decision.

## How the repo solves it

| Need | What in the repo does it |
|---|---|
| Read the file | `PDFParser` (PyMuPDF) and `WordParser` (python-docx), registered by file extension |
| Extract each field | `NameExtractor` (header rules plus spaCy NER), `EmailExtractor` (regex), and `SkillsExtractor` (GPT in JSON mode) or an offline keyword fallback |
| Fail gracefully | Each extractor fails independently, so a broken skills call still returns name and email |
| API and UI | `POST /api/parse` in FastAPI (10 MB limit, temp files deleted after) and a React upload page |

## Use-case scenarios

All of these organisations are fictional.

1. **A technical recruiting agency** turns each emailed resume into a candidate record without retyping.
2. **A university careers office** builds a searchable skills index of student resumes, with consent.
3. **An HR-tech start-up** uses the parser framework as the intake step of its own product.

## ROI: a worked model (illustrative)

These figures are **illustrative assumptions** unless a source is linked.

| Input | Value | Basis |
|---|---|---|
| Resumes a month | 1,500 | Assumption |
| Minutes to key in name, email and skills by hand | 3 | Assumption |
| Share needing no correction after parsing | 70% | Assumption |
| Coordinator loaded cost an hour | US$40 | Assumption |

Saving: 1,500 × 3 min × 70% ≈ 52 hours a month, about **US$25,000 a year**, minus LLM costs for the skills field.

## Path to production

1. Connect to the applicant-tracking system's API.
2. Measure field accuracy on a labelled sample of your own resumes.
3. Set retention and deletion rules for uploaded files and parsed data.
4. If you ever add scoring or ranking, get legal review first (see Local Law 144).

## Risks and limits

- Resumes contain personal data, and sending them to an LLM API needs a data-processing agreement.
- Skills extraction can miss or invent skills, so recruiters should see the source text.
- Commercial parsers already exist, so the case for building is about control and cost, not novelty.

**Case strength:** **Moderate.** A real, everyday need with a clean design, in a market that already has many products.

## Sources

- NYC Department of Consumer and Worker Protection, Automated Employment Decision Tools: https://www.nyc.gov/site/dca/about/automated-employment-decision-tools.page
