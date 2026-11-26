#!/usr/bin/env python3
"""News 25 front page — Wednesday 25 November 2026.

The 1024x1024 front page is already rendered and ships in this
repository as entry.png, next to this file. All this program does is
copy that finished image into the directory the grader reads from.

Deliberately standard library only. The grader runs Python 3.13 in a
sandbox without Pillow, so nothing here imports PIL or any third-party
module.
"""

import os
import shutil
import sys
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    bot_dir = Path(os.environ.get("MAKEFUN_BOT_DIR", Path(__file__).resolve().parent))
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", Path("/output")))
    src = bot_dir / "entry.png"
    if not src.is_file():
        print(f"entry.png not found in {bot_dir}", file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "entry.png"
    shutil.copyfile(src, dst)
    data = dst.read_bytes()
    if not data.startswith(PNG_MAGIC):
        print("copied file is not a PNG", file=sys.stderr)
        return 1
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if (width, height) != (1024, 1024):
        print(f"copied PNG is {width}x{height}, expected 1024x1024", file=sys.stderr)
        return 1
    if len(data) > 1024 * 1024:
        print("copied PNG exceeds 1 MiB", file=sys.stderr)
        return 1
    print(f"copied entry.png ({len(data)} bytes, {width}x{height}) to {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
