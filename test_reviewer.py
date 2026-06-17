from agents import reviewer

state = {
    "requirement": "Build an astrology RAG application.",
    "architecture": """
Use PostgreSQL for structured data.

Use ChromaDB for vector search.

Expose APIs using FastAPI.

Deploy using Docker.
"""
}

result = reviewer(state)

print("\nReview:")
print(result["review"])

print("\nConcerns:")
print(result["concerns"])
