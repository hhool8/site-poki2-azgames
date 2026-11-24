#!/usr/bin/env python3
"""Re-sync the vendored main-site stylesheet.

Usage:
    python3 tools/sync_main_css.py /path/to/poki2-online/04-source/css/style.css

Copies the poki2.online stylesheet into src/styles/main.css, prints the new
sha256, and updates the hash comment in build_site.py so drift between the
two copies is at least auditable in git history.
"""
from __future__ import annotations

import hashlib
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "src" / "styles" / "main.css"
BUILD = ROOT / "tools" / "build_site.py"


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    src = Path(sys.argv[1]).resolve()
    if not src.is_file():
        print(f"not a file: {src}")
        return 2

    shutil.copyfile(src, DEST)
    digest = hashlib.sha256(DEST.read_bytes()).hexdigest()

    text = BUILD.read_text()
    text = re.sub(r"(# \(copied [^,]+, sha256 )[0-9a-f]{64}(\))",
                  rf"\g<1>{digest}\g<2>", text)
    BUILD.write_text(text)
    print(f"copied {src} -> {DEST}")
    print(f"sha256 {digest}")
    print("next: python3 tools/build_site.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
