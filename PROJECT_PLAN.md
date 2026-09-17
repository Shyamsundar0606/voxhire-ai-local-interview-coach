# VoxHire AI: Local Voice Interview Coach

## Project Overview

VoxHire AI is a privacy-focused interview practice application that runs locally. A candidate uploads a resume and provides a job description. The system extracts relevant text, creates a personalized interview plan, conducts a voice-based interview, evaluates each answer using validated evidence, and produces a detailed final report.

The application is designed for a single local user during the MVP. Uploaded documents and recorded audio remain on the local machine. The LLM assists with extraction, question generation, transcription cleanup, and qualitative feedback, but it never calculates final scores. All score calculations are performed deterministically by Python using explicit weighted criteria.

## MVP Scope

### Included

- Local upload of PDF and DOCX resumes.
- Text input for a job description, with optional local persistence.
- File type, filename, and size validation.
- Resume text extraction with `pypdf` and `python-docx`.
- Ollama integration using a configurable local Qwen3 model.
- Structured JSON LLM responses validated by Pydantic.
- Personalized question plan containing behavioral, technical, and resume/job-specific questions.
- Browser microphone recording through the Web Media API.
- Local audio upload to FastAPI.
- Speech-to-text with locally installed `faster-whisper`.
- Text-to-speech with locally installed Piper for interviewer prompts.
- A session flow that presents one question at a time and records answers.
- Deterministic answer scoring based on explicit weighted dimensions.
- LLM-generated evidence and feedback, separated from numeric scoring.
- Final report with summary, per-question results, strengths, gaps, and recommendations.
- PostgreSQL persistence through SQLAlchemy.
- Docker Compose for PostgreSQL, backend, frontend, and optional Ollama connectivity.
- Automated backend tests with pytest and frontend workflow tests with Playwright.

### Explicitly Out of Scope for MVP

- Cloud AI, cloud speech services, paid APIs, or telemetry.
- Multi-user authentication, organizations, billing, or remote deployment.
- Live streaming transcription or real-time conversational interruption.
- Webcam/video analysis, facial analysis, emotion detection, or biometric inference.
- Automatic job-board ingestion.
- Resume rewriting or job application submission.
- Mobile-native applications.
- Training a custom speech or language model.
- LLM-controlled final scores or unbounded autonomous interview behavior.

## Architecture

### Components

1. **Next.js frontend**
   - TypeScript and Tailwind CSS.
   - Provides upload, setup, interview, progress, and report views.
   - Records microphone audio locally in the browser and sends completed answer files to FastAPI.
   - Does not access PostgreSQL, uploaded storage, Ollama, Whisper, or Piper directly.

2. **FastAPI backend**
   - Owns API contracts, validation, orchestration, file storage, database access, and background-capable processing boundaries.
   - Extracts resume text, invokes local AI services, persists session state, and calculates scores.
   - Uses Pydantic request and response models at every external boundary.

3. **PostgreSQL**
   - Stores structured metadata, extracted text references or controlled text fields, question plans, transcripts, evaluation evidence, score breakdowns, and report data.
   - Does not serve files publicly.

4. **Ollama with Qwen3**
   - Runs on the local host or as a separately managed local service.
   - Receives narrowly scoped prompts and returns JSON-only responses.
   - The backend validates the response against the appropriate Pydantic schema before using it.

5. **faster-whisper**
   - Runs inside the backend worker/runtime or a dedicated local processing service.
   - Converts uploaded answer audio into a transcript.

6. **Piper**
   - Runs locally and converts interviewer question text into an audio file.
   - The backend returns a controlled audio response to the frontend.

7. **Private file storage**
   - Stores resumes, answer recordings, generated speech, and temporary processing artifacts outside the Next.js `public` directory.
   - Uses generated internal identifiers rather than user-provided filenames for storage paths.

### Request and Data Flow

