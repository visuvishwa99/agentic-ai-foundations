---
trigger: always_on
---
# Follow roadmap.md

# AI Project Documentation & Visualization Standards

This file defines the strict rules for organizing folders, explaining technical topics, and creating visual diagrams across all weeks.

## 📁 1. Folder & File Organization Rules
- **Naming Convention**: All active script files must follow the numbering pattern: `[Section.Sub-section]_filename.py` (e.g., `[1.1]_Embeddings.py`).
- **README per Week**: Every week folder must contain a `README.md` that serves as the "source of truth" for that unit.
- **MMD Files**: Every week should have at least one Mermaid (`.mmd`) file explaining the core architecture or the specific script logic.

## 📚 2. Topic Explanation Rules (The "Jargon" Rule)
When explaining a new technical concept or "jargon," follow this 3-step structure used in Week 4:
1.  **Simple definition**: Use a "Layman's terms" first sentence.
2.  **Technical context**: Explain *why* it is used in the specific script/pipeline.
3.  **Visual comparison (Optional but encouraged)**: Mention how it compares to other methods (e.g., Fixed Size vs Semantic Chunking).
4.  **Think Like a Data Engineer (The Bridge Rule)**: When introducing AI tools, map them to data engineering equivalents to ground the concept (see table below).

### The Data Engineer's Translation Table
| Tool | Data Engineering Equivalent | Use Case |
| :--- | :--- | :--- |
| **LangGraph** | Airflow / Dagster / Prefect | DAG-based Orchestration & State Management |
| **LangSmith** | DataDog / Grafana / MLflow | Observability, Tracing & Debugging |
| **LangChain** | Pandas / Utils Scripts | Helper functions & component chaining |
| **Vector DB** | Data Warehouse (Snowflake) | Optimized storage for high-dimensional data |
| **RAG** | ETL / Reverse ETL | Fetching external context at runtime |

**Standard Jargon List to maintain:**
- Chunking, Embeddings, Cosine Similarity, Top-K, Vector DBs, Semantic Caching, RAG Pipelines.

## 🎨 3. Mermaid Diagram Design Standards

### Color Palette
- **Logic/Prompt/Decision**: `#2d3436` (Charcoal) -> `:::logic`
- **Data Storage (DBs/Cache)**: `#0984e3` (Blue) -> `:::storage`
- **Processing (Models/AI)**: `#6c5ce7` (Purple) -> `:::process`
- **User/Entrance/Output**: `#00b894` (Teal) -> `:::user`
- **Groupings (Subgraphs)**: `#f1f2f6` (Light Gray) -> `:::group`

### Global Style Block (Add to bottom of all .mmd files)
```mermaid
    classDef logic fill:#2d3436,stroke:#dfe6e9,stroke-width:2px,color:#fff
    classDef storage fill:#0984e3,stroke:#74b9ff,stroke-width:2px,color:#fff
    classDef process fill:#6c5ce7,stroke:#a29bfe,stroke-width:2px,color:#fff
    classDef user fill:#00b894,stroke:#55efc4,stroke-width:2px,color:#fff
    classDef group fill:#f1f2f6,stroke:#2f3542,stroke-width:1px,color:#2d3436
```

### Contrast Rules
- **Text Color**: Dark backgrounds (Blue, Purple, Charcoal, Teal) **MUST** use `color:#fff`.
- **Text Color**: Light backgrounds (Subgraphs/Groups) **MUST** use `color:#2d3436`.

### Technology Stack Visualization (New Requirement)
All diagrams must optionally (strongly encouraged for complex agents) include a **Technology Stack** subgraph to map libraries to components.
1.  **Create a Graph**: `subgraph Tech_Stack [System Technology Stack]`
2.  **Visual Mapping**: Use dashed arrow lines (`-.->`) to connect the stack item (e.g., `LangGraph`) to the logic flow (e.g., `Agent_Loop`).
3.  **Style**: Use a white background for the specific stack node to differentiate it from the logic flow.
4.  **DE Metaphors**: When applicable, explicitly mention the Data Engineering equivalent in the node label using the format: `(like [Tool] in DE)`.
    *   Example: `<b>ChromaDB</b><br/>Vector DB (like Snowflake in DE)`