"""CLI: envdoctor [--path .] [--format text|json|md] [--fix] [--strict]"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
from typing import Dict

from . import __version__
from .parser import parse_env_file
from .scanner import scan_usages
from .report import build_report, render_text, render_markdown

DEFAULT_ENV_NAMES = [
    ".env", ".env.local", ".env.development", ".env.production",
    ".env.example", ".env.sample",
]


def collect_env_files(root: Path) -> Dict[str, Dict[str, str]]:
    found: Dict[str, Dict[str, str]] = {}
    for name in DEFAULT_ENV_NAMES:
        p = root / name
        if p.exists():
            found[name] = parse_env_file(p)
    return found


def cmd_check(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"erro: {root} não é um diretório", file=sys.stderr)
        return 2

    env_data = collect_env_files(root)
    usages = scan_usages(root)
    report = build_report(env_data, usages)

    if args.format == "json":
        print(report.to_json())
    elif args.format == "md":
        print(render_markdown(report))
    else:
        print(render_text(report))

    if args.fix and report.missing:
        example = root / ".env.example"
        existing = parse_env_file(example) if example.exists() else {}
        added = [k for k in report.missing if k not in existing]
        if added:
            with example.open("a", encoding="utf-8") as f:
                if existing:
                    f.write("\n# adicionado por env-doctor --fix\n")
                for k in added:
                    f.write(f"{k}=\n")
            print(f"\n→ {len(added)} variáveis adicionadas em {example.name}",
                  file=sys.stderr)

    fail = bool(report.missing)
    if args.strict:
        fail = fail or bool(report.unused) or bool(report.suspicious)
    return 1 if fail else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdoctor",
        description="Audita variáveis de ambiente: encontra faltando, não usadas, vazias e segredos commitados.",
    )
    p.add_argument("--version", action="version", version=f"env-doctor {__version__}")
    sub = p.add_subparsers(dest="command")

    c = sub.add_parser("check", help="varre o projeto e reporta problemas")
    c.add_argument("--path", default=".", help="raiz do projeto (default: .)")
    c.add_argument("--format", choices=("text", "json", "md"), default="text")
    c.add_argument("--fix", action="store_true",
                   help="adiciona variáveis faltantes em .env.example")
    c.add_argument("--strict", action="store_true",
                   help="falha (exit 1) também em unused/suspicious")
    c.set_defaults(func=cmd_check)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        # default: check .
        args = parser.parse_args(["check"] + (argv or []))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
