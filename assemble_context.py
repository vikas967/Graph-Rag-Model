# assemble_context.py
from typing import Dict, List

def subgraph_to_text(subgraph: Dict, max_sentences: int = 10) -> str:
    """
    Convert nodes & edges into a textual context the LLM can consume.
    Keep it short and provenance-rich.
    """
    nodes = subgraph.get("nodes", [])
    rels = subgraph.get("relationships", [])
    lines = []
    # Node summary
    if nodes:
        node_texts = [n.get("text") for n in nodes if n.get("text")]
        lines.append("Entities found: " + ", ".join(node_texts[:30]))
    # Relationship summary with provenance-like phrasing
    for r in rels[:max_sentences]:
        subj = r.get("start") or "UNKNOWN"
        pred = r.get("predicate") or "related_to"
        obj = r.get("end") or "UNKNOWN"
        lines.append(f"- {subj} {pred} {obj}.")
    if not lines:
        return ""
    return "\n".join(lines)

def build_prompt(question: str, subgraph: Dict, instructions: str = None) -> str:
    instructions = instructions or (
        "You are an expert assistant. Use the provided facts extracted from a knowledge graph to answer the question. "
        "If facts conflict or are insufficient, say so and suggest next steps."
    )
    context_text = subgraph_to_text(subgraph)
    prompt = f"{instructions}\n\nContext:\n{context_text}\n\nQuestion: {question}\n\nAnswer:"
    return prompt
