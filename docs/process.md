# Process Description

## AI Micro-Service Architecture

### Notes

The coding challenge proposes a simple api endpoint that is able to return a summary of a given text, and also the similarity of two texts.

Sounds like building blocks to building a system for making a knowledge bucket open to be structured in certain ways.

Semantic similarity is good for retrieval, which can be sped up by having concise and 'accurate summaries' of larger corpses of text.

### Sequence Diagram

A first diagram can be thought of as there were multiple rules; Fast API, Docker, OpenAI API, PyTests

Though solely focused on the features, some stretch goals are logical to implement.

Vector Store is the bread and butter of vector storage; Summarization can be used for abstraction, streaming and it should be rate-limited as to not overwhelm the system.