1. The browser sends a resume and job description to FastAPI over localhost.
2. FastAPI validates the filename, extension, MIME signature where applicable, and size before storing the file privately.
3. The backend extracts resume text, persists the source metadata, and sends a bounded resume/job context to Ollama.
4. Ollama returns structured question-plan JSON. Pydantic validates it; invalid or incomplete output is rejected and logged without exposing raw model output to the client.
5. FastAPI saves the plan and returns a session identifier and question metadata to Next.js.
6. For each question, FastAPI optionally sends the text to Piper and returns generated audio metadata. The browser plays it.
7. The browser records an answer, uploads the audio to FastAPI, and receives a processing status.
8. FastAPI transcribes the audio with faster-whisper, stores the transcript, and asks Ollama only for structured qualitative evidence and feedback.
9. Python applies deterministic rubric rules and weights to the validated evidence and transcript-derived facts. The LLM cannot set or override numeric scores.
10. After all questions are complete, FastAPI aggregates the stored score components and returns the final report to Next.js.

### Configuration

All service URLs, model names, storage roots, limits, database connection settings, audio formats, and feature flags must be environment-driven. A committed `.env.example` documents safe defaults without secrets. The backend should fail clearly at startup when required configuration is invalid.

## Proposed Folder Structure

```text
VoxHire AI Local Voice Interview Coach/
|-- PROJECT_PLAN.md
|-- README.md
|-- .env.example
|-- .gitignore
|-- docker-compose.yml
|-- backend/
|   |-- pyproject.toml
|   |-- app/
|   |   |-- main.py
|   |   |-- core/                 # settings, logging, application errors
|   |   |-- api/                  # routers and dependency wiring
|   |   |-- schemas/              # Pydantic request, response, and AI schemas
|   |   |-- models/               # SQLAlchemy ORM models
|   |   |-- db/                   # engine, session, migrations bootstrap
|   |   |-- services/             # orchestration use cases
|   |   |-- integrations/         # Ollama, Piper, faster-whisper adapters
|   |   |-- extraction/            # PDF and DOCX extraction
|   |   |-- scoring/               # deterministic rubric and aggregation
|   |   |-- storage/               # private file storage and validation
|   |   |-- workers/               # bounded processing jobs if needed
|   |-- tests/
|       |-- unit/
|       |-- integration/
|       |-- fixtures/
|-- frontend/
|   |-- package.json
|   |-- next.config.ts
|   |-- tsconfig.json
|   |-- app/
|   |   |-- page.tsx
|   |   |-- setup/page.tsx
|   |   |-- interview/[sessionId]/page.tsx
|   |   |-- report/[sessionId]/page.tsx
|   |-- components/
|   |-- lib/                      # typed API client and browser recording helpers
|   |-- types/
|   |-- tests/
|       |-- e2e/
|-- storage/
|   |-- .gitkeep                  # runtime data only; never commit uploaded content
|-- infra/
|   |-- postgres/init/
|-- docs/
|   |-- api-contracts.md
|   |-- scoring-rubric.md
```

The exact runtime storage directory may be configured outside the repository. The `storage/` entry is only a development placeholder and must be protected by `.gitignore`.

## Database Entities

### `candidates`

MVP-local candidate profile. Stores an internal ID and timestamps. Authentication is not included, so this entity should remain minimal and should not collect unnecessary personal data.

### `resumes`

Stores candidate ID, original display filename, generated storage key, detected content type, byte size, checksum, extraction status, extracted text or a private text reference, and timestamps.

### `job_descriptions`

Stores the job description text, optional title/company labels supplied by the user, normalized text metadata, and timestamps.

### `interview_sessions`

Stores candidate, resume, and job-description references, lifecycle status, selected model metadata, rubric version, current question position, and timestamps.

### `interview_questions`

Stores session reference, order, category, prompt text, expected competencies, source references such as resume or job-description sections, and generation metadata.

### `answers`

Stores question reference, private audio storage key and checksum when retained, duration and content type, transcription status, transcript text, transcription metadata, and timestamps.

### `evaluations`

Stores answer reference, validated qualitative evidence, rubric dimension values calculated by Python, weighted score, feedback, rubric version, and timestamps. The schema should make the numeric score auditable from stored components.

### `reports`

