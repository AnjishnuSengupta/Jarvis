import re
try:
    import sympy
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
except ImportError:
    sympy = None

def evaluate_math(slots: dict) -> dict:
    """Evaluates mathematical expressions including advanced symbolic math via SymPy."""
    expression = slots.get("expression", "")
    
    if not expression:
        return {"status": "error", "message": "No math expression provided."}
        
    expr = expression.lower()
    
    # 1. Clean common word representations
    expr = expr.replace("plus", "+")
    expr = expr.replace("minus", "-")
    expr = expr.replace("times", "*")
    expr = expr.replace("multiplied by", "*")
    expr = expr.replace("divided by", "/")
    expr = expr.replace("over", "/")
    
    # 2. Parse natural language advanced math structures to SymPy syntax
    # "integrate ... dx" or "∫ ... dx"
    integrate_match = re.search(r'(?:integrate|∫)\s*(.*?)\s*(?:dx|with respect to x)', expr)
    if integrate_match:
        inner = integrate_match.group(1)
        expr = f"integrate({inner}, x)"
        
    # derivative
    diff_match = re.search(r'(?:derivative of|diff)\s*(.*?)\s*(?:with respect to x|dx)?$', expr)
    if diff_match:
        inner = diff_match.group(1)
        expr = f"diff({inner}, x)"
        
    # exponents
    expr = expr.replace("^", "**")
    
    if not sympy:
        # Fallback to basic eval if sympy is not installed
        sanitized = re.sub(r'[^0-9+\-*/().\s]', '', expr)
        if not sanitized.strip():
            return {"status": "error", "message": f"Could not parse expression: {expression}"}
        try:
            result = eval(sanitized, {"__builtins__": None}, {})
            return {"status": "success", "result": result, "original": expression}
        except Exception as e:
            return {"status": "error", "message": f"Failed to calculate {sanitized}: {str(e)}"}

    try:
        # 3. Evaluate using SymPy
        transformations = (standard_transformations + (implicit_multiplication_application,))
        parsed_expr = parse_expr(expr, transformations=transformations)
        
        if hasattr(parsed_expr, 'doit'):
            result = parsed_expr.doit()
        else:
            result = parsed_expr
            
        return {"status": "success", "result": str(result).replace("**", "^"), "original": expression}
    except Exception as e:
        return {"status": "error", "message": f"Failed to calculate symbolically: {str(e)}. (Input: {expression})"}
