"""Gera relatório em texto / JSON / markdown."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json


@dataclass
class Report:
    env_files: List[str] = field(default_factory=list)
    defined: Dict[str, str] = field(default_factory=dict)   # var -> arquivo
    used: Dict[str, List[Tuple[str, int]]] = field(default_factory=dict)
    missing: List[str] = field(default_factory=list)   # usadas e não definidas
    unused: List[str] = field(default_factory=list)    # definidas e não usadas
    empty: List[str] = field(default_factory=list)     # definidas com valor vazio
    suspicious: List[str] = field(default_factory=list)  # parecem secret commitada

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


SUSPECT_KEYS = ("KEY", "SECRET", "TOKEN", "PASSWORD", "PASS", "DSN", "PRIVATE")


def build_report(
    env_data: Dict[str, Dict[str, str]],         # {arquivo: {VAR: VAL}}
    usages: Dict[str, Set[Tuple[str, int]]],
    example_file: str | None = None,
) -> Report:
    r = Report(env_files=list(env_data.keys()))

    # mescla todas as definições
    all_defs: Dict[str, str] = {}
    for fname, kv in env_data.items():
        for k, v in kv.items():
            all_defs[k] = fname
            if not v.strip():
                r.empty.append(k)

    r.defined = all_defs
    r.used = {k: sorted(v) for k, v in usages.items()}

    used_keys = set(usages.keys())
    def_keys = set(all_defs.keys())

    r.missing = sorted(used_keys - def_keys)
    r.unused = sorted(def_keys - used_keys)
    r.empty = sorted(set(r.empty))

    # secrets suspeitos commitados (definidos com valor não-vazio em .env real, não .example)
    seen: set[str] = set()
    for fname, kv in env_data.items():
        if fname.endswith(".example") or fname.endswith(".sample"):
            continue
        for k, val in kv.items():
            if not any(s in k.upper() for s in SUSPECT_KEYS):
                continue
            if val and val not in ("changeme", "your-key-here", "xxx") and k not in seen:
                r.suspicious.append(f"{k}  ({fname})")
                seen.add(k)
    r.suspicious.sort()
    return r


def render_text(r: Report) -> str:
    out: List[str] = []
    out.append("env-doctor — relatório\n" + "=" * 30)
    out.append(f"Arquivos .env analisados : {len(r.env_files)}")
    for f in r.env_files:
        out.append(f"  - {f}")
    out.append(f"Variáveis definidas      : {len(r.defined)}")
    out.append(f"Variáveis usadas no code : {len(r.used)}")
    out.append("")

    def section(title: str, items: List[str]) -> None:
        out.append(f"[{title}] ({len(items)})")
        if not items:
            out.append("  ✓ nada a reportar")
        else:
            for it in items:
                out.append(f"  • {it}")
        out.append("")

    section("FALTANDO (usadas no código, ausentes nos .env)", r.missing)
    section("NÃO USADAS (definidas mas nunca lidas)", r.unused)
    section("VAZIAS (sem valor)", r.empty)
    section("SUSPEITAS — possível segredo commitado", r.suspicious)

    exit_bad = bool(r.missing or r.suspicious)
    out.append("Status: " + ("❌ problemas encontrados" if exit_bad else "✅ tudo certo"))
    return "\n".join(out)


def render_markdown(r: Report) -> str:
    md: List[str] = ["# env-doctor report", ""]
    md.append(f"- **Arquivos .env:** {len(r.env_files)}")
    md.append(f"- **Definidas:** {len(r.defined)}")
    md.append(f"- **Usadas:** {len(r.used)}")
    md.append("")
    for title, items in [
        ("Faltando", r.missing),
        ("Não usadas", r.unused),
        ("Vazias", r.empty),
        ("Suspeitas (possível segredo)", r.suspicious),
    ]:
        md.append(f"## {title} ({len(items)})")
        if not items:
            md.append("_Nada a reportar._")
        else:
            for it in items:
                md.append(f"- `{it}`")
        md.append("")
    return "\n".join(md)
