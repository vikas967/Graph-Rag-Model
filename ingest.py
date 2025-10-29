# ingest.py
from typing import List, Tuple, Dict
import spacy

nlp = spacy.load("en_core_web_trf")  # or en_core_web_sm for speed

def extract_entities_and_relations(text: str):
    """
    Returns:
      entities: List[dict] with keys: id, text, label
      relations: List[dict] with keys: subject, predicate, object, provenance
    """
    doc = nlp(text)
    entities = []
    ent_map = {}
    for i, ent in enumerate(doc.ents):
        eid = f"ENT{i}"
        ent_map[(ent.start_char, ent.end_char)] = eid
        entities.append({"id": eid, "text": ent.text, "label": ent.label_})

    relations = []
    # Simple pattern-based relation extraction:
    # e.g., "Drug A treats Disease B" or "A is used to treat B"
    for sent in doc.sents:
        sdoc = nlp(sent.text)  # parse sentence
        # find candidate subject/object by entity presence
        sent_ents = [e for e in sdoc.ents]
        if len(sent_ents) >= 2:
            # naive: choose first two entities as subject/object
            subj = sent_ents[0]
            obj = sent_ents[1]
            predicate = None
            # look for verbs in between
            for token in sdoc:
                if token.pos_ == "VERB":
                    predicate = token.lemma_
                    break
            if predicate is None:
                predicate = "related_to"
            relations.append({
                "subject": subj.text,
                "predicate": predicate,
                "object": obj.text,
                "provenance": sent.text
            })

    # fallback: if no NER, do noun-chunk heuristics
    if not entities:
        for i, chunk in enumerate(doc.noun_chunks):
            entities.append({"id": f"ENT_nc_{i}", "text": chunk.text, "label": "NOUN_CHUNK"})

    return entities, relations

if __name__ == "__main__":
    example = ("Aspirin treats headache. "
               "Remdesivir has been used to treat COVID-19 in hospitalized patients. "
               "Metformin is used for Type 2 Diabetes.")
    ents, rels = extract_entities_and_relations(example)
    print("ENTITIES:", ents)
    print("RELATIONS:", rels)
