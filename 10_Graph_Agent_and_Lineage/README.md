# Week 10: lineage graph

This folder turns a few sample SQL files into a small directed lineage graph.

## Files

- `[1.0]_lineage_mapper.py` asks a local model to extract source and target tables from SQL.
- `[2.0]_graph_builder.py` loads `graph_data.json` into NetworkX and can generate an HTML view.
- `[3.0]_graph_agent.py` answers upstream and downstream questions with graph traversal tools.
- `sql/` contains the sample models.
- `graph_data.json` is a checked-in fixture so the graph exercises can run without regenerating it first.

`lineage_graph.html` is generated output and is not tracked.

## Run

```bash
python "10_Graph_Agent_and_Lineage/[1.0]_lineage_mapper.py"
python "10_Graph_Agent_and_Lineage/[2.0]_graph_builder.py"
python "10_Graph_Agent_and_Lineage/[3.0]_graph_agent.py"
```

## Notes for revision

LLM extraction can miss aliases, CTEs, dynamic SQL, and macros. Graph traversal is deterministic only after the lineage data is correct.
