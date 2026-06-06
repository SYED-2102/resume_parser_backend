# AI-Powered Recruitment Agent & Resume Parser

## Overview
This project is an automated, AI-driven recruitment pipeline designed to process unstructured PDF resumes, compare them against target Job Descriptions (JDs), and output highly structured, actionable JSON analytics. 

Instead of relying purely on brittle keyword matching, this system employs a hybrid architecture: it uses deterministic NLP and Regex for precise data extraction, and delegates complex semantic reasoning (like skill gap analysis and candidate evaluation) to an LLM.

## System Architecture
The backend is built as a high-concurrency microservice capable of bulk-processing candidates.

* **Core Backend:** Python, FastAPI, Uvicorn
* **Data Ingestion (OCR/Parsing):** PyMuPDF (`fitz`) and `pypdfium2` for bypassing PDF encoding corruption and extracting visual bounding boxes.
* **Deterministic Logic:** Strict Regex for contact extraction and exact-match skill filtering.
* **LLM Engine / Reasoning Agent:** Llama 3.3 70B (via Groq API) prompted strictly to operate as a JSON-only API.

## Core Features
1. **Intelligent PDF Ingestion:** Handles complex, multi-page corporate PDFs and corrupted layouts using advanced file-handle management to prevent OS-level locks.
2. **Dynamic Cutoff Extraction:** Automatically extracts hard requirements (e.g., minimum GPA/CGPA thresholds) directly from the raw Job Description text.
3. **Skill Gap Analysis:** Calculates a deterministic match score by comparing the extracted candidate skills against the JD's missing technologies.
4. **Agentic Premium Insights:** Feeds the extracted data into an LLM agent to generate:
   * A dynamically calculated technical fit score.
   * Actionable suggestions for the candidate to fill specific skill gaps.
   * Highly targeted, technical interview questions tailored to the candidate's weaknesses.

## Data Flow
1. **POST `/analyze-bulk`:** Accepts a target JD and a batch of candidate resumes.
2. **Sanitization:** Raw bytes are stripped of non-ASCII characters and normalized.
3. **Evaluation:** Candidates failing the hard metrics (e.g., GPA < JD Minimum) are instantly rejected to save compute.
4. **Analysis:** Surviving candidates undergo full semantic analysis and LLM evaluation.
5. **Output:** Returns a comprehensive JSON payload ranking candidates by final score, complete with detailed dossiers and AI-generated interview questions.

## Local Setup
1. Clone the repository.
2. Create a virtual environment and run `pip install -r requirements.txt`.
3. Create a `.env` file in the root directory and add your Groq API key: `GROQ_API_KEY=your_key_here`.
4. Start the server: `uvicorn api2:app --reload`.
5. Access the interactive Swagger UI at `http://127.0.0.1:8000/docs` to test the endpoints.
