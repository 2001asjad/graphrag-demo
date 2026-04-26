# GraphRAG demo
 
A small, runnable demo showing how a knowledge graph plus vector search retrieves context that pure vector RAG misses. Five Python scripts, one Cypher query, about 30 minutes from clone to working query.
 
This is the companion repo to my blog post, [Why your RAG pipeline keeps hallucinating, and what one Cypher query can do about it](https://your-blog-link-here).
 
## What this shows
 
A vector store can find chunks that *look* like your question. It cannot tell you that Priya works on the Atlas team and Marco is the one who fixed the memory leak, because those are relationships, not text. A graph database stores those relationships as first-class citizens and lets you walk them in the same query that runs vector search.
 
The demo seeds a tiny knowledge graph (3 people, 2 projects, 5 documents), embeds each chunk with Ollama, and then runs a single Cypher query that does both the semantic match and the graph walk in one round trip.
 
## What you need
 
- Python 3.10 or newer
- A free [Neo4j AuraDB](https://console.neo4j.io) instance (takes 5 minutes to create)
- [Ollama](https://ollama.com) installed locally (no API key, runs on your machine)
## Setup
 
**1. Clone the repo and enter the folder**
 
```bash
git clone https://github.com/your-username/graphrag-demo.git
cd graphrag-demo
```
 
**2. Create your AuraDB instance**
 
Sign in to [console.neo4j.io](https://console.neo4j.io), click **New Instance**, choose the **Free** tier, give it a name, and pick a region. Aura will generate a password. Save the credentials file it offers, you only see the password once.
 
**3. Configure your credentials**
 
Copy the example environment file and fill in your Aura values.
 
```bash
cp .env.example .env
```
 
Open `.env` and paste in the URI, username, and password from the credentials file Aura gave you.
 
**4. Install Python dependencies**
 
```bash
python -m venv venv
source venv/bin/activate    # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```
 
**5. Set up Ollama**
 
If you don't have Ollama yet, install it from [ollama.com](https://ollama.com). On macOS the easiest path is `brew install ollama` followed by `brew services start ollama`. On Windows and Linux, follow the installer on the site.
 
Then pull the embedding model.
 
```bash
ollama pull nomic-embed-text
```
 
Verify the server is running.
 
```bash
curl http://localhost:11434
```
 
You should see `Ollama is running`.
 
## Run the demo
 
The scripts are numbered, run them in order.
 
```bash
python 01_seed_graph.py     # Creates the toy knowledge graph
python 02_create_index.py   # Creates the 768-dim vector index
python 03_embed.py          # Embeds every chunk with Ollama
python 04_ask.py            # Runs the GraphRAG retrieval query
```
 
The last script asks "What did the team that built Project Atlas ship?" and prints the top 3 chunks the graph-aware retriever returned. Output looks like this:
 
```
Question: What did the team that built Project Atlas ship?
 
[score 0.712] Priya Shah on Project Atlas
  Document: Atlas Q1 recap
  Chunk: Last quarter the Atlas team shipped the new ingestion pipeline...
 
[score 0.684] Marco Ribeiro on Project Atlas
  Document: Atlas postmortem notes
  Chunk: Marco led the debugging effort on the memory leak...
 
[score 0.588] Priya Shah on Project Atlas
  Document: Atlas roadmap
  Chunk: The Atlas roadmap for next quarter focuses on multi-region failover...
```
 
Notice how the top results all come back attributed to the right project and the right people, even though the question never named them. That is the graph traversal doing its job.
 
## The retrieval query
 
The interesting bit lives in `04_ask.py`. It's five lines.
 
```cypher
CALL db.index.vector.queryNodes('chunkEmbeddings', 3, $queryEmbedding)
YIELD node AS chunk, score
MATCH (chunk)<-[:HAS_CHUNK]-(doc:Document)-[:AUTHORED_BY]->(person:Person)
MATCH (person)-[:WORKS_ON]->(project:Project)
RETURN chunk.text, doc.title, person.name, project.name, score
ORDER BY score DESC
```
 
Line 1 runs vector search on the index. The two `MATCH` lines walk outward from each retrieved chunk, picking up the document, author, and project. The last line returns the lot.
 
## Try changing things
 
A few experiments that are quick to run and show off what the graph can do.
 
Try a question that doesn't name any project, like "Who has shipped something related to performance?" The answers should still come back from Atlas, because Priya's ingestion pipeline work and Marco's memory leak work both describe performance even though the word never appears in those chunks.
 
Add another `MATCH` clause to extend the traversal. Try pulling in a `:Team` label, or a `MENTIONS` relationship, and you'll see the retriever's awareness grow without changing the embedding step at all.
 
## What's not in this demo
 
This repo stops at retrieval. To close the RAG loop, take the `records` returned by `04_ask.py`, format them as context, and pass them to an LLM with a prompt like "answer using only the context below." That last step is independent of the graph, so I left it out to keep the demo focused on the part that's interesting.
 
## Useful links
 
- [Neo4j vector index docs](https://neo4j.com/docs/cypher-manual/current/indexes/semantic-indexes/vector-indexes/)
- [neo4j-graphrag Python package](https://pypi.org/project/neo4j-graphrag/), a production-ready wrapper around this pattern
- [GraphAcademy: Neo4j and LLM Fundamentals](https://graphacademy.neo4j.com/courses/llm-fundamentals/), a free course that walks through the full pipeline
## License
 
MIT
