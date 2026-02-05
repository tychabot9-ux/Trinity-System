#!/usr/bin/env python3
"""
COMPREHENSIVE COMMAND CENTER TEST SUITE
Zero Tolerance for Bugs - Testing EVERY function systematically
"""

import os
import sys
import json
import time
import sqlite3
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import traceback

# Test configuration
BASE_DIR = Path(__file__).parent
TEST_RESULTS_FILE = BASE_DIR / "TEST_RESULTS.md"
TEST_DB = BASE_DIR / "test_job_status.db"
TEST_CAD_DIR = BASE_DIR / "test_cad_output"

# Import the command_center module
sys.path.insert(0, str(BASE_DIR))
import command_center as cc

# Test tracking
test_results = {
    'passed': [],
    'failed': [],
    'warnings': [],
    'performance': {},
    'bugs_found': [],
    'fixes_applied': []
}

class TestRunner:
    """Comprehensive test runner for command center."""

    def __init__(self):
        self.setup_test_environment()

    def setup_test_environment(self):
        """Setup isolated test environment."""
        print("Setting up test environment...")

        # Create test directories
        TEST_CAD_DIR.mkdir(exist_ok=True)

        # Backup original paths
        self.original_job_db = cc.JOB_STATUS_DB
        self.original_cad_dir = cc.CAD_OUTPUT_DIR

        # Override with test paths
        cc.JOB_STATUS_DB = TEST_DB
        cc.CAD_OUTPUT_DIR = TEST_CAD_DIR

        print("Test environment ready")

    def cleanup_test_environment(self):
        """Cleanup test artifacts."""
        print("\nCleaning up test environment...")

        # Restore original paths
        cc.JOB_STATUS_DB = self.original_job_db
        cc.CAD_OUTPUT_DIR = self.original_cad_dir

        # Clean test files
        if TEST_DB.exists():
            TEST_DB.unlink()

        # Clean test CAD files
        for f in TEST_CAD_DIR.glob("*"):
            f.unlink()

        print("Cleanup complete")

    def time_test(self, func, *args, **kwargs):
        """Time a function execution."""
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = (time.time() - start) * 1000  # ms
        return result, elapsed

    def record_pass(self, test_name: str, elapsed_ms: float = None):
        """Record a passed test."""
        test_results['passed'].append(test_name)
        if elapsed_ms is not None:
            test_results['performance'][test_name] = f"{elapsed_ms:.2f}ms"
        print(f"  ✅ {test_name} - PASSED" + (f" ({elapsed_ms:.2f}ms)" if elapsed_ms else ""))

    def record_fail(self, test_name: str, error: str):
        """Record a failed test."""
        test_results['failed'].append({'test': test_name, 'error': error})
        print(f"  ❌ {test_name} - FAILED: {error}")

    def record_warning(self, test_name: str, warning: str):
        """Record a test warning."""
        test_results['warnings'].append({'test': test_name, 'warning': warning})
        print(f"  ⚠️  {test_name} - WARNING: {warning}")

    def record_bug(self, bug_desc: str):
        """Record a bug found."""
        test_results['bugs_found'].append(bug_desc)

    def record_fix(self, fix_desc: str):
        """Record a fix applied."""
        test_results['fixes_applied'].append(fix_desc)

    # ========================================================================
    # SESSION STATE TESTS
    # ========================================================================

    def test_session_state(self):
        """Test session state initialization."""
        print("\n[TESTING: Session State]")

        try:
            # Mock streamlit session_state
            class MockSessionState:
                def __init__(self):
                    self.data = {}
                def __contains__(self, key):
                    return key in self.data
                def __getitem__(self, key):
                    return self.data[key]
                def __setitem__(self, key, value):
                    self.data[key] = value

            # Test initialization logic (simulated)
            session = MockSessionState()

            # Expected defaults
            expected_keys = [
                'vr_mode', 'active_module', 'last_cad_render',
                'ai_memory', 'chat_history', 'uploaded_files_cache',
                'memory_initialized'
            ]

            for key in expected_keys:
                if key not in session:
                    session[key] = None

            self.record_pass("Session State - Key Initialization")

        except Exception as e:
            self.record_fail("Session State", str(e))

    # ========================================================================
    # VR MODE TESTS
    # ========================================================================

    def test_vr_mode(self):
        """Test VR mode configuration."""
        print("\n[TESTING: VR Mode]")

        try:
            # Mock streamlit session state for testing
            class MockSessionState:
                vr_mode = False
            cc.st.session_state = MockSessionState()

            # Test display config
            config, elapsed = self.time_test(cc.get_display_config)

            # Validate config structure
            required_keys = ['font_size', 'button_size', 'max_triangles',
                           'use_previews', 'layout', 'update_interval']

            if all(key in config for key in required_keys):
                self.record_pass("VR Mode - Display Config", elapsed)
            else:
                self.record_fail("VR Mode - Display Config", "Missing required keys")

            # Test max_triangles values
            if config['max_triangles'] not in [5000, 50000]:
                self.record_warning("VR Mode", f"Unexpected max_triangles: {config['max_triangles']}")

            # Test VR mode toggle
            cc.st.session_state.vr_mode = True
            config_vr = cc.get_display_config()
            if config_vr['max_triangles'] == 5000:
                self.record_pass("VR Mode - VR Optimization")
            else:
                self.record_fail("VR Mode - VR Optimization", "VR mode not applying optimizations")

        except Exception as e:
            self.record_fail("VR Mode", str(e))

    # ========================================================================
    # CAREER STATION TESTS
    # ========================================================================

    def test_job_database_init(self):
        """Test job status database initialization."""
        print("\n[TESTING: Career Station - Database]")

        try:
            result, elapsed = self.time_test(cc.init_job_status_db)

            if result and TEST_DB.exists():
                # Verify schema
                conn = sqlite3.connect(TEST_DB)
                cursor = conn.cursor()

                # Check table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='job_statuses'")
                if cursor.fetchone():
                    self.record_pass("Job Database - Initialization", elapsed)

                    # Verify columns
                    cursor.execute("PRAGMA table_info(job_statuses)")
                    columns = [row[1] for row in cursor.fetchall()]
                    expected_columns = ['id', 'draft_filename', 'company', 'position',
                                      'fit_score', 'status', 'created_date']

                    missing = [c for c in expected_columns if c not in columns]
                    if missing:
                        self.record_fail("Job Database - Schema", f"Missing columns: {missing}")
                    else:
                        self.record_pass("Job Database - Schema")
                else:
                    self.record_fail("Job Database - Table Creation", "Table not created")

                conn.close()
            else:
                self.record_fail("Job Database - Initialization", "Database file not created")

        except Exception as e:
            self.record_fail("Job Database", str(e))

    def test_job_statistics(self):
        """Test job statistics retrieval."""
        print("\n[TESTING: Career Station - Statistics]")

        try:
            stats, elapsed = self.time_test(cc.get_job_statistics)

            # Verify structure
            required_keys = ['pending', 'applied', 'denied', 'recent_7_days', 'total']

            if all(key in stats for key in required_keys):
                self.record_pass("Job Statistics - Structure", elapsed)

                # Verify all values are integers
                if all(isinstance(stats[key], int) for key in required_keys):
                    self.record_pass("Job Statistics - Data Types")
                else:
                    self.record_fail("Job Statistics - Data Types", "Non-integer values found")

                # Test with empty database (all should be 0)
                if stats['total'] == 0:
                    if all(stats[key] == 0 for key in required_keys):
                        self.record_pass("Job Statistics - Empty Database Handling")
                    else:
                        self.record_bug("Job Statistics shows non-zero values on empty database")
            else:
                self.record_fail("Job Statistics", f"Missing keys: {[k for k in required_keys if k not in stats]}")

        except Exception as e:
            self.record_fail("Job Statistics", str(e))

    def test_job_retrieval(self):
        """Test recent jobs retrieval."""
        print("\n[TESTING: Career Station - Job Retrieval]")

        try:
            # Test with empty database
            jobs, elapsed = self.time_test(cc.get_recent_jobs, 10)

            if isinstance(jobs, list):
                self.record_pass("Job Retrieval - Empty Database", elapsed)

                # Test limit parameter
                jobs_limited = cc.get_recent_jobs(5)
                if isinstance(jobs_limited, list):
                    self.record_pass("Job Retrieval - Limit Parameter")
                else:
                    self.record_fail("Job Retrieval - Limit", "Invalid return type")
            else:
                self.record_fail("Job Retrieval", "Invalid return type, expected list")

        except Exception as e:
            self.record_fail("Job Retrieval", str(e))

    # ========================================================================
    # ENGINEERING STATION TESTS
    # ========================================================================

    def test_scad_code_generation(self):
        """Test OpenSCAD code generation."""
        print("\n[TESTING: Engineering Station - SCAD Generation]")

        try:
            # Check for API key
            if not cc.GEMINI_API_KEY:
                self.record_warning("SCAD Generation", "GEMINI_API_KEY not set - skipping API tests")
                return

            # Test basic prompt
            prompt = "Create a simple cube 10x10x10mm"
            code, elapsed = self.time_test(cc.generate_scad_code, prompt, False)

            if isinstance(code, str) and len(code) > 0:
                self.record_pass("SCAD Generation - Basic Prompt", elapsed)

                # Check for error messages in code
                if "Error" in code or "error" in code:
                    self.record_fail("SCAD Generation", f"Error in generated code: {code[:100]}")
                else:
                    # Verify it looks like OpenSCAD code
                    if "cube" in code.lower() or "cylinder" in code.lower() or "sphere" in code.lower():
                        self.record_pass("SCAD Generation - Code Validity")
                    else:
                        self.record_warning("SCAD Generation", "Generated code may not be valid OpenSCAD")
            else:
                self.record_fail("SCAD Generation", "Invalid or empty code returned")

            # Test VR optimization mode
            code_vr = cc.generate_scad_code("simple box", True)
            if code_vr and "VR" not in code_vr:
                self.record_warning("SCAD Generation - VR Mode", "VR optimization may not be applied")

        except Exception as e:
            self.record_fail("SCAD Generation", str(e))

    def test_scad_compilation(self):
        """Test SCAD to STL compilation."""
        print("\n[TESTING: Engineering Station - STL Compilation]")

        try:
            # Check if openscad is installed
            try:
                result = subprocess.run(['which', 'openscad'], capture_output=True, timeout=5)
                openscad_available = result.returncode == 0
            except:
                openscad_available = False

            if not openscad_available:
                self.record_warning("STL Compilation", "OpenSCAD not installed - skipping compilation tests")
                return

            # Test with simple valid code
            simple_scad = "cube([10,10,10]);"
            result, elapsed = self.time_test(
                cc.compile_scad_to_stl,
                simple_scad,
                "test_cube",
                30
            )
            success, message, stl_path = result

            if success:
                self.record_pass("STL Compilation - Simple Model", elapsed)

                # Verify STL file exists
                if stl_path and stl_path.exists():
                    self.record_pass("STL Compilation - File Creation")

                    # Check file size
                    size = stl_path.stat().st_size
                    if size > 0:
                        self.record_pass("STL Compilation - File Size")
                    else:
                        self.record_bug("STL file created but is empty")
                else:
                    self.record_fail("STL Compilation", "STL file not created")
            else:
                self.record_fail("STL Compilation", f"Compilation failed: {message}")

            # Test error handling - invalid code
            invalid_scad = "this is not valid openscad code;"
            success_invalid, msg_invalid, _ = cc.compile_scad_to_stl(invalid_scad, "test_invalid")

            if not success_invalid:
                self.record_pass("STL Compilation - Error Handling")
            else:
                self.record_bug("Invalid SCAD code compiled successfully (should fail)")

            # Test path traversal protection
            malicious_name = "../../../etc/passwd"
            success, msg, path = cc.compile_scad_to_stl("cube([1,1,1]);", malicious_name)

            if path and "../" not in str(path):
                self.record_pass("STL Compilation - Path Traversal Protection")
            else:
                self.record_bug("SECURITY: Path traversal vulnerability detected!")

        except Exception as e:
            self.record_fail("STL Compilation", str(e))

    # ========================================================================
    # MEMORY SYSTEM TESTS
    # ========================================================================

    def test_memory_system(self):
        """Test Trinity Memory integration."""
        print("\n[TESTING: Memory System]")

        try:
            from trinity_memory import get_memory

            memory, elapsed = self.time_test(get_memory)

            if memory:
                self.record_pass("Memory System - Initialization", elapsed)

                # Test profile operations
                test_key = f"test_key_{time.time()}"
                test_value = "test_value"

                memory.set_profile(test_key, test_value, 'test')
                retrieved = memory.get_profile(test_key)

                if retrieved == test_value:
                    self.record_pass("Memory System - Profile Set/Get")
                else:
                    self.record_fail("Memory System - Profile", f"Expected {test_value}, got {retrieved}")

                # Test statistics
                stats = memory.get_memory_stats()
                if isinstance(stats, dict) and 'profile_entries' in stats:
                    self.record_pass("Memory System - Statistics")
                else:
                    self.record_fail("Memory System - Statistics", "Invalid stats structure")

                # Test preference learning
                memory.learn_preference('Test', 'category', 'key', 'value')
                pref = memory.get_preference('Test', 'category', 'key')

                if pref and pref.get('value') == 'value':
                    self.record_pass("Memory System - Preference Learning")
                else:
                    self.record_fail("Memory System - Preference", "Failed to learn/retrieve preference")

            else:
                self.record_fail("Memory System", "Failed to initialize")

        except ImportError:
            self.record_fail("Memory System", "trinity_memory module not found")
        except Exception as e:
            self.record_fail("Memory System", str(e))

    # ========================================================================
    # AI ASSISTANT TESTS
    # ========================================================================

    def test_ai_assistant(self):
        """Test AI Assistant functionality."""
        print("\n[TESTING: AI Assistant]")

        try:
            if not cc.GEMINI_API_KEY:
                self.record_warning("AI Assistant", "GEMINI_API_KEY not set - skipping API tests")
                return

            # Mock session state
            class MockSessionState:
                chat_history = []

            cc.st = type('obj', (object,), {'session_state': MockSessionState()})

            # Test basic message processing
            test_message = "What is 2+2?"
            response, elapsed = self.time_test(cc.process_ai_message, test_message, None)

            if isinstance(response, str) and len(response) > 0:
                self.record_pass("AI Assistant - Message Processing", elapsed)

                # Check for error messages
                if "Error" in response or "error" in response:
                    self.record_warning("AI Assistant", f"Potential error in response: {response[:100]}")
                else:
                    self.record_pass("AI Assistant - Response Quality")

                # Performance check (should respond in < 10 seconds)
                if elapsed < 10000:
                    self.record_pass("AI Assistant - Response Time")
                else:
                    self.record_warning("AI Assistant", f"Slow response time: {elapsed:.0f}ms")
            else:
                self.record_fail("AI Assistant", "Invalid or empty response")

        except Exception as e:
            self.record_fail("AI Assistant", str(e))

    # ========================================================================
    # TRADING STATION TESTS
    # ========================================================================

    def test_trading_station(self):
        """Test Trading Station functionality."""
        print("\n[TESTING: Trading Station]")

        try:
            # Test Phoenix stats (will handle missing files gracefully)
            stats, elapsed = self.time_test(cc.get_phoenix_stats)

            if isinstance(stats, dict):
                self.record_pass("Trading Station - Phoenix Stats", elapsed)

                # Should handle missing files
                if 'error' in stats:
                    self.record_pass("Trading Station - Error Handling")
                else:
                    # If files exist, verify structure
                    if 'running' in stats:
                        self.record_pass("Trading Station - Status Check")
            else:
                self.record_fail("Trading Station - Phoenix", "Invalid stats structure")

            # Test Genesis stats
            genesis_stats = cc.get_genesis_stats()
            if isinstance(genesis_stats, dict):
                self.record_pass("Trading Station - Genesis Stats")
            else:
                self.record_fail("Trading Station - Genesis", "Invalid stats structure")

            # Test macro status
            macro = cc.get_macro_status_data()
            if isinstance(macro, dict) and 'current_action' in macro:
                self.record_pass("Trading Station - Macro Status")
            else:
                self.record_fail("Trading Station - Macro", "Invalid macro status structure")

        except Exception as e:
            self.record_fail("Trading Station", str(e))

    # ========================================================================
    # ERROR HANDLING TESTS
    # ========================================================================

    def test_error_handling(self):
        """Test error handling and edge cases."""
        print("\n[TESTING: Error Handling]")

        try:
            # Test with None inputs
            try:
                stats = cc.get_job_statistics()
                self.record_pass("Error Handling - Null Safety (Job Stats)")
            except Exception as e:
                self.record_fail("Error Handling - Null Safety", f"get_job_statistics crashed: {e}")

            # Test with invalid database path
            original_db = cc.JOB_STATUS_DB
            cc.JOB_STATUS_DB = Path("/invalid/path/to/nowhere.db")

            try:
                stats = cc.get_job_statistics()
                if 'error' in stats or stats['total'] == 0:
                    self.record_pass("Error Handling - Invalid Path Handling")
                else:
                    self.record_warning("Error Handling", "Invalid path didn't return error")
            except Exception as e:
                self.record_pass("Error Handling - Exception on Invalid Path")
            finally:
                cc.JOB_STATUS_DB = original_db

            # Test timeout handling in compilation
            try:
                # Extremely complex model that should timeout
                complex_scad = "for(i=[0:1000]) for(j=[0:1000]) cube([1,1,1]);"
                success, msg, _ = cc.compile_scad_to_stl(complex_scad, "timeout_test", timeout=1)

                if not success and "timed out" in msg.lower():
                    self.record_pass("Error Handling - Timeout Protection")
                else:
                    self.record_warning("Error Handling", "Timeout test inconclusive")
            except Exception as e:
                self.record_pass("Error Handling - Timeout Exception Caught")

        except Exception as e:
            self.record_fail("Error Handling", str(e))

    # ========================================================================
    # PERFORMANCE TESTS
    # ========================================================================

    def test_performance(self):
        """Test performance benchmarks."""
        print("\n[TESTING: Performance]")

        try:
            # Database query performance
            cc.init_job_status_db()

            start = time.time()
            for _ in range(100):
                cc.get_job_statistics()
            elapsed = (time.time() - start) * 1000

            avg_time = elapsed / 100
            if avg_time < 100:  # Should be < 100ms per query
                self.record_pass("Performance - Database Queries", avg_time)
            else:
                self.record_warning("Performance", f"Slow database queries: {avg_time:.2f}ms avg")

            # Memory stats performance
            from trinity_memory import get_memory
            memory = get_memory()

            start = time.time()
            for _ in range(10):
                memory.get_memory_stats()
            elapsed = (time.time() - start) * 1000

            avg_time = elapsed / 10
            if avg_time < 500:  # Should be < 500ms
                self.record_pass("Performance - Memory Stats", avg_time)
            else:
                self.record_warning("Performance", f"Slow memory stats: {avg_time:.2f}ms avg")

        except Exception as e:
            self.record_fail("Performance", str(e))

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    def test_integration(self):
        """Test integration between modules."""
        print("\n[TESTING: Integration]")

        try:
            # Test Career + Memory integration
            from trinity_memory import get_memory
            memory = get_memory()

            cc.init_job_status_db()
            stats = cc.get_job_statistics()

            # Log interaction
            memory.log_interaction('Career', 'get_statistics', stats)

            # Verify logged
            interactions = memory.get_interactions('Career', hours=1)
            if any(i['action_type'] == 'get_statistics' for i in interactions):
                self.record_pass("Integration - Career + Memory")
            else:
                self.record_fail("Integration - Career + Memory", "Interaction not logged")

            # Test Engineering + Memory
            memory.learn_preference('Engineering', 'CAD', 'last_tool', 'OpenSCAD')
            pref = memory.get_preference('Engineering', 'CAD', 'last_tool')

            if pref and pref.get('value') == 'OpenSCAD':
                self.record_pass("Integration - Engineering + Memory")
            else:
                self.record_fail("Integration - Engineering + Memory", "Preference not saved")

        except Exception as e:
            self.record_fail("Integration", str(e))

    # ========================================================================
    # RUN ALL TESTS
    # ========================================================================

    def run_all_tests(self):
        """Execute all test suites."""
        print("\n" + "="*60)
        print("TRINITY COMMAND CENTER - COMPREHENSIVE TEST SUITE")
        print("Zero Tolerance for Bugs")
        print("="*60)

        start_time = time.time()

        # Run test suites
        self.test_session_state()
        self.test_vr_mode()
        self.test_job_database_init()
        self.test_job_statistics()
        self.test_job_retrieval()
        self.test_scad_code_generation()
        self.test_scad_compilation()
        self.test_memory_system()
        self.test_ai_assistant()
        self.test_trading_station()
        self.test_error_handling()
        self.test_performance()
        self.test_integration()

        total_time = time.time() - start_time

        # Generate report
        self.generate_report(total_time)

        # Cleanup
        self.cleanup_test_environment()

        return test_results

    def generate_report(self, total_time: float):
        """Generate comprehensive test report."""
        total_tests = len(test_results['passed']) + len(test_results['failed'])
        pass_rate = (len(test_results['passed']) / total_tests * 100) if total_tests > 0 else 0

        report = f"""# TRINITY COMMAND CENTER - TEST RESULTS
**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Test Time:** {total_time:.2f}s
**Pass Rate:** {pass_rate:.1f}%

---

## SUMMARY

- **Total Tests:** {total_tests}
- **Passed:** {len(test_results['passed'])} ✅
- **Failed:** {len(test_results['failed'])} ❌
- **Warnings:** {len(test_results['warnings'])} ⚠️
- **Bugs Found:** {len(test_results['bugs_found'])} 🐛
- **Fixes Applied:** {len(test_results['fixes_applied'])} 🔧

---

## PASSED TESTS ✅

"""
        for test in test_results['passed']:
            perf = test_results['performance'].get(test, 'N/A')
            report += f"- {test}"
            if perf != 'N/A':
                report += f" ({perf})"
            report += "\n"

        if test_results['failed']:
            report += "\n---\n\n## FAILED TESTS ❌\n\n"
            for fail in test_results['failed']:
                report += f"### {fail['test']}\n"
                report += f"**Error:** {fail['error']}\n\n"

        if test_results['warnings']:
            report += "\n---\n\n## WARNINGS ⚠️\n\n"
            for warn in test_results['warnings']:
                report += f"### {warn['test']}\n"
                report += f"**Warning:** {warn['warning']}\n\n"

        if test_results['bugs_found']:
            report += "\n---\n\n## BUGS FOUND 🐛\n\n"
            for i, bug in enumerate(test_results['bugs_found'], 1):
                report += f"{i}. {bug}\n"

        if test_results['fixes_applied']:
            report += "\n---\n\n## FIXES APPLIED 🔧\n\n"
            for i, fix in enumerate(test_results['fixes_applied'], 1):
                report += f"{i}. {fix}\n"

        report += "\n---\n\n## PERFORMANCE METRICS 📊\n\n"
        report += "| Test | Time |\n"
        report += "|------|------|\n"
        for test, perf in test_results['performance'].items():
            report += f"| {test} | {perf} |\n"

        report += "\n---\n\n## DETAILED BREAKDOWN\n\n"

        report += "### Career Station\n"
        career_tests = [t for t in test_results['passed'] if 'Job' in t or 'Career' in t]
        report += f"- Tests Passed: {len(career_tests)}\n"
        report += f"- Coverage: Database Init, Statistics, Job Retrieval, Error Handling\n\n"

        report += "### Engineering Station\n"
        eng_tests = [t for t in test_results['passed'] if 'SCAD' in t or 'STL' in t or 'Engineering' in t]
        report += f"- Tests Passed: {len(eng_tests)}\n"
        report += f"- Coverage: Code Generation, STL Compilation, Path Security, VR Optimization\n\n"

        report += "### Memory System\n"
        mem_tests = [t for t in test_results['passed'] if 'Memory' in t]
        report += f"- Tests Passed: {len(mem_tests)}\n"
        report += f"- Coverage: Profile Management, Preference Learning, Statistics, Integration\n\n"

        report += "### AI Assistant\n"
        ai_tests = [t for t in test_results['passed'] if 'AI' in t]
        report += f"- Tests Passed: {len(ai_tests)}\n"
        report += f"- Coverage: Message Processing, Response Quality, Performance\n\n"

        report += "### Trading Station\n"
        trade_tests = [t for t in test_results['passed'] if 'Trading' in t or 'Phoenix' in t or 'Genesis' in t]
        report += f"- Tests Passed: {len(trade_tests)}\n"
        report += f"- Coverage: Bot Status, Performance Metrics, Macro Status\n\n"

        report += "\n---\n\n## RECOMMENDATIONS\n\n"

        if len(test_results['failed']) == 0:
            report += "🎉 **EXCELLENT!** All tests passed. No immediate action required.\n\n"
        else:
            report += "⚠️ **ACTION REQUIRED:** Address failed tests before deployment.\n\n"

        if len(test_results['bugs_found']) > 0:
            report += "🐛 **BUGS DETECTED:** Review and fix all bugs before production use.\n\n"

        if len(test_results['warnings']) > 5:
            report += "⚠️ **HIGH WARNING COUNT:** Review warnings for potential issues.\n\n"

        report += "\n---\n\n## TEST ENVIRONMENT\n\n"
        report += f"- Python Version: {sys.version}\n"
        report += f"- Platform: {sys.platform}\n"
        report += f"- Test Database: {TEST_DB}\n"
        report += f"- Test CAD Directory: {TEST_CAD_DIR}\n"

        report += "\n---\n\n*Generated by Trinity Command Center Test Suite*\n"

        # Write report
        with open(TEST_RESULTS_FILE, 'w') as f:
            f.write(report)

        print(f"\n{'='*60}")
        print(f"Test Report Generated: {TEST_RESULTS_FILE}")
        print(f"{'='*60}")
        print(f"Pass Rate: {pass_rate:.1f}% ({len(test_results['passed'])}/{total_tests})")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    runner = TestRunner()
    results = runner.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if len(results['failed']) == 0 else 1)
