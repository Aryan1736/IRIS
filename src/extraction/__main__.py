"""Command line entry point: python -m src.extraction --input data/raw"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from src.extraction.pipeline import PipelinePaths, combine_months, process_pdf


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract PAIMANA Table 6 project-month data")
    parser.add_argument("--input", type=Path, default=Path("data/raw"), help="PDF file or directory to scan recursively")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root for generated artifacts")
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR"))
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(asctime)s %(levelname)s %(message)s")

    pdfs = [args.input] if args.input.is_file() else sorted(args.input.rglob("*.pdf"))
    if not pdfs:
        parser.error(f"No PDFs found under {args.input}")
    paths = PipelinePaths(args.root.resolve())
    results = [process_pdf(pdf.resolve(), paths) for pdf in pdfs]
    combined = combine_months(results, paths)
    logging.getLogger("paimana.extraction").info("Combined dataset: %s", combined)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

