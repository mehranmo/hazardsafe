# HazardSAFE: Technical Specification & Implementation Plan
**Version:** 3.0 (Free Tier A2A + RAG Edition)  
**Architecture:** A2A Multi-Agent Hub with HITL and Provenance  
**Domain:** Long-Term Hazardous Materials Storage & Transport (HazMat QI)

---

## 1. Design Goals

HazardSAFE is an **agentic infrastructure** for long-term management of **hazardous materials** (flammable, toxic, corrosive, pressurized, etc.). It aims to:

1. **Replace black-box decisions** with “Glass Box” compliance:
   - Every step is traceable, reproducible, and auditable years later.
2. **Read regulations, not just YAML:**
   - Use **dynamic RAG** over PDF standards to ground decisions in real(istic) text.
3. **Be deterministic where it matters:**
   - Use **Code-as-Policy**: LLM generates verifiers, but Python executes them.
4. **Bake in Human-in-the-Loop (HITL):**
   - Critical steps pause for human review before issuance.
5. **Be interoperable & trustworthy:**
   - Use **A2A** for multi-agent collaboration and **Verifiable Credentials (VCs)** for trust.
6. **Run on the Google agentic stack, free-tier friendly:**
   - Gemini models + ADK + optional Vertex AI Agent Engine / Cloud Run.

This spec is the **master blueprint** for the Kaggle submission.

---

## 2. High-Level Architecture

### 2.1 Logical Topology

**Core idea:** A **Frontdoor Orchestrator** talks to three main sub-agents over **A2A**, all running in one Python “monolith” for the Kaggle demo, but structurally ready for Agent Engine.

Agents (all ADK-based with A2A AgentCards):

1. **Frontdoor Agent (Hub):**  
   - Role: HazMat Compliance Assistant  
   - Responsibilities: User interaction, scenario intake, high-level orchestration, simple UI/state.

2. **Compliance Agent (Spoke):**  
   - Role: “Scientist / Safety Engineer”  
   - Responsibilities:  
     - Use RAG over HazMat standards PDFs.  
     - Generate **Code-as-Policy** Python validators.  
     - Run them in a sandbox and return structured pass/fail assessments.

3. **Provenance Agent (Spoke):**  
   - Role: “Scribe”  
   - Responsibilities:  
     - Record immutable provenance events in Firestore as a **PROV-like graph**.  
     - Support “10-year replay” by reconstructing decision histories.

4. **Report & VC Agent (Spoke):**  
   - Role: “Issuer”  
   - Responsibilities:  
     - Turn assessments + provenance into human-readable reports.  
     - Mint **HazMat Compliance Certificates** as W3C Verifiable Credentials (VCs).

*(Optional)*

5. **Auditor Agent:**  
   - Role: Governance  
   - Responsibilities:  
     - Check that trajectories satisfy policy (mandatory steps present).  
     - Compute an assurance score and support internal audits.

### 2.2 Physical Topology (Free Tier)

- **Runtime (minimal):** Local / Kaggle notebook or a single service (optionally Cloud Run).  
- **LLM models:** Gemini 1.5 Flash/Pro via Google AI Studio / Vertex AI.  
- **Vector store:** ChromaDB (local) for regulations RAG.  
- **Provenance store:** Firestore (Native Mode) to log provenance events and HITL state.  
- **Agent framework:** ADK Python for A2A agents and MCP tool integration.  

For the Kaggle submission you can run everything local/Notebook; Cloud Run is an optional deployment bonus.

---

## 3. Knowledge Layer: Dynamic RAG over HazMat Standards

**Constraint:** No hardcoded YAML rules as the primary source of truth. Rules are derived from **PDF standards** (synthetic or anonymized).

### 3.1 RAG Pipeline

1. **Ingestion (Librarian Tool)**  
   - On startup, a `Librarian` MCP tool reads `data/regulations/*.pdf`.  
   - PDFs contain synthetic but realistic paragraphs like:
     - “Flammable liquids of Class 3 shall be stored below 25°C in ventilated areas.”  
     - “Transport of toxic liquids shall not exceed 12 hours for a single trip.”

2. **Chunking & Embedding**  
   - Text is split into paragraphs and embedded into **ChromaDB** with metadata:
     - document name, page number, paragraph ID, hazard class tags.

3. **Retrieval**  
   - For each scenario, Compliance Agent queries the vector store:
     - e.g., query: “storage requirements for flammable liquid at facility temperature 28°C”
   - Retrieves top-k paragraphs to ground validator generation.

