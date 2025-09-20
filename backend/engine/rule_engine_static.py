from typing import Dict, Any, List
from .models import Claim

OP_MAP = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">": lambda a, b: (a or 0) > b,
    ">=": lambda a, b: (a or 0) >= b,
    "<": lambda a, b: (a or 0) < b,
    "<=": lambda a, b: (a or 0) <= b,
    "in": lambda a, b: a in b,
    "not in": lambda a, b: a not in b,
}


def evaluate_static_rules(claim: Claim, rules: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for category, rule_list in (rules or {}).items():
        for r in rule_list:
            field = r.get("field")
            op = r.get("operator", "==")
            value = r.get("value")
            error_type = r.get("error_type", "Technical error")
            message = r.get("message", "Rule violation")
            lhs = getattr(claim, field, None)
            fn = OP_MAP.get(op)
            try:
                ok = fn(lhs, value) if fn else False
            except Exception:
                ok = False
            if not ok:
                findings.append({
                    "category": category,
                    "rule_id": r.get("id"),
                    "field": field,
                    "operator": op,
                    "value": value,
                    "error_type": error_type,
                    "explanation": f"{message}: expected {field} {op} {value}, found {lhs}",
                    "recommendation": r.get("recommendation", f"Review {field} and correct per policy."),
                })
    return findings
