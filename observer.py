"""
Observer Component - Stream Ingestion and Event Classification
Responsible for ingesting workflow events from various sources
"""

import pathway as pw
from typing import Dict, Any
import json


class WorkflowObserver:
    """
    Observes and classifies incoming workflow events
    This is the INPUT layer of the agentic system
    """
    
    def __init__(self):
        self.event_types = {
            'error',
            'security_alert',
            'test_failure',
            'deployment',
            'code_review',
            'commit',
            'issue_created',
            'file_change',
            'build_status',
            'performance_alert'
        }
    
    def classify_event(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify and enrich raw events
        """
        event_type = raw_event.get('event_type', 'unknown')
        
        if event_type not in self.event_types:
            event_type = 'unknown'
        
        # Enrich with metadata
        enriched = {
            'event_type': event_type,
            'timestamp': raw_event.get('timestamp'),
            'data': raw_event.get('data', '{}'),
            'source': raw_event.get('source', 'system'),
            'metadata': {
                'processed': True,
                'classifier_version': '1.0'
            }
        }
        
        return enriched
    
    def validate_event(self, event: Dict[str, Any]) -> bool:
        """
        Validate event structure before processing
        """
        required_fields = ['event_type', 'timestamp', 'data']
        return all(field in event for field in required_fields)


class EventGenerator:
    """
    Utility to generate simulated workflow events
    Used for testing the agent in streaming mode
    """
    
    @staticmethod
    def generate_sample_events():
        """
        Generate sample workflow events for testing
        """
        events = [
            {
                'timestamp': '2024-01-15T10:00:00Z',
                'event_type': 'commit',
                'data': json.dumps({
                    'commit_id': 'abc123',
                    'author': 'developer1',
                    'message': 'Fix authentication bug',
                    'files_changed': 3
                })
            },
            {
                'timestamp': '2024-01-15T10:05:00Z',
                'event_type': 'test_failure',
                'data': json.dumps({
                    'test_name': 'test_user_login',
                    'error': 'AssertionError: Expected 200, got 401',
                    'suite': 'integration'
                })
            },
            {
                'timestamp': '2024-01-15T10:10:00Z',
                'event_type': 'error',
                'data': json.dumps({
                    'message': 'Database connection timeout',
                    'severity': 'critical',
                    'service': 'api-gateway',
                    'stack_trace': 'Connection refused on port 5432'
                })
            },
            {
                'timestamp': '2024-01-15T10:15:00Z',
                'event_type': 'code_review',
                'data': json.dumps({
                    'pr_id': 'PR-456',
                    'title': 'Implement OAuth2 flow',
                    'author': 'developer2',
                    'reviewers': ['reviewer1', 'reviewer2'],
                    'status': 'pending'
                })
            },
            {
                'timestamp': '2024-01-15T10:20:00Z',
                'event_type': 'security_alert',
                'data': json.dumps({
                    'alert_type': 'dependency_vulnerability',
                    'severity': 'high',
                    'details': 'CVE-2024-1234 in lodash@4.17.0',
                    'affected_services': ['frontend', 'backend']
                })
            },
            {
                'timestamp': '2024-01-15T10:25:00Z',
                'event_type': 'deployment',
                'data': json.dumps({
                    'service': 'user-service',
                    'environment': 'production',
                    'version': 'v2.3.1',
                    'status': 'success'
                })
            },
            {
                'timestamp': '2024-01-15T10:30:00Z',
                'event_type': 'test_failure',
                'data': json.dumps({
                    'test_name': 'test_payment_processing',
                    'error': 'Timeout after 30s',
                    'suite': 'e2e'
                })
            },
            {
                'timestamp': '2024-01-15T10:35:00Z',
                'event_type': 'issue_created',
                'data': json.dumps({
                    'issue_id': 'ISSUE-789',
                    'title': 'Performance degradation on dashboard',
                    'reporter': 'user123',
                    'priority': 'medium',
                    'labels': ['performance', 'frontend']
                })
            },
            {
                'timestamp': '2024-01-15T10:40:00Z',
                'event_type': 'error',
                'data': json.dumps({
                    'message': 'Out of memory error',
                    'severity': 'critical',
                    'service': 'data-processor',
                    'memory_usage': '95%'
                })
            },
            {
                'timestamp': '2024-01-15T10:45:00Z',
                'event_type': 'test_failure',
                'data': json.dumps({
                    'test_name': 'test_user_login',
                    'error': 'AssertionError: Expected 200, got 401',
                    'suite': 'integration',
                    'note': 'Third failure in a row'
                })
            }
        ]
        
        return events
