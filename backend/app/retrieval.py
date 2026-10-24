"""Versioned retrieval inputs; stored quotations retain original source text."""
import re

INDEX_VERSION = "nomic-tasks-sentence-v2"


def embedding_inputs(model, texts, task):
    if task not in {"document", "query"}:
        raise ValueError("Unknown embedding task")
    prefix = f"search_{task}: " if model.split(":")[0] == "nomic-embed-text" else ""
    return [prefix + text for text in texts]


def chunk_text(text, max_chars=1000, overlap=100):
    """Prefer paragraph/sentence boundaries, preserving contiguous quotations."""
    if not 0 <= overlap < max_chars:
        raise ValueError("Overlap must be smaller than chunk size")
    boundaries = [m.end() for m in re.finditer(r"\n\s*\n|(?<=[.!?])\s+|\n", text)]
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            candidates = [b for b in boundaries if start + max_chars // 2 <= b <= end]
            if candidates:
                end = candidates[-1]
        if text[start:end].strip():
            yield text[start:end]
        if end == len(text):
            break
        candidates = [b for b in boundaries if max(start + 1, end - overlap) <= b < end]
        start = candidates[0] if candidates else end
