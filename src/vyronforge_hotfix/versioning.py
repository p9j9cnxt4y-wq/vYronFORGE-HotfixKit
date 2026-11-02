import re

def version_key(value: str):
    if value is None:
        return ()
    parts=[]
    for token in re.findall(r"\d+|[A-Za-z]+", str(value)):
        parts.append((0,int(token)) if token.isdigit() else (1,token.lower()))
    return tuple(parts)

def at_least(current: str, minimum: str) -> bool:
    a=list(version_key(current)); b=list(version_key(minimum))
    # Numeric software versions are compared component-wise where possible.
    na=[x[1] for x in a if x[0]==0]; nb=[x[1] for x in b if x[0]==0]
    if na and nb:
        n=max(len(na),len(nb)); na += [0]*(n-len(na)); nb += [0]*(n-len(nb))
        return tuple(na) >= tuple(nb)
    return tuple(a) >= tuple(b)
