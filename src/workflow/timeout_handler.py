#!/usr/bin/env python3
"""
Timeout Handler for HITL Workflows

This script runs as a background service to check for workflows
that have exceeded the timeout period and auto-rejects them.

Usage:
    python3 src/workflow/timeout_handler.py
    
Or run as a daemon/cron job for production.
"""

import time
import sys
from src.workflow.manager import WorkflowManager
from src.agents.provenance_agent import HazardProvenanceAgent

class TimeoutHandler:
    def __init__(self, check_interval_seconds=300):
        """
        Args:
            check_interval_seconds: How often to check for timeouts (default: 5 minutes)
        """
        self.workflow_manager = WorkflowManager()
        self.provenance_agent = HazardProvenanceAgent()
        self.check_interval = check_interval_seconds

    def run_once(self):
        """Run a single timeout check"""
        print(f"[TimeoutHandler] Checking for timed-out workflows...")
        
        timed_out_ids = self.workflow_manager.check_timeouts()
        
        if timed_out_ids:
            print(f"[TimeoutHandler] Found {len(timed_out_ids)} timed-out workflows")
            
            # Log to provenance
            for workflow_id in timed_out_ids:
                workflow_state = self.workflow_manager.get_workflow_state(workflow_id)
                
                event_payload = {
                    "workflow_id": workflow_id,
                    "scenario_id": workflow_state.get("scenario_id"),
                    "timeout_reason": workflow_state.get("timeout_reason"),
                    "age_hours": (time.time() - workflow_state.get("hitl_triggered_at", 0)) / 3600
                }
                
                self.provenance_agent.log_event(
                    event_type="HITL_TIMEOUT",
                    agent_id="TimeoutHandler",
                    payload=event_payload
                )
                
                print(f"[TimeoutHandler] Logged HITL_TIMEOUT event for {workflow_id}")
        else:
            print(f"[TimeoutHandler] No timed-out workflows found")
        
        return len(timed_out_ids)

    def run_continuous(self):
        """Run continuously, checking at regular intervals"""
        print(f"[TimeoutHandler] Starting continuous mode (check every {self.check_interval}s)")
        print(f"[TimeoutHandler] Press Ctrl+C to stop")
        
        try:
            while True:
                self.run_once()
                print(f"[TimeoutHandler] Sleeping for {self.check_interval} seconds...")
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            print("\n[TimeoutHandler] Stopped by user")
            sys.exit(0)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="HITL Workflow Timeout Handler")
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Check interval in seconds (default: 300 = 5 minutes)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (useful for cron jobs)"
    )
    
    args = parser.parse_args()
    
    handler = TimeoutHandler(check_interval_seconds=args.interval)
    
    if args.once:
        count = handler.run_once()
        print(f"[TimeoutHandler] Processed {count} timeouts. Exiting.")
    else:
        handler.run_continuous()
