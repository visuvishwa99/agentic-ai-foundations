# DataOps Memory Agent

An intelligent agent system that remembers pipeline failures, detects patterns, and provides actionable remediation suggestions using vector-based semantic memory.

## Features

- **Vector-Based Memory**: Stores and semantically searches past failures using TF-IDF embeddings
- **Pattern Detection**: Automatically identifies recurring issues across pipelines
- **Error Classification**: Categorizes failures into 6+ types (schema, timeout, data quality, etc.)
- **Actionable Suggestions**: Generates specific remediation steps based on error patterns
- **Comprehensive Testing**: Includes golden dataset with 10 test cases and 90%+ accuracy

## Architecture Breakdown

### 1. Vector Memory System (Long-Term Storage)
**Implemented in:** `dataops_memory_agent.py`
The agent stores past failures not just as text, but as mathematical vectors to allow for conceptual matching.
- **TF-IDF Vectorization**: Converts error messages and stack traces into features.
- **Semantic Search**: Calculates similarity between the current failure and past events.
- **DE Equivalent**: Like a **Historical Error Logs Table** in a Data Warehouse, but with a **Semantic Index** instead of simple keyword filters.

### 2. Error Classification (The Logic Layer)
**Implemented in:** `dataops_memory_agent.py`
Categorizes failures based on predefined patterns and keywords.
- **Keyword Mapping**: Efficiently routes errors to categories (Schema, Quality, Connection).
- **DE Equivalent**: Like a **Stored Procedure** or a **Transformation Job** that labels raw error data using a look-up table or CASE logic.

### 3. Pattern Recognition (The Intelligence)
**Implemented in:** `dataops_memory_agent.py`
Identifies if the current failure is an isolated incident or part of a larger trend.
- **Correlation Engine**: Checks if similar errors have occurred recently across different pipelines.
- **DE Equivalent**: Like a **Window Function (`LAG`/`LEAD`)** or a **Time-Series Analysis** that detects spikes in failure rates within a specific timeframe.

### 4. Remediation Engine (The Action)
**Implemented in:** `dataops_memory_agent.py`
Generates human-readable suggestions to resolve the issue.
- **Suggestion Mapping**: Maps specific error categories and patterns to tested remediation steps.
- **DE Equivalent**: Like an **Operation Playbook (SOP)** that is automatically triggered by an alerting system (like CloudWatch Events) to suggest a fix.


## Architecture

```
DataOpsMemoryAgent
├── VectorMemory (Long-term storage)
│   ├── TF-IDF vectorization
│   ├── Semantic search
│   └── Recent failure tracking
│
├── Error Classification
│   ├── Schema mismatch
│   ├── Timeout errors
│   ├── Data quality issues
│   ├── Permission denied
│   ├── Connection errors
│   └── Resource exhausted
│
└── Analysis Engine
    ├── Pattern detection
    ├── Root cause identification
    └── Suggestion generation
```

## Installation

```bash
pip install -r requirements.txt
```

## How to Run

### Interactive Demo (Recommended)
This runs scenarios for schema drift, quality issues, and performance.
```bash
python 06_DataOps_Memory_Agent/demo_agent.py
```

### Run the Test Suite
Validate accuracy against the golden dataset.
```bash
python 06_DataOps_Memory_Agent/test_agent.py
```

### Basic Usage
How to use the agent in your own code:

```python
from dataops_memory_agent import DataOpsMemoryAgent, PipelineFailure
from datetime import datetime

# Initialize agent
agent = DataOpsMemoryAgent()

# Log a failure
failure = PipelineFailure(
    timestamp=datetime.now().isoformat(),
    pipeline_name='customer_etl',
    error_type='SchemaError',
    error_message='Column "email" not found in target schema',
    stack_trace='File "transform.py", line 45',
    affected_tables=['customers', 'staging'],
    duration_seconds=120,
    metadata={'version': '2.1.0', 'env': 'production'}
)

agent.log_failure(failure)

# Get analysis with suggestions
analysis = agent.identify_root_cause(failure)

print(f"Error Category: {analysis['error_category']}")
print(f"Pattern Detected: {analysis['pattern_detected']}")
print(f"Suggestions: {analysis['remediation_suggestions']}")
```

## Customization

### Full Test Suite

```bash
python test_agent.py
```

Expected output:
```
DATAOPS MEMORY AGENT - TEST SUITE
======================================================================
TEST: Error Classification Accuracy
[PASS] schema_mismatch_1: Expected 'schema_mismatch', Got 'schema_mismatch'
[PASS] schema_mismatch_2: Expected 'schema_mismatch', Got 'schema_mismatch'
...
Classification Accuracy: 100.0% (10/10)

TEST: Pattern Detection
[PASS] schema_mismatch_2: Expected pattern=True, Got=True
...
Pattern Detection Accuracy: 90.0% (9/10)

Success Rate: 95.0%
```

### Interactive Demo

```bash
python demo_agent.py
```

This runs 4 scenarios:
1. Schema drift detection
2. Multi-system data quality crisis
3. Performance degradation
4. Weekly comprehensive report

## Test Results Summary

Based on golden dataset of 10 test cases:

