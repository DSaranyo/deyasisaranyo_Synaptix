#!/usr/bin/env python3
"""
Test Runner for Agentic System
Validates all components work correctly
"""

import sys
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, '.')

from observer import WorkflowObserver, EventGenerator
from memory import AgentMemory, MemoryRetrieval
from planner import AutonomousPlanner, ActionType
from executor import ActionExecutor, ExecutionValidator


def test_observer():
    """Test Observer component"""
    print("\n" + "="*60)
    print("Testing Observer Component")
    print("="*60)
    
    observer = WorkflowObserver()
    
    # Test event classification
    raw_event = {
        'event_type': 'error',
        'timestamp': datetime.now().isoformat(),
        'data': json.dumps({
            'message': 'Test error',
            'severity': 'high'
        })
    }
    
    enriched = observer.classify_event(raw_event)
    print(f"✓ Event classified: {enriched['event_type']}")
    
    # Test validation
    is_valid = observer.validate_event(enriched)
    print(f"✓ Event validation: {is_valid}")
    
    # Test event generation
    events = EventGenerator.generate_sample_events()
    print(f"✓ Generated {len(events)} sample events")
    
    return True


def test_planner():
    """Test Planner component"""
    print("\n" + "="*60)
    print("Testing Planner Component")
    print("="*60)
    
    planner = AutonomousPlanner()
    
    # Test error event planning
    event_data = {
        'message': 'Critical database error',
        'severity': 'critical',
        'service': 'api-gateway'
    }
    
    context = {
        'event_count': 1,
        'priority': 9
    }
    
    actions = planner.plan('error', event_data, 9, context)
    print(f"✓ Planned {len(actions)} actions for error event")
    
    for i, action in enumerate(actions, 1):
        print(f"  {i}. {action.type.value} (priority: {action.priority})")
    
    # Test security alert planning
    security_data = {
        'alert_type': 'dependency_vulnerability',
        'severity': 'high',
        'details': 'CVE-2024-1234'
    }
    
    actions = planner.plan('security_alert', security_data, 10, context)
    print(f"✓ Planned {len(actions)} actions for security alert")
    
    for i, action in enumerate(actions, 1):
        print(f"  {i}. {action.type.value} (priority: {action.priority})")
    
    return True


def test_executor():
    """Test Executor component"""
    print("\n" + "="*60)
    print("Testing Executor Component")
    print("="*60)
    
    executor = ActionExecutor()
    validator = ExecutionValidator()
    
    # Test task creation
    action = {
        'type': 'create_task',
        'title': 'Test Task',
        'priority': 'high',
        'labels': ['test']
    }
    
    is_valid = validator.validate(action)
    print(f"✓ Action validation: {is_valid}")
    
    if is_valid:
        result = executor.execute(action)
        print(f"✓ Task created: {result.get('task_id')}")
    
    # Test notification
    action = {
        'type': 'notify',
        'channel': 'test',
        'message': 'Test notification'
    }
    
    result = executor.execute(action)
    print(f"✓ Notification sent: {result.get('message_id')}")
    
    # Test monitoring
    action = {
        'type': 'monitor',
        'target': 'test-service',
        'metrics': ['cpu', 'memory'],
        'duration': '5m'
    }
    
    result = executor.execute(action)
    print(f"✓ Monitoring started: {result.get('monitor_id')}")
    
    # Get stats
    stats = executor.get_execution_stats()
    print(f"\n✓ Execution stats:")
    print(f"  Total: {stats['total_executions']}")
    print(f"  Successful: {stats['successful']}")
    print(f"  Tasks: {stats['tasks_created']}")
    print(f"  Notifications: {stats['notifications_sent']}")
    
    return True


def test_memory():
    """Test Memory component"""
    print("\n" + "="*60)
    print("Testing Memory Component")
    print("="*60)
    
    memory = AgentMemory()
    retrieval = MemoryRetrieval()
    
    # Test pattern threshold
    is_pattern = retrieval.check_pattern_threshold(5, 3)
    print(f"✓ Pattern detection: {is_pattern}")
    
    # Test urgency calculation
    urgency = retrieval.calculate_urgency_score(
        priority=8,
        event_count=3,
        recency_minutes=2
    )
    print(f"✓ Urgency score: {urgency}")
    
    # Test context extraction
    memory_state = {
        'event_count': 5,
        'max_priority': 9
    }
    context = retrieval.extract_context(memory_state)
    print(f"✓ Context extracted: {context}")
    
    return True


def test_integration():
    """Test full integration"""
    print("\n" + "="*60)
    print("Testing Full Integration")
    print("="*60)
    
    # Create components
    planner = AutonomousPlanner()
    executor = ActionExecutor()
    
    # Simulate a critical error event
    event_data = {
        'message': 'Out of memory error',
        'severity': 'critical',
        'service': 'data-processor'
    }
    
    context = {
        'event_count': 3,  # Third occurrence
        'priority': 10
    }
    
    print("\n📌 Simulating: Critical error (3rd occurrence)")
    
    # Plan
    actions = planner.plan('error', event_data, 10, context)
    print(f"✓ Planned {len(actions)} actions")
    
    # Execute
    for action in actions:
        action_dict = {
            'type': action.type.value,
            'priority': action.priority,
            **action.params
        }
        result = executor.execute(action_dict)
        print(f"✓ Executed {action.type.value}: {result.get('status')}")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 AGENTIC SYSTEM TEST SUITE")
    print("="*60)
    
    tests = [
        ("Observer", test_observer),
        ("Planner", test_planner),
        ("Executor", test_executor),
        ("Memory", test_memory),
        ("Integration", test_integration)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"\n✅ {name} test PASSED")
            else:
                failed += 1
                print(f"\n❌ {name} test FAILED")
        except Exception as e:
            failed += 1
            print(f"\n❌ {name} test FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    print("="*60)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED - System ready!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
