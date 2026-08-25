import json
import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.rag.pipeline import run_hybrid_rag_pipeline
from app.models.approval import ApprovalTask, AuditLog

logger = logging.getLogger(__name__)

# High-risk action types that require human manager sign-off
HIGH_RISK_ACTIONS = ["send_official_warning_email", "execute_financial_refund", "urgent_ticket_escalation"]

TOOL_DECLARATIONS = [
    {
        "name": "search_documents",
        "description": "Searches company policies, PDFs, and text documents using hybrid RAG search.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query to look up in company documents"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_employee_info",
        "description": "Looks up employee details, department, role, and compliance status in HR database.",
        "parameters": {
            "type": "object",
            "properties": {
                "identifier": {"type": "string", "description": "Employee ID (e.g. EMP-9942) or email address"}
            },
            "required": ["identifier"]
        }
    },
    {
        "name": "get_sales_report",
        "description": "Retrieves business intelligence sales reports, revenue numbers, and growth metrics for a given period.",
        "parameters": {
            "type": "object",
            "properties": {
                "period": {"type": "string", "description": "Time period e.g. 'Q1', 'Q2', 'July', '2025'"}
            },
            "required": ["period"]
        }
    },
    {
        "name": "create_support_ticket",
        "description": "Creates an IT or HR support ticket. Urgent priority tickets require manager approval.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Brief title of the support ticket"},
                "priority": {"type": "string", "description": "Priority: 'low', 'medium', 'high', 'urgent'"}
            },
            "required": ["title", "priority"]
        }
    }
]


async def execute_tool(tool_name: str, tool_args: Dict[str, Any], owner_id: int, db: AsyncSession) -> str:
    """
    Tool Execution Dispatcher with HITL High-Risk Staging:
    Executing high-risk tools (e.g. priority 'urgent') automatically stages an ApprovalTask
    in the database for human manager review before execution.
    """
    logger.info(f"Executing Tool '{tool_name}' with args: {tool_args}")

    if tool_name == "search_documents":
        query = tool_args.get("query", "")
        rag_res = await run_hybrid_rag_pipeline(db=db, query=query, owner_id=owner_id, top_k=2)
        return json.dumps({
            "answer_summary": rag_res.answer,
            "sources": [c.filename for c in rag_res.citations]
        })

    elif tool_name == "get_employee_info":
        identifier = str(tool_args.get("identifier", "")).upper()
        mock_hr = {
            "EMP-9942": {"name": "Alice Johnson", "role": "Senior Security Architect", "dept": "Cybersecurity", "compliance_status": "Completed"},
            "EMP-1047": {"name": "Bob Smith", "role": "Financial Auditor", "dept": "Finance", "compliance_status": "Pending Training"},
            "EMP-3021": {"name": "Charlie Davis", "role": "Backend Lead", "dept": "Platform Engineering", "compliance_status": "Completed"},
        }
        info = mock_hr.get(identifier, {"status": "Employee record not found", "query": identifier})
        return json.dumps(info)

    elif tool_name == "get_sales_report":
        period = str(tool_args.get("period", "Q3")).upper()
        sales_data = {
            "period": period,
            "total_revenue_usd": 1840000,
            "growth_vs_prior_period": "+14.2%",
            "top_category": "Enterprise Subscriptions",
            "region": "North America"
        }
        return json.dumps(sales_data)

    elif tool_name == "create_support_ticket":
        title = tool_args.get("title", "Issue")
        priority = tool_args.get("priority", "medium").lower()

        # Check HITL High-Risk Rule: Urgent priority requires Human Approval
        if priority in ["urgent", "critical"]:
            approval_task = ApprovalTask(
                action_type="create_support_ticket",
                action_payload={"title": title, "priority": priority},
                risk_level="high",
                status="pending",
                requester_id=owner_id
            )
            db.add(approval_task)
            await db.commit()
            await db.refresh(approval_task)

            # Record Audit Log for staged action
            audit = AuditLog(
                action_type="create_support_ticket_staged",
                actor_id=owner_id,
                target_resource=f"ApprovalTask #{approval_task.id}",
                payload={"title": title, "priority": priority},
                status="staged_for_approval"
            )
            db.add(audit)
            await db.commit()

            return json.dumps({
                "status": "Staged for Human Approval",
                "approval_task_id": approval_task.id,
                "note": "Urgent tickets require manager sign-off before execution.",
                "title": title,
                "priority": priority
            })

        # Low/Medium/High priority -> execute directly
        ticket_id = f"TICK-{hash(title) % 10000:04d}"
        return json.dumps({
            "status": "Ticket Created Successfully",
            "ticket_id": ticket_id,
            "title": title,
            "priority": priority,
            "assigned_team": "IT Support Desk"
        })

    else:
        return json.dumps({"error": f"Unknown tool name '{tool_name}'"})
