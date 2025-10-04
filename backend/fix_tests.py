#!/usr/bin/env python3
"""
Script to fix test error message patterns for Pydantic v2.
"""

import os
import re

def fix_test_file(filepath):
    """Fix error message patterns in a test file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace error message patterns
    replacements = [
        (r'"ensure this value is greater than or equal to 0"', '"Input should be greater than or equal to 0"'),
        (r'"ensure this value is less than or equal to 100"', '"Input should be less than or equal to 100"'),
        (r'"ensure this value is less than or equal to 1"', '"Input should be less than or equal to 1"'),
        (r'"ensure this value is greater than or equal to -1"', '"Input should be greater than or equal to -1"'),
        (r'"ensure this value is greater than 0"', '"Input should be greater than 0"'),
        (r'"Positions must be a list"', '"Input should be a valid list"'),
        (r'"Pies must be a list"', '"Input should be a valid list"'),
        (r'"Individual positions must be a list"', '"Input should be a valid list"'),
    ]
    
    for old, new in replacements:
        content = re.sub(old, new, content)
    
    with open(filepath, 'w') as f:
        f.write(content)

def main():
    """Fix all test files."""
    test_dir = "tests/test_models"
    for filename in os.listdir(test_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(test_dir, filename)
            print(f"Fixing {filepath}")
            fix_test_file(filepath)

if __name__ == "__main__":
    main()