# Memory and RAG

Severino is designed with advanced memory capabilities and integrates with Retrieval Augmented Generation (RAG) systems to provide context-aware and intelligent responses. This is crucial for maintaining conversational flow, understanding project specifics, and ensuring data privacy.

## The "Memory Palace"

The "Memory Palace" is a foundational concept for Severino's local, privacy-centric knowledge management. It aims to transform raw chat history and interactions into a highly structured, navigable knowledge graph.

### Key Components:

*   **Conversational Knowledge Graph:** Beyond simple chat history, the agent extracts entities, intents, and key facts from conversations. This structured data can be stored in a lightweight graph database or a dedicated local database (e.g., SQLite).
    *   **Example:** If a user states, "Remember that project X uses PostgreSQL," Severino stores "project X" as an entity and "uses PostgreSQL" as a related fact, making it retrievable for future interactions.
*   **Local Vector Database:** Extracted knowledge elements and their embeddings (numerical representations for semantic understanding) are stored in a local, encrypted database (e.g., using `sqlite-vec` or `sqlite-vss`). This ensures maximum privacy and offline capability for user data.
*   **Navigable Structure:** The "Memory Palace" creates paths (Domains, Rooms, Loci, Pathways) that allow Severino to "walk through" its knowledge, providing a performant data structure for the LLM's context window, similar to the method of loci.
*   **Self-Observation & Learning Log:** Severino logs its own actions, tool calls, their outcomes (success/failure), and user feedback. This structured log can be used for:
    *   **Reinforcement Learning from Human Feedback (RLHF):** Over time, Severino can learn which actions and tool sequences lead to successful outcomes and positive user feedback.
    *   **Troubleshooting & Diagnostics:** When a task fails, Severino can query its past experiences to identify similar failures and potential solutions.

## Project-Specific RAG Integration

Severino leverages a secure RAG system to provide the agent with a "mnemonic" for project context. This allows Severino to access and learn from internal project documentation and codebases.

### Capabilities:

*   **Query Internal Documentation:** Access and retrieve information from internal wikis, design documents, and project plans.
*   **Learn from Codebase:** Analyze code patterns, dependencies, and common practices within the `Severino` project itself to inform its actions and suggestions.
*   **Secure Context:** Ensures that sensitive project information accessed via RAG adheres to Confidential AI principles, especially when interacting with systems like Azure Confidential VMs.

## Data Flow (Conceptual)

1.  **User Interaction:** User provides input to Severino.
2.  **Knowledge Extraction:** LLM processes input to identify entities, intents, and facts.
3.  **Memory Palace Storage:** Extracted knowledge and embeddings are stored in the local vector database.
4.  **RAG Query:** If external knowledge is needed, Severino formulates a query for the RAG system.
5.  **Contextual Retrieval:** RAG system retrieves relevant information from internal knowledge bases.
6.  **LLM Augmentation:** Retrieved information augments the LLM's context for generating a response.
7.  **Response Generation:** LLM generates a context-aware response.
8.  **Self-Observation:** Severino logs its actions and outcomes for continuous learning.
