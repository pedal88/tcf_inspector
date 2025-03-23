#!/usr/bin/env python3
import sys
from pathlib import Path
from process_gvl import process_current_file

def process_new_file(file_path):
    """Process a newly added GVL file."""
    try:
        process_current_file(Path(file_path))
        print(f"Successfully processed new GVL file: {file_path}")
        return True
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: process_current_gvl.py <path_to_new_gvl_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not Path(file_path).exists():
        print(f"Error: File {file_path} does not exist")
        sys.exit(1)
    
    success = process_new_file(file_path)
    sys.exit(0 if success else 1) 