Stores session reference, aggregate score components, final deterministic score, strengths, improvement areas, recommendations, generation/version metadata, and timestamps. Report data should be reproducible from the session's evaluations and rubric version.

Relationships should use foreign keys and cascading rules deliberately. Audio and document files are not stored as PostgreSQL blobs in the MVP; the database stores private storage keys and integrity metadata.

## API Groups

All endpoints are versioned under `/api/v1`. Responses use stable Pydantic schemas and consistent error objects.

### Health and Configuration

- `GET /health` for process health.
- `GET /api/v1/ready` for database and required local dependency readiness without leaking credentials or host details.

### Candidate and Intake

- `POST /api/v1/candidates` creates a local candidate context.
- `POST /api/v1/resumes` uploads and validates a resume.
- `POST /api/v1/job-descriptions` stores a job description.
- `GET /api/v1/resumes/{resume_id}` returns safe metadata and extraction status.

### Session and Question Plan

- `POST /api/v1/interview-sessions` creates a session and generates a validated question plan.
- `GET /api/v1/interview-sessions/{session_id}` returns session progress.
- `GET /api/v1/interview-sessions/{session_id}/questions` returns ordered questions.
- `POST /api/v1/interview-sessions/{session_id}/start` starts or resumes an interview.

### Voice Interview

- `POST /api/v1/questions/{question_id}/speech` generates or retrieves Piper audio for a question.
- `POST /api/v1/questions/{question_id}/answers` uploads one recorded answer.
- `GET /api/v1/answers/{answer_id}/status` returns transcription and evaluation status.
- `GET /api/v1/audio/{audio_id}` streams only authorized session-owned generated or recorded audio through a controlled backend response.

### Evaluation and Reports

- `POST /api/v1/interview-sessions/{session_id}/complete` closes the session after required answers are processed.
- `GET /api/v1/interview-sessions/{session_id}/evaluations` returns per-answer score details.
- `GET /api/v1/interview-sessions/{session_id}/report` returns the final report.

The initial implementation may process requests synchronously for short local operations. Audio transcription and report generation should use explicit status states so they can later move to a local worker without changing the frontend contract.

## Ten Implementation Milestones

### Milestone 1: Repository and Environment Foundation

Create the repository layout, environment configuration contract, Docker Compose skeleton, dependency manifests, formatting/linting/test configuration, and local development documentation.

**Definition of done:** The documented commands work on Windows with Docker Desktop and the selected Python and Node versions; configuration loads from environment variables; no runtime secrets or user files are tracked.

### Milestone 2: Backend Core and Database Layer

Implement FastAPI startup, settings, structured errors, health/readiness checks, SQLAlchemy engine/session wiring, initial models, and migration strategy.

**Definition of done:** The backend starts locally, PostgreSQL connectivity is verified, schema creation/migration is repeatable, and unit tests cover settings validation and database session behavior.

### Milestone 3: Secure Intake and Text Extraction

Implement resume and job-description intake, file validation, private storage, checksum generation, PDF/DOCX extraction, and extraction status handling.

**Definition of done:** Valid PDF/DOCX files are accepted, malformed or oversized files and unsafe names are rejected, extracted text is bounded and persisted safely, and tests cover file validation and both supported formats.

### Milestone 4: Ollama Structured AI Integration

Implement the Ollama adapter, prompt templates, timeout/error handling, JSON parsing, Pydantic schemas, and bounded context construction for question generation.

**Definition of done:** A local Qwen3 model can generate a validated question plan; malformed, incomplete, refusal, and timeout responses fail safely; no raw model output is trusted as application data.

### Milestone 5: Session and Question Planning APIs

Implement session creation, question persistence, ordering, lifecycle states, API versioning, and frontend-ready response contracts.

**Definition of done:** A user can create a session from validated intake data and retrieve a stable, ordered plan with categories, competencies, and source references; API tests cover normal and failure paths.

### Milestone 6: Local Speech Pipeline

Implement browser recording upload, audio validation, Piper question audio generation, faster-whisper transcription, private audio storage, and explicit processing statuses.