### 3.2 “Living Rules”

Rules are **not hardcoded** but derived each time from the retrieved text. The system still caches results (e.g., mapping extracted rule → canonical “rule id”), but the **source of truth is the PDF text**.

---

## 4. Compliance Engine: Code-as-Policy

**Goal:** LLM does *understanding* and *code generation*, Python does the **math and logic**.

### 4.1 Workflow

1. **Inputs:**
   - Scenario JSON (storage/transport, hazard_class, temp, duration, etc.).
   - Retrieved regulation paragraphs.

2. **LLM Prompt (Gemini Flash):**
   - “Given this scenario and these regulation paragraphs, write a Python function `verify(data)` that returns `(bool, str)` where `bool` is compliance and `str` is explanation. Only use deterministic operations; do not call external resources.”

3. **Generated Code Example:**

   ```python
   def verify(data):
       """
       Rule: Flammable liquids must be stored below 25°C (Regulations.pdf p.4 para 3.2)
       """
       temp = data["storage_temp_c"]
       ok = temp <= 25
       if ok:
           return True, f"OK: {temp}°C <= 25°C limit"
       else:
           diff = temp - 25
           return False, f"FAIL: {temp}°C exceeds limit by {diff}°C"
   ```

4. **Sandbox Execution:**

   * Run the code in a restricted `exec` sandbox (no `import`, no file/network access).
   * Compute:

     * `pass_fail`, `explanation`
     * `code_hash` = `sha256` of the source for provenance.

5. **Structured Output:**

   ```json
   {
     "assessment_id": "ASSM-2026-001",
     "passed": false,
     "rule_citations": [
       {"doc": "Regulations.pdf", "page": 4, "paragraph": "3.2"}
     ],
     "explanation": "FAIL: 30°C exceeds limit by 5°C",
     "code_hash": "sha256:...",
     "raw_code": "def verify(data): ..."
   }
   ```

6. **Provenance:**

   * The code, its hash, and mapping to the paragraph(s) are recorded as entities in the provenance graph.

### 4.2 Multiple Rules & Aggregation

For complex scenarios:

* LLM may generate multiple `verify_*` functions or a single function that checks multiple constraints and accumulates rule-level results.
* The Compliance Agent returns a list of rule results and a final recommendation:

  * `approve`, `approve_with_conditions`, `reject`.

---

## 5. Provenance & Immutable Audit Trail

We maintain two layers:

1. **Event log (Firestore)** – append-only provenance events.
2. **Logical graph (in memory / recomputed)** – PROV-like graph built from events when queried.

### 5.1 Firestore Event Schema

`collection: provenance_events`

```json
{
  "session_id": "sess_2026_01",
  "timestamp": "2026-03-01T10:15:00Z",
  "agent": "HazardComplianceAgent",
  "activity": "CODE_POLICY_VERIFICATION",
  "entity_ids": ["scenario:STOR-PLANT-A-B17-2026-01", "rule:R-FL-Temp"],
  "data": {
    "scenario_id": "STOR-PLANT-A-B17-2026-01",
    "hazard_class": "flammable_liquid",
    "rule_citation": "Regulations.pdf:p4:para3.2",
    "code_hash": "sha256:...",
    "result": "FAIL",
    "explanation": "FAIL: 30°C exceeds limit by 5°C"
  },
  "integrity_hash": "sha256:<event_payload>",
  "ai_card_id": "AIC-HC-2.0.0"
}
```

Other activities:

* `SCENARIO_INGESTED`
* `RAG_RETRIEVAL`
* `HITL_DECISION`
* `CERTIFICATE_ISSUED`

### 5.2 Evidence Graph

When the Provenance Agent receives a query like:

```json
{ "certificate_id": "CERT-HZ-2026-45" }
```

it:

1. Fetches all related events from Firestore.

2. Builds an in-memory PROV-style graph with:

   * **Entities:** scenario, regulation paragraphs, code snippets, assessments, certificate, VCs, AI Cards.
   * **Activities:** ingest, retrieve, generate_code, run_code, review, issue_certificate.
   * **Agents:** Frontdoor, Compliance, Provenance, Report agents + human operator.

3. Returns either:

   * The full graph JSON, or
   * A linear “replay” narrative for human consumption.

This supports the **“10-year replay”** requirement.

---

## 6. Human-in-the-Loop (HITL) Workflow

