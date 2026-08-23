# Week 5: log monitoring agent

This was my first attempt at seeing a LangGraph loop in code instead of only reading about it. I wanted to watch the agent choose a tool, receive the result, and decide whether to continue.

This is a local demo. `read_logs` returns a hard-coded log sample and `check_job_status` returns a fixture. The Discord tool makes a real HTTP request only when I give it a real webhook.

## What is in the script

`AlertingAgent.py` has three tools:

- `read_logs` returns a sample containing a database timeout.
- `check_job_status` returns a sample job state.
- `post_to_discord` sends an optional webhook message.

The graph keeps the messages and retry count in a typed state object. I used this to see how a tool call comes back into the agent before the next decision.

## Local model

This older lesson still uses Ollama through `ChatOllama`:

```text
qwen2.5-coder:1.5b
```

Week 8 uses LM Studio instead. I have kept this lesson on Ollama so I can compare the two local-model integrations later.

## Optional settings

LangSmith tracing needs `LANGCHAIN_API_KEY`. Discord needs `DISCORD_WEBHOOK_URL`. I should leave both unset when I only want to revise the graph locally.

Never commit a real webhook URL or API key.

## Run

From the repository root:

```bash
python 05_Alerting_Agent/AlertingAgent.py
```

The old `output*.log` files are failed runs I kept for debugging history. New log files are ignored by Git.

## Things I tend to forget

- Does the model return a real tool call or JSON text that needs parsing?
- Does the retry count stop where I expect it to stop?
- Is tracing disabled cleanly when there is no LangSmith key?
- Is the webhook read from the environment instead of being copied into the file?
