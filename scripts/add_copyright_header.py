#!/usr/bin/env python3
"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

import os
import re
import sys

# Construct the email dynamic to prevent self-modification/matching
EMAIL_USER = "azzar.mr.zs"
EMAIL_DOMAIN = "gmail.com"
EMAIL_ADDR = f"{EMAIL_USER}@{EMAIL_DOMAIN}"

# Define the copyright text block
COPYRIGHT_TEXT = f"""Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: {EMAIL_ADDR} for inquiries."""

# Define comment wrappers for each extension
HEADERS = {
    '.py': f'"""\n{COPYRIGHT_TEXT}\n"""',
    '.js': f'/*\n{COPYRIGHT_TEXT}\n*/',
    '.go': f'/*\n{COPYRIGHT_TEXT}\n*/',
    '.css': f'/*\n{COPYRIGHT_TEXT}\n*/',
    '.sql': f'/*\n{COPYRIGHT_TEXT}\n*/',
    '.sh': f": <<'OFF'\n{COPYRIGHT_TEXT}\nOFF",
    '.html': f'<!--\n{COPYRIGHT_TEXT}\n-->'
}

# Regex to match blocks that might contain the copyright
BLOCK_PATTERNS = {
    '.py': [
        re.compile(r'"{3}.*?"{3}', re.DOTALL),
        re.compile(r"'{3}.*?'{3}", re.DOTALL)
    ],
    '.js': [re.compile(r'/\*.*?\*/', re.DOTALL)],
    '.go': [re.compile(r'/\*.*?\*/', re.DOTALL)],
    '.css': [re.compile(r'/\*.*?\*/', re.DOTALL)],
    '.sql': [re.compile(r'/\*.*?\*/', re.DOTALL)],
    '.sh': [
        re.compile(r":\s*<<\s*['\"]?OFF['\"]?.*?OFF", re.DOTALL),
        re.compile(r":\s*<<\s*['\"]?EOF['\"]?.*?EOF", re.DOTALL)
    ],
    '.html': [re.compile(r'<!--.*?-->', re.DOTALL)]
}

# Directories and file patterns to ignore
IGNORE_DIRS = {'.git', '.github', 'node_modules', 'venv', '.venv', '__pycache__', 'instance', 'backups', 'LICENSE', 'vendor'}
IGNORE_FILES = {'jquery-3.6.0.min.js', 'add_copyright_header.py'}

def should_process_dir(name):
    return name not in IGNORE_DIRS

def should_process_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in HEADERS:
        return False
    if filename in IGNORE_FILES or '.min.' in filename:
        return False
    return True

def remove_existing_copyright(content, ext):
    """
    Finds and removes any comment blocks containing the email address.
    """
    if EMAIL_ADDR not in content:
        return content

    patterns = BLOCK_PATTERNS.get(ext, [])
    for pattern in patterns:
        matches = pattern.findall(content)
        for match in matches:
            if EMAIL_ADDR in match:
                content = content.replace(match, "")
    
    return content

def process_file(filepath, dry_run=False):
    ext = os.path.splitext(filepath)[1].lower()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        print(f"⚠️ Error reading {filepath}: {e}")
        return False

    # 1. Strip out any existing copyright comment blocks containing the email address
    cleaned_content = remove_existing_copyright(original_content, ext)

    # 2. Check if shebang exists
    shebang = ""
    rest_of_content = cleaned_content
    
    if cleaned_content.startswith("#!"):
        lines = cleaned_content.split("\n", 1)
        shebang = lines[0] + "\n"
        rest_of_content = lines[1] if len(lines) > 1 else ""

    # 3. Clean leading whitespace and newlines from the rest of the content
    rest_of_content = rest_of_content.lstrip()

    # 4. Construct the new content
    header = HEADERS[ext]
    new_content = shebang
    if shebang:
        new_content += "\n"
    new_content += header + "\n\n" + rest_of_content

    # Clean trailing whitespace/newlines at the end of file (standard code health)
    new_content = new_content.rstrip() + "\n"

    if original_content == new_content:
        return False

    if dry_run:
        print(f"✏️ [DRY RUN] Would update: {filepath}")
    else:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Updated: {filepath}")
        except Exception as e:
            print(f"❌ Error writing {filepath}: {e}")
            return False
            
    return True

def main():
    dry_run = "--dry-run" in sys.argv
    target_dir = "/home/ubuntu/projects/lilyopencms"

    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        target_dir = sys.argv[1]

    print(f"🔍 Starting copyright header check in: {target_dir}")
    if dry_run:
        print("⚠️ Running in DRY-RUN mode. No files will be modified.")

    updated_count = 0
    total_processed = 0

    for root, dirs, files in os.walk(target_dir):
        # In-place modify dirs to skip ignored directories
        dirs[:] = [d for d in dirs if should_process_dir(d)]

        for file in files:
            if should_process_file(file):
                filepath = os.path.join(root, file)
                total_processed += 1
                if process_file(filepath, dry_run):
                    updated_count += 1

    print(f"\n📊 Summary:")
    print(f"   Processed files: {total_processed}")
    print(f"   Updated files  : {updated_count}")

if __name__ == "__main__":
    main()
