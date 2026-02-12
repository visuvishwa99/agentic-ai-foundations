---
trigger: always_on
---
# Follow roadmap.md

# AI Project Documentation & Visualization Standards

This file defines the strict rules for organizing folders, explaining technical topics, and creating visual diagrams across all weeks.

## 📁 1. Folder & File Organization Rules
- **Naming Convention**: All active script files must follow the numbering pattern: `[Section.Sub-section]_filename.py` (e.g., `[1.1]_Embeddings.py`).
- **README per Week**: Every week folder must contain a `README.md` that serves as the "source of truth" for that unit.
- **MMD Files**: Every week should have at least one Mermaid (`.mmd`) file explaining the core архитекure or the specific script logic.

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

## 📝 2.1 The Explanation Format (The Walkthrough Rule)
When explaining a complex Mermaid diagram or architecture flow, ALWAYS use the following structure:
1. **Step-by-Step Breakdown**: Number each logical phase (e.g., 1. Pre-processing, 2. Retrieval).
2. **Component Function**: Explain exactly what that specific node/block does in the AI context.
3. **The DE Equivalent**: Explicitly map the AI concept to a Data Engineering concept (e.g., "Like a B-Tree Index" or "Like a Window Function").
4. **Conclusion/Why**: Briefly state the benefit of this specific architecture (e.g., "Ensures data quality" or "Optimizes for cost").


## 🎨 3. Mermaid Diagram Design Standards

### Best Practices for Mermaid Syntax (CRITICAL)
1.  **Use `flowchart TD`**: Prefer `flowchart` over `graph` for better subgraph and direction support.
2.  **Quote Node Labels**: ALWAYS quote node labels that contain whitespace or special characters (especially parentheses).
    *   ❌ `Node(Label (Text))` -> Syntax Error
    *   ✅ `Node["Label (Text)"]` -> Correct
3.  **Separate Styling**: Define styles in a separate block at the end using `class NodeName ClassName`, rather than inline `:::ClassName` which can cause parser issues.
4.  **Direction in Subgraphs**: Explicitly use `direction TB` (Top-Bottom) inside subgraphs if vertical layout is needed.

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

## 🔗 4. Script-to-Architecture Mapping Rule (The Traceability Rule)

Every Python script MUST be explicitly linked to its corresponding architecture component in **both** the Mermaid diagram and the README.

### 4.1 In Mermaid Diagrams (`.mmd` files)
1.  **Script Nodes**: Add a dedicated node for each script inside the `Tech_Stack` subgraph.
    *   Format: `ScriptName["<b>[X.Y]_filename.py</b><br/>Brief description"]`
2.  **Visual Mapping**: Use dashed arrows (`-.->`) to connect each script node to the subgraph or node it implements.
    *   Example: `HybridScript -.-> Hybrid_Search`

```mermaid
    subgraph Tech_Stack [Technology Stack & Script Mapping]
        HybridScript["<b>[1.0]_hybrid_search.py</b><br/>Implements BM25 + Vector Search"]
        AgentScript["<b>[4.0]_rag_agent.py</b><br/>Orchestrates Entire Pipeline"]
    end
    HybridScript -.-> Hybrid_Search
    AgentScript -.-> Start
```

### 4.2 In README Files (`README.md`)
1.  **"Implemented in" Tag**: Every Architecture Breakdown section header MUST include a bold `**Implemented in:**` line pointing to the script file.
2.  **Format**:
    ```markdown
    ### 1. Hybrid Search (The Search Engine)
    **Implemented in:** `[1.0]_hybrid_search.py`
    Description of the component...
    ```
3.  **Orchestrator Script**: If one script combines all components, add a final section titled "The Orchestrator" mapping it.

### Why This Rule Exists
- **Traceability**: Anyone reading the README can immediately jump to the relevant code.
- **Onboarding**: New readers understand which file does what without digging through code.
- **DE Equivalent**: Like a **Data Lineage Graph** (e.g., dbt docs, Atlan) that maps transformations back to their source models.