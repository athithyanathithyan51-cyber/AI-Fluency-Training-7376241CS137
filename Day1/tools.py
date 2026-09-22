"""Tools the agent is allowed to use, plus their JSON Schema descriptions."""
import ast
import operator
from config import ATTENDANCE, INTERNAL_MARKS

CONDONATION_LIMIT = 75


def get_attendance(roll_no: str) -> str:
    """Look up the attendance percentage for one roll number."""
    pct = ATTENDANCE.get(roll_no.strip().upper())
    return str(pct) if pct is not None else f"Unknown roll number: {roll_no}"


def get_internal_marks(roll_no: str, subject: str) -> str:
    """Look up the internal marks for one roll number and subject."""
    marks = INTERNAL_MARKS.get((roll_no.strip().upper(), subject.strip().upper()))
    return str(marks) if marks is not None else f"No marks found for {roll_no} in {subject}"


# A safe calculator: only numbers and + - * / ( ) are allowed. Never use eval().
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.USub: operator.neg}


def _evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.operand))
    raise ValueError("Unsupported expression")


def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression such as (12000 + 18000) * 0.9."""
    try:
        return str(_evaluate(ast.parse(expression, mode="eval").body))
    except Exception as error:
        return f"Calculator error: {error}"


TOOL_FUNCTIONS = {
    "get_attendance": get_attendance,
    "get_internal_marks": get_internal_marks,
    "calculator": calculator,
}

# These descriptions are what the LLM reads when deciding which tool to call
TOOLS = [
    {"type": "function", "function": {
        "name": "get_attendance",
        "description": "Get the attendance percentage for one roll number, for example CS137.",
        "parameters": {"type": "object",
                        "properties": {"roll_no": {"type": "string"}},
                        "required": ["roll_no"]}}},
    {"type": "function", "function": {
        "name": "get_internal_marks",
        "description": "Get the internal marks for one roll number in one subject, e.g. CS137, DBMS.",
        "parameters": {"type": "object",
                        "properties": {"roll_no": {"type": "string"},
                                       "subject": {"type": "string"}},
                        "required": ["roll_no", "subject"]}}},
    {"type": "function", "function": {
        "name": "calculator",
        "description": "Evaluate an arithmetic expression using + - * / and brackets.",
        "parameters": {"type": "object",
                        "properties": {"expression": {"type": "string"}},
                        "required": ["expression"]}}},
]

if __name__ == "__main__":
    print("get_attendance('cs137') ->", get_attendance("cs137"))
    print("get_internal_marks('cs137', 'dbms') ->", get_internal_marks("cs137", "dbms"))
    print("calculator('22 + 24 + 2') ->", calculator("22 + 24 + 2"))