We adopt the **LangGraph-style interrupt pattern conceptually**, but implement it using ADK + Firestore state (or LangGraph if you choose to layer it).

### 6.1 HITL Triggers

The workflow must enter HITL mode when:

1. **Ambiguity:**

   * RAG retrieval confidence below threshold (e.g. semantic similarity < 0.7).
2. **Violation:**

   * Any Code-as-Policy check returns `False`.
3. **Finality:**

   * A certificate is about to be minted for a high-risk scenario.

### 6.2 HITL State Machine

We define a `WorkflowState` record for each session, stored in Firestore:

```json
{
  "session_id": "sess_2026_01",
  "status": "PENDING_HITL",
  "pending_action": "REVIEW_CERTIFICATE",
  "evidence_snapshot_id": "graph_root_123",
  "human_approval_status": "PENDING|APPROVED|REJECTED",
  "human_comments": null
}
```

**Flow:**

1. Frontdoor Agent or LangGraph node detects a HITL trigger.
2. It writes a `WorkflowState` with `status=PENDING_HITL` and **interrupts** the agent flow.
3. The UI (Streamlit or simple CLI) polls or subscribes to PENDING_HITL items:

   * Renders scenario, key rule results, and a summary of provenance.
   * Shows Approve / Reject buttons and comment field.
4. When the user acts:

   * UI updates `human_approval_status` and `human_comments`.
   * A new provenance event `HITL_DECISION` is written.
5. Agent sees updated state and resumes:

   * If Approved: continue to certificate issuance.
   * If Rejected: escalate or terminate.

---

## 7. Verifiable Credentials (VC) & Trust

We add a lightweight **VC ecosystem** to demonstrate trust & interoperability.

### 7.1 Credential Types

1. **HazMatFacilityCredential**

   * Subject: facility DID (`did:web:example.com:facility:PLANT-A`).
   * Claims: facility type, allowed hazard classes, capacity.

2. **HazMatOperatorCredential**

   * Subject: human DID (`did:web:example.com:user:alice`).
   * Claims: role (`HazMatSafetyOfficer`), organization, validity, license ID.

3. **HazMatComplianceCertificateVC**

   * Subject: container/scenario DID.
   * Claims:

     * `certificate_id`
     * `scenario_id`
     * `decision` (approve/approve_with_conditions/reject)
     * `evidence_root_id` (provenance graph root)
     * issuing agent & organization.

We use a basic JWS-based VC format as in W3C VC Data Model examples.

### 7.2 VC Verification Flow

* **At request time:**

  * The user (safety officer) presents `HazMatOperatorCredential`.
  * Frontdoor Agent calls a `verify_vc` tool:

    * Checks signature, expiration, and that `role` includes `HazMatSafetyOfficer`.

* **At certificate issuance:**

  * Report & VC Agent issues a `HazMatComplianceCertificateVC`.
  * Stores its `id` or hash as an **entity** in provenance.

This ties the **human identity**, **facility**, and **certificate** together in an audit-ready way.

---

## 8. Google Agentic Stack & Deployment

### 8.1 ADK + A2A

We use ADK’s A2A workflow for inter-agent communication locally, which also maps cleanly to Agent Engine deployment.

* Each agent has:

  * an **AgentCard** (metadata, operations),
  * an **AgentExecutor** (code),
  * optional **LlmAgent** (for Gemini-based logic).

* A2A operations:

  * `CheckHazmatScenario` (Compliance Agent)
  * `RecordProvenanceEvent` / `GetProvenanceGraph` / `ReplayCertificate` (Provenance Agent)
  * `GenerateComplianceReport` / `IssueHazmatCertificateVC` (Report & VC Agent)

### 8.2 Optional Agent Engine Deployment

For the Kaggle **Agent Deployment bonus**:

1. Package each ADK agent with AgentCards and MCP tools.
2. Use ADK’s deployment guide to push to **Vertex AI Agent Engine** as A2A agents.
3. Configure your local Frontdoor Agent to call them via the A2A protocol.

You can still keep the Kaggle demo fully local; the deployment is a documented “reference path”.

---

## 9. Implementation Phases (Spec-Driven)

### Phase 0 – Repo Skeleton (Day 1)

* [ ] Initialize repo with `src/`, `data/`, `config/`, `spec/`, `eval/`.
* [ ] Add `project_description.md` and this `implementation_plan.md`.
* [ ] Define initial JSON schemas for scenarios, events, VCs.

### Phase 1 – RAG & Regulations (Day 1–2)

