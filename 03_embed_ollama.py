import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import ollama

load_dotenv()

URI = os.environ["NEO4J_URI"]
AUTH = (os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])

EMBEDDING_MODEL = "nomic-embed-text"

def embed(text: str) -> list[float]:
    response = ollama.embed(model=EMBEDDING_MODEL, input=text)
    return response["embeddings"][0]

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    records, _, _ = driver.execute_query(
        "MATCH (c:Chunk) RETURN id(c) AS id, c.text AS text"
    )

    for record in records:
        vector = embed(record["text"])
        driver.execute_query(
            """
            MATCH (c:Chunk) WHERE id(c) = $id
            CALL db.create.setNodeVectorProperty(c, 'embedding', $vector)
            """,
            id=record["id"],
            vector=vector,
        )
        print(f"Embedded chunk {record['id']}")

print("All chunks embedded with Ollama.")