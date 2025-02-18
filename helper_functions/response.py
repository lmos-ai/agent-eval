import json
import re
from typing import Optional, Dict

def extract_json_from_string(text: str) -> Optional[Dict]:
    try:
        # Simple pattern: look for something that starts with '{' and ends with '}'
        # This won't handle nested braces as robustly, but might work for simpler cases
        json_pattern = re.compile(r"\{.*?\}", re.DOTALL)

        match = json_pattern.search(text)
        if match:
            json_str = match.group()
            return json.loads(json_str)
        else:
            print("[!] No valid JSON found in the string.")
            return None

    except json.JSONDecodeError as e:
        print(f"⚠️ Error decoding JSON: {e}")
        return None
