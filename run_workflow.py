import json

from workflow import graph


with open("sample_prd.json", "r") as f:
    prd = json.load(f)

initial_state = {

    "prd": prd,

    "decision_context": {},

    "architecture_v1": "",

    "reviews": [],

    "approved": False
}

result = graph.invoke(
    initial_state
)

print("\n===== FINAL RESULT =====\n")

print(result)