# HazardSAFE: Agentic Quality Infrastructure for HazMat Safety

**Google Agentic AI Hackathon Submission**

**HazardSAFE** is an agentic framework designed to automate the compliance, tracking, and certification of hazardous material (HazMat) transport. It adapts the "Agentic Quality Infrastructure" (AQI) concept to the high-stakes domain of HazMat safety.

## 🏆 Kaggle Submission
The core demonstration of HazardSAFE is available in the submission notebook:
*   **[submission/hazard_safe_demo.ipynb](submission/hazard_safe_demo.ipynb)**: A comprehensive walkthrough of the end-to-end workflow, including RAG compliance, HITL approval, and Verifiable Credential issuance.

## 🚀 Key Features

*   **Compliance Agent**: Uses RAG (Retrieval-Augmented Generation) to check transport scenarios against PDF regulations.
*   **Code-as-Policy**: Generates and executes sandboxed Python code to validate safety rules deterministically.
*   **HITL Web UI**: A modern Streamlit dashboard for human reviewers to approve/reject high-risk workflows.
*   **Provenance Agent**: Logs every decision and event to an immutable ledger (Firestore).
*   **Verifiable Credentials**: Issues W3C-compliant credentials for approved scenarios.
*   **Security**: Implements JWS (JSON Web Signature) for all inter-agent communication.

## 📂 Project Structure

*   `submission/`: **Kaggle submission notebook**.
*   `src/web/`: **Streamlit Web UI** application.
*   `src/agents/`: Core agents (Compliance, Provenance, Report).
*   `src/workflow/`: Workflow state management and timeout handling.
*   `src/eval/`: Evaluation metrics and robustness tests.
*   `data/`: Regulations PDFs and mock databases.

## 🛠️ Setup & Installation

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Set up environment variables:
    *   Copy `.env.example` to `.env`
    *   Add your `GOOGLE_API_KEY`

## 🏃‍♂️ Running Demos

### 1. Web UI (Recommended)
Launch the modern Streamlit dashboard to manage workflows interactively.
```bash
./scripts/start_web_ui.sh
```
Open **http://localhost:5000** in your browser.

### 2. End-to-End Pipeline Demo
Simulates the full flow: Compliance Check -> Provenance Log -> VC Issuance.
```bash
python3 notebook.py
```

### 3. Evaluation Metrics
Run batch tests to measure accuracy and latency.
```bash
python3 src/eval/evaluate_metrics.py
```

## 📚 Documentation
*   [Web UI Guide](docs/WEB_UI_GUIDE.md)
*   [Project Description](project_description.md)
*   [Implementation Plan](spec/implementation_plan.md)

