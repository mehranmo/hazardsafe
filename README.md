# HazardSAFE: Agentic Quality Infrastructure for HazMat Safety

**HazardSAFE** is an agentic framework designed to automate the compliance, tracking, and certification of hazardous material (HazMat) transport. It adapts the "Agentic Quality Infrastructure" (AQI) concept to the high-stakes domain of HazMat safety.

## 🚀 Key Features

*   **Compliance Agent**: Uses RAG (Retrieval-Augmented Generation) to check transport scenarios against PDF regulations.
*   **Code-as-Policy**: Generates and executes sandboxed Python code to validate safety rules deterministically.
*   **Provenance Agent**: Logs every decision and event to an immutable ledger (Firestore).
*   **Verifiable Credentials**: Issues W3C-compliant credentials for approved scenarios.
*   **Security**: Implements JWS (JSON Web Signature) for all inter-agent communication and Agent Identity Cards.
*   **LangFlow Integration**: Ready for visual orchestration and Human-in-the-Loop (HITL) workflows.

## 📂 Project Structure

*   `src/agents/`: Core agents (Compliance, Provenance, Report).
*   `src/security/`: Security utilities (AgentCards, JWS Signing).
*   `src/sandbox/`: Secure code execution environment.
*   `src/integrations/`: Custom components for LangFlow.
*   `data/`: Regulations PDFs and mock databases.
*   `scripts/`: Demo and test scripts.

## 🛠️ Setup & Installation

### Option A: Docker (Recommended)
Run the full stack (App + LangFlow UI) in containers.

```bash
# Build and start services
podman-compose up --build
```
*   **LangFlow UI**: `http://localhost:7860`
*   **App Demo**: Runs automatically in the `hazardsafe-app` container.

### Option B: Local Python
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Set up environment variables:
    *   Copy `.env.example` to `.env`
    *   Add your `GOOGLE_API_KEY`

## 🏃‍♂️ Running Demos

### 1. End-to-End Pipeline Demo
Simulates the full flow: Compliance Check -> Provenance Log -> VC Issuance.
```bash
python3 notebook.py
```

### 2. Human-in-the-Loop (HITL) Demo
Interactive script that pauses for human approval before issuing a credential.
```bash
python3 scripts/hitl_demo.py
```

### 3. Adversarial Evaluation
Stress-tests the system with tricky edge-case scenarios.
```bash
python3 src/eval/evaluate.py
```

## 📚 Documentation
*   [Project Description](project_description.md)
*   [Implementation Plan](spec/implementation_plan.md)
*   [LangFlow Setup Guide](docs/LANGFLOW_SETUP.md)
