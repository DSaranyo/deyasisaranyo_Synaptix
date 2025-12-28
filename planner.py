"""
Planner Component - Autonomous Decision Making
Core agentic logic for action selection based on state
"""

from typing import List, Dict, Any, Optional
import json
from dataclasses import dataclass
from enum import Enum


class ActionType(Enum):
    """Enumeration of available action types"""
    CREATE_TASK = "create_task"
    NOTIFY = "notify"
    ESCALATE = "escalate"
    SCHEDULE = "schedule"
    MONITOR = "monitor"
    BLOCK_DEPLOYMENT = "block_deployment"
    AGGREGATE = "aggregate"
    AUTO_FIX = "auto_fix"
    REQUEST_REVIEW = "request_review"


@dataclass
class Action:
    """Structured action representation"""
    type: ActionType
    priority: str
    params: Dict[str, Any]
    reasoning: str


class AutonomousPlanner:
    """
    Autonomous planning engine - makes decisions without LLM
    Uses rule-based logic and state analysis
    """
    
    def __init__(self):
        self.action_rules = self._initialize_rules()
        self.escalation_thresholds = {
            'error': 3,
            'test_failure': 5,
            'security_alert': 1
        }
    
    def _initialize_rules(self) -> Dict[str, Any]:
        """
        Initialize decision rules for different event types
        This is deterministic autonomous behavior
        """
        return {
            'error': {
                'priority_threshold': 7,
                'actions': ['create_task', 'notify'],
                'escalation_condition': lambda count: count >= 3
            },
            'security_alert': {
                'priority_threshold': 0,  # Always act
                'actions': ['create_task', 'notify', 'block_deployment'],
                'escalation_condition': lambda count: True
            },
            'test_failure': {
                'priority_threshold': 6,
                'actions': ['create_task'],
                'escalation_condition': lambda count: count >= 5
            },
            'deployment': {
                'priority_threshold': 5,
                'actions': ['monitor', 'create_task'],
                'escalation_condition': lambda count: False
            },
            'code_review': {
                'priority_threshold': 6,
                'actions': ['schedule'],
                'escalation_condition': lambda count: count >= 10
            }
        }
    
    def plan(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        priority: int,
        context: Dict[str, Any]
    ) -> List[Action]:
        """
        Main planning method - autonomous decision making
        
        Args:
            event_type: Type of event
            event_data: Event payload
            priority: Calculated priority (0-10)
            context: Memory context (event history, patterns)
        
        Returns:
            List of actions to execute
        """
        actions = []
        
        # Get rule set for this event type
        rules = self.action_rules.get(event_type)
        if not rules:
            return self._default_plan(event_type, event_data)
        
        # Check if event meets priority threshold
        if priority < rules['priority_threshold']:
            return []
        
        # Apply rule-based action selection
        event_count = context.get('event_count', 1)
        
        # Core actions based on event type
        if 'create_task' in rules['actions']:
            actions.append(self._plan_task_creation(event_type, event_data, priority))
        
        if 'notify' in rules['actions'] and priority >= 8:
            actions.append(self._plan_notification(event_type, event_data, priority))
        
        if 'schedule' in rules['actions']:
            actions.append(self._plan_scheduling(event_type, event_data))
        
        if 'monitor' in rules['actions']:
            actions.append(self._plan_monitoring(event_type, event_data))
        
        if 'block_deployment' in rules['actions']:
            actions.append(self._plan_deployment_block(event_type, event_data))
        
        # Check escalation conditions
        if rules['escalation_condition'](event_count):
            actions.append(self._plan_escalation(event_type, event_data, event_count))
        
        # Pattern-based actions
        if event_count >= 3 and event_type in ['issue_created', 'test_failure']:
            actions.append(self._plan_aggregation(event_type, event_data, event_count))
        
        # Auto-fix for known patterns
        if self._can_auto_fix(event_type, event_data, event_count):
            actions.append(self._plan_auto_fix(event_type, event_data))
        
        return actions
    
    def _plan_task_creation(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        priority: int
    ) -> Action:
        """Plan task creation action"""
        
        title_map = {
            'error': f"Fix: {event_data.get('message', 'Unknown error')}",
            'test_failure': f"Test failed: {event_data.get('test_name', 'unknown')}",
            'security_alert': f"Security: {event_data.get('alert_type', 'unknown')}",
            'deployment': f"Verify deployment: {event_data.get('service', 'unknown')}"
        }
        
        priority_map = {
            10: 'critical',
            9: 'critical',
            8: 'high',
            7: 'high',
            6: 'medium',
            5: 'medium'
        }
        
        return Action(
            type=ActionType.CREATE_TASK,
            priority=priority_map.get(priority, 'low'),
            params={
                'title': title_map.get(event_type, f"Handle {event_type}"),
                'description': json.dumps(event_data),
                'labels': [event_type, 'automated'],
                'assignee': self._determine_assignee(event_type, event_data)
            },
            reasoning=f"Event priority {priority} requires task tracking"
        )
    
    def _plan_notification(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        priority: int
    ) -> Action:
        """Plan notification action"""
        
        channel_map = {
            'security_alert': 'security',
            'error': 'urgent' if priority >= 9 else 'alerts',
            'deployment': 'deployments'
        }
        
        return Action(
            type=ActionType.NOTIFY,
            priority='high' if priority >= 8 else 'medium',
            params={
                'channel': channel_map.get(event_type, 'general'),
                'message': self._format_notification_message(event_type, event_data),
                'mention': 'oncall' if priority >= 9 else None
            },
            reasoning=f"High priority event ({priority}) requires immediate notification"
        )
    
    def _plan_escalation(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        event_count: int
    ) -> Action:
        """Plan escalation action"""
        
        return Action(
            type=ActionType.ESCALATE,
            priority='high',
            params={
                'reason': f"Repeated {event_type} detected ({event_count} occurrences)",
                'escalate_to': 'engineering_manager',
                'include_data': True
            },
            reasoning=f"Event count {event_count} exceeds threshold"
        )
    
    def _plan_scheduling(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Action:
        """Plan scheduling action"""
        
        return Action(
            type=ActionType.SCHEDULE,
            priority='medium',
            params={
                'activity': event_type,
                'resource_id': event_data.get('pr_id') or event_data.get('issue_id'),
                'time_slot': 'next_available',
                'duration': '30m'
            },
            reasoning="Scheduling required for code review workflow"
        )
    
    def _plan_monitoring(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Action:
        """Plan monitoring action"""
        
        return Action(
            type=ActionType.MONITOR,
            priority='medium',
            params={
                'target': event_data.get('service', 'unknown'),
                'metrics': ['error_rate', 'latency', 'cpu', 'memory'],
                'duration': '30m',
                'alert_threshold': 'high'
            },
            reasoning="Post-deployment monitoring required"
        )
    
    def _plan_deployment_block(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Action:
        """Plan deployment blocking action"""
        
        return Action(
            type=ActionType.BLOCK_DEPLOYMENT,
            priority='critical',
            params={
                'reason': f"Security alert: {event_data.get('alert_type')}",
                'affected_services': event_data.get('affected_services', []),
                'until_resolved': True
            },
            reasoning="Security vulnerability requires deployment freeze"
        )
    
    def _plan_aggregation(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        event_count: int
    ) -> Action:
        """Plan aggregation action for related events"""
        
        return Action(
            type=ActionType.AGGREGATE,
            priority='medium',
            params={
                'action': 'create_epic',
                'event_type': event_type,
                'count': event_count,
                'title': f"Recurring {event_type} pattern"
            },
            reasoning=f"Multiple related events ({event_count}) suggest larger issue"
        )
    
    def _plan_auto_fix(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Action:
        """Plan automatic fix action"""
        
        return Action(
            type=ActionType.AUTO_FIX,
            priority='high',
            params={
                'fix_type': self._identify_fix_type(event_data),
                'automatic': True,
                'create_pr': True
            },
            reasoning="Known issue with automated fix available"
        )
    
    def _can_auto_fix(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        event_count: int
    ) -> bool:
        """Determine if event can be auto-fixed"""
        
        # Simple heuristics for auto-fix eligibility
        auto_fixable = {
            'dependency_vulnerability': True,
            'formatting_error': True,
            'configuration_drift': True
        }
        
        issue_type = event_data.get('alert_type') or event_data.get('error_type')
        return auto_fixable.get(issue_type, False) and event_count >= 2
    
    def _identify_fix_type(self, event_data: Dict[str, Any]) -> str:
        """Identify type of automated fix needed"""
        
        if 'dependency' in str(event_data).lower():
            return 'dependency_update'
        elif 'config' in str(event_data).lower():
            return 'config_correction'
        else:
            return 'generic_fix'
    
    def _determine_assignee(self, event_type: str, event_data: Dict[str, Any]) -> str:
        """Determine who should be assigned the task"""
        
        # Simple assignment logic
        if event_type == 'security_alert':
            return 'security_team'
        elif event_type == 'deployment':
            return 'devops_team'
        elif 'test' in event_type:
            return 'qa_team'
        else:
            return 'oncall_engineer'
    
    def _format_notification_message(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> str:
        """Format notification message"""
        
        if event_type == 'security_alert':
            return f"🚨 Security Alert: {event_data.get('alert_type')} - {event_data.get('details')}"
        elif event_type == 'error':
            return f"❌ Error: {event_data.get('message')} in {event_data.get('service')}"
        else:
            return f"⚠️ {event_type}: {json.dumps(event_data)[:100]}"
    
    def _default_plan(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> List[Action]:
        """Default plan for unrecognized event types"""
        
        return [
            Action(
                type=ActionType.CREATE_TASK,
                priority='low',
                params={
                    'title': f"Review {event_type}",
                    'description': json.dumps(event_data),
                    'labels': [event_type, 'automated', 'review']
                },
                reasoning="Unrecognized event type - creating task for review"
            )
        ]
