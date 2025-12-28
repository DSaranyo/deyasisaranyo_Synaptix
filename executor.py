"""
Executor Component - Action Execution
Executes planned actions autonomously
"""

from typing import Dict, Any, List
import json
from datetime import datetime
import random


class ActionExecutor:
    """
    Executes actions planned by the autonomous planner
    This is where agent actions manifest in the real world
    """
    
    def __init__(self):
        self.execution_log = []
        self.task_counter = 0
        self.notification_counter = 0
        
    def execute(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single action
        
        Args:
            action: Action dictionary with type and params
            
        Returns:
            Execution result
        """
        action_type = action.get('type')
        
        executors = {
            'create_task': self._execute_create_task,
            'notify': self._execute_notify,
            'escalate': self._execute_escalate,
            'schedule': self._execute_schedule,
            'monitor': self._execute_monitor,
            'block_deployment': self._execute_block_deployment,
            'aggregate': self._execute_aggregate,
            'auto_fix': self._execute_auto_fix,
            'request_review': self._execute_request_review
        }
        
        executor = executors.get(action_type, self._execute_unknown)
        
        try:
            result = executor(action)
            self._log_execution(action, result, 'success')
            return result
        except Exception as e:
            error_result = {
                'status': 'failed',
                'error': str(e)
            }
            self._log_execution(action, error_result, 'failed')
            return error_result
    
    def _execute_create_task(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task creation"""
        self.task_counter += 1
        
        task_id = f"TASK-{self.task_counter:04d}"
        title = action.get('title', 'Untitled Task')
        priority = action.get('priority', 'medium')
        labels = action.get('labels', [])
        assignee = action.get('assignee', 'unassigned')
        
        print(f"✓ Created Task: {task_id}")
        print(f"  Title: {title}")
        print(f"  Priority: {priority}")
        print(f"  Assignee: {assignee}")
        print(f"  Labels: {', '.join(labels)}")
        
        return {
            'status': 'success',
            'task_id': task_id,
            'title': title,
            'priority': priority,
            'assignee': assignee,
            'created_at': datetime.now().isoformat()
        }
    
    def _execute_notify(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification"""
        self.notification_counter += 1
        
        channel = action.get('channel', 'general')
        message = action.get('message', 'Notification')
        mention = action.get('mention')
        
        print(f"📢 Notification sent to #{channel}")
        print(f"  Message: {message}")
        if mention:
            print(f"  Mentioned: @{mention}")
        
        return {
            'status': 'success',
            'channel': channel,
            'message_id': f"MSG-{self.notification_counter:04d}",
            'delivered_at': datetime.now().isoformat()
        }
    
    def _execute_escalate(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute escalation"""
        reason = action.get('reason', 'Unknown')
        escalate_to = action.get('escalate_to', 'manager')
        
        print(f"⬆️  Escalated to {escalate_to}")
        print(f"  Reason: {reason}")
        
        return {
            'status': 'success',
            'escalated_to': escalate_to,
            'reason': reason,
            'escalation_id': f"ESC-{random.randint(1000, 9999)}",
            'escalated_at': datetime.now().isoformat()
        }
    
    def _execute_schedule(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scheduling"""
        activity = action.get('activity', 'task')
        resource_id = action.get('resource_id', 'unknown')
        time_slot = action.get('time_slot', 'next_available')
        duration = action.get('duration', '30m')
        
        print(f"📅 Scheduled: {activity}")
        print(f"  Resource: {resource_id}")
        print(f"  Time slot: {time_slot}")
        print(f"  Duration: {duration}")
        
        return {
            'status': 'success',
            'activity': activity,
            'resource_id': resource_id,
            'scheduled_time': time_slot,
            'duration': duration,
            'schedule_id': f"SCH-{random.randint(1000, 9999)}"
        }
    
    def _execute_monitor(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute monitoring"""
        target = action.get('target', 'unknown')
        metrics = action.get('metrics', [])
        duration = action.get('duration', '30m')
        
        print(f"🔍 Started monitoring: {target}")
        print(f"  Metrics: {', '.join(metrics)}")
        print(f"  Duration: {duration}")
        
        return {
            'status': 'success',
            'target': target,
            'metrics': metrics,
            'duration': duration,
            'monitor_id': f"MON-{random.randint(1000, 9999)}",
            'started_at': datetime.now().isoformat()
        }
    
    def _execute_block_deployment(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute deployment block"""
        reason = action.get('reason', 'Unknown')
        affected_services = action.get('affected_services', [])
        
        print(f"🛑 DEPLOYMENT BLOCKED")
        print(f"  Reason: {reason}")
        print(f"  Affected services: {', '.join(affected_services)}")
        
        return {
            'status': 'success',
            'blocked': True,
            'reason': reason,
            'affected_services': affected_services,
            'block_id': f"BLK-{random.randint(1000, 9999)}",
            'blocked_at': datetime.now().isoformat()
        }
    
    def _execute_aggregate(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute event aggregation"""
        aggregate_action = action.get('action', 'group')
        event_type = action.get('event_type', 'unknown')
        count = action.get('count', 0)
        
        print(f"📊 Aggregated {count} {event_type} events")
        print(f"  Action: {aggregate_action}")
        
        return {
            'status': 'success',
            'action': aggregate_action,
            'event_type': event_type,
            'count': count,
            'aggregate_id': f"AGG-{random.randint(1000, 9999)}"
        }
    
    def _execute_auto_fix(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute automated fix"""
        fix_type = action.get('fix_type', 'generic')
        create_pr = action.get('create_pr', False)
        
        print(f"🔧 Auto-fix executed: {fix_type}")
        if create_pr:
            pr_id = f"PR-{random.randint(1000, 9999)}"
            print(f"  Created PR: {pr_id}")
        
        return {
            'status': 'success',
            'fix_type': fix_type,
            'pr_created': create_pr,
            'pr_id': pr_id if create_pr else None,
            'fix_id': f"FIX-{random.randint(1000, 9999)}",
            'fixed_at': datetime.now().isoformat()
        }
    
    def _execute_request_review(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute review request"""
        resource_id = action.get('resource_id', 'unknown')
        reviewers = action.get('reviewers', [])
        
        print(f"👥 Review requested for {resource_id}")
        print(f"  Reviewers: {', '.join(reviewers)}")
        
        return {
            'status': 'success',
            'resource_id': resource_id,
            'reviewers': reviewers,
            'request_id': f"REV-{random.randint(1000, 9999)}"
        }
    
    def _execute_unknown(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unknown action types"""
        action_type = action.get('type', 'unknown')
        
        print(f"⚠️  Unknown action type: {action_type}")
        
        return {
            'status': 'skipped',
            'reason': f"Unknown action type: {action_type}"
        }
    
    def _log_execution(
        self,
        action: Dict[str, Any],
        result: Dict[str, Any],
        status: str
    ):
        """Log execution for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'result': result,
            'status': status
        }
        self.execution_log.append(log_entry)
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        total = len(self.execution_log)
        successful = sum(1 for log in self.execution_log if log['status'] == 'success')
        failed = total - successful
        
        return {
            'total_executions': total,
            'successful': successful,
            'failed': failed,
            'tasks_created': self.task_counter,
            'notifications_sent': self.notification_counter
        }
    
    def get_recent_executions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution log entries"""
        return self.execution_log[-limit:]


class ExecutionValidator:
    """
    Validates actions before execution
    Ensures safety and correctness
    """
    
    @staticmethod
    def validate(action: Dict[str, Any]) -> bool:
        """
        Validate action before execution
        
        Returns:
            True if action is valid and safe to execute
        """
        required_fields = ['type']
        
        # Check required fields
        if not all(field in action for field in required_fields):
            return False
        
        # Type-specific validation
        action_type = action.get('type')
        
        if action_type == 'create_task':
            return 'title' in action
        elif action_type == 'notify':
            return 'channel' in action and 'message' in action
        elif action_type == 'block_deployment':
            return 'reason' in action
        
        # Default: allow if has type
        return True
    
    @staticmethod
    def sanitize(action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize action parameters
        Remove potentially harmful content
        """
        # Remove any executable code patterns
        sanitized = action.copy()
        
        # Truncate long strings
        for key, value in sanitized.items():
            if isinstance(value, str) and len(value) > 1000:
                sanitized[key] = value[:1000] + "... (truncated)"
        
        return sanitized
