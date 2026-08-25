# Phase 6: AI Agent & Tool Calling

## Explain Like I'm 10
Imagine hiring a personal executive assistant:
1. **Direct LLM Call:** You ask: *"What is 25 x 4?"*. The assistant answers `"100"` using memory.
2. **RAG Pipeline:** You ask: *"What is our HR policy?"*. The assistant looks up the policy book and reads page 12.
3. **AI Agent (with Tools):** You ask: *"Find out who EMP-9942 is, check if they completed security training, and if not, create a support ticket."*
   - The assistant thinks (**Reasoning**).
   - Pulls out a tool box (**Tool Selection**).
   - Runs `get_employee_info("EMP-9942")` (**Action**).
   - Reads the output (**Observation**).
   - Runs `create_support_ticket(...)` (**Action**).
   - Returns the final summary to you!

---

## Technical Definition
* **Autonomous AI Agent:** An LLM-driven control loop that evaluates user intent, formulates sequential action plans, dynamically selects and executes external tools via standardized function schemas, observes tool outputs, and iterates until the goal state is satisfied.
* **Function / Tool Calling:** Injecting JSON Schema function definitions into the LLM system context, allowing the model to return structured JSON payloads specifying target function names and parameter arguments instead of conversational text.
* **Agent Reasoning Loop (ReAct Framework):** An iterative architecture pattern: `Reason (Plan) -> Act (Execute Tool) -> Observe (Parse Output) -> Synthesize (Respond)`.

---

## How the Agent Loop Works Step-by-Step

```text
[ User Prompt: "Look up details for EMP-9942" ]
                       │
                       ▼
             [ 1. Agent Reasoning ]
     (Analyzes prompt against Tool Declarations)
                       │
                       ▼
          [ 2. Tool Selection (JSON) ]
   {"tool": "get_employee_info", "args": {"identifier": "EMP-9942"}}
                       │
                       ▼
          [ 3. Tool Dispatcher Exec ] ──> Calls Python function in backend/app/ai/tools/registry.py
                       │
                       ▼
          [ 4. Tool Observation Result ]
   {"name": "Alice Johnson", "role": "Security Architect", ...}
                       │
                       ▼
          [ 5. Final Synthesis Response ]
   "Employee EMP-9942 is Alice Johnson, Senior Security Architect..."
```

---

## Where We Use It in Our Project
* [`backend/app/ai/tools/registry.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/ai/tools/registry.py): Tool declarations & Python execution dispatchers (`search_documents`, `get_employee_info`, `get_sales_report`, `create_support_ticket`).
* [`backend/app/ai/agents/orchestrator.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/ai/agents/orchestrator.py): Iterative agent reasoning loop (`run_agent_loop`).
* [`backend/app/schemas/agent.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/schemas/agent.py): Pydantic validation schemas.
* [`backend/app/api/agent.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/api/agent.py): Authenticated `POST /api/ai/agent/chat` endpoint.
* [`backend/tests/test_agent.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/tests/test_agent.py): Integration test suite.

---

## Interview Questions an AI Engineer Could Ask
1. **Q: Why are unrestricted AI agents dangerous in production environments?**
   * *A:* Unrestricted agents can execute unintended or malicious tool calls (e.g. deleting database rows, sending emails to real users, or running infinite loops consuming thousands of API dollars). Enterprise systems enforce strict parameter validation, execution timeouts, maximum iteration bounds, and Human-in-the-Loop (HITL) approval gates for high-risk actions.
2. **Q: What is the difference between a deterministic workflow and an AI Agent?**
   * *A:* A deterministic workflow follows hardcoded, fixed `if/else` control logic defined by a software engineer. An AI Agent dynamically decides *which* tools to call, in *what* order, and *how many times* to loop based on runtime reasoning over unstructured user inputs.
