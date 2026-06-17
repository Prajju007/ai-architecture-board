from langgraph.graph import StateGraph

from state import AgentState
from agents import architect, reviewer, consensus

# Initialize the graph
graph = StateGraph(AgentState)

print("Graph initialized successfully!")

# (We will add nodes and edges in the next step)