# Day 1 Lab — Observations

Provider used: Groq (`llama-3.1-8b-instant`)

## 10. Observation Table

| Criterion | Chatbot | Workflow | Agent |
|---|---|---|---|
| Q1 correct? | N — guessed a plausible-sounding fee, not Rs. 18,000 | Y | Y |
| Q2 correct? | N — guessed both course fees, wrong total | Y | Y |
| Q3 correct? | N — guessed both fees and the difference | N — no rule written for a "which is more expensive" comparison | Y |
| Q4 handled well? | Y — no data needed, plain language task | N — falls back to "I can only answer questions about course fees" | Y |
| Challenge question handled? | — (not tested on chatbot) | N — no rule for a budget-fitting question | Y — looked up all three fees and tested pairs with the calculator |
| Same output on a repeat run? | N — wording and even the guessed numbers vary between runs | Y — identical every time | N — tool-call order and phrasing can vary slightly, though the final numeric answer stayed correct |
| Approximate response time | ~1 second | Instant (<0.01s) | 2–4 seconds (multiple LLM calls per question) |
| Number of LLM calls per question | 1 | 0 | 1–3 (one reasoning call per tool call, plus the final answer) |
| One strength | Fluent, natural language for any question | Perfectly reliable and instant for the questions it was built for | Gets the private data right by using tools instead of guessing |
| One weakness | Hallucinates confidently on private-data questions | Breaks completely on any wording or question type it wasn't coded for | Slower, costs more LLM calls, and its exact path can vary between runs |
| Best suited for (one real use case) | Explaining a general concept or drafting text with no private data involved | Generating fee receipts or hall tickets, where the same input must always give the same output | An academic-advisor bot that has to combine several pieces of data to answer varied student questions |

## Agent Trace — Question 2
"What is the total fee for CS101 and AI202 after a 10% scholarship?"

| Step | Tool called and arguments | Result (observation) |
|---|---|---|
| 1 | `get_course_fee({'course_code': 'CS101'})` | 12000 |
| 2 | `get_course_fee({'course_code': 'AI202'})` | 18000 |
| 3 | `calculator({'expression': '(12000 + 18000) * 0.9'})` | 27000.0 |
| 4 | — final answer — | "The total fee after a 10% scholarship is Rs. 27,000." |

## 11. Discussion Questions

**1. The chatbot gave a confident but wrong fee. Why is that more dangerous than replying "I don't know"?**
A wrong-but-confident answer gives no signal to the reader that they should double-check it. A student reading "the fee for AI202 is Rs. 25,000" has no reason to doubt it unless they already know the real figure — the error only surfaces later, when it's harder to trace back and fix. "I don't know" is far safer because it correctly transfers the responsibility for finding the real number back to the user instead of quietly handing them a fabricated one.

**2. The workflow was always correct for questions 1 and 2. Why might a finance office still prefer it over the agent?**
The workflow is fully deterministic — the same input always produces the same output, with zero LLM calls, so there is nothing to audit beyond reading the code once. A finance office cares about traceability, speed, and cost: every rupee figure it produces must be exactly reproducible and explainable to an auditor. The agent, even when it gets the right answer, takes a path that can vary slightly between runs and depends on a paid or rate-limited external model, which is unnecessary risk and cost for a task whose logic never changes.

**3. The agent's steps can change between runs. What problems would that cause in a real product?**
Two identical requests from two different students could take different numbers of tool calls, different latencies, and occasionally different (or incomplete) answers, which makes the product harder to test, debug, and trust. Support tickets become hard to reproduce ("it worked when I tried it") and monitoring dashboards can't rely on a single expected trace, since the "correct" trace is not fixed — only the desired final answer is.

**4. Design a system that uses a workflow for common questions and an agent for the rest. Where would you draw the line?**
A router step would first try to match the question against the workflow's known patterns (single-course fee lookup, total with scholarship, hall ticket requests, etc.), since those are frequent and must be exact. If no pattern matches — an unusual phrasing, a multi-condition comparison, or a question spanning several data sources — the request would fall through to the agent, which has the tools to reason it out. The line should sit at "is this a known, fixed, auditable calculation?" — if yes, workflow; if the number or order of steps genuinely can't be predicted in advance, agent.

**5. Which parts of agent.py are the LLM, the tools, and the loop?**
The LLM is the `client.chat.completions.create(...)` call inside `agent()` — it is consulted once per step to decide what happens next. The tools are the functions imported from `tools.py` (`get_course_fee` and `calculator`) together with their `TOOLS` JSON-schema descriptions, which are what the LLM is allowed to request. The loop is the `for step in range(1, max_steps + 1):` block — the plain Python code that keeps calling the LLM, running whichever tool it asks for, and feeding the result back into `messages` until the LLM stops requesting tools or the step limit is reached.

## 14. Result

Thus, a Python environment was set up in VS Code and connected to an open large language model (via the Groq API), and a chatbot, a rule-based workflow, and an AI agent were implemented and compared on the same task. The observations show that **the chatbot is fluent but unreliable on private data, the workflow is perfectly reliable but only within the exact question patterns it was coded for, and the AI agent is the most flexible of the three because it combines LLM reasoning with tool calls to get the private data right, correctly handling the challenge question that broke the workflow — at the cost of slower, less exactly-repeatable responses.**
