import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.environ["NEO4J_URI"]
AUTH = (os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"])

SEED = """
// Clean slate so this script is safe to re-run
MATCH (n) DETACH DELETE n;
"""

CREATE = """
// People
CREATE (priya:Person {name: 'Priya Shah'})
CREATE (marco:Person {name: 'Marco Ribeiro'})
CREATE (aisha:Person {name: 'Aisha Khan'})

// Projects
CREATE (atlas:Project {name: 'Project Atlas'})
CREATE (beacon:Project {name: 'Project Beacon'})

// Who works on what
CREATE (priya)-[:WORKS_ON]->(atlas)
CREATE (marco)-[:WORKS_ON]->(atlas)
CREATE (aisha)-[:WORKS_ON]->(beacon)

// Documents and the chunks inside them
CREATE (d1:Document {title: 'Atlas Q1 recap'})
CREATE (c1:Chunk {text: 'Last quarter the Atlas team shipped the new ingestion pipeline and cut average latency from 800ms to 120ms.'})
CREATE (d1)-[:HAS_CHUNK]->(c1)
CREATE (d1)-[:AUTHORED_BY]->(priya)

CREATE (d2:Document {title: 'Atlas postmortem notes'})
CREATE (c2:Chunk {text: 'Marco led the debugging effort on the memory leak that blocked the March release of Atlas.'})
CREATE (d2)-[:HAS_CHUNK]->(c2)
CREATE (d2)-[:AUTHORED_BY]->(marco)

CREATE (d3:Document {title: 'Beacon design doc'})
CREATE (c3:Chunk {text: 'Aisha proposed a new caching layer for Beacon that would sit between the API gateway and the auth service.'})
CREATE (d3)-[:HAS_CHUNK]->(c3)
CREATE (d3)-[:AUTHORED_BY]->(aisha)

CREATE (d4:Document {title: 'Atlas roadmap'})
CREATE (c4:Chunk {text: 'The Atlas roadmap for next quarter focuses on multi-region failover and a redesign of the write path.'})
CREATE (d4)-[:HAS_CHUNK]->(c4)
CREATE (d4)-[:AUTHORED_BY]->(priya)

CREATE (d5:Document {title: 'Beacon launch notes'})
CREATE (c5:Chunk {text: 'Beacon went live in production on April 2 and currently handles about 4000 requests per second at peak.'})
CREATE (d5)-[:HAS_CHUNK]->(c5)
CREATE (d5)-[:AUTHORED_BY]->(aisha)
"""

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    driver.execute_query(SEED)
    driver.execute_query(CREATE)
    print("Seed graph created.")