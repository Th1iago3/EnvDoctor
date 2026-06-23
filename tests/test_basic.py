import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from envdoctor.parser import parse_env_file
from envdoctor.scanner import scan_usages
from envdoctor.report import build_report


def test_full_flow(tmp_path: Path):
    (tmp_path / ".env").write_text(
        '# comentário\nDB_URL="postgres://x"\nAPI_KEY=abc123\nUNUSED_VAR=1\nEMPTY=\n',
        encoding="utf-8",
    )
    (tmp_path / ".env.example").write_text("DB_URL=\nAPI_KEY=\n", encoding="utf-8")
    (tmp_path / "app.py").write_text(
        'import os\nx = os.environ["DB_URL"]\ny = os.getenv("MISSING_ONE")\n',
        encoding="utf-8",
    )
    (tmp_path / "front.ts").write_text(
        'const k = process.env.API_KEY;\nconst v = import.meta.env.VITE_PUB;\n',
        encoding="utf-8",
    )

    env_data = {
        ".env": parse_env_file(tmp_path / ".env"),
        ".env.example": parse_env_file(tmp_path / ".env.example"),
    }
    usages = scan_usages(tmp_path)
    r = build_report(env_data, usages)

    assert "MISSING_ONE" in r.missing
    assert "VITE_PUB" in r.missing
    assert "UNUSED_VAR" in r.unused
    assert "EMPTY" in r.empty
    assert any("API_KEY" in s for s in r.suspicious)
    print("OK")


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        test_full_flow(Path(d))
