"""
ENHANCED CHUNKING WITH DOCUMENT PARSING
Demonstrates: Unstructured.io integration + table handling
"""

import re
import json
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np

# Simulating unstructured.io output (install with: pip install unstructured)
# from unstructured.partition.auto import partition

class AdvancedChunkingSystem:
    """
    Chunking system that handles parsed document elements
    """
    
    def __init__(self, chunk_size: int = 512, overlap_percent: float = 0.2):
        self.chunk_size = chunk_size
        self.overlap = int(chunk_size * overlap_percent)
        self.embed_model = SentenceTransformer('all-MiniLM-L6-v2')
        # LlamaParse API key would normally be set here or in env
        # self.llama_parse_key = "LLAMA_CLOUD_API_KEY"
        
    def parse_with_llamaparse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Simulates parsing with LlamaParse - Excellent for complex PDFs and tables.
        In a real app, uses: llama_parse.LlamaParse(result_type="markdown")
        """
        print(f"\n--- Simulating LlamaParse for {file_path} ---")
        return [
            {"type": "Title", "content": "Complex Financial Audit Report"},
            {"type": "Table", "content": "| Quarter | Revenue |\n|---|---|\n| Q1 | $10M |"},
            {"type": "NestedList", "content": [
                {"text": "Revenue Drivers", "level": 1},
                {"text": "Domestic Sales", "level": 2}
            ]}
        ]

    def parse_with_unstructured(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Simulates parsing with Unstructured.io
        Returns structured elements: text, tables, titles, images
        """
        print(f"\n--- Simulating Unstructured.io for {file_path} ---")
        return [
            {"type": "Title", "content": "Q4 Sales Report"},
            {"type": "NarrativeText", "content": "Our Q4 performance exceeded expectations."},
            {"type": "Table", "content": {"headers": ["Region", "Sales"], "rows": [["North", "$1.2M"]]}},
            {"type": "Image", "content": "chart_q4.png", "caption": "Monthly sales trend"}
        ]
    
    def chunk_structured_document(self, elements: List[Dict[str, Any]], 
                                  doc_name: str = "document") -> List[Dict[str, Any]]:
        """
        Chunks a document while preserving element structure
        Key insight: Tables and images need special handling
        """
        chunks = []
        current_text_buffer = []
        current_buffer_size = 0
        
        for idx, element in enumerate(elements):
            elem_type = element["type"]
            content = element["content"]
            
            # STRATEGY 1: Tables get their own chunk
            if elem_type == "Table":
                # Flush any accumulated text first
                if current_text_buffer:
                    chunks.append(self._create_chunk_from_buffer(
                        current_text_buffer, doc_name, len(chunks), "text"
                    ))
                    current_text_buffer = []
                    current_buffer_size = 0
                
                # Convert table to markdown for better retrieval
                table_markdown = self._table_to_markdown(content)
                chunks.append({
                    "content": table_markdown,
                    "chunk_id": f"{doc_name}_table_{len(chunks)}",
                    "chunk_type": "table",
                    "element_type": "Table",
                    "source_doc": doc_name,
                    "chunk_position": len(chunks),
                    "table_data": content  # Preserve original structure
                })
            
            # STRATEGY 2: Images reference with caption
            elif elem_type == "Image":
                if current_text_buffer:
                    chunks.append(self._create_chunk_from_buffer(
                        current_text_buffer, doc_name, len(chunks), "text"
                    ))
                    current_text_buffer = []
                    current_buffer_size = 0
                
                caption = element.get("caption", "")
                chunks.append({
                    "content": f"[Image: {content}] {caption}",
                    "chunk_id": f"{doc_name}_image_{len(chunks)}",
                    "chunk_type": "image_reference",
                    "element_type": "Image",
                    "source_doc": doc_name,
                    "image_path": content,
                    "caption": caption,
                    "chunk_position": len(chunks)
                })
            
            # STRATEGY 3: Nested Structures (Lists)
            elif elem_type == "NestedList":
                list_text = "NESTED LIST STRUCTURE:\n"
                for item in content:
                    indent = "  " * (item["level"] - 1)
                    bullet = "•" if item["level"] == 1 else "-"
                    list_text += f"{indent}{bullet} {item['text']}\n"
                
                chunks.append({
                    "content": list_text,
                    "chunk_id": f"{doc_name}_list_{len(chunks)}",
                    "chunk_type": "nested_list",
                    "element_type": "NestedList",
                    "source_doc": doc_name,
                    "chunk_position": len(chunks)
                })

            # STRATEGY 4: Regular text - accumulate until size limit
            else:
                text = str(content)
                text_size = len(text)
                
                # If adding this would exceed limit, create chunk
                if current_buffer_size + text_size > self.chunk_size and current_text_buffer:
                    chunks.append(self._create_chunk_from_buffer(
                        current_text_buffer, doc_name, len(chunks), "text"
                    ))
                    current_text_buffer = []
                    current_buffer_size = 0
                
                current_text_buffer.append({
                    "text": text,
                    "type": elem_type
                })
                current_buffer_size += text_size
        
        # Flush remaining text
        if current_text_buffer:
            chunks.append(self._create_chunk_from_buffer(
                current_text_buffer, doc_name, len(chunks), "text"
            ))
        
        return chunks
    
    def _table_to_markdown(self, table_data: Dict) -> str:
        """Convert table dict to markdown string"""
        if isinstance(table_data, str):
            return table_data
        
        headers = table_data.get("headers", [])
        rows = table_data.get("rows", [])
        
        # Build markdown table
        md = "| " + " | ".join(headers) + " |\n"
        md += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        
        for row in rows:
            md += "| " + " | ".join(row) + " |\n"
        
        return md
    
    def _create_chunk_from_buffer(self, buffer: List[Dict], doc_name: str, 
                                  position: int, chunk_type: str) -> Dict[str, Any]:
        """Create chunk from accumulated text buffer"""
        combined_text = " ".join([item["text"] for item in buffer])
        
        return {
            "content": combined_text,
            "chunk_id": f"{doc_name}_{chunk_type}_{position}",
            "chunk_type": chunk_type,
            "source_doc": doc_name,
            "chunk_position": position,
            "element_types": [item["type"] for item in buffer],
            "length": len(combined_text)
        }
    
    def retrieve_with_context(self, query: str, chunks: List[Dict[str, Any]], 
                            top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Enhanced retrieval that understands chunk types
        """
        query_embedding = self.embed_model.encode([query])[0]
        
        results_with_scores = []
        for chunk in chunks:
            # Embed chunk content
            chunk_embedding = self.embed_model.encode([chunk["content"]])[0]
            similarity = self._cosine_similarity(query_embedding, chunk_embedding)
            
            # Boost table chunks for data queries
            if chunk.get("chunk_type") == "table" and any(
                word in query.lower() for word in ["how many", "what", "sales", "data", "numbers"]
            ):
                similarity *= 1.2  # 20% boost
            
            results_with_scores.append((similarity, chunk))
        
        results_with_scores.sort(key=lambda x: x[0], reverse=True)
        
        return [
            {**chunk, "relevance_score": float(score)} 
            for score, chunk in results_with_scores[:top_k]
        ]
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


# DEMO: Compare simple vs structured chunking
if __name__ == "__main__":
    chunker = AdvancedChunkingSystem(chunk_size=300)
    
    # Run LlamaParse Demo
    parsed_llama = chunker.parse_with_llamaparse("audit_report.pdf")
    llama_chunks = chunker.chunk_structured_document(parsed_llama, "audit_report")
    
    print(f"\nGENERATED {len(llama_chunks)} LLAMAPARSE CHUNKS:")
    for chunk in llama_chunks:
        print(f"[{chunk['chunk_type'].upper()}] {chunk['content'][:100]}...")

    # Run Unstructured Demo
    parsed_unstructured = chunker.parse_with_unstructured("q4_report.docx")
    unstructured_chunks = chunker.chunk_structured_document(parsed_unstructured, "q4_report")
    
    print(f"\nGENERATED {len(unstructured_chunks)} UNSTRUCTURED CHUNKS:")
    for chunk in unstructured_chunks:
        print(f"[{chunk['chunk_type'].upper()}] {chunk['content'][:100]}...")
    
    # Test retrieval
    print("\n" + "=" * 60)
    print("RETRIEVAL TEST")
    print("=" * 60)
    
    queries = [
        "What was the growth in the South region?",
        "What improvements were made?"
    ]
    all_chunks = llama_chunks + unstructured_chunks
    for query in queries:
        print(f"\nQuery: '{query}'")
        results = chunker.retrieve_with_context(query, all_chunks, top_k=2)
        
        for i, result in enumerate(results, 1):
            print(f"\n  Result {i} (score: {result['relevance_score']:.3f})")
            print(f"  Type: {result['chunk_type']}")
            print(f"  Content: {result['content'][:150]}...")