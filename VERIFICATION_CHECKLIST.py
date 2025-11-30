#!/usr/bin/env python3
"""
VERIFICATION_CHECKLIST.md

Quick verification that all components are in place.
Run this to ensure your nesting_cog_omega implementation is complete.
"""

import os
from pathlib import Path
import json


def check_file_exists(path: str, description: str) -> tuple[bool, str]:
    """Check if a file exists and return status."""
    p = Path(path)
    exists = p.exists()
    status = "✅ FOUND" if exists else "❌ MISSING"
    return exists, f"{status} - {path:<50} ({description})"


def check_directory_exists(path: str, description: str) -> tuple[bool, str]:
    """Check if a directory exists and return status."""
    p = Path(path)
    exists = p.is_dir()
    status = "✅ EXISTS" if exists else "⚠️  NOT FOUND" 
    return exists, f"{status} - {path:<50} ({description})"


def main():
    print("\n" + "=" * 80)
    print("nesting_cog_omega - VERIFICATION CHECKLIST")
    print("=" * 80 + "\n")
    
    all_ok = True
    
    # ========================================================================
    # CORE PYTHON MODULES
    # ========================================================================
    print("📦 CORE PYTHON MODULES")
    print("-" * 80)
    
    core_files = [
        ("nesting_cog_omega.py", "Main orchestrator"),
        ("cog_nexus.py", "Agent runner module"),
        ("cog_keys.py", "Credential management"),
        ("test_orchestrator.py", "Test suite"),
    ]
    
    for file_path, desc in core_files:
        ok, msg = check_file_exists(file_path, desc)
        print(msg)
        all_ok = all_ok and ok
    
    # ========================================================================
    # DOCUMENTATION
    # ========================================================================
    print("\n📚 DOCUMENTATION FILES")
    print("-" * 80)
    
    doc_files = [
        ("QUICKREF.md", "Quick reference guide"),
        ("ORCHESTRATOR_README.md", "Complete documentation"),
        ("IMPLEMENTATION_SUMMARY.md", "Project summary"),
        ("PROJECT_INDEX.md", "Navigation guide"),
    ]
    
    for file_path, desc in doc_files:
        ok, msg = check_file_exists(file_path, desc)
        print(msg)
        all_ok = all_ok and ok
    
    # ========================================================================
    # STAGE 1 NOTES (INPUT DATA)
    # ========================================================================
    print("\n📝 STAGE 1 NOTES (Input Data)")
    print("-" * 80)
    
    stage1_files = [
        ("00_INBOX/stage1_perplexity.md", "Perplexity notes"),
        ("00_INBOX/stage1_groq.md", "Groq notes"),
        ("00_INBOX/stage1_grok.md", "Grok notes"),
        ("00_INBOX/stage1_claude.md", "Claude notes"),
        ("00_INBOX/stage1_deepseek.md", "DeepSeek notes"),
    ]
    
    for file_path, desc in stage1_files:
        ok, msg = check_file_exists(file_path, desc)
        print(msg)
        all_ok = all_ok and ok
    
    # ========================================================================
    # TEST IMPORTS
    # ========================================================================
    print("\n🧪 MODULE IMPORT TEST")
    print("-" * 80)
    
    try:
        import cog_keys
        print("✅ IMPORT OK - cog_keys module imports successfully")
    except Exception as e:
        print(f"❌ IMPORT FAILED - cog_keys: {e}")
        all_ok = False
    
    try:
        import cog_nexus
        print("✅ IMPORT OK - cog_nexus module imports successfully")
    except Exception as e:
        print(f"❌ IMPORT FAILED - cog_nexus: {e}")
        all_ok = False
    
    try:
        import nesting_cog_omega
        print("✅ IMPORT OK - nesting_cog_omega module imports successfully")
    except Exception as e:
        print(f"❌ IMPORT FAILED - nesting_cog_omega: {e}")
        all_ok = False
    
    # ========================================================================
    # FUNCTION AVAILABILITY TEST
    # ========================================================================
    print("\n⚙️  FUNCTION AVAILABILITY TEST")
    print("-" * 80)
    
    functions_to_check = [
        ("cog_keys", ["get_api_keys", "get_api_key", "require_api_key", "key_is_available"]),
        ("cog_nexus", ["run_analyzer", "run_planner", "run_reviewer", "run_agent", "batch_run_agents"]),
        ("nesting_cog_omega", ["run_stage2_synthesizer", "stage2_extract_unique_ideas", "stage3_build_master_plan"]),
    ]
    
    for module_name, functions in functions_to_check:
        try:
            module = __import__(module_name)
            for func_name in functions:
                if hasattr(module, func_name):
                    print(f"✅ FUNCTION OK - {module_name}.{func_name}()")
                else:
                    print(f"❌ MISSING - {module_name}.{func_name}()")
                    all_ok = False
        except Exception as e:
            print(f"❌ ERROR checking {module_name}: {e}")
            all_ok = False
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    if all_ok:
        print("✅ VERIFICATION COMPLETE - All checks passed!")
        print("\nYou're ready to run:")
        print("  1. python test_orchestrator.py     (Run tests)")
        print("  2. python nesting_cog_omega.py     (Run orchestrator)")
        print("\nRead:")
        print("  - QUICKREF.md for quick start")
        print("  - ORCHESTRATOR_README.md for full docs")
    else:
        print("❌ VERIFICATION FAILED - Some checks did not pass")
        print("\nPlease ensure all files are present before running.")
    
    print("=" * 80 + "\n")
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
