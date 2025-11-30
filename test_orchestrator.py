#!/usr/bin/env python3
"""
Test runner and quick-start guide for nesting_cog_omega orchestrator.

This script demonstrates how to:
1. Run the orchestrator with sample data
2. Verify output artifacts
3. Check logs and intermediate files
"""

import json
import subprocess
import sys
from pathlib import Path


def test_imports():
    """Test that all required modules can be imported."""
    print("\n" + "=" * 70)
    print("TEST 1: Verifying imports...")
    print("=" * 70)
    
    try:
        import cog_keys
        print("✓ cog_keys imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import cog_keys: {e}")
        return False
    
    try:
        import cog_nexus
        print("✓ cog_nexus imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import cog_nexus: {e}")
        return False
    
    try:
        import nesting_cog_omega
        print("✓ nesting_cog_omega imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import nesting_cog_omega: {e}")
        return False
    
    return True


def test_cog_keys():
    """Test the API key management module."""
    print("\n" + "=" * 70)
    print("TEST 2: Testing cog_keys module...")
    print("=" * 70)
    
    try:
        from cog_keys import get_summary, list_available_keys, get_api_keys
        
        summary = get_summary()
        print("\nAPI Key Availability Summary:")
        print(json.dumps(summary, indent=2))
        
        return True
    except Exception as e:
        print(f"✗ Error testing cog_keys: {e}")
        return False


def test_cog_nexus():
    """Test the agent runner module."""
    print("\n" + "=" * 70)
    print("TEST 3: Testing cog_nexus module...")
    print("=" * 70)
    
    try:
        from cog_nexus import run_analyzer, run_planner, run_reviewer
        
        # Test analyzer
        print("\nTesting run_analyzer...")
        result = run_analyzer(
            task_id="test-analyzer-1",
            instructions="Test: Extract ideas from this text.",
            temperature=0.1,
            max_tokens=500,
        )
        print(f"✓ Analyzer response status: {result.get('model', 'N/A')}")
        
        # Test planner
        print("Testing run_planner...")
        result = run_planner(
            task_id="test-planner-1",
            instructions="Test: Create a plan.",
            temperature=0.15,
            max_tokens=800,
        )
        print(f"✓ Planner response status: {result.get('model', 'N/A')}")
        
        # Test reviewer
        print("Testing run_reviewer...")
        result = run_reviewer(
            task_id="test-reviewer-1",
            instructions="Test: Review this.",
            temperature=0.0,
            max_tokens=400,
        )
        print(f"✓ Reviewer response status: {result.get('model', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"✗ Error testing cog_nexus: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stage1_notes():
    """Verify Stage 1 notes exist in 00_INBOX."""
    print("\n" + "=" * 70)
    print("TEST 4: Verifying Stage 1 notes...")
    print("=" * 70)
    
    inbox_dir = Path("00_INBOX")
    if not inbox_dir.exists():
        print(f"✗ Directory 00_INBOX not found")
        return False
    
    stage1_files = list(inbox_dir.glob("stage1_*.md"))
    print(f"Found {len(stage1_files)} Stage 1 note files:")
    for f in sorted(stage1_files):
        print(f"  ✓ {f.name}")
    
    return len(stage1_files) > 0


def test_orchestrator_dry_run():
    """Run a dry-run of the orchestrator (with placeholder agents)."""
    print("\n" + "=" * 70)
    print("TEST 5: Running orchestrator (dry-run with placeholders)...")
    print("=" * 70)
    
    try:
        from nesting_cog_omega import run_stage2_synthesizer
        
        print("\nStarting orchestrator...")
        result = run_stage2_synthesizer()
        
        print("\n✓ Orchestrator completed")
        print(f"  Handoff file path: {result.get('artifacts', {}).get('stage2_handoff.json', 'N/A')}")
        
        # Check that output files were created
        project_root = Path("projects/current_project")
        if project_root.exists():
            print(f"\n✓ Project directory created: {project_root}")
            json_files = list(project_root.glob("*.json"))
            md_files = list(project_root.glob("*.md"))
            print(f"  Generated {len(json_files)} JSON files")
            print(f"  Generated {len(md_files)} Markdown files")
        
        return True
    except Exception as e:
        print(f"✗ Error running orchestrator: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_outputs():
    """Verify that expected output files exist and are valid."""
    print("\n" + "=" * 70)
    print("TEST 6: Verifying output artifacts...")
    print("=" * 70)
    
    expected_files = [
        "projects/current_project/stage2_unique_ideas.json",
        "projects/current_project/stage3_master_plan.json",
        "projects/current_project/stage3_master_plan.md",
        "projects/current_project/stage4_tasks.json",
        "projects/current_project/stage2_handoff.json",
        "projects/current_project/_meta/monitor_summary.json",
        "projects/current_project/_meta/clean_report.json",
        "projects/current_project/_meta/stage6_review.json",
    ]
    
    all_exist = True
    for file_path in expected_files:
        path = Path(file_path)
        if path.exists():
            # Check if JSON files are valid
            if file_path.endswith(".json"):
                try:
                    with open(path) as f:
                        json.load(f)
                    print(f"✓ {file_path} (valid JSON)")
                except json.JSONDecodeError:
                    print(f"⚠ {file_path} (invalid JSON)")
                    all_exist = False
            else:
                print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (not found)")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  nesting_cog_omega Orchestrator - Test Suite".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    tests = [
        ("Import modules", test_imports),
        ("API key management", test_cog_keys),
        ("Agent runners", test_cog_nexus),
        ("Stage 1 notes", test_stage1_notes),
        ("Orchestrator dry-run", test_orchestrator_dry_run),
        ("Output artifacts", verify_outputs),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Unexpected error in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
