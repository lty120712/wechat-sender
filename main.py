# -*- coding: utf-8 -*-
import sys
import os

_src = os.path.join(os.path.dirname(__file__), "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from src.app import run

if __name__ == "__main__":
    raise SystemExit(run())
