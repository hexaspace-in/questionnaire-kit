import pytest

from questionnaire_kit import QuestionError, check_questions, clean_answers, quiz_data, score_style, summary_rows, visible

SECTIONS = [{"title": "Home", "questions": [
    {"id": "type", "label": "Home type", "type": "single", "required": True, "options": [{"label": "Flat"}, {"label": "Villa"}]},
    {"id": "floors", "label": "How many floors?", "type": "number", "required": True, "show_if": {"q": "type", "equals": "Villa"}},
    {"id": "rooms", "label": "Rooms to design", "type": "multi", "options": [{"label": "Kitchen"}, {"label": "Living"}]},
    {"id": "happy", "label": "How happy are you with your current home?", "type": "rating"},
]}]


def test_check_questions_ok_and_errors():
    check_questions(SECTIONS)
    with pytest.raises(QuestionError):
        check_questions([{"questions": [{"id": "a", "label": "Pick", "type": "single", "options": [{"label": "x"}]}]}])
    with pytest.raises(QuestionError):
        check_questions([{"questions": [{"id": "a", "label": "Later", "show_if": {"q": "zz", "equals": "1"}}]}])


def test_clean_and_conditional():
    out = clean_answers(SECTIONS, {"type": "Flat", "floors": "2", "rooms": ["Kitchen", "Garage"], "happy": "9"}, final=True)
    assert out == {"type": "Flat", "rooms": ["Kitchen"]}          # floors hidden, bad option and bad rating dropped
    with pytest.raises(QuestionError):
        clean_answers(SECTIONS, {"type": "Villa"}, final=True)    # floors now required
    rows = summary_rows(SECTIONS, {"type": "Villa", "floors": 2.0, "happy": 4})
    assert rows[1] == ["Home", "How many floors?", "2"] and rows[2][2] == "4 / 5"


def test_style_quiz():
    d = quiz_data()
    assert len(d["profiles"]) >= 6
    first = d["questions"][0]["options"][1]                       # Bedroom: private, calm
    r = score_style([first, first])
    assert r["primary"] in d["profiles"] and r["profile"]["name"]


def test_any_of_visibility_and_required_answers():
    condition = {"id": "floors", "label": "Floors", "type": "number", "required": True,
                 "show_if": {"q": "type", "any_of": ["Villa", "Penthouse"]}}
    sections = [{"questions": [SECTIONS[0]["questions"][0], condition]}]
    check_questions(sections)
    for answer in ("Villa", "Penthouse", ["Flat", "Villa"]):
        assert visible(condition, {"type": answer})
    for answer in ("Flat", ["Flat"], []):
        assert not visible(condition, {"type": answer})
    assert not visible(condition, {})
    assert clean_answers(sections, {"type": "Flat", "floors": 2}, final=True) == {"type": "Flat"}
    with pytest.raises(QuestionError, match="Floors"):
        clean_answers(sections, {"type": "Villa"}, final=True)
    assert clean_answers(sections, {"type": "Villa", "floors": 2}, final=True)["floors"] == 2.0


@pytest.mark.parametrize("condition", [
    {"q": "type", "any_of": "Villa"},
    {"q": "type", "any_of": []},
    {"q": "type", "any_of": ["Villa"], "equals": "Villa"},
    {"q": "type"},
    {"q": "later", "any_of": ["Villa"]},
])
def test_bad_any_of_conditions(condition):
    sections = [{"questions": [SECTIONS[0]["questions"][0],
                              {"id": "floors", "label": "Floors", "show_if": condition}]}]
    with pytest.raises(QuestionError):
        check_questions(sections)
