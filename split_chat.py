#!/usr/bin/env python3
"""
Split chat_hr_bot_1.json into separate metadata and entries files.
"""
import json
from pathlib import Path

def main():
    # Input and output paths
    input_file = Path("chat_hr_bot_1.json")
    meta_file = Path("chat_hr_bot_1.meta.json")
    entries_file = Path("chat_hr_bot_1.entries.json")
    
    # Read the combined file
    with input_file.open('r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract meta and entries sections
    meta = data.get('meta', {})
    entries = data.get('entries', [])
    
    # Write metadata file
    with meta_file.open('w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)
    
    # Write entries file
    with entries_file.open('w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2)
    
    print(f"✓ Created {meta_file} ({len(json.dumps(meta))} bytes)")
    print(f"✓ Created {entries_file} ({len(json.dumps(entries))} bytes)")
    print(f"✓ Split complete. Original file: {input_file}")

if __name__ == "__main__":
    main()