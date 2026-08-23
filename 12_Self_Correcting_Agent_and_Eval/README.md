# Week 12: adversarial checks and self-correction

This folder experiments with adversarial prompts, response scoring, and a generate-review-regenerate loop.

## Files

- `[1.0]_red_teamer.py` produces a small set of attack prompts.
- `[2.0]_evaluator.py` scores sample responses with local rules.
- `[3.0]_self_correcting_agent.py` asks the model to critique and retry its answer.

The evaluator is a learning fixture. Its score is not a security benchmark, and model self-critique is not independent validation.

## Run

```bash
python "12_Self_Correcting_Agent_and_Eval/[1.0]_red_teamer.py"
python "12_Self_Correcting_Agent_and_Eval/[2.0]_evaluator.py"
python "12_Self_Correcting_Agent_and_Eval/[3.0]_self_correcting_agent.py"
```

## Notes for revision

Keep attack generation separate from evaluation. If the same model creates and grades the attacks, correlated mistakes can make the score look better than it is.
