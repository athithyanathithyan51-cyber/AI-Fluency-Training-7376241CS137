"""System 2: a rule-based workflow. Fixed if/else rules, no LLM at all."""
import re
from config import ATTENDANCE, INTERNAL_MARKS, QUESTIONS

CONDONATION_LIMIT = 75


def workflow(question):
    text = question.upper()
    roll_match = re.search(r"\bCS\d{3}\b", text)
    roll = roll_match.group(0) if roll_match else None

    if "ATTENDANCE" in text and "BELOW" not in text and roll:
        pct = ATTENDANCE.get(roll)
        if pct is None:
            return f"No attendance record for {roll}."
        return f"Attendance for {roll}: {pct}%"

    if "BELOW" in text and "75" in text and roll:
        pct = ATTENDANCE.get(roll)
        if pct is None:
            return f"No attendance record for {roll}."
        if pct < CONDONATION_LIMIT:
            return f"Yes, {roll} is below 75% by {CONDONATION_LIMIT - pct} points."
        return f"No, {roll} meets the 75% condonation limit."

    if "TOTAL" in text and "INTERNAL" in text and roll:
        subjects = re.findall(r"[A-Z_]+(?=[, ]|$)", text)
        marks = [INTERNAL_MARKS[(roll, s)] for s in subjects if (roll, s) in INTERNAL_MARKS]
        if not marks:
            return "Sorry, I do not have marks for the subjects mentioned."
        total = sum(marks)
        bonus_match = re.search(r"(\d+)\s*BONUS", text)
        if bonus_match:
            total += int(bonus_match.group(1))
        return f"Total internal marks for {roll}: {total}"

    return "Sorry, I do not have a rule for this type of question."


if __name__ == "__main__":
    print("\n=== SYSTEM 2: RULE-BASED WORKFLOW (no LLM) ===\n")
    for question in QUESTIONS:
        print("Q:", question)
        print("A:", workflow(question))
        print("-" * 70)
