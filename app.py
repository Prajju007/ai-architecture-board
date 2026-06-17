from langgraph.graph import StateGraph

from state import AgentState
from agents import architect, reviewer, consensus

# Initialize the graph
graph = StateGraph(AgentState)

print("AI Engineering Board")

# (We will add nodes and edges in the next step)