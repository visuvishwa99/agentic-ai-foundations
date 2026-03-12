# Week 12: Self-Evaluation and Red Team Week

## Weekly Goals
1.  **Red Teaming**: Actively try to break your AI agents with adversarial attacks.
2.  **Self-Correction**: Implement loops where the agent checks its own work.
3.  **Failure Analysis**: Document how/why agents fail (Hallucination, Tool Error, Context Win).

## Resources
- [Ragas](https://docs.ragas.io/en/stable/) (RAG Assessment)
- [Giskard](https://docs.giskard.ai/en/latest/) (AI Quality)
- [Prompt Injection List](https://github.com/minimaxir/big-list-of-naughty-strings)

## Architecture: The Resilient Agent

### 1. The Red Teamer (Attacker)
**Implemented in:** `[1.0]_red_teamer.py`
-   **Role**: Automatically generates adversarial prompts to test system robustness.
-   **Output**: A list of "attacks" (e.g., "Ignore previous instructions", "Drop table users").

### 2. The Evaluator (Judge)
**Implemented in:** `[2.0]_evaluator.py`
-   **Role**: Scores the agent's response to the attacks.
-   **Metrics**:
    -   **Refusal Rate**: Did the agent correctly refuse the attack?
    -   **Safety Score**: 0-1 score based on whether PII was leaked or harmful actions taken.

### 3. The Self-Correcting Agent
**Implemented in:** `[3.0]_self_correcting_agent.py`
-   **Logic**:
    1.  Generate Initial Response.
    2.  Self-Critique: "Is this safe? Does it answer the user?"
    3.  If unsafe/wrong -> Regenerate with improved prompt.
    4.  Final Output.

## Jargon Buster

| Term | Simple Definition | Technical Context | DE Equivalent |
| :--- | :--- | :--- | :--- |
| **Red Teaming** | Playing "devil's advocate" to find security holes. | Adversarial testing of AI models. | **Penetration Testing** |
| **Constitutional AI** | Giving the AI a "constitution" (rules) to follow. | RLAIF (Reinforcement Learning from AI Feedback). | **Policy Constraints** (IAM Roles) |
| **Hallucination Rate** | How often the AI makes stuff up. | Percentage of generated facts not found in source context. | **Data Quality Error Rate** |
| **Refusal** | When the model politely declines a request. | "I cannot fulfill this request due to safety guidelines." | **Access Denied (403)** |

## Experiments and Deliverables
-   [ ] **Attack Suite**: Run 10 different attacks against your Week 11 agent.
-   [ ] **Scorecard**: Evaluate the agent's defense (e.g., 8/10 blocked).
-   [ ] **Self-Reflection**: Enhance the agent to catch its own mistakes before outputting.

## How to Run

### Run the Self-Correcting Agent
This script demonstrates the response -> critique -> regenerate loop.
```bash
python week12/[3.0]_self_correcting_agent.py
```

### Run Red Teaming Attacks
Generate and evaluate adversarial prompts.
```bash
python week12/[1.0]_red_teamer.py
python week12/[2.0]_evaluator.py
```
