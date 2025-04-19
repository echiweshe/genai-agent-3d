import os
import subprocess
import tempfile
import shutil

# ✅ Set the path to your Blender executable
BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

# 🔎 Check if Blender exists
if not os.path.exists(BLENDER_PATH):
    print(f"❌ Blender not found at: {BLENDER_PATH}")
    exit(1)

# 📝 Create a temporary Blender script
script_content = 'print("✅ Hello from Blender CLI!")'
with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as temp_script:
    temp_script.write(script_content)
    temp_script_path = temp_script.name

print(f"🚀 Running Blender test using script: {temp_script_path}")

try:
    result = subprocess.run(
        [BLENDER_PATH, "--background", "--python", temp_script_path],
        capture_output=True,
        text=True,
        timeout=30,
    )

    print("📤 Blender Output:\n" + result.stdout)

    if result.stderr:
        print("⚠️ Blender STDERR:\n" + result.stderr)

    if "Hello from Blender CLI!" in result.stdout:
        print("✅ Blender CLI test succeeded.")
    else:
        print("❌ Blender CLI test did not return expected output.")
finally:
    if os.path.exists(temp_script_path):
        os.remove(temp_script_path)


git add .
