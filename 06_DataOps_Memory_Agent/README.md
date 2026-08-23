# Week 6: DataOps memory agent

This exercise stores synthetic pipeline failures, classifies them with keyword rules, and uses TF-IDF similarity to find related failures.

## Files

- `dataops_memory_agent.py` contains the failure model, in-memory vector store, classifier, and suggestion rules.
- `demo_agent.py` runs a few synthetic failure scenarios.
- `test_agent.py` contains the deterministic test cases.
- `generate_metrics.py` creates a text report and an optional HTML dashboard.

The reported percentages come from ten repository-authored cases. They show whether the current rules still match those fixtures. They do not measure production accuracy.

## Run

From the repository root:

```bash
.venv/Scripts/python.exe "06_DataOps_Memory_Agent/demo_agent.py"
.venv/Scripts/python.exe -m pytest -q "06_DataOps_Memory_Agent/test_agent.py"
.venv/Scripts/python.exe "06_DataOps_Memory_Agent/generate_metrics.py"
```

`dashboard.html` and `metrics_report.txt` are generated locally and are not tracked.

## Notes for revision

This is a rule-based classifier with TF-IDF retrieval. It is useful for studying state and similarity, but it is not an autonomous incident-remediation system.
