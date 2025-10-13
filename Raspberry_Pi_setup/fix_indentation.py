#!/usr/bin/env python3
"""
Fix indentation issues in phone_system.py
This script will find and fix mixed tab/space indentation
"""

import re
import sys

def fix_indentation(file_path):
    """Fix mixed tab/space indentation in a Python file"""
    
    print(f"Checking indentation in {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        issues_found = 0
        
        for i, line in enumerate(lines, 1):
            original_line = line
            
            # Check if line has tabs
            if '\t' in line:
                print(f"Line {i}: Found tab character")
                issues_found += 1
                # Replace tabs with 4 spaces
                line = line.expandtabs(4)
            
            # Check for mixed indentation
            leading_whitespace = len(line) - len(line.lstrip())
            if leading_whitespace > 0:
                # Get the leading whitespace
                indent = line[:leading_whitespace]
                if '\t' in indent and ' ' in indent:
                    print(f"Line {i}: Mixed tabs and spaces in indentation")
                    issues_found += 1
                    # Convert all to spaces
                    line = line.expandtabs(4)
            
            fixed_lines.append(line)
        
        if issues_found > 0:
            print(f"\nFound {issues_found} indentation issues. Fixing...")
            
            # Create backup
            backup_path = file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"Backup created: {backup_path}")
            
            # Write fixed file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            
            print(f"✅ Fixed {issues_found} indentation issues in {file_path}")
            
            # Test if it's valid Python now
            try:
                with open(file_path, 'r') as f:
                    compile(f.read(), file_path, 'exec')
                print("✅ File now has valid Python syntax")
            except SyntaxError as e:
                print(f"❌ Syntax error still exists: {e}")
                print(f"   Line {e.lineno}: {e.text}")
                
        else:
            print("✅ No indentation issues found")
            
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return False
    
    return True

def check_specific_line(file_path, line_number):
    """Check a specific line for issues"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if line_number <= len(lines):
            line = lines[line_number - 1]
            print(f"Line {line_number}: {repr(line)}")
            
            if '\t' in line:
                print("  → Contains tab characters")
            
            leading_whitespace = len(line) - len(line.lstrip())
            if leading_whitespace > 0:
                indent = line[:leading_whitespace]
                if '\t' in indent and ' ' in indent:
                    print("  → Mixed tabs and spaces in indentation")
                elif '\t' in indent:
                    print("  → Uses tabs for indentation")
                else:
                    print("  → Uses spaces for indentation")
        else:
            print(f"Line {line_number} does not exist (file has {len(lines)} lines)")
            
    except Exception as e:
        print(f"Error checking line: {e}")

if __name__ == "__main__":
    file_path = "phone_system.py"
    
    print("=== Python Indentation Fixer ===")
    print()
    
    # Check specific line 281 first
    print("Checking line 281 specifically:")
    check_specific_line(file_path, 281)
    print()
    
    # Fix the entire file
    if fix_indentation(file_path):
        print("\n=== Fix Complete ===")
        print("You can now restart the service:")
        print("  sudo systemctl restart phone-gossip")
        print("  sudo journalctl -u phone-gossip -f")
    else:
        print("\n=== Fix Failed ===")
        print("Manual intervention may be required")