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

RETRIEVAL_QUERY = """
CALL db.index.vector.queryNodes('chunkEmbeddings', 3, $queryEmbedding)
YIELD node AS chunk, score
MATCH (chunk)<-[:HAS_CHUNK]-(doc:Document)-[:AUTHORED_BY]->(person:Person)
MATCH (person)-[:WORKS_ON]->(project:Project)
RETURN chunk.text AS text,
       doc.title AS document,
       person.name AS author,
       project.name AS project,
       score
ORDER BY score DESC
"""

question = "What did the team that built Project Atlas ship?"
query_vector = embed(question)

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    records, _, _ = driver.execute_query(
        RETRIEVAL_QUERY, queryEmbedding=query_vector
    )

    print(f"\nQuestion: {question}\n")
    for r in records:
        print(f"[score {r['score']:.3f}] {r['author']} on {r['project']}")
        print(f"  Document: {r['document']}")
        print(f"  Chunk: {r['text']}\n")