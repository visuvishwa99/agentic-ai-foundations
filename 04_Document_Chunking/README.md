# Week 4: document chunking

These scripts compare a basic text chunker with a version that treats tables and narrative text differently.

## Files

- `[0.1]_chunk_system.py` contains the basic chunking, overlap, validation, and retrieval logic.
- `[1.1]_advancedchunkingsystem.py` adds element-aware parsing and gives table chunks a score boost for numeric questions.
- The `.mmd` files contain the diagrams I used while learning the flow.

The table boost is a hand-written rule, not a learned ranking model. It can improve one query and hurt another, so it should be tested against a real retrieval set before reuse.

## Run

```bash
python "04_Document_Chunking/[0.1]_chunk_system.py"
python "04_Document_Chunking/[1.1]_advancedchunkingsystem.py"
```

## Notes for revision

Chunk size, overlap, parser output, and retrieval metric all affect the result. Changing several at once makes it hard to tell which change helped.