* [ ] Create synthetic HazMat regulations PDF(s) in `data/regulations/`.
* [ ] Implement `Librarian` MCP tool for PDF → chunks → ChromaDB.
* [ ] Verify basic retrieval from a Python script.

### Phase 2: Compliance Agent & Code-as-Policy
- [ ] **Agent Implementation**
    - [ ] Create `agents/compliance_agent.py` using ADK.
    - [ ] Define `CheckHazmatScenario` tool using MCP.
    - [ ] **Security**: Implement signed `agent-card.json` (JWS) for agent discovery integrity.
- [ ] **Code-as-Policy Engine**
    - [ ] Implement `sandbox/executor.py` (safe Python execution).
    - [ ] Implement `sandbox/generator.py` (LLM prompt for code generation).
    - [ ] Ensure generated code is deterministic and stateless.

### Phase 3: Provenance Agent & Firestore
- [ ] **Firestore Setup**
    - [ ] Create Firestore database (or emulator for local dev).
    - [ ] Define collections: `provenance_events`, `agent_state`.
- [ ] **Provenance Agent**
    - [ ] Create `agents/provenance_agent.py`.
    - [ ] Implement `LogEvent` tool.
    - [ ] **Security**: Implement **Message-Level Signing Interceptor**:
        - [ ] Create a middleware/interceptor to sign all outgoing A2A JSON-RPC requests with JWS.
        - [ ] Verify signatures on incoming requests before processing.
        - [ ] Log signature and key ID (`kid`) in provenance events for non-repudiation.
* [ ] Log events for at least scenario ingest, RAG retrieval, code execution, and certificate issuance.

### Phase 4 – Report & VC Agent (Day 4–5)

* [ ] Implement **Report & VC Agent** with Gemini Pro/Flash for report text.
* [ ] Define VC schemas and static keys in `data/credentials/`.
* [ ] Implement `IssueHazmatComplianceVC`, linking VC → provenance graph root.
* [ ] Expose `GenerateComplianceReport` A2A operation.

### Phase 5 – HITL Workflow (Day 5–6)

* [ ] Implement a small `WorkflowState` collection in Firestore.
* [ ] Add HITL trigger logic (ambiguity, violation, pre-issuance).
* [ ] Implement a simple UI (Streamlit or CLI) that:

  * lists pending approvals,
  * shows summary evidence,
  * lets user Approve/Reject.
* [ ] Wire resume logic so the flow continues only after HITL decision.

### Phase 6: Evaluation & Packaging
- [ ] **Evaluation Framework**
    - [ ] Implement `eval/evaluate.py` to run scenarios and score agent performance.
    - [ ] Define metrics: Success Rate, Compliance Accuracy, Provenance Completeness.
    - [ ] **Adversarial Testing / Red Teaming**:
        - [ ] Create "Red Team" scenarios with subtle regulatory violations or ambiguous data to test agent robustness.
        - [ ] Verify that the Compliance Agent correctly rejects unsafe proposals even when pressured.
- [ ] **Kaggle Notebook**
    - [ ] Create `notebooks/submission.ipynb`.
    - [ ] Ensure all code is self-contained or installed via pip in the notebook.
    - [ ] Add demo walkthrough with a complex HazMat scenario.

---

## 10. Success Criteria Matrix

| Dimension | Success Metric |
| ----------------------- | ------------------------------------------------------------------------------- |
| **Dynamic RAG**         | Changing text in the PDF changes decisions without altering code.               |
| **Code-as-Policy**      | Generated Python validators pass static sanity tests and handle math safely.    |
| **A2A Multi-Agent**     | Frontdoor calls Compliance/Provenance/Report via A2A operations.                |
| **HITL**                | Critical flows pause until a human approves/rejects, state stored in Firestore. |
| **Provenance & Replay** | A `replay` tool reconstructs a certificate decision using only Firestore logs.  |
| **VC Integration**      | Certificates are also minted as VCs referencing provenance graph roots.         |
| **Kaggle Fit**          | README + code clearly show use of ADK, A2A, MCP tools, Gemini, evaluation.      |

---

This implementation plan unifies:

* the **dynamic RAG + Code-as-Policy + HITL + “Glass Box”** ideas from the Gemini spec,
* with **A2A, ADK, VCs, AI Cards, and long-term QI-style provenance** from our original HazardSAFE design,
* all on top of the **Google agentic stack** and within realistic **free-tier** constraints.
