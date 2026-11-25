"""Recompute, print, and preserve both improvements and negative controls."""
import json
from unknown_unknown import run

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