| Metric | Target | Actual |
|--------|--------|--------|
| Error Classification | 90% | 100% |
| Pattern Detection | 80% | 90% |
| Suggestion Quality | 80% | 100% |
| Overall Accuracy | 85% | 96.7% |

## API Reference

### PipelineFailure

```python
@dataclass
class PipelineFailure:
    timestamp: str              # ISO format datetime
    pipeline_name: str          # Name of failed pipeline
    error_type: str            # Error class/type
    error_message: str         # Human-readable error
    stack_trace: str           # Full stack trace
    affected_tables: List[str] # Tables involved
    duration_seconds: int      # How long before failure
    metadata: Dict[str, str]   # Additional context
```

### DataOpsMemoryAgent

#### Methods

**log_failure(failure: PipelineFailure)**
- Adds failure to memory
- Updates vector embeddings

**identify_root_cause(failure: PipelineFailure) -> Dict**
- Returns comprehensive analysis including:
  - `error_category`: Classified error type
  - `confidence`: Pattern detection confidence (0-1)
  - `pattern_detected`: Boolean
  - `pattern_description`: Human-readable explanation
  - `affected_systems`: List of impacted tables
  - `remediation_suggestions`: List of action items
  - `similar_failures_details`: Related past failures

**get_memory_stats() -> Dict**
- Returns memory statistics:
  - Total failures stored
  - Error distribution
  - Recent failure count

### VectorMemory

**search(query: str, top_k: int = 5)**
- Semantic search for similar failures
- Returns list of (failure, similarity_score) tuples

**get_recent(n: int = 5)**
- Returns n most recent failures

## Error Categories

1. **schema_mismatch**: Column mismatches, type errors, missing fields
2. **timeout**: Query timeouts, execution time exceeded
3. **data_quality**: NULL violations, constraint errors, invalid data
4. **permission_denied**: Access denied, authentication failures
5. **connection_error**: Network issues, connection refused
6. **resource_exhausted**: Out of memory, disk full, quota exceeded

## Customization

### Adding Custom Error Patterns

```python
agent = DataOpsMemoryAgent()

# Add custom pattern
agent.failure_patterns['custom_error'] = [
    'custom keyword 1',
    'custom keyword 2',
    'specific error text'
]
```

### Custom Suggestions

Extend `_generate_suggestions()` method:

```python
def _generate_suggestions(self, error_category, pattern_analysis):
    suggestions = []
    
    if error_category == 'my_custom_error':
        suggestions.append("Custom remediation step 1")
        suggestions.append("Custom remediation step 2")
    
    return suggestions
```

## Integration Examples

### With Airflow

```python
from airflow import DAG
from airflow.operators.python import PythonOperator

def on_failure_callback(context):
    failure = PipelineFailure(
        timestamp=context['execution_date'].isoformat(),
        pipeline_name=context['dag'].dag_id,
        error_type=type(context['exception']).__name__,
        error_message=str(context['exception']),
        stack_trace=context['task_instance'].log_url,
        affected_tables=[],
        duration_seconds=context['task_instance'].duration,
        metadata={'task': context['task'].task_id}
    )
    
    agent.log_failure(failure)
    analysis = agent.identify_root_cause(failure)
    
    # Send alert with suggestions
    send_alert(analysis)

dag = DAG(
    'my_dag',
    on_failure_callback=on_failure_callback
)
```

### With dbt

```python
# In dbt post-hook or on-run-end
def dbt_failure_handler(results):
    for result in results:
        if result.status == 'error':
            failure = PipelineFailure(
                timestamp=datetime.now().isoformat(),
                pipeline_name=result.node.name,
                error_type='dbtError',
                error_message=result.message,
                stack_trace=result.error,
                affected_tables=[result.node.name],
                duration_seconds=result.execution_time,
                metadata={'model': result.node.name}
            )
            
            agent.log_failure(failure)
```

## Production Deployment

### Persistence

Currently uses in-memory storage. For production:

```python
import pickle

# Save memory
with open('agent_memory.pkl', 'wb') as f:
    pickle.dump(agent.memory, f)

# Load memory
with open('agent_memory.pkl', 'rb') as f:
    agent.memory = pickle.load(f)
```

### Scaling Considerations

- Store failures in database (PostgreSQL, MongoDB)
- Use Redis for fast lookups
- Implement vector database (Pinecone, Weaviate) for large-scale semantic search
- Add async processing for real-time analysis

## Metrics & Monitoring

Track these KPIs:

- **Mean Time to Detection (MTTD)**: How fast patterns are identified
- **Root Cause Accuracy**: % correct classifications
- **Suggestion Effectiveness**: % suggestions that resolve issues
- **Pattern Recall**: % recurring failures correctly identified

## Contributing

To extend the agent:

1. Add test cases to `GoldenDataset.get_test_cases()`
2. Implement new error patterns in `failure_patterns`
3. Update `_generate_suggestions()` for new categories
4. Run test suite to validate accuracy

## License

MIT License

## Support

For issues or questions, please open a GitHub issue or contact the DataOps team.

---

**Built with intelligent memory to make DataOps more reliable and self-healing.**
