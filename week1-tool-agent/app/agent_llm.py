import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from .tools import calculator

load_dotenv()


@dataclass
class AgentResult:
    answer: str
    used_tools: bool = False
    tool_name: str | None = None
    tool_input: str | None = None
    tool_output: str | None = None


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def run_agent_llm(question: str) -> AgentResult:
    """
    LLM decides whether to call a tool. If tool call happens:
      1) We execute tool locally
      2) Send tool output back to LLM
      3) Return final answer + tool metadata
    """

    tools: list[dict[str, Any]] = [
        {
            "type": "function",
            "name": "calculator",
            "description": "Evaluate a basic arithmetic expression safely. Use for exact math.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression, e.g., '23*47'.",
                    }
                },
                "required": ["expression"],
            },
        }
    ]

    # 1) First call: let the model decide tool usage
    resp1 = client.responses.create(
        model=MODEL,
        instructions=(
            "You are a tool-using AI agent.\n"
            "- Use the calculator tool ONLY when exact arithmetic is needed.\n"
            "- Never fabricate tool outputs.\n"
            "- Be concise.\n"
        ),
        input=question,
        tools=tools,
    )

    # If no tools were called, output_text will contain the final answer.
    # If tools were called, we need to execute them and do a second call.
    tool_calls = []
    for item in resp1.output:
        # The SDK returns structured output items; tool calls appear as function tool call items
        if getattr(item, "type", None) in ("tool_call", "function_call"):
            tool_calls.append(item)

    if not tool_calls:
        return AgentResult(answer=resp1.output_text, used_tools=False)

    # 2) Execute tools (we'll support only 1 tool call this week)
    tc = tool_calls[0]
    tool_name = (
        getattr(tc, "name", None) or getattr(tc, "tool_name", None) or "calculator"
    )
    args = getattr(tc, "arguments", None) or {}
    expression = args.get("expression", "")

    tool_output = calculator(expression)

    # 3) Second call: provide tool result back to model
    resp2 = client.responses.create(
        model=MODEL,
        instructions=(
            "You are a tool-using AI agent.\n"
            "Use the provided tool output to answer. Be concise."
        ),
        input=[
            {"role": "user", "content": question},
            {
                "role": "tool",
                "name": tool_name,
                "content": tool_output,
            },
        ],
        tools=tools,
    )

    return AgentResult(
        answer=resp2.output_text,
        used_tools=True,
        tool_name=tool_name,
        tool_input=expression,
        tool_output=tool_output,
    )
