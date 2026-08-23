# Week 11: human review

This folder adds a review step around the Week 8 SQL generator.

## Files

- `[1.0]_risk_analyzer.py` assigns a risk level from SQL keywords.
- `[2.0]_human_review.py` asks for approval in the terminal.
- `[3.0]_interactive_agent.py` combines generation, risk analysis, and review.

The example does not execute SQL. Approval is a terminal interaction, not a durable workflow or authorization system.

## Run

```bash
python "11_Interactive_Agent_and_Human_Review/[1.0]_risk_analyzer.py"
python "11_Interactive_Agent_and_Human_Review/[3.0]_interactive_agent.py"
```

## Notes for revision

A real approval flow needs an authenticated reviewer, a stored decision, the exact proposed action, an expiry time, and protection against the action changing after approval.
