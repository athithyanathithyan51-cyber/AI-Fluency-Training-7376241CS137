# Analysis: Chatbot vs Rule-Based Workflow vs AI Agent
### Scenario: Academic Status Assistant (attendance % and internal marks lookup)

## 1. The Scenario

The scenario used here is an **Academic Status Assistant**: a small system that answers
questions about a student's attendance percentage and internal marks, and does simple
arithmetic on them (for example, adding bonus marks, or checking how far a student's
attendance is below the 75% condonation limit). The underlying data — attendance and
internal marks for a handful of roll numbers — is private college data. No public LLM has
ever been trained on it, since it exists only inside this project's `config.py`.

Four questions were used to test all three systems:
1. What is my attendance percentage for roll number CS137?
2. What is my total internal mark for DBMS and COMPUTER_NETWORKS for CS137 after adding 2 bonus marks?
3. Is CS137's attendance below the 75% condonation limit, and by how much?
4. Write a two-line motivational message for exam week.

## 2. Explanation of Each Approach

### 2.1 Plain Chatbot
The chatbot (`chatbot.py`) sends the user's question straight to the LLM and returns
whatever the model produces. It has no access to the attendance or marks data at all —
that data was never part of its training, and the code never places it in the prompt. For
questions 1 to 3, the chatbot has no choice but to guess a plausible-sounding number, or
to admit it does not know. When it guesses, the answer is fluent and confident but wrong;
this is hallucination, and it is dangerous precisely because nothing in the answer signals
that it might be false. Question 4 needs no private data, so the chatbot handles it well,
since generating a short motivational message is exactly the kind of free-form language
task an LLM is good at. In short, a plain chatbot provides responses using the LLM alone,
with no rules and no tools standing between the question and the answer.

### 2.2 Rule-Based Workflow
The workflow (`workflow.py`) uses no LLM anywhere. It is ordinary Python: a regular
expression pulls out a roll number, an if/else chain checks for keywords like "attendance",
"total", "internal", or "below", and a fixed calculation runs when a matching rule is found.
For questions 1 and 2, which match the patterns the code was written for, the workflow is
exact and instant every time, because the same input always runs through the same code
path. For question 3 it correctly compares against the fixed 75% limit. But it has no
concept of "understanding" the question — it only recognizes the specific keywords and
sentence shapes it was written to expect. Question 4 has no roll number and no numeric
keyword, so it falls through to the workflow's "no rule for this" fallback, even though it is a
perfectly reasonable request. Rephrasing any of questions 1 to 3 in different words (for
example, asking "how many bonus marks bring the total for CS137 up to X" instead of "total
... after adding") would very likely break the matching rules, since the workflow follows
predefined steps and conditions, with no reasoning about intent.

### 2.3 AI Agent
The agent (`agent.py` with `tools.py`) combines an LLM with two tools —
`get_attendance` and `get_internal_marks` for private-data lookups, and `calculator` for
arithmetic — inside a loop. For each question, the LLM reasons about what it needs,
requests a tool call, receives the result as an observation, and decides whether to call
another tool or give a final answer. For question 2, this means calling
`get_internal_marks` twice (once per subject) and then `calculator` to add the two marks
plus the bonus, all without the arithmetic ever being done by the LLM itself. For question 3,
it calls `get_attendance` and then reasons about the 75% limit directly, since simple
comparison does not need the calculator tool. For question 4, no tool is needed, so the
agent recognizes this and answers directly from the LLM, exactly as it should. The
limitation that shows up here is reliability: because the model decides the path itself, the
exact sequence of tool calls (and whether a tool is used at all) can vary between runs,
especially with a small local model, which sometimes ignores the available tools and
guesses instead — the same failure mode documented in the lab manual's troubleshooting
section.

## 3. Comparison Table

| Basis for comparison   | Plain chatbot                          | Rule-based workflow                       | AI agent                                             |
|-------------------------|-----------------------------------------|---------------------------------------------|--------------------------------------------------------|
| Flexibility              | High in language, but not in facts     | Very low — breaks outside its written rules | High — can combine tools in new ways for new questions |
| Decision-making          | Made once, within a single LLM reply    | None — path is fixed by the programmer      | Made repeatedly by the LLM across multiple steps        |
| Tool usage                | None                                    | Fixed function calls in a fixed order       | LLM chooses which tool to call and when                |
| Private-data access       | None                                    | Full, but only in ways the code anticipated | Full, and adaptable to how the question is phrased      |
| Multi-step task handling  | Poor — one reply, no follow-up actions  | Only the exact multi-step patterns coded    | Good — loop lets it chain several tool calls            |
| Automation                 | Fully automatic, but often wrong        | Fully automatic and correct, within scope   | Fully automatic, and correct across a wider range       |
| Reliability                | Low on private-data questions           | Very high — deterministic, same answer every time | Medium — path and wording can vary between runs   |

## 4. Suitability Analysis

For this Academic Status Assistant scenario, the **AI agent is the most suitable
approach overall**, but not for every part of it. The rule-based workflow is excellent for the
two or three exact question shapes it was written for — a finance or exam office running
the same fixed queries every day would prefer it, since its output is deterministic and easy
to audit, which matters when marks or attendance figures feed into official records. Its
weakness is that students rarely phrase questions exactly the way a programmer
anticipated, so the moment a question is unusual (question 4, or the challenge question
comparing two students), the workflow simply fails. The plain chatbot is the weakest
choice here: precisely because attendance and marks are private data, the chatbot cannot
get them right, and its confident wrong answers are worse than no answer at all. The
agent is the best fit because it can access the same private data as the workflow (through
tools, not training), but it can also combine that data flexibly — looking up two subjects
instead of one, comparing two students, or handling a phrasing nobody wrote a rule for
— while still keeping the actual numbers grounded in the tool results rather than
invented by the model. Its only real downside for this scenario is that a small or
unreliable model can occasionally skip a tool call and guess, so for a production version, it
would be worth adding a rule-based check that verifies a fee or mark was actually looked
up before the answer is shown to the student.

## 5. Conclusion

Across the three systems tested, a clear pattern emerges that generalizes well beyond this
one scenario. A **plain chatbot** is the right choice only when the task is truly single-turn,
needs no private or current data, and correctness is not critical — writing a welcome
message, drafting an email, or explaining a concept in the model's own words. A
**rule-based workflow** is the right choice when the steps are known in advance, the same
input must always give the same output, and errors are costly or must be traceable — fee
receipts, hall-ticket generation, and grade calculations are classic examples, since
predictability and auditability matter more than flexibility. An **AI agent** is the right
choice when the task is open-ended, the number or order of steps cannot be predicted in
advance, and the system needs to combine several sources of data or tools to answer
questions phrased in many different ways — an academic advisor bot, a research
assistant, or an IT support agent all fit this pattern. In practice, these are not mutually
exclusive: a real system might use a workflow for its common, well-defined queries and
fall back to an agent only when a question does not match any known pattern, giving both
the reliability of rules and the flexibility of reasoning where each is actually needed.
