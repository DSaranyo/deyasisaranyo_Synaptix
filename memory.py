"""
Memory Component - State Management using Pathway Reducers
Maintains agent's internal state across stream processing
"""

import pathway as pw
from typing import Dict, List, Any
from collections import defaultdict
import json


class AgentMemory:
    """
    Agent's memory system using Pathway's reducer mechanism
    Tracks patterns, frequencies, and historical context
    """
    
    def __init__(self):
        # Memory schemas for different aspects
        self.event_history_limit = 100
        self.pattern_threshold = 3  # For pattern detection
    
    def create_event_memory(self, events: pw.Table) -> pw.Table:
        """
        Create event-based memory using Pathway reducers
        Tracks event frequencies and patterns
        """
        
        # Aggregate events by type to detect patterns
        event_patterns = events.groupby(pw.this.event_type).reduce(
            event_type=pw.this.event_type,
            total_count=pw.reducers.count(),
            first_seen=pw.reducers.earliest(pw.this.timestamp),
            last_seen=pw.reducers.latest(pw.this.timestamp),
            # Track recent events using tuple reducer
            recent_events=pw.reducers.tuple(pw.this.data)
        )
        
        return event_patterns
    
    def create_priority_memory(self, events: pw.Table) -> pw.Table:
        """
        Track priority-based patterns
        Identifies high-priority event clusters
        """
        
        # Filter high priority events
        high_priority_events = events.filter(pw.this.priority >= 7)
        
        # Group by event type and track urgency patterns
        priority_patterns = high_priority_events.groupby(
            pw.this.event_type
        ).reduce(
            event_type=pw.this.event_type,
            urgent_count=pw.reducers.count(),
            max_priority=pw.reducers.max(pw.this.priority),
            avg_priority=pw.reducers.avg(pw.this.priority)
        )
        
        return priority_patterns
    
    def create_temporal_memory(self, events: pw.Table) -> pw.Table:
        """
        Temporal memory - tracks event timing and sequences
        Uses sliding window approach
        """
        
        # Use Pathway's windowing to track recent activity
        # Group events in 5-minute windows
        windowed_events = events.windowby(
            pw.this.timestamp,
            window=pw.temporal.sliding(
                duration=pw.Duration('5m'),
                hop=pw.Duration('1m')
            ),
            behavior=pw.temporal.common_behavior(cutoff=None)
        ).reduce(
            window_start=pw.this._pw_window_start,
            window_end=pw.this._pw_window_end,
            event_count=pw.reducers.count(),
            event_types=pw.reducers.tuple(pw.this.event_type),
            max_priority=pw.reducers.max(pw.this.priority)
        )
        
        return windowed_events
    
    def create_error_memory(self, events: pw.Table) -> pw.Table:
        """
        Specialized memory for error tracking
        Maintains error patterns and recurring issues
        """
        
        # Filter error events
        error_events = events.filter(
            pw.this.event_type == 'error'
        )
        
        # Extract error signatures for grouping similar errors
        error_memory = error_events.select(
            *pw.this,
            error_signature=pw.apply(
                self._extract_error_signature,
                pw.this.data
            )
        )
        
        # Group by error signature to detect recurring issues
        recurring_errors = error_memory.groupby(
            pw.this.error_signature
        ).reduce(
            error_signature=pw.this.error_signature,
            occurrence_count=pw.reducers.count(),
            first_occurrence=pw.reducers.earliest(pw.this.timestamp),
            last_occurrence=pw.reducers.latest(pw.this.timestamp)
        )
        
        return recurring_errors
    
    def _extract_error_signature(self, data: str) -> str:
        """
        Extract a signature from error data for grouping
        """
        try:
            data_dict = json.loads(data)
            message = data_dict.get('message', '')
            service = data_dict.get('service', 'unknown')
            
            # Create a simplified signature
            # Remove variable parts (timestamps, IDs, etc.)
            signature_parts = [
                service,
                message.split(':')[0] if ':' in message else message[:50]
            ]
            
            return '::'.join(signature_parts)
        except:
            return 'unknown'


class MemoryRetrieval:
    """
    Utilities for querying and retrieving from agent memory
    """
    
    @staticmethod
    def check_pattern_threshold(event_count: int, threshold: int = 3) -> bool:
        """
        Check if event count exceeds pattern threshold
        """
        return event_count >= threshold
    
    @staticmethod
    def calculate_urgency_score(
        priority: int, 
        event_count: int, 
        recency_minutes: int
    ) -> float:
        """
        Calculate urgency score based on multiple factors
        Higher score = more urgent
        """
        # Base score from priority (0-10)
        score = priority
        
        # Boost for frequency (repeated events)
        if event_count > 1:
            score += min(3, event_count * 0.5)
        
        # Boost for recency (recent events more urgent)
        if recency_minutes < 5:
            score += 2
        elif recency_minutes < 15:
            score += 1
        
        return min(10.0, score)
    
    @staticmethod
    def extract_context(memory_state: Dict[str, Any]) -> str:
        """
        Extract relevant context from memory state
        """
        context_parts = []
        
        if 'event_count' in memory_state and memory_state['event_count'] > 1:
            context_parts.append(
                f"This event has occurred {memory_state['event_count']} times"
            )
        
        if 'max_priority' in memory_state:
            context_parts.append(
                f"Maximum priority seen: {memory_state['max_priority']}"
            )
        
        return '; '.join(context_parts) if context_parts else "First occurrence"


class MemoryConsolidation:
    """
    Periodic memory consolidation and cleanup
    Prevents memory bloat in long-running agent
    """
    
    @staticmethod
    def consolidate_old_events(
        memory_table: pw.Table, 
        age_threshold_hours: int = 24
    ) -> pw.Table:
        """
        Consolidate or archive old events
        """
        # In production, this would filter by timestamp
        # For demo, we keep all events
        return memory_table
    
    @staticmethod
    def identify_significant_patterns(
        event_patterns: pw.Table,
        significance_threshold: int = 5
    ) -> pw.Table:
        """
        Identify statistically significant patterns
        """
        significant = event_patterns.filter(
            pw.this.total_count >= significance_threshold
        )
        
        return significant
