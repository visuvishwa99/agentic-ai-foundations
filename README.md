# Agentic AI Foundations

A hands-on learning repo for the foundations behind AI-assisted DataOps and agentic data platform workflows.

This repo collects small projects, notes, and examples around LLM concepts, embeddings, RAG, document chunking, agent memory, SQL agents, guardrails, observability, and human review. The goal is to understand the building blocks before combining them into larger AI-ready data systems.

## Why This Repo Exists

AI agents are becoming easier to demo, but harder to operate responsibly. For data engineering use cases, the agent is only one part of the system.

The bigger questions are:

- How is context retrieved?
- How are documents chunked?
- What memory should the agent keep?
- How does the agent choose a model or tool?
- How do we guard against unsafe actions?
- How do we evaluate whether the agent is correct?
- How do we make the workflow observable?

This repo breaks those questions into focused modules.

## Repository Structure

```text
agentic-ai-foundations/
├── 01_LLM_concepts/
├── 03_Vector_DBs_and_Embeddings/
├── 04_Document_Chunking/
├── 05_Alerting_Agent/
├── 06_DataOps_Memory_Agent/
├── 07_Advanced_RAG_and_Search/
├── 08_Model_Routing_and_SQL_Agent/
├── 09_Secure_Agent_and_Guards/
├── 10_Graph_Agent_and_Lineage/
├── 11_Interactive_Agent_and_Human_Review/
├── 12_Self_Correcting_Agent_and_Eval/
├── 13_Observable_Agent_and_Dashboard/
├── 14_5_MCP_Client_and_Server/
├── 14_Agent_API_and_Docker/
├── 15_LLM_optimizations/
├── all_requirements.txt
└── roadmap.md
```

## Topics Covered

- LLM fundamentals
- embeddings and vector search
- document chunking
- RAG and search patterns
- alerting agents
- DataOps memory agents
- model routing
- SQL agent workflows
- secure agents and guardrails
- graph agents and lineage
- human-in-the-loop review
- self-correction and evaluation
- observability dashboards
- MCP client/server basics
- API and Docker packaging
- LLM optimization patterns

## How This Connects To My Data Engineering Work

My interest is not in replacing data engineering with AI. It is in understanding how AI can sit on top of good data engineering.

For AI-assisted DataOps to be useful, the underlying platform still needs:

- reliable pipelines
- clear metadata
- strong lineage
- observable jobs
- governed access
- repeatable operations
- human review for risky decisions

This repo explores the AI side of that equation while keeping the data platform mindset in view.

## What This Demonstrates

- Learning AI foundations through working modules instead of scattered notes
- Connecting RAG, memory, tools, and guardrails to real DataOps use cases
- Thinking about AI workflows as systems that need testing and observability
- Building toward AI-ready data platform patterns

## Suggested Reading Path

1. Start with `01_LLM_concepts`
2. Move into embeddings and document chunking
3. Study RAG and search
4. Explore memory, SQL agents, and graph lineage
5. Review guardrails, evaluation, and observability
6. Finish with API, Docker, MCP, and optimization modules

## Related Writing Ideas

- What data engineers should learn before building AI agents
- Why RAG quality starts with document structure
- Designing AI-assisted DataOps workflows with memory and guardrails
- Human review patterns for SQL and data platform agents
