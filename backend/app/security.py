"""Best-effort screening; authorization and evidence checks remain mandatory."""
import re
import unicodedata


def redact(text: str) -> str:
    text = re.sub(r"-----BEGIN (?:[A-Z ]*PRIVATE KEY)-----.*?-----END (?:[A-Z ]*PRIVATE KEY)-----",
                  "[PRIVATE KEY REDACTED]", text, flags=re.S)
    text = re.sub(r"(?i)([a-z][a-z0-9+.-]*://)[^\s/@]+:[^\s@]+@", r"\1[REDACTED]@", text)
    text = re.sub(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b", "[ACCESS KEY REDACTED]", text)
    text = re.sub(r"(?i)(\b(?:bearer|basic)\s+)[A-Za-z0-9._~+/=-]+", r"\1[REDACTED]", text)
    text = re.sub(r'''(?ix)(["']?\b(?:api[_-]?key|password|passwd|pwd|secret|(?:access[_-]?|refresh[_-]?)?token|client[_-]?secret)["']?\s*[=:]\s*)(?:"[^"\r\n]*"|'[^'\r\n]*'|[^\s,;&}]+)''',
                  r"\1[REDACTED]", text)
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[EMAIL]", text)
    return re.sub(r"\b\d{3}-\d{4}-\d{7}-\d\b", "[IDENTITY]", text)


def injection_risk(text: str) -> bool:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = "".join(c for c in normalized if unicodedata.category(c) != "Cf")
    normalized = re.sub(r"\s+", " ", normalized)
    patterns = (
        r"\b(?:ignore|disregard|override|forget)\b.{0,60}\b(?:instructions|rules|guidelines|directions)\b",
        r"\bsystem\s+(?:prompt|override)\b",
        r"\b(?:reveal|dump|print|repeat|exfiltrate)\b.{0,70}\b(?:secrets?|credentials|configuration|text above)\b",
        r"\bexecute\s+(?:shell|command)\b",
        r"<\|(?:system|im_start)\|>",
    )
    return any(re.search(pattern, normalized, re.I) for pattern in patterns)
