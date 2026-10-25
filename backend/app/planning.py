"""Bound model-generated search text without changing submitted incident evidence."""
import re

from .models import MAX_DECISION_REASON, MAX_SEARCH_QUERY


# Keep diagnostic codes/acronyms even when the model puts them at the end of a
# verbose query. This selects only text already present; it never invents terms.
DIAGNOSTIC_TERM = re.compile(r"\b(?:ORA-\d{5}|(?i:error(?:\s+code)?\s*[:=]?\s*\d+)|[A-Z][A-Z_]+\d+[A-Z0-9_-]*|[45]\d{2}|[A-Z]{2,})\b")


def compact_query(text, limit=MAX_SEARCH_QUERY):
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    candidates = DIAGNOSTIC_TERM.findall(normalized) + normalized.split()
    selected, seen = [], set()
    length = 0
    for token in candidates:
        token = token.strip(",;:.()[]")
        key = token.casefold()
        if not token or key in seen:
            continue
        seen.add(key)
        extra = len(token) + bool(selected)
        if length + extra <= limit:
            selected.append(token)
            length += extra
    return " ".join(selected)


def prepare_decision(content):
    """Normalize bounded text only; tool/type/extra-field validation stays strict."""
    if not isinstance(content, dict):
        return content, []
    prepared = dict(content)
    adjusted = []
    query = prepared.get("query")
    if isinstance(query, str):
        bounded = "" if prepared.get("tool") == "request_human" else compact_query(query)
        if bounded != query:
            prepared["query"] = bounded
            adjusted.append("query")
    reason = prepared.get("reason")
    if isinstance(reason, str) and len(reason) > MAX_DECISION_REASON:
        # The explanation is display text, never a command or an evidence quote.
        excerpt = reason[:MAX_DECISION_REASON - 1].rsplit(" ", 1)[0]
        prepared["reason"] = excerpt + "?"
        adjusted.append("reason")
    return prepared, adjusted

def enforce_tool_intent(decision, incident, signals):
    """Memory retrieval needs explicit user intent, not a model-invented reason."""
    if decision['tool'] != 'search_memory':
        return decision, False
    title = incident['title']
    history = r'(?:previous|prior|past|historical|history|earlier|similar)'
    requested = (re.search(r'\b(?:find|search|recall|compare|show|review|look up)\b.{0,100}\b' + history + r'\b', title, re.I)
                 or re.search(r'^\s*' + history + r'\s+incidents?\b', title, re.I))
    if requested:
        return decision, False
    concrete = bool(signals['categories'] or signals['http_codes'] or re.search(
        r'\b(?:[A-Z]{2,}\d{2,}|ECONNRESET|\w+Exception)\b|\berror(?:\s+code)?\s*[:=]?\s*\d+\b', incident['logs']))
    return {'tool': 'search_runbooks' if concrete else 'request_human',
            'query': decision['query'] if concrete else '',
            'reason': ('Search current failure guidance; previous-incident retrieval was not requested.' if concrete
                       else 'Previous-incident retrieval was not requested. Please supply a concrete failure observation.')}, True
