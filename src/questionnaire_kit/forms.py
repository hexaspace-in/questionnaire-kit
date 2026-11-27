"""Form engine: sections of questions, "show only if" logic, answer cleaning, required checks, summary rows.

A question is a dict: {"id", "label", "type", "help"?, "required"?, "options"?: [{"label", "image"?, "swatch"?}],
"multi_image"?, "show_if"?: {"q": earlier_id, "equals": value} or {"q": earlier_id, "any_of": [values]}}.
Types: short, long, single, multi, image (picture choice), rating (1-5), dropdown, number, date, photo (file ids).
"""
from typing import Dict, List, Optional

QTYPES = ("short", "long", "single", "multi", "image", "rating", "dropdown", "number", "date", "photo")
CHOICE = ("single", "multi", "image", "dropdown")
MAX_FILES = 5


class QuestionError(ValueError):
    """Raised with a message you can show to the form builder or the person filling it."""


def _question(raw: dict) -> dict:
    label = str(raw.get("label") or "")
    if not raw.get("id") or len(str(raw["id"])) > 40:
        raise QuestionError(f"Question “{label or '?'}”: needs an id (max 40 characters)")
    if not (2 <= len(label) <= 240):
        raise QuestionError(f"Question “{label or '?'}”: label must be 2-240 characters")
    q = {"type": "short", **raw}
    if q["type"] not in QTYPES:
        raise QuestionError(f"Question “{label}”: unknown type {q['type']}")
    if len(q.get("options") or []) > 20:
        raise QuestionError(f"Question “{label}”: at most 20 options")
    return q


def check_questions(sections: List[dict]) -> None:
    """Raise QuestionError on a bad question set (ids unique across the form, choices have options, show_if points back)."""
    seen = {}
    for s in sections:
        for raw in s.get("questions") or []:
            q = _question(raw)
            if q["id"] in seen:
                raise QuestionError(f"Two questions use the id {q['id']}")
            if q["type"] in CHOICE and len(q.get("options") or []) < 2:
                raise QuestionError(f"“{q['label']}” needs at least 2 options")
            condition = q.get("show_if")
            if condition:
                if not isinstance(condition, dict) or condition.get("q") not in seen:
                    raise QuestionError(f"“{q['label']}”: 'show only if' must point to an earlier question")
                if ("equals" in condition) == ("any_of" in condition):
                    raise QuestionError(f"“{q['label']}”: 'show only if' needs exactly one of equals or any_of")
                if "any_of" in condition and (not isinstance(condition["any_of"], list) or not condition["any_of"]):
                    raise QuestionError(f"“{q['label']}”: 'any_of' must be a non-empty list")
            seen[q["id"]] = q


def visible(q: dict, answers: dict) -> bool:
    c = q.get("show_if")
    if not c:
        return True
    a = answers.get(c["q"])
    values = c["any_of"] if "any_of" in c else [c["equals"]]
    return any(value in a for value in values) if isinstance(a, list) else a in values


def clean_answers(sections: List[dict], answers: dict, final: bool, uploads: Optional[Dict[str, str]] = None) -> dict:
    """Keep only valid answers for known questions; on submit, required visible questions must be answered."""
    out, missing = {}, []
    for s in sections:
        for q in s.get("questions") or []:
            a = answers.get(q["id"])
            labels = [o["label"] for o in q.get("options") or []]
            if q["type"] in ("multi",) or (q["type"] == "image" and q.get("multi_image")):
                a = [x for x in (a if isinstance(a, list) else []) if x in labels][:20]
            elif q["type"] in ("single", "dropdown", "image"):
                a = a if a in labels else None
            elif q["type"] == "photo":           # ids of files this client uploaded for this question
                a = [x for x in (a if isinstance(a, list) else []) if (uploads or {}).get(x) == q["id"]][:MAX_FILES]
            elif q["type"] == "rating":
                a = int(a) if str(a).isdigit() and 1 <= int(a) <= 5 else None
            elif q["type"] == "number":
                try:
                    a = float(a) if a not in (None, "") else None
                except (TypeError, ValueError):
                    a = None
            else:
                a = str(a).strip()[:2000] if a not in (None, "") else None
            if a not in (None, "", []):
                out[q["id"]] = a
    for s in sections:                     # answers to questions that are hidden by an earlier answer are dropped
        for q in s.get("questions") or []:
            if q["id"] in out and not visible(q, out):
                out.pop(q["id"])
    if final:
        for s in sections:
            for q in s.get("questions") or []:
                if q.get("required") and visible(q, out) and q["id"] not in out:
                    missing.append(q["label"])
        if missing:
            raise QuestionError("Please answer: " + "; ".join(missing[:5]))
    return out


def format_answer(a, q: Optional[dict] = None) -> str:
    if q and q.get("type") == "photo":
        return f"{len(a)} file{'s' if len(a) != 1 else ''} uploaded"
    if isinstance(a, list):
        return ", ".join(a)
    if isinstance(a, float):
        return f"{a:g}"
    if isinstance(a, int):
        return f"{a} / 5"
    return str(a)


def summary_rows(sections: List[dict], answers: dict) -> List[List[str]]:
    rows = []
    for s in sections:
        for q in s.get("questions") or []:
            if q["id"] in answers and visible(q, answers):
                rows.append([s.get("title") or "", q["label"], format_answer(answers[q["id"]], q)])
    return rows
