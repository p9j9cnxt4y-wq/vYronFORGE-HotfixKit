import re

_SENSITIVE_FIELD_PATTERN = r'(?:token|access[_-]?token|refresh[_-]?token|auth[_-]?token|api[_-]?key|x[_-]?api[_-]?key|password|passwd|secret|client[_-]?secret|secret[_-]?key|authorization|proxy[_-]?authorization|cookie|set[_-]?cookie|session[_-]?id)'

_PATTERNS = [
    # Preserve the entire credential boundary before general key:value redaction.
    (re.compile(r'(?i)\b((?:proxy-)?authorization\s*[:=]\s*)(?:bearer|basic)\s+[^\s\"\',;}]+'), r'\1[REDACTED_SECRET]'),
    (re.compile(r'(?i)\b(?:\d{1,3}\.){3}\d{1,3}\b'), '[REDACTED_IP]'),
    (re.compile(r'(?i)\b[0-9a-f]{2}(?::[0-9a-f]{2}){5}\b'), '[REDACTED_MAC]'),
    (re.compile(r'(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'), '[REDACTED_EMAIL]'),
    (re.compile(r'https?://[^\s/@]+:[^\s/@]+@[^\s]+'), '[REDACTED_PRIVATE_URL]'),
    # key=value, key: value and JSON-style secret fields
    (re.compile(rf'''(?ix)(["']?{_SENSITIVE_FIELD_PATTERN}["']?\s*[:=]\s*)["']?[^"'\s,;}}]+["']?'''), r'\1"[REDACTED_SECRET]"'),
    # Infrastructure identifiers in JSON-like evidence. Product names/versions are intentionally preserved.
    (re.compile(r'''(?ix)(["']?(?:asset_id|hostname|host_name|ssid|bssid|postal_code|postcode|plz|router_model|infra_model)["']?\s*[:=]\s*)["']?[^"'\n,}]+["']?'''), r'\1"[REDACTED_IDENTIFIER]"'),
]

def redact(text: str) -> str:
    out = str(text)
    for pattern, replacement in _PATTERNS:
        out = pattern.sub(replacement, out)
    return out


_SENSITIVE_KEYS = {
    'asset_id','hostname','host_name','ssid','bssid','postal_code','postcode','plz',
    'router_model','infra_model','username','user_name','email','ip','ip_address','mac','mac_address',
    'token','access_token','refresh_token','auth_token','api_key','apikey','x_api_key',
    'password','passwd','secret','client_secret','secret_key','authorization','proxy_authorization',
    'cookie','set_cookie','session_id','private_url'
}

def redact_data(value):
    """Recursively scrub evidence fields before serialization.

    This intentionally redacts identifiers even when they appear inside arrays such
    as ``unassessed_assets``; regex-only post-processing cannot safely guarantee that.
    """
    if isinstance(value, dict):
        out={}
        for key, item in value.items():
            lk=str(key).lower()
            if lk in _SENSITIVE_KEYS:
                if lk in {'token','access_token','refresh_token','auth_token','api_key','apikey','x_api_key',
                          'password','passwd','secret','client_secret','secret_key','authorization',
                          'proxy_authorization','cookie','set_cookie','session_id'}:
                    out[key]='[REDACTED_SECRET]'
                elif lk in {'ip','ip_address'}:
                    out[key]='[REDACTED_IP]'
                elif lk in {'mac','mac_address','bssid'}:
                    out[key]='[REDACTED_MAC]'
                elif lk == 'email':
                    out[key]='[REDACTED_EMAIL]'
                elif lk == 'private_url':
                    out[key]='[REDACTED_PRIVATE_URL]'
                else:
                    out[key]='[REDACTED_IDENTIFIER]'
            elif lk == 'unassessed_assets' and isinstance(item, list):
                out[key]=['[REDACTED_IDENTIFIER]' for _ in item]
            else:
                out[key]=redact_data(item)
        return out
    if isinstance(value, list):
        return [redact_data(v) for v in value]
    if isinstance(value, str):
        return redact(value)
    return value
