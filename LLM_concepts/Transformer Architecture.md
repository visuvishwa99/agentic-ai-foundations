# Transformer Architecture

---

## Full Forward Pass — Text to Token

```
"Write SQL to"
        |
        v
+---------------------------------------+
|           TOKENIZATION                |
|                                       |
|   "Write"    "SQL"     "to"           |
|      |         |         |            |
|   [5234]    [6826]     [284]          |
|                                       |
|   Note: one word can become multiple  |
|   tokens. "pipeline" -> "pipe"+"line" |
+----------------+----------------------+
                 |
                 v
+---------------------------------------+
|          EMBEDDING LAYER              |
|                                       |
|   Two separate lookup tables:         |
|                                       |
|   token_emb   (what the word means)   |
|   +                                   |
|   position_emb (where it sits)        |
|   =                                   |
|   combined vector                     |
|                                       |
|   5234 -> [0.23, -0.45, ..., 0.89]    |
|   6826 -> [0.81,  0.12, ..., 0.34]    |
|    284 -> [0.56, -0.21, ..., 0.67]    |
|                                       |
|   each vector: 12,288 dimensions      |
+----------------+----------------------+
                 |
                 v
+---------------------------------------+
|        TRANSFORMER LAYER 1            |
|                                       |
|   x -----> LayerNorm                  |
|                 |                     |
|                 v                     |
|       Multi-Head Attention            |
|       +------------------------+      |
|       | Head1  Head2  Head3 ...|      |
|       |  Q,K,V  Q,K,V  Q,K,V  |      |
|       |                        |      |
|       | Q = what am I looking  |      |
|       |     for?               |      |
|       | K = what do I contain? |      |
|       | V = what is my content?|      |
|       |                        |      |
|       | score = softmax(       |      |
|       |   QK^T / sqrt(d)) * V  |      |
|       +------------------------+      |
|                 |                     |
|                 v                     |
|   x = x + attention_output           |
|         (residual connection)         |
|                 |                     |
|                 v                     |
|            LayerNorm                  |
|                 |                     |
|                 v                     |
|       Feed-Forward Network            |
|       Linear -> ReLU -> Linear        |
|       expand 4x    compress back      |
|       (512->2048->512)                |
|                 |                     |
|                 v                     |
|   x = x + ffn_output                 |
|         (residual connection)         |
+----------------+----------------------+
                 |
                 v
        (repeat x 96 layers)
                 |
                 v
+---------------------------------------+
|        TRANSFORMER LAYER 96           |
|        (same structure as layer 1)    |
|                                       |
|   early layers:  syntax, grammar      |
|   middle layers: local meaning        |
|   deep layers:   complex reasoning    |
+----------------+----------------------+
                 |
                 v
+---------------------------------------+
|            UNEMBEDDING                |
|                                       |
|   take LAST token vector only         |
|   [0.34, -1.27, ..., 1.19]            |
|                 |                     |
|                 v                     |
|   multiply by unembedding matrix      |
|   -> 50,000 raw scores (logits)       |
+----------------+----------------------+
                 |
                 v
+---------------------------------------+
|              SOFTMAX                  |
|                                       |
|   logits -> probabilities             |
|                                       |
|   "select"   P = 0.65                 |
|   "fetch"    P = 0.18                 |
|   "get"      P = 0.10                 |
|   ...        ...                      |
|                                       |
|   temperature controls sharpness:     |
|   low  (0.1) -> deterministic         |
|   high (1.8) -> creative, random      |
+----------------+----------------------+
                 |
                 v
+---------------------------------------+
|             SAMPLING                  |
|   pick "select"  (P = 0.65)           |
+----------------+----------------------+
                 |
                 v
   append -> "Write SQL to select"
                 |
                 v
+---------------------------------------+
|   REPEAT -- full forward pass again   |
|   all 96 layers, new token included   |
|   until [END] token or max tokens     |
+---------------------------------------+
```

---

## Key Components Explained

### Tokenization

Raw text is split into subwords, not whole words. Each subword gets a numeric ID from a fixed vocabulary. The model never sees raw text — only integers.

```
"pipeline" -> ["pipe", "line"] -> [6870, 1370]
```

### Embedding Layer

Two separate lookup tables are added together to form one vector per token.

```
token_emb    answers: what does this word mean?
position_emb answers: where does this word sit?

"not good" vs "good not"
  same token rows, different position rows
  -> different combined vectors
  -> model can tell them apart
```

### LayerNorm

Normalizes the values in a vector before passing them into attention or feed-forward. Keeps numbers stable so training does not blow up across 96 layers.

### Multi-Head Attention

Each head independently learns a different type of relationship between tokens.

```
Head 1: learns grammar links (subject -> verb)
Head 2: learns semantic links (cat -> animal)
Head 3: learns positional links (nearby words)
...
Head N: learns long-range dependencies

All heads concatenated -> projected back to original size
```

The attention formula:

```
Attention(Q, K, V) = softmax( QK^T / sqrt(d_k) ) * V

QK^T  = similarity score between every pair of tokens
sqrt  = scaling to prevent huge values
softmax = converts scores to probabilities
* V   = weighted mix of token content
```

### Residual Connections

After every sub-layer, the input is added back to the output.

```
x = x + attention(x)
x = x + feedforward(x)
```

This is why 96-layer models can train at all. Gradients flow straight back through the addition without vanishing.

### Feed-Forward Network

Each token's vector is processed independently through two linear layers with a ReLU in between.

```
input [512] -> Linear -> [2048] -> ReLU -> Linear -> [512] output
               expand 4x           activate  compress back
```

### Unembedding

Only the last token's final vector is used to predict the next word. It is multiplied by the unembedding matrix to produce 50,000 scores — one per vocabulary word.

### Softmax + Temperature

```
low temperature  (0.0 - 0.3):  confident, deterministic
                               good for code, math, factual Q&A

medium temperature (0.7 - 1.0): balanced
                               good for general conversation

high temperature (1.5+):       creative, unpredictable
                               good for brainstorming, fiction
```

---

## Model Scale Reference

```
Model        Dimensions    Parameters    Notes
-----------  ----------    ----------    ----------------------------
BERT-base       768          110M        syntax, basic semantics
GPT-2          1024            1.5B      general language
GPT-3        12,288          175B        nuanced reasoning, rare words
GPT-4 (est)  16,000            1.76T     complex multi-step reasoning
```

Larger dimensions = more aspects of meaning encoded per token = more memory and compute required.

---

## Transformers vs RNNs / LSTMs

```
Problem with RNNs          How Transformers fix it
----------------------     --------------------------------
Sequential processing      All tokens processed in parallel
  (slow, no GPU benefit)     (fast matrix operations on GPU)

Gradient vanishing         Residual connections carry
  over long sequences        gradients directly

Short memory               Attention scores any token
  (forgets early context)    against any other directly
                             no distance penalty
```

---

## Inside One Transformer Block (full detail)

```
input x
   |
   +---------> (saved for residual)
   |
   v
LayerNorm
   |
   v
Multi-Head Attention
   |
   v
   + <--------- (add saved input back)
   |
   +---------> (saved for residual)
   |
   v
LayerNorm
   |
   v
Feed-Forward Network
Linear -> ReLU -> Linear
   |
   v
   + <--------- (add saved input back)
   |
   v
output x  (same shape as input, richer meaning)
   |
   v
(passed to next block)
```