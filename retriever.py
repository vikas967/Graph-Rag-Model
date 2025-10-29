# retriever.py
from graph_db import GraphDB
from typing import List
import re

def extract_seed_terms_from_question(question: str):
    # naive: return nouns / proper nouns from question using spaCy
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(question)
    seeds = []
    for token in doc:
        if token.pos_ in ("NOUN", "PROPN"):
            seeds.append(token.text)
    # also pick named entities
    seeds += [ent.text for ent in doc.ents]
    # de-dup & simple cleaning
    seeds = list(dict.fromkeys([s.strip() for s in seeds if len(s.strip()) > 1]))
    return seeds or [question]  # fallback

class GraphRetriever:
    def __init__(self, graph_db: GraphDB):
        self.graph_db = graph_db

    def retrieve(self, question: str, depth: int = 2):
        seeds = extract_seed_terms_from_question(question)
        subgraph = self.graph_db.query_subgraph(seeds, depth=depth)
        return {"seeds": seeds, "subgraph": subgraph}
