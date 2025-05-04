# Chunking Strategies Research
## Introduction

Using Gemini 2.5 Pro Deep Research for quicker research, a distilled version of the research is processed here.
Chunking Strategies are applied to turn different paragraphs, sentences, segements with semantic coherence into chunks.


The reason this is important is because of the following:

* Model Input Limits (Context Window)
* Improve Semantic Representation
* Better RAG and Semantic Search
* Possibile to optimize computational efficiency
* Chunking can be seen as pre-processing for various NLP tasks

The notes under  is a distilled version, the full paper: [Optimizing Text Embeddings](https://docs.google.com/document/d/1T_XtskN-5yg83D-QiN566EHD0zQNFHLFbIfMQzsRk6Q/edit?usp=sharing)

I read through and based on the paper made my conclusions further documented in  [Chunking](process.md#chunking).

## Gemini Deep Research Result

Distilled Guide to Text Chunking for Embeddings1. What is Text Chunking and Why Does It Matter?
Definition: Dividing large texts into smaller, manageable segments ("chunks").1
Importance:

Model Input Limits: Embeddings models and LLMs have maximum input sizes (context windows).5 Chunking prevents truncation and information loss.8
Semantic Representation: Smaller chunks allow for more focused and accurate vector embeddings compared to a single embedding for a large document.10
Retrieval Quality (RAG/Search): Defines the units indexed and searched. Good chunks improve relevance and accuracy.3
Efficiency: Processing smaller chunks is faster and less resource-intensive.2


Challenge: Finding the right balance – chunks small enough for focus and model limits, but large enough for context.10 No single "best" method exists.6
2. Foundational Chunking Strategies
Fixed-Size Chunking:

How: Splits text into fixed character/token counts.2 Often uses overlap.6
Pros: Simple, fast, predictable size.19
Cons: Ignores text structure/meaning, fragments context.11


Sentence Splitting:

How: Splits based on sentence boundaries (punctuation or NLP libraries).2
Pros: Respects basic semantic units.18
Cons: Variable chunk sizes, short sentences lack context, long sentences may exceed limits, needs robust NLP for accuracy.12


Paragraph Splitting:

How: Splits based on paragraph markers (e.g., \n\n).22
Pros: Often aligns with topical structure.23
Cons: Highly variable sizes, ineffective for unstructured text.23


Recursive Character Splitting:

How: Tries splitting hierarchically using a list of separators (e.g., ["\n\n", "\n", " ", ""]) to maintain structure while respecting size limits.2
Pros: Good balance between size and structure, adaptable.26 Often a good starting point.28
Cons: More complex, can still fragment if forced to split small, separator choice matters.29


3. Advanced Chunking Strategies
Semantic Chunking:

How: Uses embedding similarity between sentences/groups to find topic shifts and split points.19
Pros: Creates semantically coherent chunks, improves retrieval relevance.19
Cons: Computationally expensive, complex, needs quality embedding model, requires threshold tuning.19


Layout-Aware / Structure-Aware Chunking:

How: Uses document structure (headings, lists, tables in HTML, PDF, Markdown, code) as boundaries.8
Pros: Preserves author's intended structure, good for formatted documents.8
Cons: Depends heavily on consistent formatting, needs format-specific parsers, unsuitable for plain text.29


Agentic / LLM-Based Chunking:

How: Uses an LLM with prompts to determine optimal split points based on deep understanding.19
Pros: Potentially most nuanced and adaptive chunking.19
Cons: Very expensive, slow, experimental, risk of LLM errors.29


Hierarchical / Parent Document Retriever:

How: Creates small "child" chunks for embedding/retrieval, linked to larger "parent" chunks (e.g., sections) that provide context.34
Pros: Balances retrieval precision (child) with contextual richness (parent).34
Cons: Increased complexity, metadata management.34


4. Chunk Overlap
Purpose: Maintains context continuity across chunk boundaries, especially for fixed-size or recursive methods.4
Trade-off: Reduces lost context vs. increases redundancy and storage.15
Guidance: Start with modest overlap (e.g., 10-15% of chunk size 9) and tune based on evaluation.15 Less needed for semantic/structural methods.
5. Impact on Downstream Applications
RAG: Chunking directly impacts retrieved context quality, affecting LLM response accuracy and relevance.3 Chunk size needs balance: specific enough for retrieval, broad enough for generation.10
Semantic Search: Chunk coherence and size affect precision and recall.27 Semantic chunking often beneficial.19
Clustering/Classification: Coherent chunks lead to better feature representations (embeddings).28
6. Choosing a Strategy: Key Factors
Text Type: Structured (use layout-aware) vs. unstructured (recursive/semantic).8
Embedding Model: Align chunk size/type with model's optimal input.3
Downstream Task: RAG (needs context) vs. Search (needs precision).10
Constraints: Balance performance needs with computational cost, latency, and complexity.19
7. Best Practices
Start Simple: Begin with Recursive Character Splitting unless data structure dictates otherwise.24
Know Your Data: Analyze structure, formatting, and content type.3
Consider Models: Account for embedding model preferences and LLM context limits.3
Task-Driven: Optimize for your primary application (RAG, search, etc.).22
Evaluate End-to-End: Test chunking impact on final task performance, not in isolation.15
Iterate: Experiment with strategies, sizes, and overlap based on evaluation metrics.15
Use Metadata: Store source info, section headers, etc., with chunks to aid retrieval and context.9
