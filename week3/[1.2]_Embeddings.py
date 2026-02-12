from sentence_transformers import SentenceTransformer
import numpy as np

# --- STEP 1: INITIALIZATION ---
# Use a free local embedding model from sentence-transformers.
# 'all-MiniLM-L6-v2' is a lightweight model that converts text into 384-dimensional vectors.
model = SentenceTransformer('all-MiniLM-L6-v2')

# --- STEP 2: DEFINE SAMPLE TEXTS ---
# We define different strings to see how the model represents different meanings.
text1 = "Python programming language"
text2 = "Machine learning algorithms"
text3 = "Italian pasta recipes"

# --- STEP 3: GENERATE EMBEDDINGS ---
# This code snippet performs a core operation in AI: converting text into numerical 
# representations (embeddings) using the model.encode() function.
emb1 = model.encode(text1)
emb2 = model.encode(text2)
emb3 = model.encode(text3)

# --- STEP 4: INSPECT THE RESULTS ---
# Large Language Models see these "dense vectors" instead of words.
print(f"Embedding shape: {emb1.shape}")  # Output: (384,)
print(f"First 5 values of 'Python' embedding: {emb1[:5]}")