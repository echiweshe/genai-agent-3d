import os
import subprocess
import sys
import time

# ✅ Toggle live output from child scripts (True = print in real time, False = capture output)
LIVE_OUTPUT = True
SCRIPT_TIMEOUT_SECONDS = 180  # Or higher. 120 is good

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "examples")

def run_script(script_path):
    print(f"\n🚀 Running: {os.path.basename(script_path)}")
    print(f"📍 Path: {script_path}")
    print(f"🐍 Python: {sys.executable}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=os.path.dirname(script_path),
            capture_output=not LIVE_OUTPUT,
            text=True,
            timeout=SCRIPT_TIMEOUT_SECONDS,
        )
        if not LIVE_OUTPUT:
            print(result.stdout)
            if result.stderr:
                print(f"⚠️ STDERR:\n{result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout while running {script_path}")
        return False
    except Exception as e:
        print(f"❌ Error while running {script_path}:\n{e}")
        return False

def main():
    if not os.path.isdir(EXAMPLES_DIR):
        print(f"❌ Examples directory not found: {EXAMPLES_DIR}")
        return

    py_files = sorted(f for f in os.listdir(EXAMPLES_DIR) if f.endswith(".py"))
    if not py_files:
        print("📭 No Python scripts found in examples/")
        return

    success_count = 0
    for file in py_files:
        full_path = os.path.join(EXAMPLES_DIR, file)
        if run_script(full_path):
            success_count += 1
        else:
            print(f"⚠️ Script failed: {file}")

    print(f"\n✅ Done: {success_count}/{len(py_files)} scripts ran successfully.")

if __name__ == "__main__":
    start = time.time()
    main()
    duration = time.time() - start
    print(f"🕒 Elapsed time: {duration:.2f} seconds")
