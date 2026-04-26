import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.environ["NEO4J_URI"]
AUTH = (os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])

DROP_INDEX = "DROP INDEX chunkEmbeddings IF EXISTS"

CLEAR_OLD_EMBEDDINGS = """
MATCH (c:Chunk)
REMOVE c.embedding
"""

CREATE_INDEX = """
CREATE VECTOR INDEX chunkEmbeddings IF NOT EXISTS
FOR (c:Chunk) ON c.embedding
OPTIONS {indexConfig: {
  `vector.dimensions`: 768,
  `vector.similarity_function`: 'cosine'
}}
"""

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.execute_query(DROP_INDEX)
    print("Old index dropped.")
    driver.execute_query(CLEAR_OLD_EMBEDDINGS)
    print("Old embeddings removed from chunks.")
    driver.execute_query(CREATE_INDEX)
    print("New 768-dim index created.")