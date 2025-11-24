# HazardSAFE HITL Examples and Best Practices

Based on research from LangFlow and RAGFlow implementations, this document outlines proven patterns for Human-in-the-Loop workflows in AI systems.

## Key Patterns from Industry Examples

### 1. LangFlow HITL Pattern (Email Approval Workflow)

**Flow Structure:**
```
Input → LLM Generation → Human Review Node → Conditional Router → [Approved/Edited/Rejected Paths]
```

**Critical Components:**
- **Pause Mechanism**: Workflow stops at the HITL node
- **External Interface**: Web app/Slack/Email for human review
- **State Persistence**: LangGraph's ability to save workflow state
- **Conditional Routing**: If-Else component routes based on approval

**Implementation in HazardSAFE:**
We've adapted this pattern:
```
Scenario Input → Compliance Agent → Chat Input (HITL) → Conditional Logic → Provenance → Report
```

### 2. RAGFlow HITL Best Practices

**Multiple Intervention Points:**
1. **Data Ingestion**: Human reviews document chunking
2. **Retrieval Feedback**: Human judges relevance of retrieved docs
3. **Generation Validation**: Human fact-checks LLM output
4. **Continuous Improvement**: Human feedback refines the system

**Implementation in HazardSAFE:**
- Compliance Agent uses RAG for regulation retrieval
- HITL step validates AI's compliance decision
- Provenance Agent logs human approval decisions
- System can be refined based on approval/rejection patterns

### 3. Conditional Routing Patterns

**LangFlow If-Else Component:**
- Compare approval decision ("Approved" vs "Rejected")
- Route to `true_result` (approved path) or `false_result` (rejected path)
- Can chain multiple conditions for complex logic

**HazardSAFE Implementation:**
```python
# In our components, we use:
if decision.get('compliant'):
    # Issue VC
else:
    # Skip VC issuance
```

## Improved HITL Component Design

Based on industry patterns, here's our enhanced approach:

### Option A: Chat Input (Current - Simple)
- User types "yes" or "no" in the LangFlow UI
- Lightweight, no external dependencies
- Good for demos

### Option B: External Approval System (Production)
- API webhook receives approval request
- Human reviews in external UI (web app, Slack)
- Callback sends decision back to LangFlow
- Better for real-world deployments

### Option C: LangGraph Interrupts (Advanced)
- Using `interrupt_before` or `interrupt_after`
- Automatically pauses at specific nodes
- Resume with human command
- Best for complex, multi-step approvals

## Visual Workflow in LangFlow UI

```
┌─────────────────┐
│  Scenario Input │
│  (JSON)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Compliance      │
│ Agent           │
│ (RAG + Code-as- │
│  Policy)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 🛑 HITL Node   │ ◄─── Human reviews AI recommendation
│ (Chat Input)    │      Types: "yes" | "no"
└────────┬────────┘
         │
         ├────────── If "yes" (approved) ─────┐
         │                                     │
         ▼                                     ▼
┌─────────────────┐                  ┌─────────────────┐
│ Provenance      │                  │ Report Agent    │
│ Agent           │                  │ (Issue VC)      │
│ (Log Decision)  │                  └─────────────────┘
└─────────────────┘
```

## Recommended Enhancements

1. **Add Conditional Router Component**
   - Explicit if-else based on approval decision
   - Separate "Approved" and "Rejected" paths

2. **External Approval UI**
   - Simple web form for approvals
   - Webhook integration back to LangFlow

3. **Audit Trail**
   - Log WHO approved/rejected
   - Log WHEN decision was made
   - Include human's rationale

4. **Role-Based Access**
   - Different approval levels (e.g., junior vs senior reviewer)
   - Escalation workflows

5. **Timeout Handling**
   - Auto-reject if no decision within X hours
   - Send reminders to approvers

## Implementation Files

- `components/hazardsafe/compliance_agent.py` - AI decision maker
- `components/hazardsafe/provenance_agent.py` - Audit logging
- `components/hazardsafe/report_agent.py` - VC issuance

**To test:** Open `http://localhost:7860` and build the flow manually using these components.
