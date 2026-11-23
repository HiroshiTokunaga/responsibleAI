"""
Main experiment runner. Run from the repo root:

    python exp_runner.py

Builds the district table if needed, then runs every experiment in order.
Results tables are written to results/.
"""

import exp_01_replication
import exp_02_confusion
import exp_03_province_groups

EXPERIMENTS = [
    ("Experiment 1: replicate the paper's Indonesia validation", exp_01_replication),
    ("Experiment 2: 2x2 tables for aid targeting", exp_02_confusion),
    ("Experiment 3: where the misses are", exp_03_province_groups),
]

if __name__ == "__main__":
    for title, module in EXPERIMENTS:
        print("=" * len(title))
        print(title)
        print("=" * len(title))
        module.run()
        print()
