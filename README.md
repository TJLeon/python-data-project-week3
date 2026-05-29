
---

# 🤖 Resume Helper Chatbot

A containerized, full-stack microservices chat application that uses a hybrid analytic pipeline (Deterministic Regex + Generative LLM via Gemini) to parse resumes out of plain text strings, track structural differences against a live job listings database, and calculate operational skill gaps.

---

## 📋 Project Overview

The goal of this project is to build and containerize a scalable full-stack application using a separate microservices design architecture. The frontend interface serves an interactive chat window where users can talk normally or attach PDF resumes. The backend processes requests across three distinct evaluation states (Casual chat, resume summarization, or deep-dive target market skill gap analyses) integrated natively with Google’s `gemini-3.1-flash-lite` model.

---

## 🛠️ Setup Instructions

### 1. Prerequisites

Ensure you have the following installed on your host computer:

* **Docker** (Desktop or Engine v20.10+)


* **Docker Compose** (v2.0+)


* *(Optional)* Python 3.14 + `uv` package manager (if executing scripts or debugging natively outside containers).

### 2. Environment Configuration

Create a `.env` file at the root of the project directory (at the same level as your `docker-compose.yml` file).

```env
# Google Gemini API Key authentication
GEMINI_API_KEY="api_key_here"

# Path to the SQLite job tracking database inside the container mount point
DATABASE_PATH="data/jobs_d3_eval.db"

# The target address where the frontend proxy will forward chat payloads.
# Toggle based on your current execution strategy:
BACKEND_URL="http://backend:8001"
```

> ⚠️ **Security Warning:** The `.env` file contains sensitive API secrets. It is ignored by Git. A `.env.example` template file is included in the repository tracking default non-sensitive properties.
>
>

---

## 🚀 Usage

### Running the Application

Make sure you are on the same directory as the **"docker-compose.yml"** file

Then start up the isolated multi-container stack from your terminal with:

```bash
docker compose up --build
```

Once the compilation wraps up and your services report healthy status, access the user interface via your local browser:
👉 **Frontend Link:** `http://localhost:8000`

### Expected Inputs and Outputs

1. **Scenario A (Casual Chat):** Type any plain-text message into the input field and hit enter. The UI displays your prompt and streams back context from the AI agent.
2. **Scenario B (Resume Context Summary):** Click the `+ PDF` button to attach a resume. Type a general inquiry (e.g., *"Summarize my experience"*). The browser extracts the layout text, pushes it to the backend, and renders a tailored response.
3. **Scenario C (Skill Gap Matrix calculation):** Attach your resume file and type a query containing trigger phrases like `"skill gap"`, `"gaps"`, or `"missing skills"`. The application bypasses basic chat logic, processes your skills against the jobs database using exact string parsing and AI extraction, and delivers a formatted table of missing items.

---

## 📡 API & Function Reference

1. Backend Endpoint: `POST /chat`

The main ingress gateway handling inbound user traffic.

* **Expected Request JSON Payload:**


```json
{
  "message": "What technical skills am I missing for the current job listings?",
  "pdf_text": "John Doe\nSoftware Engineer\nPython, Docker, JavaScript expert..."
}
```


* **Expected Response JSON Format:**


```json
{
  "reply": "📊 **Skill Gap Analysis Matrix**\n\nI scanned your resume text... ❌ **Identified Technical Gaps (2):** `kubernetes`, `golang`..."
}
```

2. Frontend Operations & Reverse Proxy Engine

* **`chatForm.addEventListener` (`frontend/src/templates/chat_page.html`):** JavaScript Function responsible for sending user input request including pdf files, and receiving server response to render chat history
* **`Frontend Backend Connection` (`Backend API endpoint`):** Frontend server container is connected via a User-Defined Docker Network Bridge to backend container, it's the essential communication tunnel for both services

### 3. Core Analytical Functions (`backend/find_skill_gaps.py`)

* **`fetch_db_skills(db_url: str) -> set`:** Establishes a database thread connection to the workspace SQLite database path. It reads `tech_stack` text records out of the tracking tables, explodes the comma-separated arrays into independent tokens, and transforms characters to lowercase inside an isolated python `set` to guarantee distinct entries.
* **`extract_resume_skills_with_llm(resume_text: str, model_name: str) -> set`:** Prepares a secure context frame using jailbreak sanitizers. It formats structured prompt instructions explicitly commanding Gemini to isolate technical assets as clean JSON string lists while stripping soft metrics. Includes an exponential backoff loop configuration to recover from API rate limits.

---

## 🔄 Data & System Architecture Flow

System Data Flow Model

