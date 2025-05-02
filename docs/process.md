# Process Description

- [Process Description](#process-description)
  - [AI Micro-Service Architecture](#ai-micro-service-architecture)
    - [Notes](#notes)
    - [Sequence Diagram](#sequence-diagram)
  - [Chunking](#chunking)


## AI Micro-Service Architecture

### Notes

The coding challenge proposes a simple api endpoint that is able to return a summary of a given text, and also the similarity of two texts.

Sounds like building blocks to building a system for making a knowledge bucket open to be structured in certain ways.

Semantic similarity is good for retrieval, which can be sped up by having concise and 'accurate summaries' of larger corpses of text.

### Sequence Diagram

A first diagram can be thought of as there were multiple rules; Fast API, Docker, OpenAI API, PyTests

Though solely focused on the features, some stretch goals are logical to implement because of scaling/production features.

Vector Store is the bread and butter of vector storage; Summarization can be used for abstraction, streaming and it should be rate-limited as to not overwhelm the system.

```mermaid
sequenceDiagram
    participant Client as Text Input
    participant API as FastAPI
    participant Service as Summary/Semantic
    participant Store as Vector Store

    Client->>API: POST /process\n(submit text(s))
    API->>Service: summarize(text)
    Service-->>API: summary
    API->>Service: compute_similarity(text1, text2)
    Service-->>API: similarity_score
    API->>Store: upsert_vectors(summary, embeddings)
    Store-->>API: acknowledgment
    API-->>Client: 200 OK\n{ summary, similarity_score }

 ```

 Looking at this diagram, it's easy to just leave out the vector store.


```mermaid
sequenceDiagram
    participant Client as Text Input
    participant API as FastAPI
    participant Service as Summary/Semantic
    Client->>API: POST /process\n(submit text(s))
    API->>Service: summarize(text)
    Service-->>API: summary
    API->>Service: compute_similarity(text1, text2)
    Service-->>API: similarity_score
    API-->>Client: 200 OK\n{ summary, similarity_score }

 ```

 And we can focus on the core functionalities.

 This could expand or be used as a reusable component for other applications, features, or use cases.

 Zooming in, the Summary/Semantic techniques will need some extra attention, as this will be the bottleneck for most applications. 

Things to consider:
* Chunking Strategies
* Similarity Strategies
* Summary Strategies
  
## Chunking