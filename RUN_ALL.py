#!/usr/bin/env python3
"""
Run all analyses in sequence for end-to-end validation.

Pipeline:
  1. analyze_guilds.py         - Constrained reconstruction (Table 7.6)
  2. synthetic_guild.py        - 5000 synthetic reconstructions
  3. analyze_appendix71.py     - Complete dataset validation (Appendix 7.1)
  4. analyze_sites.py          - Site distribution analysis
"""

import subprocess
import sys
import time

SCRIPTS = [
    "analyze_guilds.py",
    "synthetic_guild.py",
    "analyze_appendix71.py",
    "analyze_sites.py",
]

print("=" * 70)
print("HARAPPAN POWER LAW - FULL PIPELINE RUN")
print("=" * 70)
print()

start_time = time.time()
failed = []

for i, script in enumerate(SCRIPTS, 1):
    print(f"[{i}/{len(SCRIPTS)}] Running {script}...")
    print("-" * 70)
    
    result = subprocess.run(
        [sys.executable, script],
        capture_output=False
    )
    
    if result.returncode != 0:
        print(f"❌ FAILED: {script}")
        failed.append(script)
    else:
        print(f"✅ PASSED: {script}")
    print()

elapsed = time.time() - start_time
print("=" * 70)
if failed:
    print(f"❌ PIPELINE FAILED: {len(failed)} script(s) errored")
    for script in failed:
        print(f"   - {script}")
    sys.exit(1)
else:
    print(f"✅ FULL PIPELINE COMPLETE - All {len(SCRIPTS)} analyses passed")
    print(f"   Total time: {elapsed:.1f} seconds (~{elapsed/60:.1f} minutes)")
    sys.exit(0)
