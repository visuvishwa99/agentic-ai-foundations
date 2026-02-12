from sentence_transformers import SentenceTransformer
import numpy as np
from numpy.linalg import norm

# --- STEP 1: INITIALIZATION ---
# Load the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# --- STEP 2: GENERATE EMBEDDINGS ---
text1 = "Python programming language"
text2 = "Machine learning algorithms"
text3 = "Italian pasta recipes"

emb1 = model.encode(text1)
emb2 = model.encode(text2)
emb3 = model.encode(text3)

# --- STEP 3: SIMILARITY CALCULATION ---
# This function calculates the cosine similarity between two vectors.
# Range: -1 to 1 (A score near 1 means meanings are very close).
def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

# --- STEP 4: COMPARE SEMANTIC MEANINGS ---
# We compare our embeddings to see which topics are related.
sim_12 = cosine_similarity(emb1, emb2) # Python vs ML
sim_13 = cosine_similarity(emb1, emb3) # Python vs Pasta

print(f"Similarity (Python vs ML): {sim_12:.3f}")      # High similarity (Tech vs Tech)
print(f"Similarity (Python vs Pasta): {sim_13:.3f}")   # Low similarity (Tech vs Food)