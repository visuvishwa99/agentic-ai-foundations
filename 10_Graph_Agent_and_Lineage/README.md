# Week 10: Data Integration and Graph RAG

## Weekly Goals
1.  **Graph RAG**: Move beyond vector similarity to *structural* understanding.
2.  **Knowledge Graph**: Build a graph of your data assets (Tables, Columns, Dashboards).
3.  **Dependency Mapping**: Answer questions like "If I change table X, what breaks?"
4.  **NetworkX Integration**: Use a lightweight graph library to model relationships.

## Resources
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag)
- [Neo4j Graph RAG](https://neo4j.com/developer-blog/graph-rag-llm-knowledge-graph/)
- [NetworkX Documentation](https://networkx.org/documentation/stable/)

## Architecture: The Lineage Agent

### 1. The Mapper (Entity Extractor)
**Implemented in:** `[1.0]_lineage_mapper.py`
Reads SQL/dbt files and uses an LLM to extract:
-   **Nodes**: Tables (`source_table`, `target_table`), Columns.
-   **Edges**: `SELECTS_FROM`, `JOINS_WITH`, `LOADS_INTO`.

### 2. The Graph Builder (NetworkX)
**Implemented in:** `[2.0]_graph_builder.py`
Takes the extracted entities and builds a directed graph (DAG).
-   **Visual**: Generates a visual plot of the data lineage.
-   **DE Equivalent**: Like the **DAG** in Airflow or the **Lineage View** in dbt.

### 3. The Graph Agent (RAG)
**Implemented in:** `[3.0]_graph_agent.py`
An agent that has access to the Graph tool.
-   **Capability**: Can traverse the graph to find upstream/downstream dependencies.
-   **Query**: "What dashboards will break if I drop table `dim_users`?"

## Jargon Buster

| Term | Simple Definition | Technical Context | DE Equivalent |
| :--- | :--- | :--- | :--- |
| **Knowledge Graph** | Data organized as connected dots (nodes) and lines (edges). | A graph database storing entities and relationships. | **ER Diagram** / **Lineage Graph** |
| **Graph RAG** | RAG, but retrieving *connected/related* info, not just similar text. | Navigating edges (A->B->C) to find indirect answers. | **Recursive SQL Queries** (CTEs) |
| **Triplets** | The basic unit of a graph: (Subject, Predicate, Object). | (Table A) -> [FEEDS] -> (Table B). | **Foreign Key Relationship** |
| **Centrality** | Finding the most "important" node in a network. | PageRank algorithm to find core tables. | **Critical Path Analysis** |

## Experiments and Deliverables
-   [ ] **Extraction**: Parse 3 SQL files into nodes/edges using LLM.
-   [ ] **Visualization**: Generate a PNG image of your data lineage graph.
-   [ ] **Query**: Ask the agent "What depends on `raw_orders`?" and get a correct list.

## How to Run

### Run the Graph Agent
This script enables the agent to traverse relationships and answer lineage questions.
```bash
python 10_Graph_Agent_and_Lineage/[3.0]_graph_agent.py
```

### Build the Knowledge Graph
Extract entities and visualize the data lineage.
```bash
python 10_Graph_Agent_and_Lineage/[1.0]_lineage_mapper.py
python 10_Graph_Agent_and_Lineage/[2.0]_graph_builder.py
```
