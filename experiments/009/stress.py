"""MOTIF-009 development stress protocol.

The first v1 trial began with 16 labels and hit a predictive ceiling before
active inquiry could demonstrate extra value. This separately labeled v2
*post-observation* stress test starts with 6 labels and permits 12 further
requests. It is NOT independently preregistered and must not replace v1.
"""
from __future__ import annotations
import json
from benchmark import report

if __name__ == "__main__":
    print(json.dumps(report(initial=6, requests=12,
          version="active-tree-cartridges-v2-development-stress"),
          indent=2, sort_keys=True))
