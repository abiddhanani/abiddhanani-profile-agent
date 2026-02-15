#!/usr/bin/env python3
"""
Build a minimal folder for Gradio/HF Spaces deploy to avoid "large folder" upload errors.
Then run:  cd .gradio_deploy_bundle && uv run gradio deploy
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUNDLE = ROOT / ".gradio_deploy_bundle"

# Only these are needed on the Space (keeps upload small)
FILES = [
    "app.py",
    "agent.py",
    "rag.py",
    "tools.py",
    "main.py",
    "__init__.py",
    "requirements.txt",
    "README.md",
    ".env.example",
]
ME_DIR = "me"


def main():
    if BUNDLE.exists():
        shutil.rmtree(BUNDLE)
    BUNDLE.mkdir(parents=True)

    for name in FILES:
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, BUNDLE / name)
        else:
            print(f"Warning: {name} not found, skipping", file=sys.stderr)

    # Copy me/ (summary.txt; PDF optional)
    me_src = ROOT / ME_DIR
    me_dst = BUNDLE / ME_DIR
    if me_src.is_dir():
        me_dst.mkdir(exist_ok=True)
        for f in me_src.iterdir():
            if f.is_file():
                shutil.copy2(f, me_dst / f.name)

    print(f"Bundle ready in {BUNDLE}")
    print("Run:  cd .gradio_deploy_bundle && uv run --project .. gradio deploy")
    print()

    # Optional: run deploy from bundle (use parent project's venv so gradio is available)
    if "--deploy" in sys.argv:
        subprocess.run(
            ["uv", "run", "--project", str(ROOT), "gradio", "deploy"],
            cwd=BUNDLE,
            check=False,
        )
    else:
        print("Add --deploy to run gradio deploy from the bundle now.")


if __name__ == "__main__":
    main()
