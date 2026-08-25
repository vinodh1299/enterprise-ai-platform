# Phase 7: Natural Language Text-to-SQL Agent & Database Security

## Explain Like I'm 10
Imagine hiring an assistant to answer questions about your company's sales ledger:
1. **Natural Language Question:** You ask: *"Which department made the most money last month?"*
2. **Text-to-SQL Translation:** The AI translates your question into a database search command: `SELECT name, SUM(amount) FROM sales GROUP BY name ORDER BY SUM(amount) DESC LIMIT 1;`.
3. **The Bouncer (SQL Security Validator):** Before running the command, a security bouncer checks it. If the AI accidentally generates a dangerous command like `DROP TABLE users;`, the bouncer instantly blocks it!
4. **Read-Only Execution:** The computer runs the safe `SELECT` query, gets the numbers, and the AI explains them to you in plain English!

---

## Technical Definition
* **Text-to-SQL:** The task of converting unstructured natural language questions into syntactically valid SQL queries targeting a relational database schema.
* **SQL Injection & AST Validation:** Analyzing generated SQL strings using keyword filtering and AST (Abstract Syntax Tree) parsing to enforce read-only execution constraints before database invocation.
* **Principle of Least Privilege:** Database security model restricting AI database service accounts exclusively to `SELECT` permissions on authorized tables, disabling `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, and DDL/DML mutations.

---

## How the Text-to-SQL Security Pipeline Works

```text
[ User Question: "Which department had highest sales?" ]
                         │
                         ▼
        [ 1. LLM SQL Generator ] ──> Generates ANSI SQL SELECT query
                         │
                         ▼
        [ 2. Security Validator ] ──> Verifies SELECT-only, blocks DROP/DELETE, adds LIMIT 100
                         │
                         ▼
        [ 3. DB Execution ]      ──> Runs query asynchronously on PostgreSQL / SQLite
                         │
                         ▼
        [ 4. AI Explanation ]    ──> Synthesizes 2-sentence executive summary of data findings
```

---

## Where We Use It in Our Project
* [`backend/app/models/sales.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/models/sales.py): SQLAlchemy models for `departments`, `employee_records`, and `sales`.
* [`backend/app/ai/tools/sql_validator.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/ai/tools/sql_validator.py): SQL security validator blocking dangerous mutating keywords.
* [`backend/app/ai/tools/sql_agent.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/ai/tools/sql_agent.py): Text-to-SQL translation & execution engine.
* [`backend/app/api/sql_agent.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/api/sql_agent.py): Authenticated `POST /api/ai/sql/query` endpoint.
* [`backend/tests/test_sql_agent.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/tests/test_sql_agent.py): Integration test suite verifying read-only execution & threat blocking.

---

## Interview Questions an AI Engineer Could Ask
1. **Q: Why is giving an LLM direct database access dangerous, and how do you secure Text-to-SQL systems?**
   * *A:* LLMs can hallucinate malicious SQL, be exploited via indirect prompt injection, or generate destructive commands (`DROP TABLE`, `DELETE FROM users`). To secure Text-to-SQL: (1) Connect via a read-only database user; (2) Validate SQL strings through security parsers enforcing `SELECT`-only execution; (3) Restrict accessible tables; (4) Enforce row limits (`LIMIT 100`) and statement execution timeouts.
