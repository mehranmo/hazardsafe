# HazardSAFE Project Description

**HazardSAFE** is an agentic infrastructure for long-term management of hazardous materials (flammable, toxic, corrosive, pressurized, etc.).

## Core Philosophy
1. **Glass Box Compliance**: Traceable, reproducible, and auditable decisions.
2. **Dynamic RAG**: Rules are derived from PDF standards, not hardcoded.
3. **Code-as-Policy**: LLM generates verifiers, Python executes them.
4. **Human-in-the-Loop (HITL)**: Critical steps pause for review.
5. **Trust**: Uses A2A for multi-agent collaboration and Verifiable Credentials (VCs).

## Architecture
- **Frontdoor Agent**: User interaction and orchestration.
- **Compliance Agent**: RAG over PDFs and Code-as-Policy execution.
- **Provenance Agent**: Records immutable events in Firestore.
- **Report & VC Agent**: Issues human-readable reports and W3C VCs.

## Stack
- **Language**: Python
- **AI**: Gemini Models (Flash/Pro)
- **Framework**: Google ADK + A2A
- **Database**: ChromaDB (Vector), Firestore (Provenance)
