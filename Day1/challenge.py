"""A question none of the three systems was designed for."""
from workflow import workflow
from agent import agent

QUESTION = "Between CS137 and CS101, who has better attendance and by how much?"

print("Q:", QUESTION)
print("\nWorkflow :", workflow(QUESTION))
print("\nAgent    :", agent(QUESTION))
