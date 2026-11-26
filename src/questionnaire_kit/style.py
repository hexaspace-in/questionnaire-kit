"""Interior style quiz: 6 profiles (modern minimalist, warm contemporary, industrial chic, bohemian eclectic,
luxury classic, japandi zen). Each answer option carries tags; tags map to profiles; the highest score wins."""
import json
from importlib import resources
from typing import List, Optional


def quiz_data() -> dict:
    """{"questions": [...], "profiles": {...}, "tag_map": {tag: [profile ids]}}"""
    return json.loads(resources.files(__package__).joinpath("style_quiz.json").read_text(encoding="utf-8"))


def score_style(answers: List[dict], data: Optional[dict] = None) -> dict:
    """answers: the chosen options (each with "tags"). Returns primary, secondary and the top scores."""
    d = data or quiz_data()
    scores = {p: 0 for p in d["profiles"]}
    for a in answers:
        for tag in a.get("tags", []):
            for p in d["tag_map"].get(tag, []):
                scores[p] = scores.get(p, 0) + 1
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary = ranked[0][0] if ranked else None
    return {"primary": primary, "secondary": ranked[1][0] if len(ranked) > 1 else None,
            "scores": dict(ranked[:4]), "profile": d["profiles"].get(primary) if primary else None}
