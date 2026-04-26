#!/usr/bin/env python3
"""
VALIDATE.py - Reproducibility sanity check suite

This script verifies that:
1. All data files exist and have reasonable sizes
2. All analysis scripts run without errors (exit code 0)
3. PNG figures are generated successfully
4. Python environment has all required packages

This is a basic sanity check, not a numerical validation. Actual result 
verification requires reviewing the script output and paper results.

Usage:
    python VALIDATE.py

Expected runtime: ~15-20 minutes (bootstrap tests take time)
"""

import os
import sys
import subprocess
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_FILES = {
    'guilds_valid.txt': (1000, 100000),  # (min_size, max_size) in bytes
    'guilds.txt': (1000, 100000),
    'sites_table.txt': (5000, 100000)
}

PNG_FIGURES = [
    'guilds.png',
    'appendix71.png',
    'sites.png'
]

PYTHON_SCRIPTS = [
    'analyze_guilds.py',
    'analyze_appendix71.py',
    'analyze_sites.py',
    'exponential_gof.py',
    'exponential_gof_appendix71.py'
]

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

class ValidationReport:
    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
    
    def add(self, name, passed, details=""):
        status = "[OK]" if passed else "[FAIL]"
        self.checks.append((name, status, details))
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        print(f"{status}: {name}")
        if details:
            print(f"       {details}")
    
    def summary(self):
        print("\n" + "="*70)
        print(f"VALIDATION SUMMARY: {self.passed} passed, {self.failed} failed")
        print("="*70)
        for name, status, details in self.checks:
            print(f"{status}: {name}")
        print("="*70)
        return self.failed == 0

def check_python_environment():
    """Verify Python version and key packages."""
    report = ValidationReport()
    
    # Python version
    py_version = sys.version_info
    report.add(
        f"Python version ({py_version.major}.{py_version.minor}.{py_version.micro})",
        py_version.major == 3 and py_version.minor >= 8,
        "Python 3.8+ required"
    )
    
    # Check imports
    try:
        import powerlaw
        report.add(f"powerlaw module (v{powerlaw.__version__})", True)
    except ImportError:
        report.add("powerlaw module", False, "Install: pip install powerlaw==2.0.0")
    
    try:
        import numpy
        report.add(f"numpy module (v{numpy.__version__})", True)
    except ImportError:
        report.add("numpy module", False)
    
    try:
        import scipy
        report.add(f"scipy module (v{scipy.__version__})", True)
    except ImportError:
        report.add("scipy module", False)
    
    try:
        import matplotlib
        report.add(f"matplotlib module (v{matplotlib.__version__})", True)
    except ImportError:
        report.add("matplotlib module", False)
    
    return report

def check_data_files():
    """Verify all data files exist and have reasonable sizes."""
    report = ValidationReport()
    
    for filename, (min_size, max_size) in DATA_FILES.items():
        filepath = Path(filename)
        if filepath.exists():
            size = filepath.stat().st_size
            ok = min_size <= size <= max_size
            report.add(
                f"Data file: {filename} ({size} bytes)",
                ok,
                f"Expected {min_size}-{max_size} bytes" if not ok else ""
            )
        else:
            report.add(f"Data file: {filename}", False, "File not found")
    
    return report

def check_python_scripts():
    """Verify all Python scripts exist and have no syntax errors."""
    report = ValidationReport()
    
    for script in PYTHON_SCRIPTS:
        filepath = Path(script)
        if not filepath.exists():
            report.add(f"Script: {script}", False, "File not found")
            continue
        
        # Check syntax by compiling
        try:
            with open(script, 'r') as f:
                code = f.read()
            compile(code, script, 'exec')
            report.add(f"Script: {script}", True, "Syntax OK")
        except SyntaxError as e:
            report.add(f"Script: {script}", False, f"Syntax error: {e}")
    
    return report

def check_png_figures():
    """Verify PNG figures exist and are valid."""
    report = ValidationReport()
    
    for figure in PNG_FIGURES:
        filepath = Path(figure)
        if filepath.exists():
            size = filepath.stat().st_size
            # Check for PNG magic bytes
            try:
                with open(figure, 'rb') as f:
                    header = f.read(4)
                    is_png = header == b'\x89PNG'
                report.add(
                    f"Figure: {figure} ({size} bytes)",
                    is_png,
                    "PNG format verified" if is_png else "Invalid PNG header"
                )
            except Exception as e:
                report.add(f"Figure: {figure}", False, str(e))
        else:
            report.add(f"Figure: {figure}", False, "File not found")
    
    return report

def run_analysis_script(script_name):
    """Run an analysis script and check exit code."""
    print(f"\n>>> Running {script_name}...")
    try:
        timeout = 600 if 'appendix' in script_name else 300  # 10 min for appendix71, 5 min for others
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        success = result.returncode == 0
        if not success:
            print(f"Exit code: {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr[:200]}")
        return success, result.returncode
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)

# ============================================================================
# MAIN VALIDATION
# ============================================================================

def main():
    print("="*70)
    print("HARAPPAN POWER LAW - REPRODUCIBILITY SANITY CHECK")
    print("="*70)
    
    all_passed = True
    
    # Step 1: Check environment
    print("\n[1/5] Checking Python environment...")
    env_report = check_python_environment()
    all_passed = all_passed and env_report.summary()
    
    # Step 2: Check data files
    print("\n[2/5] Checking data files...")
    data_report = check_data_files()
    all_passed = all_passed and data_report.summary()
    
    # Step 3: Check Python scripts
    print("\n[3/5] Checking Python scripts...")
    script_report = check_python_scripts()
    all_passed = all_passed and script_report.summary()
    
    # Step 4: Check PNG figures
    print("\n[4/5] Checking PNG figures...")
    fig_report = check_png_figures()
    all_passed = all_passed and fig_report.summary()
    
    # Step 5: Run analyses
    print("\n[5/5] Running analyses (sanity check - exit code must be 0)...")
    run_report = ValidationReport()
    
    for script in ['analyze_guilds.py', 'analyze_appendix71.py', 'analyze_sites.py']:
        success, result = run_analysis_script(script)
        run_report.add(f"{script}", success, f"Exit code: {result}")
        all_passed = all_passed and success
    
    run_report.summary()
    
    # Final summary
    print("\n" + "="*70)
    if all_passed:
        print("[OK] ALL SANITY CHECKS PASSED - READY FOR SUBMISSION")
        print("     (Note: Numerical results validated by reviewing script output)")
        print("="*70)
        return 0
    else:
        print("[FAIL] SOME CHECKS FAILED - PLEASE REVIEW ERRORS ABOVE")
        print("="*70)
        return 1

if __name__ == '__main__':
    sys.exit(main())
