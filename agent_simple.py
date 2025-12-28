"""
Agentic Developer Workflow Agent - Main Orchestrator (Simplified)
Uses Pathway for streaming event processing and agentic decision-making
"""

import pathway as pw
from typing import Any, Dict
import json
from datetime import datetime

from observer import WorkflowObserver
from memory import AgentMemory
from planner import AutonomousPlanner, Action
from executor import ActionExecutor


class AgenticSystem:
    """
    Main agentic system that continuously processes workflow events
    and autonomously manages developer productivity
    """
    
    def __init__(self):
        self.observer = WorkflowObserver()
        self.memory = AgentMemory()
        self.planner = AutonomousPlanner()
        self.executor = ActionExecutor()
        
    def build_pipeline(self, event_stream: pw.Table) -> pw.Table:
        """
        Build the complete agentic pipeline using Pathway
        
        Pipeline: Events → Memory Update → Planning → Execution
        """
        
        # STEP 1: Observe and classify events
        classified_events = event_stream.select(
            timestamp=pw.this.timestamp,
            event_type=pw.this.event_type,
            data=pw.this.data,
            priority=pw.apply(self._calculate_priority, pw.this.event_type, pw.this.data)
        )
        
        # STEP 2: Update agent memory using Pathway reducers
        # Group events by type and maintain running state
        memory_state = classified_events.groupby(pw.this.event_type).reduce(
            event_type=pw.this.event_type,
            event_count=pw.reducers.count(),
            last_seen=pw.reducers.latest(pw.this.timestamp),
            accumulated_data=pw.reducers.tuple(pw.this.data)
        )
        
        # STEP 3: Join events with memory state for context-aware planning
        events_with_context = classified_events.join(
            memory_state,
            pw.left.event_type == pw.right.event_type,
            how=pw.JoinMode.LEFT
        ).select(
            timestamp=pw.left.timestamp,
            event_type=pw.left.event_type,
            data=pw.left.data,
            priority=pw.left.priority,
            event_count=pw.right.event_count,
            historical_context=pw.right.accumulated_data
        )
        
        # STEP 4: Autonomous planning - decide what actions to take
        planned_actions = events_with_context.select(
            *pw.this,
            action_plan=pw.apply(
                self._plan_actions,
                pw.this.event_type,
                pw.this.data,
                pw.this.priority,
                pw.this.event_count
            )
        )
        
        # STEP 5: Execute actions autonomously
        executed_actions = planned_actions.select(
            *pw.this,
            execution_result=pw.apply(
                self._execute_actions,
                pw.this.action_plan,
                pw.this.event_type
            )
        )
        
        return executed_actions
    
    def _calculate_priority(self, event_type: str, data: str) -> int:
        """Calculate event priority based on type and content"""
        try:
            data_dict = json.loads(data)
        except:
            data_dict = {}
        
        priority_map = {
            'error': 10,
            'security_alert': 10,
            'test_failure': 8,
            'deployment': 7,
            'code_review': 6,
            'commit': 5,
            'issue_created': 4,
            'file_change': 3
        }
        
        base_priority = priority_map.get(event_type, 5)
        
        # Boost priority for urgent keywords
        urgent_keywords = ['critical', 'urgent', 'blocker', 'security']
        if any(keyword in str(data_dict).lower() for keyword in urgent_keywords):
            base_priority = min(10, base_priority + 3)
            
        return base_priority
    
    def _plan_actions(
        self, 
        event_type: str, 
        data: str, 
        priority: int, 
        event_count: int
    ) -> str:
        """
        Autonomous planning logic - deterministic action selection
        This is the core agentic behavior
        """
        try:
            data_dict = json.loads(data)
        except:
            data_dict = {}
        
        context = {
            'event_count': event_count if event_count else 1,
            'priority': priority
        }
        
        # Use the autonomous planner
        actions = self.planner.plan(event_type, data_dict, priority, context)
        
        # Convert Action objects to dicts
        action_dicts = []
        for action in actions:
            action_dict = {
                'type': action.type.value,
                'priority': action.priority,
                **action.params
            }
            action_dicts.append(action_dict)
        
        return json.dumps(action_dicts)
    
    def _execute_actions(self, action_plan: str, event_type: str) -> str:
        """
        Execute the planned actions autonomously
        """
        try:
            actions = json.loads(action_plan)
            
            if not actions:
                return json.dumps({
                    'status': 'no_action',
                    'reason': 'No actions required for this event'
                })
            
            results = []
            for action in actions:
                result = self.executor.execute(action)
                results.append(result)
            
            return json.dumps({
                'status': 'completed',
                'actions_executed': len(results),
                'results': results
            })
            
        except Exception as e:
            return json.dumps({
                'status': 'error',
                'error': str(e)
            })


