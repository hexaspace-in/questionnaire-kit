# questionnaire-kit

Client questionnaires for Python apps, plus an interior-design style quiz.

**Form engine** (any domain: client intake, site surveys, onboarding):
- Sections of questions in 10 types: short and long text, single and multiple choice, picture choice (photo or colour swatch), rating 1–5, dropdown, number, date, and photo upload
- **"Show only if"** logic: show a question only when an earlier answer matches `{"q": "type", "equals": "Villa"}` or any value in `{"q": "type", "any_of": ["Villa", "Penthouse"]}`. A multi-choice answer matches if at least one selected value matches. Use one operator per condition and a non-empty list for `any_of`.
- `check_questions()` validates a form: unique ids, at least 2 options for choices, conditions point back to earlier questions
- `clean_answers()` keeps only valid answers, drops answers to hidden questions, and on submit lists the required questions still unanswered
- `summary_rows()` gives (section, question, answer) rows for a PDF, an email or a CRM note

**Interior style quiz:** 6 questions and 6 style profiles (modern minimalist, warm contemporary, industrial chic, bohemian eclectic, luxury classic, japandi zen), with traits, materials and colour palettes. `score_style()` ranks the profiles from the client's answers.

Built from the client brief questionnaire and style quiz Hexaspace uses with clients.

## Example

```python
from questionnaire_kit import check_questions, clean_answers, summary_rows, quiz_data, score_style

check_questions(sections)                                  # when the form is saved
answers = clean_answers(sections, raw_answers, final=True) # when the client presses Submit
rows = summary_rows(sections, answers)

quiz = quiz_data()
result = score_style([chosen_option_1, chosen_option_2])  # {'primary': 'japandi-zen', 'profile': {...}, ...}
```

## Licence

MIT. Maintained by [Hexaspace](https://hexaspace.in).
