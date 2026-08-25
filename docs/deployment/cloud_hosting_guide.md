# Enterprise Single-Tenant Cloud Hosting & Deployment Guide

## 1. Single-Tenant Dedicated Instance Strategy
As selected in your deployment strategy, each enterprise client gets an **isolated, dedicated instance deployment**:
* **100% Data Isolation:** Dedicated PostgreSQL database + dedicated vector index per client.
* **Independent Resource Allocation:** Dedicated CPU/RAM scaling for compute-heavy RAG operations.
* **Custom Security Policy:** Client-specific encryption keys and approval compliance.

---

## 2. Cloud Architecture Options & Cost Comparison

```text
                                [ CLIENT ENTERPRISE CLOUD ]
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
          [ OPTION A: GCP Cloud Run ]                 [ OPTION B: AWS ECS Fargate ]
         - Auto-scaling to 0 (Serverless)            - 100% Dedicated VPC Networking
         - Managed GCP Cloud SQL (PostgreSQL)        - Managed AWS RDS (PostgreSQL + pgvector)
         - Managed GCP Memorystore (Redis)          - Managed AWS ElastiCache (Redis)
         - Cost: ~$15 - $40 / month                   - Cost: ~$50 - $120 / month
```

---

## 3. Option A: Google Cloud Platform (GCP Cloud Run) — Recommended for Lowest Cost

### Why GCP Cloud Run?
* **Auto-Scale to 0:** You pay \$0 when no queries are being processed!
* **Built-in HTTPS & Custom Domains:** Free SSL certificates managed by Google.

### Step-by-Step Deployment Steps:
1. **Set up GCP Project & Install gcloud CLI:**
   ```bash
   gcloud auth login
   gcloud config set project your-gcp-project-id
   ```
2. **Create Managed Cloud SQL PostgreSQL Instance (with pgvector):**
   ```bash
   gcloud sql instances create enterprise-db \
     --database-version=POSTGRES_16 \
     --cpu=2 --memory=7.5GiB --region=us-central1
   ```
3. **Build & Deploy Backend to Cloud Run:**
   ```bash
   gcloud builds submit --tag gcr.io/your-gcp-project-id/ai-backend:latest ./backend
   gcloud run deploy ai-enterprise-backend \
     --image gcr.io/your-gcp-project-id/ai-backend:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars DATABASE_URL="postgresql+asyncpg://user:pass@/cloudsql-connection-name/ai_enterprise"
   ```

---

## 4. Option B: Amazon Web Services (AWS ECS Fargate) — Enterprise Standard

### Why AWS ECS Fargate?
* **Serverless Containers:** No EC2 server management.
* **AWS RDS PostgreSQL + pgvector:** Industry-standard database durability and automatic backups.

### Deployment Steps:
1. **Create AWS ECR Repository:**
   ```bash
   aws ecr create-repository --repository-name ai-enterprise-backend
   ```
2. **Push Container Image to AWS ECR:**
   ```bash
   docker tag ai-enterprise-backend:latest <account_id>.dkr.ecr.us-east-1.amazonaws.com/ai-enterprise-backend:latest
   docker push <account_id>.dkr.ecr.us-east-1.amazonaws.com/ai-enterprise-backend:latest
   ```
3. **Deploy ECS Task Definition & Service:**
   Attach AWS ALB (Application Load Balancer) pointing to target group on port `8000`.

---

## 5. Option C: Render / Railway — Easiest 1-Click Platform (Lowest Setup Time)

### Why Render?
* **1-Click Web Service + Postgres + Redis:** Takes 3 minutes to deploy without CLI commands.
* **Automatic SSL & GitHub Integration:** Automatically redeploys on every `git push`.

### Steps for Render:
1. Push repository to GitHub.
2. Log into [Render.com](https://render.com) $\rightarrow$ Click **New Blueprint**.
3. Point to `docker-compose.yml` $\rightarrow$ Click **Deploy**!
