import os
import re

TARGET_DIR = "examples"
LLM_KEYWORDS = [
    "llama3",
    "llama3:latest",
    "llama3.2",
    "deepseek",
    "deepseek-coder",
    "deepseek-coder-v2",
    "deepseek-coder:latest",
    "deepseek-r1",
]

# Regex for matching model names inside quotes
LLM_PATTERN = re.compile(r'(["\'])(%s)(:latest)?(["\'])' % "|".join(re.escape(k) for k in LLM_KEYWORDS))

def contains_llm_reference(code):
    return bool(LLM_PATTERN.search(code))

def patch_file(path):
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    if "get_config()" in original or "config['llm']['model']" in original:
        print(f"⚠️ Skipped (already using config): {os.path.basename(path)}")
        return False

    if not contains_llm_reference(original):
        print(f"ℹ️ No LLM match: {os.path.basename(path)}")
        return False

    print(f"🔍 Patching: {path}")

    # Replace hardcoded model name strings with `llm_model`
    modified = LLM_PATTERN.sub("llm_model", original)

    # Inject config loading
    inject_imports = "import os, yaml\nfrom env_loader import get_config\n"
    inject_config = "config = get_config()\nllm_model = config['llm']['model']\n"

    lines = modified.splitlines()
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("import"):
            insert_idx = i + 1
    lines.insert(insert_idx, inject_imports + inject_config)

    final_code = "\n".join(lines)
    with open(path, "w", encoding="utf-8") as f:
        f.write(final_code)

    print(f"✅ Patched: {os.path.basename(path)}")
    return True

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    examples_dir = os.path.join(base_dir, TARGET_DIR)
    patched_count = 0

    print(f"\n🔎 Scanning directory: {examples_dir}\n")
    for root, _, files in os.walk(examples_dir):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                if patch_file(full_path):
                    patched_count += 1

    print(f"\n✅ Completed. Patched {patched_count} file(s).")

if __name__ == "__main__":
    main()
