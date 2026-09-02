import re
import ast

def evaluate_math(slots: dict) -> dict:
    """Evaluates a basic math expression safely."""
    expression = slots.get("expression", "")
    
    if not expression:
        return {"status": "error", "message": "No math expression provided."}
    
    # 1. Clean the string to replace words with math symbols if they were transcribed
    expr = expression.lower()
    expr = expr.replace("plus", "+")
    expr = expr.replace("minus", "-")
    expr = expr.replace("times", "*")
    expr = expr.replace("multiplied by", "*")
    expr = expr.replace("divided by", "/")
    expr = expr.replace("over", "/")
    
    # 2. Sanitize: allow only numbers, basic operators, and spaces
    sanitized = re.sub(r'[^0-9+\-*/().\s]', '', expr)
    
    if not sanitized.strip():
        return {"status": "error", "message": f"Could not parse expression: {expression}"}
        
    try:
        # Use ast.literal_eval for safe evaluation of literal structures, but it doesn't do arithmetic operations directly.
        # However, for simple math without variables, a strictly sanitized eval is reasonably safe locally.
        # Here we only allow digits and operators.
        result = eval(sanitized, {"__builtins__": None}, {})
        return {"status": "success", "result": result, "original": expression}
    except Exception as e:
        return {"status": "error", "message": f"Failed to calculate {sanitized}: {str(e)}"}
