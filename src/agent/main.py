"""
Entrypoint for the Documentation Consistency Agent (starter).
Run: python -m src.agent.main
"""
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("doc-agent")

def scan_repo(path: str):
    p = Path(path)
    logger.info("Scanning: %s", p.resolve())
    # placeholder: list repo files
    for f in p.rglob("*"):
        print(f.relative_to(p))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=".", help="Path to repository to scan")
    args = parser.parse_args()
    scan_repo(args.path)

if __name__ == "__main__":
    main()
