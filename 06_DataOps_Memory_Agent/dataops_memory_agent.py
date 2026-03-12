"""
DataOps Memory Agent with Vector-based Long-term Memory
Remembers last 5 failed pipeline runs and identifies patterns
"""

import json
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class PipelineFailure:
    """Represents a single pipeline failure event"""
    timestamp: str
    pipeline_name: str
    error_type: str
    error_message: str
    stack_trace: str
    affected_tables: List[str]
    duration_seconds: int
    metadata: Dict[str, str]
    
    def to_text(self) -> str:
        """Convert failure to searchable text"""
        return f"{self.error_type} {self.error_message} {self.pipeline_name} {' '.join(self.affected_tables)}"


class VectorMemory:
    """Vector-based memory system for semantic search"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.failures: List[PipelineFailure] = []
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.vectors = None
        
    def add(self, failure: PipelineFailure):
        """Add a failure to memory"""
        self.failures.append(failure)
        
        # Keep only recent failures
        if len(self.failures) > self.max_size:
            self.failures = self.failures[-self.max_size:]
        
        # Recompute vectors
        self._update_vectors()
    
    def _update_vectors(self):
        """Update TF-IDF vectors for all stored failures"""
        if not self.failures:
            return
        
        texts = [f.to_text() for f in self.failures]
        self.vectors = self.vectorizer.fit_transform(texts)
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[PipelineFailure, float]]:
        """Search for similar failures using semantic similarity"""
        if not self.failures or self.vectors is None:
            return []
        
        # Vectorize query
        query_vec = self.vectorizer.transform([query])
        
        # Compute similarities
        similarities = cosine_similarity(query_vec, self.vectors)[0]
        
        # Get top-k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = [
            (self.failures[idx], float(similarities[idx]))
            for idx in top_indices
        ]
        
        return results
    
    def get_recent(self, n: int = 5) -> List[PipelineFailure]:
        """Get n most recent failures"""
        return self.failures[-n:] if self.failures else []


class DataOpsMemoryAgent:
    """Intelligent agent that analyzes pipeline failures with memory"""
    
    def __init__(self):
        self.memory = VectorMemory(max_size=100)
        self.failure_patterns = {
            'schema_mismatch': ['schema', 'column', 'type mismatch', 'field not found'],
            'timeout': ['timeout', 'timed out', 'execution time exceeded'],
            'data_quality': ['null value', 'constraint violation', 'invalid data', 'data quality'],
            'permission_denied': ['permission denied', 'access denied', 'authentication failed'],
            'connection_error': ['connection refused', 'network error', 'unable to connect'],
            'resource_exhausted': ['out of memory', 'disk full', 'quota exceeded']
        }
    
    def log_failure(self, failure: PipelineFailure):
        """Log a new failure to memory"""
        self.memory.add(failure)
    
    def identify_root_cause(self, current_failure: PipelineFailure) -> Dict[str, any]:
        """Analyze current failure and identify root cause using memory"""
        
        # Get similar past failures
        similar_failures = self.memory.search(current_failure.to_text(), top_k=5)
        recent_failures = self.memory.get_recent(5)
        
        # Classify error type
        error_category = self._classify_error(current_failure)
        
        # Find patterns in recent failures
        pattern_analysis = self._analyze_patterns(recent_failures, current_failure)
        
        # Generate remediation suggestions
        suggestions = self._generate_suggestions(error_category, pattern_analysis)
        
        return {
            'error_category': error_category,
            'confidence': pattern_analysis['confidence'],
            'similar_past_failures': len(similar_failures),
            'pattern_detected': pattern_analysis['pattern_detected'],
            'pattern_description': pattern_analysis['description'],
            'affected_systems': pattern_analysis['affected_systems'],
            'remediation_suggestions': suggestions,
            'similar_failures_details': [
                {
                    'timestamp': f.timestamp,
                    'pipeline': f.pipeline_name,
                    'error': f.error_type,
                    'similarity': round(score, 3)
                }
                for f, score in similar_failures[:3]
            ]
        }
    
    def _classify_error(self, failure: PipelineFailure) -> str:
        """Classify the error into a category"""
        error_text = failure.to_text().lower()
        
        for category, keywords in self.failure_patterns.items():
            if any(keyword in error_text for keyword in keywords):
                return category
        
        return 'unknown'
    
    def _analyze_patterns(self, recent_failures: List[PipelineFailure], 
                          current_failure: PipelineFailure) -> Dict[str, any]:
        """Analyze patterns in recent failures"""
        
        if not recent_failures:
            return {
                'pattern_detected': False,
                'confidence': 0.0,
                'description': 'No recent failures to compare',
                'affected_systems': []
            }
        
        # Get current error category
        current_error_type = self._classify_error(current_failure)
        
        # Count occurrences of current error type in recent history
        same_error_count = 1  # Current failure
        error_counts = {current_error_type: 1}
        affected_systems = set(current_failure.affected_tables)
        
        for failure in recent_failures:
            error_type = self._classify_error(failure)
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
            affected_systems.update(failure.affected_tables)
            
            if error_type == current_error_type:
                same_error_count += 1
        
        # Pattern detected if current error type appears 2+ times in recent history
        pattern_detected = same_error_count >= 2
        confidence = min(same_error_count / (len(recent_failures) + 1), 1.0)
        
        description = f"No clear pattern" if not pattern_detected else \
                      f"Recurring {current_error_type} errors ({same_error_count} occurrences)"
        
        return {
            'pattern_detected': pattern_detected,
            'confidence': confidence,
            'description': description,
            'affected_systems': list(affected_systems),
            'error_distribution': error_counts
        }
    
    def _generate_suggestions(self, error_category: str, 
                             pattern_analysis: Dict) -> List[str]:
        """Generate actionable remediation suggestions"""
        
        suggestions = []
        
        # Category-specific suggestions
        if error_category == 'schema_mismatch':
            suggestions.append("Review recent schema changes in source and target tables")
            suggestions.append("Validate data type mappings in transformation logic")
            suggestions.append("Check for new columns added to source without updating pipeline")
        
        elif error_category == 'timeout':
            suggestions.append("Analyze query execution plan for inefficiencies")
            suggestions.append("Consider increasing timeout threshold or implementing pagination")
            suggestions.append("Review recent data volume increases")
        
        elif error_category == 'data_quality':
            suggestions.append("Implement data validation checks earlier in pipeline")
            suggestions.append("Review source data quality rules")
            suggestions.append("Add null-handling logic for affected fields")
        
        elif error_category == 'permission_denied':
            suggestions.append("Verify service account credentials are valid")
            suggestions.append("Review IAM permissions for affected resources")
            suggestions.append("Check for recent access policy changes")
        
        elif error_category == 'connection_error':
            suggestions.append("Verify network connectivity to data sources")
            suggestions.append("Check firewall rules and security groups")
            suggestions.append("Implement retry logic with exponential backoff")
        
        else:
            suggestions.append("Review error logs for additional context")
            suggestions.append("Check system resource utilization")
        
        # Pattern-based suggestions
        if pattern_analysis['pattern_detected']:
            suggestions.insert(0, f"URGENT: {pattern_analysis['description']} - investigate systemic issue")
        
        if len(pattern_analysis.get('affected_systems', [])) > 3:
            suggestions.append(f"Multiple systems affected ({len(pattern_analysis['affected_systems'])}) - check upstream dependencies")
        
        return suggestions

    def get_memory_stats(self) -> Dict[str, any]:
        """Get statistics about stored failures"""
        recent = self.memory.get_recent(5)
        
        error_types = {}
        for failure in recent:
            error_type = self._classify_error(failure)
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_failures_in_memory': len(self.memory.failures),
            'recent_failures_count': len(recent),
            'error_type_distribution': error_types,
            'most_recent_failure': recent[-1].timestamp if recent else None
        }