```
[ Browser UI ] ---> (1) Submit Form File/Text ---> [ Frontend Proxy (Port 8000) ]
                                                               |
                                                               v (2) Routes to $BACKEND_URL
[ AI Response ] <--- (4) Output Reply String <--- [ Backend Container (Port 8001) ]
                                                       |               |
                                                       v               v
                                            [ SQLite Database ]   [ Gemini API ]
                                            (Read Job Skills)    (Extract / Chat)
```

1. **Submission:** The user uploads a PDF and types a request. JavaScript converts the PDF to string characters, packs it next to the message field in an unified object structure, and makes a local fetch call to `/chat`.
2. **Reverse Proxy:** The Frontend receives the JSON structure. It checks `os.getenv("BACKEND_URL")` to pass the payload across the virtual Docker bridge network boundary cleanly.
3. **Inference & Analytical Pipeline Decision:** The Backend intercepts the route. If a resume is provided alongside a skill-gap keyword, the backend retrieves records from the local SQLite path. It executes regex mapping concurrently against an LLM-guided extraction process and creates a union of results.
4. **Resolution:** The set difference identifies the missing elements. The markdown result is returned back through the frontend proxy to display inside the user's browser.

Design Assumptions & Constraints

* **Input expectations:** PDF processing happens directly inside the client machine's browser sandbox using `PDF.js`. It relies on standard structured text blocks being visible. Flat images or scanned document pages require OCR and are out of scope.

* **Database format:** The system assumes that job tech stacks are stored as flat, comma-separated lowercase strings in the `jobs` database table.
* **State Management:** The chat interface operates completely statelessly. Chat history is cleared on page refresh and is not persisted in a backend database.

---

## 🧪 Testing

1. Backend Endpoint Verification (Independent of UI)

You can test the backend's response processing logic directly using `curl` from your terminal:

```bash
curl -X POST http://localhost:8001/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Give me a skill gap report", "pdf_text": "Experienced engineer with skills in python and docker"}'
```

2. Frontend Proxy Integration Verification

1. Open `http://localhost:8000` in your web browser.

2. Open your browser Developer Tools Console (`F12`).
3. Upload a sample PDF resume file.

4. Type `"gaps"` and click Send. Verify that the browser logs show the network request returning a status `200 OK` and displaying the formatted Skill Gap Analysis dashboard window.

---

⚠️ Limitations & Boundary Awareness

* **Context Length & File Size Constraints:** Very large PDFs containing excessive boilerplate or structural decoration may generate high token usage or cause client-side browser slowdowns during client-side extraction.


* **Stateless Chat Memory:** The conversation history is maintained only in the active browser UI state. Since the backend microservice does not persist sessions to a database, refreshing the browser page completely resets the chat context.

* **Accuracy Trade-offs:** The regex matching engine uses rigid word boundaries (`\b`). While this prevents substring false positives (like matching "go" inside "good"), it may miss subtle skill variations or alternate spellings unless caught by the companion LLM extraction pass.

---

## 🧠 Architecture Reflection

Design Choices

* **Microservices Separation:** Splitting the system into an independent frontend container and backend container isolates their concerns. The frontend only manages client-side presentation, proxy routing, and asset extraction. The heavy-lifting processing dependencies (such as SQLite drivers, Pydantic validations, and Google GenAI clients) are isolated to the backend container, reducing the attack surface and keeping individual service resource usage low.


* **Containerization Framework:** Containerizing with Docker ensures cross-platform consistency ("works on my machine"). The build stages use an explicit `python:3.14-slim-bookworm` foundation alongside Astral's `uv` package manager. This results in fast, reproducible builds and smaller image sizes compared to traditional pip layer caching.

Trade-offs

* **Ease of Deployment vs. State Retention:** We prioritized zero-configuration deployment simplicity via `docker compose up --build` by embedding an active SQLite tracking database file directly into the local workspace volume. The trade-off is that this local file system structure is unsuited for multi-instance production environments, which would require an external database service like PostgreSQL.
* **Client-side PDF Extraction vs. Network Bandwidth:** Extracting text from PDFs inside the user's browser using `PDF.js` shifts the processing load to the client. This design minimizes backend processing bottlenecks and significantly reduces network payload sizes, as the frontend only transmits plain text strings over the network instead of heavy binary files.

Future Improvements

If given more development time, the following enhancements would be added to expand the system beyond its current boundaries:

1.
**Persistent Session Layer:** Integrate a Redis database tier inside Docker Compose to cache transaction histories across sessions, allowing users to return to previous conversations.


2. **Production-grade API Routing:** Replace the simple FastAPI `httpx` forwarder proxy with an Nginx reverse proxy layer configured to handle CORS configurations and automated request rate-limiting.
3. **Enhanced Vector Search (RAG):** Transition from a combination of strict regex matching and direct LLM calls to a Vector DB search system (using Chroma or Pgvector), enabling semantic matching between resumes and target job profiles.
