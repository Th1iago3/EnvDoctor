"""Parser de arquivos .env (suporta KEY=VAL, aspas, comentários, export)."""
from __future__ import annotations
from pathlib import Path
from typing import Dict
import re

_LINE = re.compile(r"""^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$""")


def parse_env_file(path: Path) -> Dict[str, str]:
    """Lê um arquivo .env e retorna {chave: valor}. Ignora comentários e linhas inválidas."""
    out: Dict[str, str] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _LINE.match(line)
        if not m:
            continue
        key, val = m.group(1), m.group(2)
        # tira aspas
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
            val = val[1:-1]
        # remove comentário inline em valores não-quotados
        elif "#" in val:
            val = val.split("#", 1)[0].rstrip()
        out[key] = val
    return out