**Definition of done:** A supported local audio recording can be accepted, transcribed, and linked to one question; Piper can produce playable question audio; missing binaries/models and unsupported audio fail with actionable local errors.

### Milestone 7: Deterministic Evaluation and Scoring

Implement the versioned scoring rubric, evidence schema, Python score calculation, weighting, completeness rules, and evaluation persistence.

**Definition of done:** Identical validated inputs always produce identical scores; score totals can be recomputed from stored components; LLM responses contain qualitative evidence only and cannot supply or override numeric scores; boundary and weighting tests pass.

### Milestone 8: Frontend Interview Workflow

Implement the Next.js setup, upload, session progress, question playback, recording controls, answer submission, retry/error states, and accessible responsive layout.

**Definition of done:** A browser can complete the setup and interview workflow against the local backend, shows processing states accurately, prevents invalid transitions, and remains usable on desktop and narrow viewport sizes.

### Milestone 9: Final Report Experience

Implement report aggregation, report API, score visualizations with Recharts, per-question evidence, strengths, gaps, recommendations, and print-friendly presentation.

**Definition of done:** A completed session displays an auditable report whose totals match backend calculations, handles incomplete/failed answers clearly, and contains no sensitive data in public static assets or client logs.

### Milestone 10: Hardening, Documentation, and Release Verification

Complete integration tests, Playwright workflows, Docker Compose verification, resource limits, logging review, data-retention behavior, Windows setup documentation, and a manual privacy/security review.

**Definition of done:** The documented clean-machine setup works on Windows, backend and frontend test suites pass, core failure modes are covered, containers restart predictably, and the MVP acceptance checklist is signed off without adding post-MVP features.

## Testing Strategy

### Backend Unit Tests

- Pydantic validation for API and AI schemas.
- Filename, extension, MIME, size, checksum, and path-safety validation.
- PDF/DOCX extraction using fixtures and malformed documents.
- Prompt context truncation and deterministic normalization.
- Ollama JSON parsing and invalid-response handling with mocked HTTP responses.
- Piper and faster-whisper adapters with mocked subprocess/model boundaries.
- Rubric dimension scoring, weights, rounding, missing evidence, and aggregate calculations.
- Session state transition rules.

### Backend Integration Tests

- FastAPI endpoints using a test database.
- Upload-to-extraction flow.
- Session creation and question persistence.
- Answer processing with mocked local AI adapters.
- Report reproducibility from persisted evaluation components.

### Frontend Tests

- Playwright setup flow from upload through question plan.
- Microphone permission-denied and recording-failure states.
- Answer submission and processing states.
- Resume/reload behavior for an in-progress session.
- Completed report rendering and score consistency.
- Desktop and mobile-width smoke coverage.

### Manual and Operational Checks

- Run with Ollama unavailable, Piper unavailable, and Whisper unavailable.
- Verify no uploaded file is reachable from the frontend static directory.
- Verify logs redact document text, transcripts, environment secrets, and raw audio paths where appropriate.
- Verify Docker Compose behavior on Windows Docker Desktop.

## Security and Privacy Considerations

- Keep all service endpoints local by default and document any host binding explicitly.
- Do not send resume, job description, audio, or transcript data to external services.
- Store uploads outside `frontend/public` and never construct paths directly from user filenames.
- Generate opaque storage keys and validate path containment before every file operation.
- Enforce configurable maximum sizes for documents, audio, extracted text, and request bodies.
- Validate extension, detected content type, and file signatures where practical; do not trust a browser MIME header.
- Sanitize display filenames and store them separately from internal paths.
- Use allowlisted CORS origins, restrictive response headers, and controlled audio download routes.
- Avoid logging raw resumes, transcripts, prompts containing personal data, model output, tokens, or secrets.
- Treat Ollama output as untrusted input. Parse JSON strictly, validate Pydantic schemas, reject extra or unsafe fields where appropriate, and bound list lengths and text lengths.
- Use prompt instructions and context delimiters to reduce resume/job-description prompt injection risk, but rely on schema validation and deterministic business rules rather than prompt compliance alone.
- Never let the LLM provide final scores, weights, pass/fail decisions, or rubric configuration.
- Pin or constrain dependency versions and scan dependencies during release verification.
- Define retention and deletion behavior for resumes, recordings, transcripts, and reports before production-like use.
- Keep database credentials in environment variables and use separate development credentials.
- Do not expose PostgreSQL or Ollama ports beyond the local development boundary unless explicitly required.

