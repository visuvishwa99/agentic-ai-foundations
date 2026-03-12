"""
PLAN 1: CHUNKING SYSTEM
=======================

Takes pre-parsed text/content and applies different chunking strategies.
Focus: Understanding how different chunking approaches affect retrieval quality.

Input: Clean text content (assumes document already extracted)
Output: List of chunks with metadata, ready for embedding
"""

import re
import json
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
import numpy as np

class ChunkingSystem:
    """
    Comprehensive chunking system with multiple strategies.
    Handles text that's already been extracted from documents.
    """
    
    def __init__(self, chunk_size: int = 512, overlap_percent: float = 0.2):
        self.chunk_size = chunk_size
        self.overlap = int(chunk_size * overlap_percent)
        self.embed_model = SentenceTransformer('all-MiniLM-L6-v2')
        print(f"Chunking System initialized:")
        print(f"  Chunk size: {chunk_size} characters")
        print(f"  Overlap: {self.overlap} characters ({overlap_percent*100}%)")
    
    def chunk_by_sentences(self, text: str, doc_name: str = "unknown") -> List[Dict[str, Any]]:
        """
        Sentence-based chunking: Respects sentence boundaries
        Good for: General text, preserving semantic meaning
        """
        sentences = re.split(r'[.!?]+\s+', text.strip())
        chunks = []
        current_chunk = ""
        sentence_index = 0
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            # Add sentence to current chunk
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                # Save current chunk if it exists
                if current_chunk:
                    chunks.append(self._create_chunk_metadata(
                        content=current_chunk.strip(),
                        chunk_id=f"{doc_name}_sent_{len(chunks)}",
                        chunk_type="sentence_based",
                        source_doc=doc_name,
                        chunk_position=len(chunks),
                        original_boundaries="sentence",
                        sentence_start=sentence_index - current_chunk.count('.'),
                        sentence_end=sentence_index
                    ))
                
                # Start new chunk with current sentence
                current_chunk = sentence
            
            sentence_index += 1
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(self._create_chunk_metadata(
                content=current_chunk.strip(),
                chunk_id=f"{doc_name}_sent_{len(chunks)}",
                chunk_type="sentence_based",
                source_doc=doc_name,
                chunk_position=len(chunks),
                original_boundaries="sentence"
            ))
        
        return chunks
    
    def chunk_by_fixed_size(self, text: str, doc_name: str = "unknown") -> List[Dict[str, Any]]:
        """
        Fixed-size chunking with overlap: Simple sliding window
        Good for: Consistent chunk sizes, when structure doesn't matter
        """
        chunks = []
        start = 0
        
        while start < len(text):
            # Extract chunk
            end = start + self.chunk_size
            chunk_content = text[start:end]
            
            # Adjust to word boundary (don't break mid-word)
            if end < len(text):
                last_space = chunk_content.rfind(' ')
                if last_space > self.chunk_size * 0.8:  # If space is reasonably close
                    chunk_content = chunk_content[:last_space]
                    end = start + last_space
            
            chunks.append(self._create_chunk_metadata(
                content=chunk_content.strip(),
                chunk_id=f"{doc_name}_fixed_{len(chunks)}",
                chunk_type="fixed_size",
                source_doc=doc_name,
                chunk_position=len(chunks),
                original_boundaries=f"chars_{start}_{end}",
                char_start=start,
                char_end=end,
                overlap_with_previous=start > 0
            ))
            
            # Move start position (with overlap)
            start = end - self.overlap
            if start <= 0:
                break
        
        return chunks
    
    def chunk_by_sections(self, text: str, doc_name: str = "unknown") -> List[Dict[str, Any]]:
        """
        Section-aware chunking: Preserves document structure
        Good for: Structured documents, maintaining hierarchy
        """
        sections = self._detect_sections(text)
        chunks = []
        
        for i, section in enumerate(sections):
            section_title = section['title']
            section_content = section['content']
            
            # If section is small enough, keep as one chunk
            if len(section_content) <= self.chunk_size:
                chunks.append(self._create_chunk_metadata(
                    content=section_content,
                    chunk_id=f"{doc_name}_sec_{i}",
                    chunk_type="section_based",
                    source_doc=doc_name,
                    chunk_position=len(chunks),
                    original_boundaries="section",
                    section_title=section_title,
                    section_number=i
                ))
            else:
                # Large section - break into sub-chunks
                sub_chunks = self.chunk_by_sentences(section_content, f"{doc_name}_sec_{i}")
                for j, sub_chunk in enumerate(sub_chunks):
                    sub_chunk.update({
                        'chunk_id': f"{doc_name}_sec_{i}_sub_{j}",
                        'chunk_type': "section_subsection",
                        'section_title': section_title,
                        'section_number': i,
                        'subsection_number': j,
                        'chunk_position': len(chunks)
                    })
                    chunks.append(sub_chunk)
        
        return chunks
    
    def chunk_by_semantic_similarity(self, text: str, doc_name: str = "unknown", 
                                   similarity_threshold: float = 0.75) -> List[Dict[str, Any]]:
        """
        Semantic chunking: Uses embedding similarity to detect boundaries
        Good for: Maintaining topic coherence, natural boundaries
        """
        sentences = re.split(r'[.!?]+\s+', text.strip())
        if len(sentences) <= 1:
            return [self._create_chunk_metadata(
                content=text,
                chunk_id=f"{doc_name}_sem_0",
                chunk_type="semantic_single",
                source_doc=doc_name,
                chunk_position=0
            )]
        
        # Get embeddings for sentences
        sentence_embeddings = self.embed_model.encode(sentences)
        
        chunks = []
        current_chunk_sentences = [sentences[0]]
        
        for i in range(1, len(sentences)):
            # Calculate similarity with previous sentence
            similarity = self._cosine_similarity(
                sentence_embeddings[i-1], 
                sentence_embeddings[i]
            )
            
            current_chunk_text = " ".join(current_chunk_sentences)
            
            # If similarity is low OR chunk is getting too large, create new chunk
            if (similarity < similarity_threshold or 
                len(current_chunk_text) + len(sentences[i]) > self.chunk_size):
                
                chunks.append(self._create_chunk_metadata(
                    content=current_chunk_text,
                    chunk_id=f"{doc_name}_sem_{len(chunks)}",
                    chunk_type="semantic_based",
                    source_doc=doc_name,
                    chunk_position=len(chunks),
                    original_boundaries="semantic_boundary",
                    boundary_similarity=similarity,
                    sentence_count=len(current_chunk_sentences)
                ))
                
                current_chunk_sentences = [sentences[i]]
            else:
                current_chunk_sentences.append(sentences[i])
        
        # Add final chunk
        if current_chunk_sentences:
            chunks.append(self._create_chunk_metadata(
                content=" ".join(current_chunk_sentences),
                chunk_id=f"{doc_name}_sem_{len(chunks)}",
                chunk_type="semantic_based",
                source_doc=doc_name,
                chunk_position=len(chunks),
                original_boundaries="semantic_final"
            ))
        
        return chunks
    
    def retrieve_relevant_chunks(self, query: str, chunks: List[Dict[str, Any]], top_k: int = 1) -> List[Dict[str, Any]]:
        """
        Retrieval step: Find the most relevant chunks for a given query.
        Uses the internal embedding model to perform semantic search.
        """
        if not chunks:
            return []
            
        # 1. Embed the query
        query_embedding = self.embed_model.encode([query])[0]
        
        # 2. Embed all chunks (if not already embedded)
        chunk_contents = [c['content'] for c in chunks]
        chunk_embeddings = self.embed_model.encode(chunk_contents)
        
        # 3. Calculate similarities
        similarities = []
        for i, chunk_emb in enumerate(chunk_embeddings):
            sim = self._cosine_similarity(query_embedding, chunk_emb)
            similarities.append((sim, i))
            
        # 4. Sort and return top results
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, idx in similarities[:top_k]:
            result = chunks[idx].copy()
            result['relevance_score'] = float(score)
            results.append(result)
            
        return results

    def validate_chunks(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validation step: Check chunk quality and detect issues
        """
        validation_report = {
            'total_chunks': len(chunks),
            'issues': [],
            'statistics': {},
            'quality_score': 0
        }
        
        if not chunks:
            validation_report['issues'].append("No chunks generated")
            return validation_report
        
        # Check for orphaned/broken chunks
        orphaned_count = 0
        very_short_count = 0
        very_long_count = 0
        empty_count = 0
        
        chunk_lengths = []
        
        for chunk in chunks:
            content = chunk.get('content', '')
            length = len(content)
            chunk_lengths.append(length)
            
            # Empty chunks
            if not content.strip():
                empty_count += 1
                validation_report['issues'].append(f"Empty chunk: {chunk.get('chunk_id')}")
            
            # Very short chunks (less than 20 characters)
            elif length < 20:
                very_short_count += 1
                validation_report['issues'].append(f"Very short chunk: {chunk.get('chunk_id')} ({length} chars)")
            
            # Very long chunks (more than 2x target size)
            elif length > self.chunk_size * 2:
                very_long_count += 1
                validation_report['issues'].append(f"Very long chunk: {chunk.get('chunk_id')} ({length} chars)")
            
            # Orphaned chunks (broken mid-sentence)
            if (content and 
                not content[0].isupper() and 
                chunk.get('chunk_position', 0) > 0):
                orphaned_count += 1
                validation_report['issues'].append(f"Possible orphaned chunk: {chunk.get('chunk_id')}")
        
        # Calculate statistics
        validation_report['statistics'] = {
            'avg_length': np.mean(chunk_lengths) if chunk_lengths else 0,
            'min_length': min(chunk_lengths) if chunk_lengths else 0,
            'max_length': max(chunk_lengths) if chunk_lengths else 0,
            'std_length': np.std(chunk_lengths) if chunk_lengths else 0,
            'empty_chunks': empty_count,
            'very_short_chunks': very_short_count,
            'very_long_chunks': very_long_count,
            'orphaned_chunks': orphaned_count
        }
        
        # Calculate quality score (0-100)
        total_issues = empty_count + very_short_count + very_long_count + orphaned_count
        quality_score = max(0, 100 - (total_issues / len(chunks)) * 100)
        validation_report['quality_score'] = quality_score
        
        return validation_report
    
    def _create_chunk_metadata(self, content: str, **kwargs) -> Dict[str, Any]:
        """Helper to create standardized chunk metadata"""
        return {
            'content': content,
            'length': len(content),
            'word_count': len(content.split()),
            **kwargs
        }
    
    def _detect_sections(self, text: str) -> List[Dict[str, str]]:
        """Simple section detection based on headers"""
        lines = text.split('\n')
        sections = []
        current_section = []
        current_title = "Introduction"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect headers (simple patterns)
            if (line.startswith('Chapter') or 
                'Overview' in line or
                'Framework' in line or
                line.isupper() or
                (len(line.split()) <= 4 and not line.endswith('.'))):
                
                # Save previous section
                if current_section:
                    sections.append({
                        'title': current_title,
                        'content': ' '.join(current_section)
                    })
                    current_section = []
                
                current_title = line
            else:
                current_section.append(line)
        
        # Add final section
        if current_section:
            sections.append({
                'title': current_title,
                'content': ' '.join(current_section)
            })
        
        return sections
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def compare_chunking_strategies(text: str, doc_name: str = "test_doc"):
    """Compare all chunking strategies on the same text"""
    
    chunker = ChunkingSystem(chunk_size=300, overlap_percent=0.2)
    
    strategies = {
        'sentence_based': chunker.chunk_by_sentences,
        'fixed_size': chunker.chunk_by_fixed_size,
        'section_based': chunker.chunk_by_sections,
        'semantic': chunker.chunk_by_semantic_similarity
    }
    
    results = {}
    
    print(f"\nCOMPARING CHUNKING STRATEGIES")
    print(f"Input text length: {len(text)} characters")
    print("=" * 50)
    
    # Process the text using each strategy and collect performance/quality metrics
    for strategy_name, strategy_func in strategies.items():
        print(f"\n{strategy_name.upper()} CHUNKING:")
        
        # 1. Generate chunks using the current strategy
        # Each strategy returns a list of dictionaries containing text content and metadata
        chunks = strategy_func(text, doc_name)
        
        # 2. Run the validation engine to identify potential issues
        # This checks for empty chunks, orphaned sentences, and size violations
        validation = chunker.validate_chunks(chunks)
        
        # Store results for the final comparative analysis report
        results[strategy_name] = {
            'chunks': chunks,
            'validation': validation
        }
        
        # 3. Print a quick summary of this strategy's output
        print(f"  Chunks generated: {len(chunks)}")
        print(f"  Average length: {validation['statistics']['avg_length']:.0f} chars")
        print(f"  Quality score: {validation['quality_score']:.1f}/100")
        print(f"  Issues: {len(validation['issues'])}")
        
        # 4. Display a small preview of the first chunk to see the visual boundary result
        if chunks:
            print(f"  First chunk preview: {chunks[0]['content'][:100]}...")
    
    return results, chunker

# --- DEMO: TEST WITH SAMPLE TEXT ---
if __name__ == "__main__":
    
    # Sample text for testing different chunking strategies
    sample_text = """
Python Programming Language Guide

Chapter 1: Introduction
Python was created by Guido van Rossum and first released in 1991. It is an interpreted, high-level programming language with dynamic semantics. Its high-level built-in data structures, combined with dynamic typing and dynamic binding, make it very attractive for Rapid Application Development.

Chapter 2: Core Features
Python emphasizes code readability with its notable use of significant whitespace. Its language constructs and object-oriented approach aim to help programmers write clear, logical code for small and large-scale projects.

Python supports multiple programming paradigms, including procedural, object-oriented, and functional programming. It has a comprehensive standard library and is often described as a "batteries included" language.

Chapter 3: Popular Libraries
NumPy is the fundamental package for scientific computing with Python. It provides support for large, multi-dimensional arrays and matrices, along with mathematical functions to operate on these arrays.

Pandas offers data structures and operations for manipulating numerical tables and time series. It is built on top of NumPy and provides easy-to-use data structures and data analysis tools.

TensorFlow is an end-to-end open source platform for machine learning. It has a comprehensive, flexible ecosystem of tools, libraries and community resources that lets researchers push the state-of-the-art in ML.

Chapter 4: Web Development
Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. It follows the model-view-template architectural pattern.

FastAPI is a modern, fast web framework for building APIs with Python based on standard Python type hints. It provides automatic API documentation and data validation.

Flask is a lightweight WSGI web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications.
"""
    
    # Run comparison
    results, chunker = compare_chunking_strategies(sample_text, "When was javascript released?")
    
    # Detailed analysis with a Visual Scorecard
    print(f"\n" + "="*60)
    print(f"{'STRATEGY':<20} | {'SCORE':<10} | {'REASONING'}")
    print("-" * 60)
    
    for strategy_name, result in results.items():
        val = result['validation']
        score = val['quality_score']
        
        # Create a simple visual progress bar
        bar_length = int(score / 10)
        bar = "█" * bar_length + "░" * (10 - bar_length)
        
        # Determine the primary reason for the score
        reason = "Perfect structural integrity"
        if score < 100:
            if val['statistics']['orphaned_chunks'] > 0:
                reason = f"Broken sentences ({val['statistics']['orphaned_chunks']} issues)"
            elif val['statistics']['very_short_chunks'] > 0:
                reason = "Too many small fragments"
        
        name_display = strategy_name.replace('_', ' ').title()
        print(f"{name_display:<20} | {bar} {score:>3.0f}% | {reason}")
    
    # --- SEARCH DEMO: Which strategy finds the answer best? ---
    query = "When was Python released?"
    print(f"\nSEARCHING FOR: '{query}'")
    print("=" * 60)
    print(f"{'STRATEGY':<20} | {'SCORE':<7} | {'RECOVERY PREVIEW (Top Match)'}")
    print("-" * 60)
    
    for strategy_name, result in results.items():
        chunks = result['chunks']
        # Use our new retrieval function to find the answer
        best_matches = chunker.retrieve_relevant_chunks(query, chunks, top_k=1)
        
        if best_matches:
            best = best_matches[0]
            score = best['relevance_score'] * 100
            # Clean preview: remove newlines for the table
            preview = best['content'].replace('\n', ' ')[:50] + "..."
            print(f"{strategy_name.replace('_', ' ').title():<20} | {score:>5.1f}% | {preview}")

    print("=" * 60)
    print("\nFINAL SUMMARY:")
    print("1. Structural Score: Measures if the chunks are 'broken' (sentences cut in half).")
    print("2. Search Score: Measures how well the AI found the SPECIFIC answer.")
    print("Notice how 'Fixed Size' might find the answer, but the text might be cut off!")
    
