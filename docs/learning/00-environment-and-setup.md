# Phase 0: Project Environment & Architecture Setup

## Explain Like I'm 10
Imagine building a modern enterprise toy factory. Before assembling toys, you need:
1. A **clean blueprint** (Project Structure) so workers know where to find parts.
2. An **isolated workbench** (Virtual Environment) so tools for this project don't get mixed up with tools from another project.
3. A **secret safe** (Environment Variables) to hide keys and passwords so intruders can't steal them.
4. **Standardized shipping containers** (Docker) so the factory works identically whether it's running on your computer, your teammate's computer, or in the cloud.

---

## Technical Definition
* **Virtual Environment (`venv`):** An isolated directory tree containing a dedicated Python installation and set of libraries, preventing global dependency collisions across projects.
* **Environment Variables (`.env`):** Configuration variables injected into an application process at runtime, separating code from secret credentials and target environment configurations (12-Factor App methodology).
* **Docker & Containers:** Operating-system-level virtualization that packages software, system libraries, and configuration files into self-contained executable units called containers.

---

## Why We Need It
1. **Security:** Hardcoding credentials in code leads to catastrophic data breaches when code is pushed to public or private Git repositories.
2. **Reproducibility:** Eliminates "works on my machine" errors by freezing dependency versions and containerizing underlying services like PostgreSQL and Redis.
3. **Maintainability:** Modular directory organization keeps business logic, AI orchestration, database models, and API endpoints cleanly decoupled.

---

## How It Works (Phase 0 Setup)

```text
[ Developer Machine ]
        │
        ├──> Virtual Environment (.venv)  ---> Isolated Python Binaries & Packages
        │
        ├──> Config File (.env)           ---> Injects API Keys & DB Credentials
        │
        └──> Git Repository (.git)        ---> Tracks source code (.gitignore blocks .env)
```

---

## Where We Use It in Our Project
* `.gitignore`: Prevents pushing `.venv`, `.env`, and cache folders to Git repository.
* `.env.example`: Safe configuration template provided to team members.
* `docker-compose.yml`: Launches PostgreSQL + `pgvector` and Redis locally.
* `backend/requirements.txt`: Manages Python dependencies.

---

## Common Mistakes Beginners Make
1. **Committing `.env` files to Git:** Exposes API keys to web crawlers and security scanners within seconds.
2. **Installing packages globally:** Running `pip install` outside a virtual environment corrupts system Python binaries.
3. **Ignoring `.gitignore`:** Committing `__pycache__` or `.venv` folders bloats Git history with hundreds of megabytes of binary junk.

---

## Interview Questions an AI Engineer Could Ask
1. **Q: Why separation of configuration and code is essential in cloud-native applications?**
   * *A:* Following 12-Factor App principles, separating configuration allows the exact same code build to run across development, staging, and production environments simply by injecting different environment variables.
2. **Q: How does `pgvector` differ from running a standalone vector database like Qdrant or Pinecone?**
   * *A:* `pgvector` is a PostgreSQL extension that adds vector search capability directly into an existing relational database. It eliminates data duplication and operational overhead for small-to-medium scale systems, while dedicated vector DBs specialize in extreme horizontal scaling for billions of vectors.

---

## Mini Exercise
See the end of the Phase 0 lesson in chat!
