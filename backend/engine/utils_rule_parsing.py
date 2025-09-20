import json
import yaml
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Union
from django.core.files.uploadedfile import UploadedFile


def load_rules_from_file(file_or_path: Union[str, UploadedFile, Path]) -> Dict[str, Any]:
    if isinstance(file_or_path, (str, Path)):
        p = Path(str(file_or_path))
        if not p.exists():
            raise FileNotFoundError(str(file_or_path))
        suffix = p.suffix.lower()
        if suffix in {".yml", ".yaml"}:
            return yaml.safe_load(p.read_text(encoding="utf-8"))
        if suffix == ".json":
            return json.loads(p.read_text(encoding="utf-8"))
        if suffix in {".csv", ".xlsx"}:
            df = pd.read_csv(p) if suffix == ".csv" else pd.read_excel(p)
        else:
            raise ValueError(f"Unsupported rule file: {file_or_path}")
    else:
        name = file_or_path.name.lower()
        if name.endswith((".yml", ".yaml")):
            return yaml.safe_load(file_or_path.read().decode("utf-8"))
        if name.endswith(".json"):
            return json.loads(file_or_path.read().decode("utf-8"))
        if name.endswith((".csv", ".xlsx")):
            file_or_path.seek(0)
            if name.endswith(".csv"):
                df = pd.read_csv(file_or_path)
            else:
                df = pd.read_excel(file_or_path)
        else:
            raise ValueError(f"Unsupported rule file: {name}")
        rules = {}
        for _, row in df.iterrows():
            cat = str(row.get("category", "general")).strip()
            rule = {
                "id": str(row.get("id", f"rule_{_}")),
                "type": str(row.get("type", "threshold")).strip(),
                "field": str(row.get("field", "paid_amount_aed")).strip(),
                "operator": str(row.get("operator", ">")).strip(),
                "value": row.get("value", 0),
                "severity": str(row.get("severity", "medium")).strip(),
                "message": str(row.get("message", "Rule violation")).strip(),
                "error_type": str(row.get("error_type", "Technical error")).strip(),
            }
            rules.setdefault(cat, []).append(rule)
        return rules
