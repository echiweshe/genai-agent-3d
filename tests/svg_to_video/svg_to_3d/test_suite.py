#!/usr/bin/env python3
"""
Comprehensive test suite for SVG to 3D converter

This script runs all tests and generates a complete report.
"""

import os
import sys
import subprocess
import json
import shutil
from datetime import datetime
from pathlib import Path

# Add current directory to path for importing test runner
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the test runner
from run_tests import find_blender, run_blender_script

def setup_test_environment():
    """Set up the test environment"""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(test_dir, "test_results")
    
    # Clean up previous test results
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    os.makedirs(output_dir, exist_ok=True)
    
    return output_dir

def run_test_suite(blender_path):
    """Run the complete test suite"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "blender_path": blender_path,
        "tests": {},
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0
        }
    }
    
    # Set up test environment
    output_dir = setup_test_environment()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define tests to run
    tests = [
        {
            "name": "Basic Test",
            "script": "test_converter.py",
            "background": True,
            "description": "Basic functionality test with simple shapes"
        },
        {
            "name": "Debug Test",
            "script": "debug_converter.py",
            "background": True,
            "description": "Detailed debug test with edge cases"
        },
        {
            "name": "Batch Test",
            "script": "batch_test.py",
            "background": True,
            "description": "Batch test with multiple SVG files"
        },
        {
            "name": "Visual Test",
            "script": "visual_test.py",
            "background": False,
            "description": "Visual test with complex SVG elements"
        }
    ]
    
    # Run each test
    for test in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test['name']}")
        print(f"Description: {test['description']}")
        print(f"{'='*60}")
        
        script_path = os.path.join(script_dir, test['script'])
        start_time = datetime.now()
        
        # Capture output
        log_file = os.path.join(output_dir, f"{test['script']}.log")
        
        try:
            # Run the test
            cmd = [blender_path]
            if test['background']:
                cmd.append("--background")
            cmd.extend(["--python", script_path])
            
            with open(log_file, "w") as log:
                result = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
            
            success = result.returncode == 0
            
            # Record result
            results["tests"][test['name']] = {
                "status": "passed" if success else "failed",
                "script": test['script'],
                "duration": (datetime.now() - start_time).total_seconds(),
                "log_file": os.path.basename(log_file),
                "description": test['description']
            }
            
            results["summary"]["total"] += 1
            if success:
                results["summary"]["passed"] += 1
                print(f"✓ {test['name']} PASSED")
            else:
                results["summary"]["failed"] += 1
                print(f"✗ {test['name']} FAILED")
                
        except Exception as e:
            results["tests"][test['name']] = {
                "status": "error",
                "error": str(e),
                "script": test['script'],
                "duration": (datetime.now() - start_time).total_seconds()
            }
            results["summary"]["total"] += 1
            results["summary"]["failed"] += 1
            print(f"✗ {test['name']} ERROR: {e}")
    
    # Generate report
    report_file = os.path.join(output_dir, "test_suite_report.json")
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate HTML report
    generate_html_report(results, output_dir)
    
    return results

def generate_html_report(results, output_dir):
    """Generate an HTML report of the test results"""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SVG to 3D Converter Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .test {{ border: 1px solid #ddd; margin: 10px 0; padding: 10px; border-radius: 5px; }}
        .passed {{ background-color: #e7f5e7; }}
        .failed {{ background-color: #f5e7e7; }}
        .error {{ background-color: #f5f0e7; }}
        .status {{ font-weight: bold; }}
        .log-link {{ color: blue; text-decoration: underline; cursor: pointer; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f0f0f0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SVG to 3D Converter Test Report</h1>
        <p>Generated: {results['timestamp']}</p>
        <p>Blender: {results['blender_path']}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <table>
            <tr>
                <th>Total Tests</th>
                <th>Passed</th>
                <th>Failed</th>
                <th>Success Rate</th>
            </tr>
            <tr>
                <td>{results['summary']['total']}</td>
                <td>{results['summary']['passed']}</td>
                <td>{results['summary']['failed']}</td>
                <td>{(results['summary']['passed'] / results['summary']['total'] * 100):.1f}%</td>
            </tr>
        </table>
    </div>
    
    <div class="tests">
        <h2>Test Results</h2>
    """
    
    for test_name, test_result in results['tests'].items():
        status = test_result['status']
        status_class = status
        
        html_content += f"""
        <div class="test {status_class}">
            <h3>{test_name}</h3>
            <p><span class="status">Status:</span> {status.upper()}</p>
            <p>Script: {test_result['script']}</p>
            <p>Duration: {test_result['duration']:.2f} seconds</p>
            {f"<p>Description: {test_result.get('description', '')}</p>" if 'description' in test_result else ''}
            {f'<p><a href="{test_result["log_file"]}" class="log-link">View Log</a></p>' if 'log_file' in test_result else ''}
            {f'<p>Error: {test_result["error"]}</p>' if 'error' in test_result else ''}
        </div>
        """
    
    html_content += """
    </div>
</body>
</html>
    """
    
    report_file = os.path.join(output_dir, "test_report.html")
    with open(report_file, "w") as f:
        f.write(html_content)
    
    print(f"\nHTML report generated: {report_file}")

def main():
    """Main function to run the test suite"""
    print("SVG to 3D Converter Test Suite")
    print("="*30)
    
    # Find Blender
    blender_path = find_blender()
    
    if not blender_path:
        print("ERROR: Could not find Blender installation")
        sys.exit(1)
    
    print(f"Using Blender: {blender_path}")
    
    # Run test suite
    results = run_test_suite(blender_path)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUITE SUMMARY")
    print("="*60)
    print(f"Total Tests: {results['summary']['total']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Success Rate: {(results['summary']['passed'] / results['summary']['total'] * 100):.1f}%")
    
    # Print detailed results
    print("\nDetailed Results:")
    for test_name, test_result in results['tests'].items():
        status_symbol = "✓" if test_result['status'] == 'passed' else "✗"
        print(f"{status_symbol} {test_name}: {test_result['status'].upper()}")
    
    # Exit with appropriate code
    if results['summary']['failed'] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
