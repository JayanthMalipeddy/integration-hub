"""Best-effort screening; authorization and evidence checks remain mandatory."""
import re
import base64
import binascii
import unicodedata


def _redact_basic(match):
    # A bare Basic value is a credential only if it decodes to username:password.
    # Explicit Authorization headers are always redacted, even malformed values.
    try:
        value = match.group(2)
        decoded = base64.b64decode(value + "=" * (-len(value) % 4), altchars=b"-_", validate=True)
    except (ValueError, binascii.Error):
        return match.group(0)
    return match.group(1) + "[REDACTED]" if b":" in decoded else match.group(0)


def redact(text: str) -> str:
    text = re.sub(r"-----BEGIN (?:[A-Z ]*PRIVATE KEY)-----.*?-----END (?:[A-Z ]*PRIVATE KEY)-----",
                  "[PRIVATE KEY REDACTED]", text, flags=re.S)
    text = re.sub(r"(?i)([a-z][a-z0-9+.-]*://)[^\s/@]+:[^\s@]+@", r"\1[REDACTED]@", text)
    text = re.sub(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b", "[ACCESS KEY REDACTED]", text)
    text = re.sub(r"""(?i)(["']?\bauthorization["']?\s*[:=]\s*["']?(?:basic|bearer)\s+)[A-Za-z0-9._~+/=-]+""", r"\1[REDACTED]", text)
    text = re.sub(r"(?i)(\bbearer\s+)[A-Za-z0-9._~+/=-]+", r"\1[REDACTED]", text)
    text = re.sub(r"(?i)(\bbasic\s+)([A-Za-z0-9+/_-]+={0,2})", _redact_basic, text)
    text = re.sub(r'''(?ix)(["']?\b(?:api[_-]?key|password|passwd|pwd|secret|(?:access[_-]?|refresh[_-]?)?token|client[_-]?secret)["']?\s*[=:]\s*)(?:"[^"\r\n]*"|'[^'\r\n]*'|[^\s,;&}]+)''',
                  r"\1[REDACTED]", text)
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[EMAIL]", text)
    text = re.sub(r"\b\d{3}-\d{4}-\d{7}-\d\b", "[IDENTITY]", text)
    text = re.sub(r"(?<!\w)\+\d{1,3}(?:[ -]?\d){7,14}(?!\d)", "[PHONE]", text)
    for label, replacement in ((r"(?:customer[ _-]?name|full[ _-]?name|patient[ _-]?name)", "[NAME]"),
                               (r"(?:phone|mobile|telephone)(?:[ _-]?number)?", "[PHONE]")):
        text = re.sub(r'(?i)(["\']?\b' + label + r'["\']?\s*[:=]\s*)(?:"[^"\r\n]*"|\'[^\'\r\n]*\'|[^\r\n,;}]+)',
                      lambda m: m.group(1) + replacement, text)
    return text


def redact_data(value):
    """Sanitize nested payloads without changing IDs, numeric usage or schema keys."""
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, list):
        return [redact_data(item) for item in value]
    if isinstance(value, dict):
        private = {"password", "passwd", "pwd", "secret", "api_key", "apikey", "access_token",
                   "refresh_token", "client_secret", "customer_name", "full_name", "patient_name",
                   "phone", "phone_number", "mobile", "telephone"}
        return {key: "[REDACTED]" if str(key).lower().replace("-", "_") in private else redact_data(item)
                for key, item in value.items()}
    return value


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
        r"\b(?:send|transmit|upload|forward|post|copy)\b.{0,100}\b(?:incident record|credentials|secrets|customer data|internal documents)\b.{0,100}(?:https?://|external|attacker)",
    )
    return any(re.search(pattern, normalized, re.I) for pattern in patterns)
