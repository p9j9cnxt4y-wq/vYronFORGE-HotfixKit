import re

def _parsed(value: str):
    if not isinstance(value, str):
        return None
    value=value.strip()
    if re.fullmatch(r'\d+(?:\.\d+)*',value):
        return 'numeric',tuple(int(n) for n in value.split('.'))
    if re.fullmatch(r'\d+(?:\.\d+)+-\d+',value):
        # A numeric vendor build is comparable only to another declared build.
        # Against a plain version, a numeric hyphen suffix could be prerelease.
        return 'numeric-build',tuple(int(n) for n in re.split(r'[.-]',value))
    vendor=re.fullmatch(r'(\d+)H([12])(?:u(\d+))?',value,re.IGNORECASE)
    if vendor:
        return 'halfyear',tuple(int(n or 0) for n in vendor.groups())
    return None

def is_supported_version(value: str) -> bool:
    """Only explicitly supported release formats may establish a fixed state."""
    return _parsed(value) is not None

def version_key(value: str):
    if value is None:
        return ()
    parts=[]
    for token in re.findall(r"\d+|[A-Za-z]+", str(value)):
        parts.append((0,int(token)) if token.isdigit() else (1,token.lower()))
    return tuple(parts)

def at_least(current: str, minimum: str) -> bool:
    a=_parsed(current); b=_parsed(minimum)
    if a is None or b is None or a[0]!=b[0]:
        return False
    n=max(len(a[1]),len(b[1]))
    return a[1]+(0,)*(n-len(a[1])) >= b[1]+(0,)*(n-len(b[1]))
