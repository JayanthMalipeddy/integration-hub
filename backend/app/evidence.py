"""Conservative evidence contract: observations are quoted, causes remain unverified.

This module does not pretend lexical matching proves semantic entailment. Model
prose is a draft; accepted summaries are rendered from supplied evidence only.
"""
import hashlib
import json
import re

CATEGORY_PATTERNS = {
    "authentication": r"\b401\b|invalid[_ ]token|expired[_ ]token|token expired|unauthorized",
    "rate_limit": r"\b429\b|rate.?limit|too many requests",
    "timeout": r"\b(?:408|504)\b|timed? ?out|timeout",
    "connection_pool": r"pool.{0,100}(?:exhaust|maximum|full|connection not available)|SQLTransientConnectionException|connection acquisition",
    "database_storage": r"ORA-016(?:53|54|91)\b|unable to extend (?:table|index|lob)",
    "authentication_load": r"PBKDF2|password verification|CPU.{0,25}(?:saturat|9\d\s*%)",
}


def categories(text):
    return [name for name, pattern in CATEGORY_PATTERNS.items() if re.search(pattern, text, re.I)]


def observations(logs, limit=8):
    """Exact source excerpts with stable line references, scanning the entire input."""
    found = []
    for number, line in enumerate(logs.splitlines(), 1):
        matches = list(re.finditer('|'.join(CATEGORY_PATTERNS.values()), line, re.I))
        if not matches:
            continue
        for match in matches:
            start = max(0, match.start() - 50)
            quote = line[start:start + 160].strip()
            if quote and not any(item['quote'] == quote for item in found):
                found.append({'source_id': 'incident:logs', 'line_id': f'L{number}',
                              'quote': quote, 'categories': categories(quote)})
    # Cover different signals before repeating one family of errors.
    chosen, covered = [], set()
    for item in found:
        if set(item['categories']) - covered:
            chosen.append(item); covered.update(item['categories'])
    chosen += [item for item in found if item not in chosen]
    return chosen[:limit]


def select_context(logs, limit=1800):
    selected, used, seen = [], 0, set()
    candidates = [(item['line_id'], item['quote']) for item in observations(logs)]
    candidates += [(f'L{i}', line) for i, line in enumerate(logs.splitlines(), 1) if line.strip()]
    for line_id, text in candidates:
        if (line_id, text) in seen:
            continue
        seen.add((line_id, text))
        remaining = limit - used - len(line_id) - 4
        if remaining < 20:
            break
        excerpt = text[:remaining]
        selected.append({'line_id': line_id, 'text': excerpt})
        used += len(excerpt) + len(line_id) + 4
    return {'source_id': 'incident:logs', 'lines': selected,
            'total_characters': len(logs), 'selection_limit': limit,
            'coverage': 'selected excerpts; full evidence retained'}


def grounded_summary(logs):
    facts = observations(logs, 3)
    text = '; '.join(f"{f['line_id']}: {f['quote'][:130]}" for f in facts)
    return ('Reported observations: ' + (text or 'No supported failure observation supplied.')
            + ' Root cause is not established.')[:600]


def questions(logs):
    active = set(categories(logs))
    result = []
    if 'database_storage' in active:
        result.append('Ask the DBA to provide the affected tablespace, allocation error and available capacity at the incident time; paste their sanitized findings or state unavailable.')
    if 'authentication_load' in active:
        result.append('Provide timestamped CPU readings and two thread-dump summaries showing authentication work, plus request rate/concurrency; state unavailable for anything you cannot obtain.')
    if 'connection_pool' in active:
        result.append('Provide active/max connections, acquisition wait time and any database errors at the same timestamp; a connection acquisition failure alone does not establish a leak.')
    if 'timeout' in active:
        result.append('Provide the request timeout location, elapsed duration and correlated upstream timing; identify which observations came from the same node and time window.')
    if 'authentication' in active:
        result.append('Provide the sanitized rejection reason, token expiry/clock observations and issuer/audience checks; never paste credentials.')
    if 'rate_limit' in active:
        result.append('Provide Retry-After, the agreed quota and request concurrency; do not replay non-idempotent operations to test a theory.')
    result.append('Provide the incident time, affected scope, recent changes and an exact error or observation; explicitly label unavailable evidence and conflicting observations.')
    return result[:4]


def source_guidance(evidence, citations):
    cited = {c['source_id'] for c in citations}
    guidance = []
    for passage in evidence:
        if passage['id'] not in cited or passage.get('kind') == 'reviewed_hypothesis':
            continue
        for sentence in re.split(r'(?<=[.!?])\s+', passage['text']):
            if re.match(r'(?:Check|Inspect|Capture|Correlate|Verify|Respect|Use bounded|Never|Do not|Escalate|Ask)\b', sentence):
                guidance.append(f"[{passage['id']}] {sentence}")
    return guidance[:4] or ['Collect the missing evidence and obtain operator review before any operational change.']


def ground_finding(draft, evidence, logs):
    """Preserve model citations/category for verification; never promote free prose."""
    return {**draft, 'hypothesis': grounded_summary(logs), 'confidence': 'low',
            'checks': questions(logs), 'recovery': source_guidance(evidence, draft['citations']),
            'uncertainty': 'Root cause has not been verified. Correlation and exact quotations do not establish causation. Conflicting or missing evidence requires operator investigation.'}


def evidence_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