def main():
    """
    Main entry point - sets up Pathway streaming and runs the agent
    """
    
    print("="*80)
    print("🤖 AGENTIC DEVELOPER WORKFLOW AGENT")
    print("="*80)
    print("Framework: Pathway (Streaming)")
    print("Architecture: Observer → Memory → Planner → Executor")
    print("Mode: Autonomous (No Chat Interface)")
    print("="*80)
    print()
    
    # Create agentic system
    agent = AgenticSystem()
    
    # Define event stream schema
    class EventSchema(pw.Schema):
        timestamp: str
        event_type: str
        data: str
    
    # Set up Pathway input stream from CSV
    print("📡 Setting up event stream from CSV...")
    event_stream = pw.io.csv.read(
        './data/workflow_events.csv',
        schema=EventSchema,
        mode='streaming'
    )
    
    # Build the agentic pipeline
    print("🔧 Building agentic pipeline...")
    output_stream = agent.build_pipeline(event_stream)
    
    # Output results to console
    print("✓ Pipeline ready")
    print()
    print("="*80)
    print("🚀 AGENT STARTED - Processing Events...")
    print("="*80)
    print()
    
    # Subscribe to output for console logging
    def handle_event(key, row, time, is_addition):
        if not is_addition:
            return
            
        print(f"\n{'─'*80}")
        print(f"⏰ [{row['timestamp']}]")
        print(f"📌 Event: {row['event_type']} (Priority: {row['priority']})")
        
        # Parse and display data
        try:
            data = json.loads(row['data'])
            print(f"📄 Data: {json.dumps(data, indent=2)}")
        except:
            print(f"📄 Data: {row['data']}")
        
        print(f"🧠 Memory: Event #{row['event_count']}")
        
        # Display action plan
        try:
            actions = json.loads(row['action_plan'])
            if actions:
                print(f"📋 Planned Actions ({len(actions)}):")
                for i, action in enumerate(actions, 1):
                    print(f"   {i}. {action.get('type', 'unknown')}")
            else:
                print(f"📋 No actions planned (event logged)")
        except:
            print(f"📋 Actions: {row['action_plan']}")
        
        # Display execution result
        try:
            result = json.loads(row['execution_result'])
            status = result.get('status', 'unknown')
            print(f"✅ Execution: {status}")
            
            if result.get('actions_executed'):
                print(f"   → {result['actions_executed']} action(s) executed")
        except:
            print(f"✅ Result: {row['execution_result']}")
        
        print(f"{'─'*80}")
    
    pw.io.subscribe(
        output_stream,
        on_change=handle_event
    )
    
    # Also write to jsonlines for persistence
    pw.io.jsonlines.write(output_stream, './output/agent_actions.jsonl')
    
    # Run the Pathway computation engine
    try:
        pw.run(
            monitoring_level=pw.MonitoringLevel.NONE,
            with_http_server=False
        )
    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("🛑 Agent stopped by user")
        print("="*80)
        
        # Display stats
        stats = agent.executor.get_execution_stats()
        print("\n📊 Execution Statistics:")
        print(f"   Total executions: {stats['total_executions']}")
        print(f"   Successful: {stats['successful']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Tasks created: {stats['tasks_created']}")
        print(f"   Notifications sent: {stats['notifications_sent']}")
        print()


if __name__ == "__main__":
    main()
