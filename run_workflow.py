import json

from workflow import graph

with open("sample_prd.json", "r") as f:
    prd = json.load(f)

initial_state = {

    "prd": prd,

    "decision_context": {},

    "gpt_initial_position": "",

    "gemini_initial_position": "",

    "deliberation_history": [],

    "gpt_final_position": "",

    "gemini_final_position": "",

    "consensus_artifact": ""
}

result = graph.invoke(
    initial_state
)

print("\n==============================")
print("DECISION CONTEXT")
print("==============================\n")

print(
    json.dumps(
        result["decision_context"],
        indent=2
    )
)

print("\n==============================")
print("GPT INITIAL POSITION")
print("==============================\n")

print(
    result["gpt_initial_position"]
)

print("\n==============================")
print("GEMINI INITIAL POSITION")
print("==============================\n")

print(
    result["gemini_initial_position"]
)

print("\n==============================")
print("DELIBERATION")
print("==============================\n")

for item in result["deliberation_history"]:

    print(
        f"\n[{item['author']}]\n"
    )

    print(
        item["comment"]
    )

print("\n==============================")
print("GPT FINAL POSITION")
print("==============================\n")

print(
    result["gpt_final_position"]
)

print("\n==============================")
print("GEMINI FINAL POSITION")
print("==============================\n")

print(
    result["gemini_final_position"]
)