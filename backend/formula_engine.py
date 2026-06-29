"""
formula_engine.py — Safe formula evaluation for admin-editable calculator logic.

WHY THIS EXISTS:
The admin panel lets you type formulas like:
    (loan_amount * rate_monthly * (1+rate_monthly)**tenure_months) / ((1+rate_monthly)**tenure_months - 1)

We CANNOT use Python's eval() directly on this — that would let anyone who gets your
admin secret run arbitrary code on your server (read files, hit other sites, crash the app).

Instead we parse the formula into an Abstract Syntax Tree (AST) and only allow a safe
whitelist of operations: +, -, *, /, **, %, comparisons, and a small set of math functions
(min, max, round, abs, sqrt, log, pow, etc). Anything else (imports, function defs,
attribute access like __class__, etc.) is rejected before it ever runs.
"""
import ast
import math
import operator as op

# Allowed binary/unary operators
_ALLOWED_BINOPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Pow: op.pow, ast.Mod: op.mod, ast.FloorDiv: op.floordiv,
}
_ALLOWED_UNARYOPS = {ast.USub: op.neg, ast.UAdd: op.pos}
_ALLOWED_COMPARE = {
    ast.Lt: op.lt, ast.LtE: op.le, ast.Gt: op.gt, ast.GtE: op.ge,
    ast.Eq: op.eq, ast.NotEq: op.ne,
}

# Allowed function calls inside formulas
_ALLOWED_FUNCS = {
    "min": min, "max": max, "round": round, "abs": abs,
    "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
    "pow": pow, "floor": math.floor, "ceil": math.ceil,
    "exp": math.exp,
}

# Allowed constants usable in any formula even if not declared as an input/constant
_GLOBAL_CONSTANTS = {"pi": math.pi, "e": math.e}


class FormulaError(Exception):
    pass


class _SafeEval(ast.NodeVisitor):
    def __init__(self, variables: dict):
        self.variables = variables

    def visit(self, node):
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, None)
        if visitor is None:
            raise FormulaError(
                f"Disallowed expression type: {node.__class__.__name__}. "
                "Only arithmetic, comparisons, and whitelisted functions are permitted."
            )
        return visitor(node)

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        raise FormulaError("Only numeric constants are allowed.")

    # Python <3.8 fallback (not expected here, but harmless to keep)
    def visit_Num(self, node):
        return node.n

    def visit_Name(self, node):
        if node.id in self.variables:
            return self.variables[node.id]
        if node.id in _GLOBAL_CONSTANTS:
            return _GLOBAL_CONSTANTS[node.id]
        raise FormulaError(
            f"Unknown variable '{node.id}'. Must be an input key or constant defined for this calculator."
        )

    def visit_BinOp(self, node):
        if type(node.op) not in _ALLOWED_BINOPS:
            raise FormulaError(f"Operator '{type(node.op).__name__}' is not allowed.")
        left = self.visit(node.left)
        right = self.visit(node.right)
        try:
            return _ALLOWED_BINOPS[type(node.op)](left, right)
        except ZeroDivisionError:
            raise FormulaError("Division by zero in formula.")

    def visit_UnaryOp(self, node):
        if type(node.op) not in _ALLOWED_UNARYOPS:
            raise FormulaError(f"Unary operator '{type(node.op).__name__}' is not allowed.")
        return _ALLOWED_UNARYOPS[type(node.op)](self.visit(node.operand))

    def visit_Compare(self, node):
        left = self.visit(node.left)
        result = True
        for cmp_op, comparator in zip(node.ops, node.comparators):
            if type(cmp_op) not in _ALLOWED_COMPARE:
                raise FormulaError(f"Comparison '{type(cmp_op).__name__}' is not allowed.")
            right = self.visit(comparator)
            result = result and _ALLOWED_COMPARE[type(cmp_op)](left, right)
            left = right
        return result

    def visit_IfExp(self, node):
        # supports: value_if_true if condition else value_if_false
        return self.visit(node.body) if self.visit(node.test) else self.visit(node.orelse)

    def visit_BoolOp(self, node):
        # supports: a and b and c  /  a or b or c
        if isinstance(node.op, ast.And):
            result = True
            for v in node.values:
                result = result and self.visit(v)
                if not result:
                    return False
            return result
        elif isinstance(node.op, ast.Or):
            for v in node.values:
                val = self.visit(v)
                if val:
                    return val
            return False
        raise FormulaError("Unsupported boolean operator.")

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_FUNCS:
            raise FormulaError(
                f"Function '{getattr(node.func, 'id', '?')}' is not allowed. "
                f"Allowed: {', '.join(_ALLOWED_FUNCS.keys())}"
            )
        args = [self.visit(a) for a in node.args]
        return _ALLOWED_FUNCS[node.func.id](*args)

    def visit_List(self, node):
        return [self.visit(e) for e in node.elts]

    def visit_Tuple(self, node):
        return tuple(self.visit(e) for e in node.elts)


def evaluate_formula(formula: str, variables: dict) -> float:
    """
    Safely evaluate a single formula string given a dict of variable name -> value.
    Raises FormulaError on any disallowed syntax, unknown variable, or math error.
    """
    if not formula or not formula.strip():
        raise FormulaError("Formula is empty.")
    try:
        tree = ast.parse(formula, mode="eval")
    except SyntaxError as e:
        raise FormulaError(f"Syntax error in formula: {e}")

    evaluator = _SafeEval(variables)
    result = evaluator.visit(tree)

    if isinstance(result, bool):
        return result
    if not isinstance(result, (int, float)):
        raise FormulaError("Formula did not evaluate to a number.")
    if isinstance(result, float) and (math.isnan(result) or math.isinf(result)):
        raise FormulaError("Formula produced an invalid result (NaN or Infinity). Check your inputs.")
    return result


def run_calculator(inputs_values: dict, formula_steps: list, final_formula: str, constants: dict = None):
    """
    Runs a full calculator: executes formula_steps in order (each can reference prior
    step results + original inputs + constants), then evaluates the final formula.

    inputs_values: { "loan_amount": 5000000, "annual_rate": 8.5, "tenure_months": 240 }
    formula_steps: [ { "var": "rate_monthly", "expr": "annual_rate / 12 / 100" }, ... ]
    final_formula: the last expression OR, if formula_steps already assigns to a var
                   named in outputs, final_formula can just reference that var.
    constants: extra named values available to all formulas, e.g. { "inflation_rate": 6.0 }

    Returns: dict of all intermediate + final variables computed.
    """
    variables = dict(constants or {})
    variables.update(inputs_values)

    for step in (formula_steps or []):
        var_name = step.get("var")
        expr = step.get("expr")
        if not var_name or not expr:
            continue
        try:
            variables[var_name] = evaluate_formula(expr, variables)
        except FormulaError as e:
            raise FormulaError(f"Error computing '{var_name}': {e}")

    if final_formula and final_formula.strip():
        try:
            variables["__result__"] = evaluate_formula(final_formula, variables)
        except FormulaError as e:
            raise FormulaError(f"Error computing final result: {e}")

    return variables


def validate_formula_syntax(formula: str, known_vars: list) -> dict:
    """
    Used by the admin panel's formula editor to validate a formula BEFORE saving,
    by running it once with dummy values (all known_vars = 1.0).
    Returns { "valid": True } or { "valid": False, "error": "..." }
    """
    dummy_vars = {v: 1.0 for v in known_vars}
    try:
        evaluate_formula(formula, dummy_vars)
        return {"valid": True}
    except FormulaError as e:
        return {"valid": False, "error": str(e)}
