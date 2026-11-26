#!/usr/bin/env python3
"""News 25 front page — Wednesday 25 November 2026.

The 1024x1024 front page is already rendered and ships in this
repository as entry.png, next to this file. All this program does is
copy that finished image into the directory the grader reads from.

Deliberately standard library only. The grader runs Python 3.13 in a
sandbox without Pillow, so nothing here imports PIL or touches system
fonts — a plain file copy cannot fail on a missing third-party
package. The repository is mounted read-only while grading, so this
program never writes beside itself; it only writes to the output
directory named by MAKEFUN_OUTPUT_DIR (falling back to /output).
"""

import os
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
DEST_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main() -> int:
    source = BASE / "entry.png"
    target = DEST_DIR / "entry.png"
    if not source.is_file():
        print(f"entry image missing: {source}", file=sys.stderr)
        return 1
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    data = target.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or len(data) != source.stat().st_size:
        print("copied image failed PNG validation", file=sys.stderr)
        return 1
    print(f"copied {source} -> {target} ({target.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
