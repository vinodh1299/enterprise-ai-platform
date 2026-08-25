# Phase 9: Multi-Turn Conversation Memory & Context Management

## Explain Like I'm 10
Imagine talking to a doctor:
1. **Stateless AI (No Memory):** Every time you say something, the doctor forgets who you are! You have to re-explain your whole medical history from scratch every 30 seconds.
2. **Short-Term Window Memory (The Last 10 Sentences):** The doctor remembers the last 10 things you said in your current appointment.
3. **Long-Term Memory & Rolling Summary (The Medical Chart):** When your appointment reaches 50 sentences, the doctor writes a 3-sentence summary on your chart and flips to a fresh page, so their desk never gets cluttered!

---

## Technical Definition
* **Stateful Conversation Memory:** An architectural design pattern storing structured turn-by-turn chat history (`user` and `assistant` messages) in persistent database storage, restoring previous conversation context on subsequent API calls.
* **Sliding Window Memory:** Retaining only the $N$ most recent message turns in the active LLM prompt payload to constrain token usage.
* **Rolling Context Summarization:** Periodically invoking an LLM summarization pipeline over older historical messages, storing a compressed summary string in the database to prevent token window overflow while preserving long-term semantic context.

---

## How Stateful Conversation Memory Works

```text
[ Turn 1: User says "My favorite color is Blue" ]
                        │
                        ▼
       [ 1. Store Message in PostgreSQL ]
                        │
                        ▼
       [ 2. Assistant Responds & Stores Answer ]
                        │
                        ▼
[ Turn 2: User asks "What is my favorite color?" ]
                        │
                        ▼
       [ 3. Memory Manager Fetches Recent Messages + Summary ]
                        │
                        ▼
       [ 4. Passes Memory Window to LLM Client ]
                        │
                        ▼
       [ 5. Assistant Responds: "Your favorite color is Blue!" ]
```

---

## Where We Use It in Our Project
* [`backend/app/models/conversation.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/models/conversation.py): SQLAlchemy models for `Conversation` and `Message`.
* [`backend/app/ai/memory/manager.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/ai/memory/manager.py): Memory manager fetching active context windows and performing rolling summarization.
* [`backend/app/api/conversation.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/api/conversation.py): Stateful REST API endpoints (`POST /api/conversations`, `GET /api/conversations`, `POST /api/conversations/{id}/chat`).
* [`backend/app/schemas/conversation.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/schemas/conversation.py): Pydantic validation schemas.
* [`backend/tests/test_conversation.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/tests/test_conversation.py): Integration test suite verifying multi-turn state retention.

---

## Interview Questions an AI Engineer Could Ask
1. **Q: Why are raw LLM REST APIs stateless, and how do backends manage conversation state in distributed systems?**
   * *A:* Cloud LLM APIs (like Gemini or OpenAI) are pure REST endpoints that process each HTTP request independently without retaining session state. Enterprise backends store conversation threads in persistent databases (PostgreSQL/Redis), load recent messages using session IDs, and pass the structured message array in each API call payload.
