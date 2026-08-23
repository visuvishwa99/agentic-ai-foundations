# Week 13: tracing and regression checks

This folder explores local tracing with Phoenix and a small model-response regression suite.

## Files

- `[1.0]_observable_agent.py` instruments the SQL-agent path.
- `[2.0]_regression_test.py` contains optional model checks that need Phoenix and the observability dependencies.
- `[3.0]_dashboard.py` starts Phoenix and reads trace data.

These checks are not part of the default pytest run because they require optional services and model inference.

## Run

```bash
python "13_Observable_Agent_and_Dashboard/[3.0]_dashboard.py"
python "13_Observable_Agent_and_Dashboard/[1.0]_observable_agent.py"
python "13_Observable_Agent_and_Dashboard/[2.0]_regression_test.py"
```

## Notes for revision

A trace proves that a call happened. It does not prove that the answer was correct. Keep latency, errors, retrieval quality, and answer checks separate.
