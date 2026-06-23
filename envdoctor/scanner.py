"""Varre o código-fonte procurando referências a variáveis de ambiente."""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Iterable, Set, Tuple
import re

# Padrões por linguagem
PATTERNS = [
    # Python: os.environ["X"], os.environ.get("X"), os.getenv("X")
    re.compile(r"""os\.environ\s*\[\s*['"]([A-Z0-9_]+)['"]\s*\]"""),
    re.compile(r"""os\.environ\.get\(\s*['"]([A-Z0-9_]+)['"]"""),
    re.compile(r"""os\.getenv\(\s*['"]([A-Z0-9_]+)['"]"""),
    # JS/TS: process.env.X, process.env["X"], import.meta.env.X
    re.compile(r"""process\.env\.([A-Z0-9_]+)"""),
    re.compile(r"""process\.env\[\s*['"]([A-Z0-9_]+)['"]\s*\]"""),
    re.compile(r"""import\.meta\.env\.([A-Z0-9_]+)"""),
    # Go: os.Getenv("X")
    re.compile(r"""os\.Getenv\(\s*"([A-Z0-9_]+)"\s*\)"""),
    # Shell: $VAR, ${VAR}
    re.compile(r"""\$\{?([A-Z][A-Z0-9_]{2,})\}?"""),
]

CODE_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
             ".go", ".rb", ".sh", ".bash", ".zsh", ".env.example"}

IGNORE_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__",
               "dist", "build", ".next", ".nuxt", "target", ".cache"}


def iter_source_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        if p.suffix in CODE_EXTS:
            yield p


def scan_usages(root: Path) -> Dict[str, Set[Tuple[str, int]]]:
    """Retorna {VAR: {(arquivo_relativo, linha), ...}}."""
    usages: Dict[str, Set[Tuple[str, int]]] = {}
    for path in iter_source_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for pat in PATTERNS:
                for m in pat.finditer(line):
                    var = m.group(1)
                    usages.setdefault(var, set()).add(
                        (str(path.relative_to(root)), lineno)
                    )
    return usages
