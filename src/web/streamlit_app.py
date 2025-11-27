import streamlit as st
import time
import yaml
import os
import sys
import random
import pandas as pd
import graphviz
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.workflow.manager import WorkflowManager
from src.agents.provenance_agent import HazardProvenanceAgent
from src.agents.compliance_agent import HazardComplianceAgent

# Page Configuration
st.set_page_config(
    page_title="HazardSAFE Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Configuration
CONFIG_PATH = "config/hitl_config.yaml"
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    return {}

config = load_config()

# Initialize Managers (Cached to prevent reloading on every rerun)
@st.cache_resource
def get_managers():
    return {
        "workflow": WorkflowManager(),
        "provenance": HazardProvenanceAgent(),
        "compliance": HazardComplianceAgent()
    }

managers = get_managers()

# --- Sidebar ---
with st.sidebar:
    st.title("🛡️ HazardSAFE")
    st.markdown("Human-in-the-Loop Approval System")
    st.divider()
    
    # User Identity
    st.subheader("👤 Reviewer Profile")
    user_id = st.text_input("User ID / Email", value="reviewer@hazardsafe.ai")
    
    st.divider()
    
    # Stats
    pending_workflows = managers["workflow"].get_pending_workflows()
    st.metric("Pending Approvals", len(pending_workflows))
    st.metric("Timeout Setting", f"{config.get('timeout_hours', 24)} hours")
    
    st.divider()
    st.caption(f"System Time: {datetime.now().strftime('%H:%M:%S')}")

# --- Main Content ---

# Tabs
tab_approvals, tab_generator, tab_architecture, tab_history = st.tabs([
    "📋 Pending Approvals", 
    "🧪 Test Generator", 
    "🏗️ Architecture", 
    "📜 History & Audit"
])

# --- Tab 1: Pending Approvals ---
with tab_approvals:
    st.header("Pending Approvals")
    
    if not pending_workflows:
        st.success("✅ No pending approvals. All caught up!")
        st.balloons()
    else:
        for wf in pending_workflows:
            with st.container():
                # Card-like layout using columns
                c1, c2 = st.columns([3, 1])
                
                with c1:
                    st.subheader(f"Scenario: {wf.get('scenario_id')}")
                    
                    # Scenario Data Expander
                    with st.expander("📄 View Scenario Details", expanded=False):
                        st.json(wf.get('scenario_data', {}))
                    
                    # AI Decision Display
                    decision = wf.get('decision_data', {})
                    if decision.get('compliant'):
                        st.success(f"**AI Recommendation:** ✅ Compliant\n\n**Reason:** {decision.get('reason')}")
                    else:
                        st.error(f"**AI Recommendation:** ❌ Non-Compliant\n\n**Reason:** {decision.get('reason')}")
                
                with c2:
                    st.markdown(f"**Age:** {((time.time() - wf.get('hitl_triggered_at', 0)) / 3600):.1f} hours")
                    
                    comments = st.text_area("Comments", key=f"comment_{wf['id']}", placeholder="Optional rationale...")
                    
                    col_approve, col_reject = st.columns(2)
                    with col_approve:
                        if st.button("✅ Approve", key=f"approve_{wf['id']}", use_container_width=True):
                            managers["workflow"].approve_workflow(wf['id'], user_id, comments)
                            managers["provenance"].log_event(
                                "HITL_APPROVED", "StreamlitUI", 
                                {"workflow_id": wf['id'], "user_id": user_id, "comments": comments}
                            )
                            st.rerun()
                            
                    with col_reject:
                        if st.button("❌ Reject", key=f"reject_{wf['id']}", use_container_width=True):
                            if not comments:
                                st.warning("Comment required for rejection.")
                            else:
                                managers["workflow"].reject_workflow(wf['id'], user_id, comments)
                                managers["provenance"].log_event(
                                    "HITL_REJECTED", "StreamlitUI", 
                                    {"workflow_id": wf['id'], "user_id": user_id, "comments": comments}
                                )
                                st.rerun()
                st.divider()

# --- Tab 2: Test Generator ---
with tab_generator:
    st.header("🧪 Mock Test Generator")
    st.markdown("Generate synthetic scenarios to test the HITL workflow.")
    
    c1, c2 = st.columns([1, 2])
    
    with c1:
        test_type = st.selectbox("Scenario Type", ["Random", "Pass (Compliant)", "Fail (Non-Compliant)", "Edge Case"])
        
        if st.button("⚡ Generate Scenario", type="primary", use_container_width=True):
            with st.spinner("Simulating Agent Workflow..."):
                # Logic copied from previous Flask app
                scenarios = {
                    'Pass (Compliant)': {
                        'material_class': 'Class 7', 'package_type': 'Type B(U)',
                        'ambient_temperature_c': round(random.uniform(20, 35), 1),
                        'transport_index': round(random.uniform(0.1, 0.9), 2)
                    },
                    'Fail (Non-Compliant)': {
                        'material_class': 'Class 7', 'package_type': 'Type B(U)',
                        'ambient_temperature_c': round(random.uniform(40, 50), 1),
                        'transport_index': round(random.uniform(0.1, 0.9), 2)
                    },
                    'Edge Case': {
                        'material_class': 'Class 7', 'package_type': 'Type B(U)',
                        'ambient_temperature_c': 38.0,
                        'transport_index': round(random.uniform(0.1, 0.9), 2)
                    }
                }
                
                selected_type = test_type if test_type != "Random" else random.choice(list(scenarios.keys()))
                scenario_data = scenarios.get(selected_type, scenarios['Pass (Compliant)'])
                scenario_id = f"TEST-{selected_type.split()[0].upper()}-{int(time.time())}"
                scenario_data['id'] = scenario_id
                
                # Execute Workflow
                wf_id = managers["workflow"].create_workflow(scenario_id, scenario_data)
                decision = managers["compliance"].check_scenario(scenario_data)
                managers["workflow"].trigger_hitl(wf_id, decision)
                
                st.session_state['last_generated'] = {
                    "id": wf_id, "scenario": scenario_data, "decision": decision
                }
                st.success(f"Generated {selected_type} Scenario!")
                time.sleep(1)
                st.rerun()

    with c2:
        if 'last_generated' in st.session_state:
            last = st.session_state['last_generated']
            st.subheader("Last Generated Test")
            st.info(f"**Workflow ID:** {last['id']}")
            
            sc_col, dec_col = st.columns(2)
            with sc_col:
                st.markdown("#### Scenario Data")
                st.json(last['scenario'])
            with dec_col:
                st.markdown("#### AI Decision")
                if last['decision']['compliant']:
                    st.success(f"✅ Compliant\n\n{last['decision']['reason']}")
                else:
                    st.error(f"❌ Non-Compliant\n\n{last['decision']['reason']}")

# --- Tab 3: Architecture ---
with tab_architecture:
    st.header("🏗️ Workflow Architecture")
    
    st.markdown("### State Machine Visualization")
    
    graph = graphviz.Digraph()
    graph.attr(rankdir='LR')
    
    # Nodes
    graph.node('DRAFT', 'DRAFT', shape='ellipse')
    graph.node('PENDING', 'PENDING_HITL', shape='box', style='filled', color='lightyellow')
    graph.node('APPROVED', 'APPROVED', shape='doublecircle', color='green')
    graph.node('REJECTED', 'REJECTED', shape='doublecircle', color='red')
    graph.node('TIMEOUT', 'TIMEOUT', shape='doublecircle', color='grey')
    graph.node('CANCELLED', 'CANCELLED', shape='octagon')
    
    # Edges
    graph.edge('DRAFT', 'PENDING', label='AI Decision')
    graph.edge('DRAFT', 'CANCELLED', label='Manual')
    graph.edge('PENDING', 'APPROVED', label='Human Approve')
    graph.edge('PENDING', 'REJECTED', label='Human Reject')
    graph.edge('PENDING', 'TIMEOUT', label='Timer Expired')
    
    st.graphviz_chart(graph)
    
    st.markdown("### Agent Roles")
    
    roles = [
        {"Agent": "Compliance Agent", "Role": "Analyzes scenarios against regulations (RAG + Code-as-Policy)", "Icon": "🕵️"},
        {"Agent": "Provenance Agent", "Role": "Logs all events to immutable Firestore ledger", "Icon": "📝"},
        {"Agent": "Report Agent", "Role": "Issues W3C Verifiable Credentials for compliant scenarios", "Icon": "🏆"},
        {"Agent": "Workflow Manager", "Role": "Orchestrates state transitions and HITL triggers", "Icon": "⚙️"}
    ]
    st.table(pd.DataFrame(roles).set_index("Agent"))

# --- Tab 4: History & Audit ---
with tab_history:
    st.header("📜 History & Audit Trail")
    
    if st.button("🔄 Refresh History"):
        st.rerun()
        
    all_workflows = managers["workflow"].db.get_all_documents()
    
    if all_workflows:
        # Convert to DataFrame for easier display
        data = []
        for wf in all_workflows:
            data.append({
                "Timestamp": datetime.fromtimestamp(wf.get('created_at', 0)).strftime('%Y-%m-%d %H:%M'),
                "Scenario ID": wf.get('scenario_id'),
                "Status": wf.get('status'),
                "Reviewer": wf.get('human_reviewer', 'N/A'),
                "Comments": wf.get('human_comments', 'N/A'),
                "ID": wf.get('id')
            })
            
        df = pd.DataFrame(data).sort_values("Timestamp", ascending=False)
        
        # Color coding for status
        def color_status(val):
            color = 'black'
            if val == 'APPROVED': color = 'green'
            elif val == 'REJECTED': color = 'red'
            elif val == 'PENDING_HITL': color = 'orange'
            elif val == 'TIMEOUT': color = 'grey'
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            df.style.map(color_status, subset=['Status']),
            use_container_width=True,
            hide_index=True
        )
        
        # Detailed View
        st.divider()
        st.subheader("Detailed Audit View")
        selected_id = st.selectbox("Select Workflow ID to Inspect", df['ID'].tolist())
        
        if selected_id:
            selected_wf = next((w for w in all_workflows if w['id'] == selected_id), None)
            if selected_wf:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("#### State History")
                    for event in selected_wf.get('history', []):
                        ts = datetime.fromtimestamp(event['timestamp']).strftime('%H:%M:%S')
                        st.text(f"{ts}: {event['from_status']} -> {event['to_status']}")
                
                with c2:
                    st.markdown("#### Full Metadata")
                    st.json(selected_wf)
    else:
        st.info("No history found.")
