import json
import logging
import re
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.agent import AgentResponse, ToolCallStep
from app.ai.tools.registry import TOOL_DECLARATIONS, execute_tool
from app.ai.llm.client import llm_client
from app.schemas.ai import ChatMessage

logger = logging.getLogger(__name__)


async def run_agent_loop(
    db: AsyncSession,
    prompt: str,
    owner_id: int,
    max_iterations: int = 5
) -> AgentResponse:
    """
    Autonomous AI Agent Loop:
    1. Evaluates user intent against registered enterprise tools.
    2. Decides whether to invoke a tool OR answer directly.
    3. Executes chosen tools, observes output, and loops until goal is achieved.
    4. Enforces max_iterations bound to prevent infinite loops.
    """
    tool_calls_executed: List[ToolCallStep] = []
    conversation_history: List[ChatMessage] = []
    total_tokens = 0
    total_cost = 0.0

    tools_summary = json.dumps(TOOL_DECLARATIONS, indent=2)
    system_instruction = (
        "You are an autonomous Enterprise AI Agent. You have access to controlled software tools:\n"
        f"{tools_summary}\n\n"
        "REASONING & TOOL SELECTION RULES:\n"
        "1. If answering the user's request requires fetching data or taking an action, call a tool.\n"
        "2. To call a tool, respond ONLY with a valid JSON object in this exact format:\n"
        '{"tool": "tool_name", "args": {"param_name": "value"}}\n'
        "3. If you have received all required tool outputs or don't need tools, return your final answer in plain text without tool JSON.\n"
        "4. Be accurate, concise, and professional."
    )

    current_prompt = prompt

    for iteration in range(1, max_iterations + 1):
        logger.info(f"Agent Loop Iteration {iteration}/{max_iterations}")

        llm_response = await llm_client.generate_chat_response(
            prompt=current_prompt,
            system_instruction=system_instruction,
            temperature=0.1,
            history=conversation_history
        )

        total_tokens += llm_response.total_tokens
        total_cost += llm_response.estimated_cost_usd
        response_text = llm_response.answer.strip()

        # Check if the LLM decided to call a tool (JSON format)
        tool_call = _parse_tool_call(response_text)

        if tool_call:
            tool_name = tool_call.get("tool")
            tool_args = tool_call.get("args", {})

            # Execute tool safely
            tool_result_str = await execute_tool(tool_name, tool_args, owner_id=owner_id, db=db)

            # Record tool execution trace
            step_record = ToolCallStep(
                step_number=iteration,
                tool_name=tool_name,
                tool_args=tool_args,
                tool_result=tool_result_str
            )
            tool_calls_executed.append(step_record)

            # Append agent thought & tool observation to conversation history
            conversation_history.append(ChatMessage(role="user", content=current_prompt))
            conversation_history.append(ChatMessage(role="assistant", content=response_text))
            current_prompt = f"TOOL OBSERVATION RESULT for '{tool_name}':\n{tool_result_str}\nNow synthesize the final answer for the user."

        else:
            # Agent produced final text answer!
            return AgentResponse(
                answer=response_text,
                tool_calls=tool_calls_executed,
                iterations=iteration,
                model_name=llm_response.model_name,
                total_tokens=total_tokens,
                estimated_cost_usd=round(total_cost, 6)
            )

    # Reached max iterations fallback
    return AgentResponse(
        answer="Agent reached maximum iteration limit before completing request.",
        tool_calls=tool_calls_executed,
        iterations=max_iterations,
        model_name="agent-loop-max-exceeded",
        total_tokens=total_tokens,
        estimated_cost_usd=round(total_cost, 6)
    )


def _parse_tool_call(text: str) -> Dict[str, Any]:
    """
    Parses JSON tool call from LLM response text if present.
    """
    try:
        # Check if text contains JSON block
        match = re.search(r"\{.*\"tool\".*\}", text, re.DOTALL)
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)
            if "tool" in data:
                return data
    except Exception:
        pass
    return {}
