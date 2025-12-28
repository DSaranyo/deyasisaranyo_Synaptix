"""
Agentic Developer Workflow Agent - Main Orchestrator
Uses Pathway for streaming event processing and agentic decision-making
"""

import pathway as pw
from pathway.xpacks.llm import llms
from typing import Any, Dict, List
import json
from datetime import datetime

from observer import WorkflowObserver
from memory import AgentMemory
from planner import AutonomousPlanner
from executor import ActionExecutor


class AgenticSystem:
    """
    Main agentic system that continuously processes workflow events
    and autonomously manages developer productivity
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.observer = WorkflowObserver()
        self.memory = AgentMemory()
        self.planner = AutonomousPlanner()
        self.executor = ActionExecutor()
        
    def build_pipeline(self, event_stream: pw.Table) -> pw.Table:
        """
        Build the complete agentic pipeline using Pathway
        
        Pipeline: Events → Memory Update → Planning → Reasoning → Execution
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
        
        # STEP 5: LLM reasoning layer - refine and explain decisions
        reasoned_actions = planned_actions.select(
            *pw.this,
            reasoning=pw.apply_async(
                self._llm_reason,
                pw.this.event_type,
                pw.this.data,
                pw.this.action_plan
            )
        )
        
        # STEP 6: Execute actions autonomously
        executed_actions = reasoned_actions.select(
            *pw.this,
            execution_result=pw.apply(
                self._execute_actions,
                pw.this.action_plan,
                pw.this.reasoning
            )
        )
        
        return executed_actions
    
    def _calculate_priority(self, event_type: str, data: str) -> int:
        """Calculate event priority based on type and content"""
        data_dict = json.loads(data)
        
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
        This is the core agentic behavior (no LLM needed here)
        """
        data_dict = json.loads(data)
        actions = []
        
        # Rule-based autonomous decision making
        if event_type == 'error' and priority >= 8:
            actions.append({
                'type': 'create_task',
                'title': f"Fix: {data_dict.get('message', 'Unknown error')}",
                'priority': 'high',
                'labels': ['bug', 'automated']
            })
            actions.append({
                'type': 'notify',
                'channel': 'urgent',
                'message': f"Critical error detected: {data_dict.get('message')}"
            })
            
        elif event_type == 'test_failure':
            actions.append({
                'type': 'create_task',
                'title': f"Test failed: {data_dict.get('test_name')}",
                'priority': 'medium',
                'labels': ['test', 'automated']
            })
            if event_count and event_count > 3:
                actions.append({
                    'type': 'escalate',
                    'reason': 'Repeated test failures detected'
                })
                
        elif event_type == 'code_review' and priority >= 6:
            actions.append({
                'type': 'schedule',
                'activity': 'code_review',
                'pr_id': data_dict.get('pr_id'),
                'time_slot': 'next_available'
            })
            
        elif event_type == 'deployment':
            actions.append({
                'type': 'monitor',
                'target': data_dict.get('service'),
                'duration': '30m'
            })
            actions.append({
                'type': 'create_task',
                'title': 'Post-deployment verification',
                'priority': 'high',
                'labels': ['deployment', 'automated']
            })
            
        elif event_type == 'security_alert':
            actions.append({
                'type': 'create_task',
                'title': f"Security: {data_dict.get('alert_type')}",
                'priority': 'critical',
                'labels': ['security', 'automated']
            })
            actions.append({
                'type': 'notify',
                'channel': 'security',
                'message': data_dict.get('details')
            })
            actions.append({
                'type': 'block_deployment',
                'reason': 'Security alert active'
            })
            
        elif event_type == 'issue_created':
            # Auto-triage based on content
            if event_count and event_count > 10:
                actions.append({
                    'type': 'aggregate',
                    'action': 'create_epic',
                    'reason': 'Multiple related issues detected'
                })
                
        return json.dumps(actions)
    
    async def _llm_reason(
        self, 
        event_type: str, 
        data: str, 
        action_plan: str
    ) -> str:
        """
        LLM reasoning layer - provides context and refinement
        NOT for blind decision-making, only for interpretation
        """
        try:
            data_dict = json.loads(data)
            actions = json.loads(action_plan)
            
            if not actions:
                return "No actions required - event logged for monitoring"
            
            # Use LLM to explain and validate the autonomous decisions
            prompt = f"""You are an AI reasoning engine for a developer workflow agent.

Event Type: {event_type}
Event Data: {json.dumps(data_dict, indent=2)}
Planned Actions: {json.dumps(actions, indent=2)}

Your task:
1. Validate that the planned actions are appropriate
2. Provide concise reasoning for why these actions make sense
3. Suggest any critical adjustments if needed

Respond in JSON format:
{{
    "validation": "approved|adjusted|rejected",
    "reasoning": "brief explanation",
    "adjustments": [] // if any
}}
"""
            
            response = await self.llm(prompt)
            return response
            
        except Exception as e:
            return json.dumps({
                "validation": "approved",
                "reasoning": f"LLM reasoning failed, using autonomous plan: {str(e)}",
                "adjustments": []
            })
    
    def _execute_actions(self, action_plan: str, reasoning: str) -> str:
        """
        Execute the planned actions autonomously
        """
        try:
            actions = json.loads(action_plan)
            reasoning_data = json.loads(reasoning) if reasoning else {}
            
            if reasoning_data.get('validation') == 'rejected':
                return json.dumps({
                    'status': 'rejected',
                    'reason': reasoning_data.get('reasoning')
                })
            
            # Apply adjustments if LLM suggested any
            if reasoning_data.get('adjustments'):
                actions = reasoning_data['adjustments']
            
            results = []
            for action in actions:
                result = self.executor.execute(action)
                results.append(result)
                
                # Log execution
                print(f"[EXECUTOR] {action['type']}: {result}")
            
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
    
    # Initialize LLM client (using pathway's LLM abstraction)
    llm_client = llms.LiteLLMChat(
        model="claude-3-5-sonnet-20241022",
        temperature=0.1,
        max_tokens=500
    )
    
    # Create agentic system
    agent = AgenticSystem(llm_client)
    
    # Define event stream schema
    class EventSchema(pw.Schema):
        timestamp: str
        event_type: str
        data: str
    
    # Set up Pathway input stream from CSV
    # This simulates continuous workflow events
    event_stream = pw.io.csv.read(
        './data/workflow_events.csv',
        schema=EventSchema,
        mode='streaming'
    )
    
    # Build the agentic pipeline
    output_stream = agent.build_pipeline(event_stream)
    
    # Output results to console for monitoring
    pw.io.jsonlines.write(output_stream, './output/agent_actions.jsonl')
    
    # Also print to stdout for debugging
    def print_action(
        timestamp, 
        event_type, 
        action_plan, 
        reasoning, 
        execution_result
    ):
        print(f"\n{'='*80}")
        print(f"[{timestamp}] Event: {event_type}")
        print(f"Actions: {action_plan}")
        print(f"Reasoning: {reasoning}")
        print(f"Result: {execution_result}")
        print(f"{'='*80}\n")
    
    pw.io.subscribe(
        output_stream,
        on_change=lambda key, row, time, is_addition: print_action(
            row['timestamp'],
            row['event_type'],
            row['action_plan'],
            row['reasoning'],
            row['execution_result']
        ) if is_addition else None
    )
    
    # Run the Pathway computation engine
    print("🤖 Agentic Developer Workflow Agent Starting...")
    print("Monitoring workflow events and autonomously managing tasks...\n")
    
    pw.run(
        monitoring_level=pw.MonitoringLevel.NONE,
        with_http_server=False
    )


if __name__ == "__main__":
    main()
