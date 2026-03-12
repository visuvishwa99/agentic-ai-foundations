import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# --- STEP 1: INITIALIZATION ---
# Load the embedding model (384-dimensional output)
model = SentenceTransformer('all-MiniLM-L6-v2')

# --- STEP 2: PREPARE DATA ---
docs = [
    "Python programming tutorial",
    "Machine learning basics", 
    "Pasta cooking recipe",
    "JavaScript frameworks"
]

# Convert documents to numerical vectors (embeddings)
# FAISS requires input data in 'float32' format for efficiency.
embeddings = np.array([model.encode(doc) for doc in docs]).astype('float32')

# --- STEP 3: CREATE VECTOR INDEX ---
# IndexFlatL2 uses Euclidean distance (L2) to measure similarity.
dimension = embeddings.shape[1]  # 384
index = faiss.IndexFlatL2(dimension)

# Add our document vectors to the searchable index
index.add(embeddings)
print(f"Index built with {index.ntotal} documents.")

# --- STEP 4: PERFORM SEMANTIC SEARCH ---
query = "How to learn programming?"

# 1. Convert query to vector
query_emb = model.encode(query).reshape(1, -1).astype('float32')

# 2. Search for the Top K most similar documents
k = 2 
distances, indices = index.search(query_emb, k)

# --- STEP 5: DISPLAY RESULTS ---
print(f"\nSearch results for: '{query}'")
for i, idx in enumerate(indices[0]):
    print(f"{i+1}. {docs[idx]} (Distance: {distances[0][i]:.3f})")