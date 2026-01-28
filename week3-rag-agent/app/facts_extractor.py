import re

NAME_PATTERNS = [
    re.compile(r"\bbenim adım\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\b", re.IGNORECASE),
    re.compile(r"\bben\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\b(?:yim|ım)\b", re.IGNORECASE),
]


def extract_name(text: str) -> str | None:
    t = text.strip()
    for p in NAME_PATTERNS:
        m = p.search(t)
        if m:
            return m.group(1)
    return None
