import os
import re
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.report import ReportGenerationResponse
from app.ai.rag.pipeline import run_hybrid_rag_pipeline
from app.ai.analytics.bi_engine import run_bi_analytics_pipeline
from app.ai.llm.client import llm_client

logger = logging.getLogger(__name__)

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


async def generate_enterprise_report(
    db: AsyncSession,
    topic: str,
    owner_id: int,
    period: str = "2025 Q3"
) -> ReportGenerationResponse:
    """
    Multi-Section Business Report Generator:
    1. Gathers context from Document RAG (Company Policies).
    2. Gathers verified quantitative metrics from BI Engine (PostgreSQL tables).
    3. Synthesizes a formal multi-section enterprise Markdown report.
    4. Saves report as a downloadable .md file artifact.
    """
    # 1. RAG Context Retrieval
    rag_res = await run_hybrid_rag_pipeline(db=db, query=topic, owner_id=owner_id, top_k=2)

    # 2. BI Metrics Retrieval
    bi_res = await run_bi_analytics_pipeline(db=db, query=topic, period=period)

    # 3. Build Prompt Template
    sources_summary = "\n".join([f"- {c.filename} (Page {c.page_number})" for c in rag_res.citations]) or "None"
    kpi_summary = "\n".join([f"- {k.label}: {k.value}" for k in bi_res.kpis])

    prompt = (
        f"REPORT TOPIC: {topic}\n"
        f"REPORTING PERIOD: {period}\n\n"
        f"VERIFIED BI METRICS:\n{kpi_summary}\n\n"
        f"RELEVANT POLICY DOCUMENT SOURCES:\n{sources_summary}\n\n"
        f"DOCUMENT RAG EXCERPTS:\n{rag_res.answer}\n\n"
        "Generate a formal, multi-section Markdown Executive Business Report with these exact headers:\n"
        f"# {topic}\n"
        "## 1. Executive Summary\n"
        "## 2. Quantitative BI Performance Metrics\n"
        "## 3. Policy & Compliance Audit\n"
        "## 4. Strategic Recommendations\n"
    )

    llm_resp = await llm_client.generate_chat_response(
        prompt=prompt,
        system_instruction="You are a Chief Operations Officer writing a formal executive report. Use GFM markdown tables and bullet points.",
        temperature=0.2
    )

    report_markdown = llm_resp.answer.strip()

    # Ensure title header exists
    if not report_markdown.startswith("#"):
        report_markdown = f"# {topic}\n**Reporting Period: {period}**\n\n" + report_markdown

    # 4. Save Report File Artifact
    sanitized_filename = re.sub(r"[^\w\-]", "_", topic.lower()).strip("_") + f"_{int(datetime.now(timezone.utc).timestamp())}.md"
    file_path = os.path.join(REPORTS_DIR, sanitized_filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_markdown)

    # Count sections (count lines starting with ##)
    section_count = len(re.findall(r"^##\s+", report_markdown, re.MULTILINE)) or 4

    total_tokens = rag_res.total_tokens + bi_res.total_tokens + llm_resp.total_tokens
    total_cost = rag_res.estimated_cost_usd + bi_res.estimated_cost_usd + llm_resp.estimated_cost_usd

    return ReportGenerationResponse(
        report_title=topic,
        period=period,
        markdown_content=report_markdown,
        file_path=file_path,
        sections_count=section_count,
        model_name=llm_resp.model_name,
        total_tokens=total_tokens,
        estimated_cost_usd=round(total_cost, 6)
    )
