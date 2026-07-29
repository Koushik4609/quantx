import os
import re
import json

frontend_dir = "frontend/src"
pattern = re.compile(r'(?:axios\.(get|post|put|delete)|fetch)\s*\(\s*[`\'"](.*?)[`\'"]')

api_calls = []

for root, _, files in os.walk(frontend_dir):
    for file in files:
        if file.endswith(".ts") or file.endswith(".tsx"):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = pattern.finditer(content)
                for match in matches:
                    method = match.group(1) or "GET (fetch)"
                    url = match.group(2)
                    api_calls.append({
                        "file": filepath.replace(frontend_dir, ""),
                        "method": method.upper(),
                        "url": url
                    })

with open('frontend_api_calls.json', 'w') as f:
    json.dump(api_calls, f, indent=2)

print(f"Extracted {len(api_calls)} API calls.")
