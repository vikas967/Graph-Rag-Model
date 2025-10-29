# graph_db.py
from neo4j import GraphDatabase
from typing import List, Dict
import os

NEO4J_URI = ".com"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Neo4J_password"

class GraphDB:
    def __init__(self, uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def upsert_entity(self, tx, entity: Dict):
        tx.run(
            """
            MERGE (e:Entity {text:$text, label:$label})
            ON CREATE SET e.created = timestamp()
            """,
            text=entity["text"], label=entity.get("label", "UNKNOWN")
        )

    def upsert_relation(self, tx, subj_text: str, rel: str, obj_text: str, provenance: str = None):
        tx.run(
            """
            MERGE (s:Entity {text:$subj})
            MERGE (o:Entity {text:$obj})
            MERGE (s)-[r:RELATION {predicate:$rel}]->(o)
            ON CREATE SET r.provenance = $prov, r.created = timestamp()
            """,
            subj=subj_text, obj=obj_text, rel=rel, prov=provenance
        )

    def ingest(self, entities: List[Dict], relations: List[Dict]):
        with self.driver.session() as sess:
            for e in entities:
                sess.execute_write(self.upsert_entity, e)  # ✅ updated
            for r in relations:
                sess.execute_write(
                    self.upsert_relation,
                    r["subject"],
                    r["predicate"],
                    r["object"],
                    r.get("provenance")
                )

    def query_subgraph(self, seed_terms: List[str], depth: int = 1, limit: int = 50):
        query = """
        UNWIND $seeds AS seed
        MATCH (s:Entity {text:seed})
        CALL apoc.path.subgraphAll(s, {maxLevel: $depth}) YIELD nodes, relationships
        RETURN nodes, relationships
        LIMIT $limit
        """
        with self.driver.session() as sess:
            result = sess.run(query, seeds=seed_terms, depth=depth, limit=limit)
            records = result.single()
            if records is None:
                return {"nodes": [], "relationships": []}
            nodes = [dict(n) for n in records["nodes"]]
            relationships = []
            for r in records["relationships"]:
                relationships.append({
                    "start": r.start_node["text"] if r.start_node else None,
                    "end": r.end_node["text"] if r.end_node else None,
                    "predicate": r.get("predicate") or r.type
                })
            return {"nodes": nodes, "relationships": relationships}

        





