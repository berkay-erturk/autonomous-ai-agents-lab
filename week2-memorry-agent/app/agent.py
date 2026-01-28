import re
from dataclasses import dataclass
from .tools import calculator


@dataclass
class AgentResult:
    answer: str
    used_tools: bool = False
    tool_name: str | None = None
    tool_input: str | None = None
    tool_output: str | None = None


_ARITHMETIC_PATTERN = re.compile(r"^[\d\s\.\+\-\*\/\(\)\%\^]+$")


def run_agent(question: str) -> AgentResult:
    q = question.strip()

    # Very simple heuristic for Week 1:
    # If question includes a standalone arithmetic expression, use calculator.
    # Examples: "23 * 47", "(12+3)/5", "2**10"
    expr = q.replace("^", "**")

    # If the entire input looks like math OR contains "kaç eder" etc. with an expression
    possible_expr = None
    if _ARITHMETIC_PATTERN.match(expr):
        possible_expr = expr
    else:
        # try extracting expression from Turkish question patterns
        m = re.search(r"([\d\.\s\+\-\*\/\(\)\%\^]+)", expr)
        if m and _ARITHMETIC_PATTERN.match(m.group(1).strip()):
            possible_expr = m.group(1).strip()

    if possible_expr:
        out = calculator(possible_expr)
        return AgentResult(
            answer=(
                out
                if not out.startswith("Error:")
                else "İfadeyi hesaplayamadım. Daha net bir matematiksel ifade yazar mısın?"
            ),
            used_tools=True,
            tool_name="calculator",
            tool_input=possible_expr,
            tool_output=out,
        )

    # Non-tool path (Week 1): simple direct response
    # We keep it short and honest until LLM integration in Week 2.
    return AgentResult(
        answer="Bu sprintte (Week 1) agent iskeletini ve tool pipeline'ını kuruyoruz. Bu soruyu Week 2'de LLM ekleyince doğru şekilde yanıtlayacağım. Şimdilik bana bir matematik işlemi sorarsan tool ile hesaplayabilirim."
    )
