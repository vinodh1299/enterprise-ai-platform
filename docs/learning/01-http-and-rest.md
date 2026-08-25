# Phase 1: Python, FastAPI & REST Backend Foundations

## Explain Like I'm 10
Imagine ordering food at a restaurant:
1. **Client (Browser/Frontend):** You sitting at a table.
2. **HTTP Request (The Order):** You tell the waiter what you want: *"I want to view my profile"* (`GET /users/me`).
3. **HTTP Verb (GET vs POST):** 
   - `GET`: Asking to look at or fetch information (reading the menu).
   - `POST`: Giving new data to create something (submitting your food order).
4. **Backend Server (The Kitchen):** FastAPI receives your request, checks your password or wristband, prepares the data, and puts it on a plate.
5. **JSON (The Covered Plate):** The standardized, lightweight text format used to deliver data back to the client (`{"email": "user@example.com", "status": "active"}`).

---

## Technical Definition
* **REST (Representational State Transfer):** An architectural style for network applications using stateless, standard HTTP verbs (`GET`, `POST`, `PUT`, `DELETE`) to manipulate resource representations formatted in JSON.
* **FastAPI:** A modern, high-performance web framework for building APIs with Python 3.8+ based on standard Python type hints and ASGI (Asynchronous Server Gateway Interface).
* **JWT (JSON Web Token):** An open standard (RFC 7519) that defines a compact, self-contained way for securely transmitting claims between parties as a digitally signed JSON object.
* **Bcrypt Password Hashing:** A one-way cryptographic hash function incorporating a salt to protect stored user credentials against rainbow table attacks.

---

## Why We Need It
AI platforms cannot expose direct database or LLM access to unauthenticated web users. 
The FastAPI backend acts as an authoritative **Security & Authorization Gateway**:
1. Verifies user identity via JWT tokens before processing requests.
2. Validates incoming request payloads using Pydantic schemas to prevent malformed data injection.
3. Protects sensitive company database records behind Role-Based Access Control (RBAC).

---

## How It Works (Authentication Flow)

```text
[ Web Frontend ]                                  [ FastAPI Backend ]
       │                                                   │
       │─── 1. POST /api/users (Register) ───────────────>│ Hash Password (Bcrypt) -> Save to Postgres
       │                                                   │
       │─── 2. POST /api/auth/login ─────────────────────>│ Verify Hash -> Issue Signed JWT Access Token
       │<── Returns Token {"access_token": "eyJ..."} ──────│
       │                                                   │
       │─── 3. GET /api/users/me (With Header) ──────────>│ Validate JWT Signature -> Return User Profile
       │    Header: "Authorization: Bearer eyJ..."         │
```

---

## Where We Use It in Our Project
* [`backend/app/main.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/main.py): Entrypoint instantiating the FastAPI app.
* [`backend/app/core/security.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/core/security.py): Password hashing with bcrypt & JWT token encoding/decoding.
* [`backend/app/api/auth.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/api/auth.py): User registration, authentication, and token verification routes.
* [`backend/app/schemas/user.py`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/backend/app/schemas/user.py): Pydantic validation schemas.

---

## Common Mistakes Beginners Make
1. **Storing passwords in plain text:** Storing unhashed passwords in a database is a major security breach. Always use strong one-way hashing (`bcrypt`).
2. **Putting secret keys in source code:** Hardcoding JWT secret keys inside Python code instead of loading them from `.env`.
3. **Synchronous DB calls in async routes:** Blocking the async event loop by using legacy synchronous database drivers instead of `asyncpg`.

---

## Interview Questions an AI Engineer Could Ask
1. **Q: Why are JWT tokens stateless and how does the server verify them?**
   * *A:* JWTs are signed with a server secret key using a cryptographic algorithm (e.g. HS256). When the client presents the token in the `Authorization` header, the server decodes the signature using its secret key. If the signature matches and the `exp` timestamp hasn't passed, the server trusts the payload without needing to query a session database on every request.
2. **Q: What is the purpose of Pydantic in FastAPI?**
   * *A:* Pydantic provides type-safe runtime data validation and serialization. It parses incoming JSON request bodies against declared schemas, raises structured 422 Unprocessable Entity errors for invalid data, and sanitizes output responses.