## Prerequisites to Install

### Required

- Windows 10 or 11 with Docker Desktop and WSL2 integration enabled.
- Git, if the project will later be versioned.
- Python 3.12 with a working virtual environment support.
- Node.js LTS and npm.
- A modern Chromium-based browser with microphone permissions available.
- Ollama for Windows, with a compatible Qwen3 model pulled locally and enough disk/RAM for the chosen model.

### Speech Runtime

- `faster-whisper` Python dependencies and a compatible CPU or optional local GPU runtime.
- Piper executable and a locally downloaded Piper voice model. The exact model path must be configured through environment variables.
- FFmpeg only if the selected browser audio formats require conversion in the backend. Prefer a tested, minimal conversion path rather than assuming every browser codec is available.

### Developer Tools

- PostgreSQL is supplied by Docker Compose for the default workflow; a native PostgreSQL install is not required.
- Optional: VS Code extensions for Python, Pylance, ESLint, Tailwind CSS, Docker, and Playwright.
- Optional: `uv` or another Python dependency manager, provided the documented workflow remains reproducible with standard Python tooling.

Hardware requirements depend heavily on the selected Qwen3 and Whisper models. The plan should begin with small local models and expose model paths and compute settings through configuration.

## Technical Risks and Fallbacks

| Risk | Impact | Fallback |
|---|---|---|
| Qwen3 output is not valid JSON | Question/evaluation flow fails | Strict schema validation, bounded retries with a repair prompt, then a clear local error; keep a deterministic question-template fallback for session creation if approved by the rubric |
| Model quality or latency is poor on Windows hardware | Slow or weak personalization | Use smaller quantized local models, reduce context size, and preserve a deterministic baseline question set |
| faster-whisper lacks suitable CPU/GPU performance | Long processing times | Make model size configurable, use CPU-safe defaults, expose processing status, and allow transcript text entry as a development-only fallback if explicitly enabled |
| Piper executable/model setup differs across Windows machines | Question audio unavailable | Configure executable and voice paths, provide a readiness check, and allow text-only interview mode without changing the interview data model |
| Browser audio codec is unsupported by the processing runtime | Answer upload fails | Allow a documented set of MIME types, use FFmpeg conversion when configured, and return a precise unsupported-format error |
| Docker-to-host Ollama networking is inconsistent | Backend cannot reach Ollama | Support a configurable Ollama base URL, document Windows host routing, and allow running the backend outside Docker while PostgreSQL remains containerized |
| Large files or long prompts exhaust memory | Service instability | Enforce request/file/text limits, stream uploads where practical, truncate context by explicit rules, and record processing failures |
| Prompt injection in resume or job description | Unsafe or irrelevant model output | Delimit untrusted text, request structured output, validate aggressively, and keep all authorization, scoring, and state decisions in Python |
| Partial session failure leaves inconsistent state | Incorrect report | Use explicit state transitions, idempotency keys or duplicate detection for answer submission, and only finalize reports from completed evaluations |
| Privacy data remains after a session | User data exposure | Provide controlled deletion/retention behavior, keep storage private, and include cleanup verification in the hardening milestone |

## Definition of Done for the MVP

The MVP is complete when a local Windows user can start the documented services, upload a supported resume, enter a job description, generate a validated personalized question plan through local Ollama, hear questions through Piper or use the documented text-only fallback, record and transcribe answers with faster-whisper, view deterministic weighted scores with qualitative evidence, and read a final report. The full flow must operate without paid or cloud APIs, persist required metadata in PostgreSQL, keep uploaded data outside public frontend directories, pass the focused backend and Playwright tests, and satisfy the security, failure-mode, and documentation checks above.

Implementation must stop at each milestone until it is reviewed. No milestone should automatically begin the next one.