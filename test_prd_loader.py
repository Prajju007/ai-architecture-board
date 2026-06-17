import json


with open("sample_prd.json", "r") as f:
    prd = json.load(f)

print("\n===== PRD LOADED =====\n")

print(json.dumps(
    prd,
    indent=2
))
