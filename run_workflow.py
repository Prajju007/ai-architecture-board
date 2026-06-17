from workflow import graph

initial_state = {

    "requirement": """
Build an AI architecture board.

Multiple LLMs should discuss architecture decisions.

Decision history should be retained.

Claude should eventually execute approved decisions.
""",

    "architecture_v1": "",

    "reviews": [],

    "approved": False
}

result = graph.invoke(
    initial_state
)

print("\n===== FINAL RESULT =====\n")

print(result)