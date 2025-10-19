#!/usr/bin/env python3
import argparse, os, sys
from pathlib import Path
from dotenv import load_dotenv
import requests

def read_file(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"(failed to read {p}: {e})"

def collect_context(day_dir: Path, only_recent: bool = False, only_index: bool = False) -> str:
    recent = day_dir / "RECENT.md"
    indexf = day_dir / "INDEX.md"
    if only_index:
        return f"# INDEX.md\n{read_file(indexf)}" if indexf.exists() else ""
    if only_recent:
        return f"# RECENT.md\n{read_file(recent)}" if recent.exists() else ""

    parts = []
    if recent.exists():
        parts.append(f"# RECENT.md\n{read_file(recent)}")
    md_files = sorted(
        [p for p in day_dir.glob("*.md") if p.name not in {"INDEX.md", "RECENT.md"}],
        key=lambda p: p.stat().st_mtime, reverse=True
    )[:3]
    for p in md_files:
        txt = read_file(p)
        parts.append(f"# {p.name}\n{txt[:8000]}")
    return "\n\n".join(parts)

def chat_ollama(model: str, prompt: str) -> str:
    base = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
    r = requests.post(f"{base}/api/generate",
                      json={"model": model, "prompt": prompt, "stream": False},
                      timeout=300)
    r.raise_for_status()
    return r.json().get("response", "").strip()

def main(argv=None) -> int:
    load_dotenv()
    ap = argparse.ArgumentParser(description="MOONLACE: local chat over STELLARWIND")
    ap.add_argument("-p", "--provider", choices=["ollama"], default="ollama")
    ap.add_argument("-d", "--date", required=True, help="YYYY-MM-DD (derived day)")
    ap.add_argument("-q", "--query", required=True, help="Your question")
    ap.add_argument("--only-recent", action="store_true",
                    help="Restrict context to RECENT.md only")
    ap.add_argument("--only-index", action="store_true",
                    help="Restrict context to INDEX.md only")
    args = ap.parse_args(argv)

    base = Path(os.environ.get("MOONLACE_STELLARWIND", "")).expanduser().resolve()
    if not base.exists():
        print(f"Set MOONLACE_STELLARWIND to your STELLARWIND path. Missing: {base}", file=sys.stderr)
        return 2

    day_dir = base / "data" / "derived" / args.date
    if not day_dir.is_dir():
        print(f"No derived directory for {args.date}; expected {day_dir}", file=sys.stderr)
        return 3

    system_preamble = (
        "You are MOONLACE, a precise, concise assistant summarizing and answering from provided Markdown context.\n"
        "If unsure, say so and suggest where to look next.\n"
    )
    ctx = collect_context(day_dir, only_recent=args.only_recent, only_index=args.only_index)
    context_body = ctx.strip()
    if context_body:
        context_block = f"# CONTEXT\n```CONTEXT\n{context_body}\n```"
    else:
        context_block = "# CONTEXT\n```CONTEXT\n```"
    strict_instructions = "Answer ONLY from the context; if missing, say 'insufficient context'."
    prompt = "\n\n".join([
        strict_instructions,
        system_preamble.strip(),
        f"# QUESTION\n{args.query}",
        context_block
    ])

    model = os.environ.get("MOONLACE_OLLAMA_MODEL", "llama3.1:8b-instruct-q4_K_M")
    out = chat_ollama(model, prompt)
    print(out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
