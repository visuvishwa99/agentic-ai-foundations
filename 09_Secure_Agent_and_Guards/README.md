# Week 9: input and SQL guards

This folder contains simple examples for prompt screening, PII masking, and SQL keyword checks.

## Files

- `[1.0]_input_guard.py` uses Presidio for PII masking and a short keyword list for prompt-injection examples.
- `[2.0]_output_guard.py` blocks several SQL keywords and multiple statements.
- `[3.0]_secure_agent.py` places both checks around the Week 8 SQL generator.

These guards are demonstrations, not a security boundary. The SQL check is string-based. It does not parse an AST, enforce table ownership, or replace a read-only database role. Inputs such as `CALL`, `COPY`, and reads from an unauthorized schema need stronger controls than this code provides.

## Run

```bash
python "09_Secure_Agent_and_Guards/[1.0]_input_guard.py"
python "09_Secure_Agent_and_Guards/[2.0]_output_guard.py"
python "09_Secure_Agent_and_Guards/[3.0]_secure_agent.py"
```

## Notes for revision

Prompt filtering, SQL validation, authorization, and database permissions are different controls. A production design needs all of them at the correct boundary.
