"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

import glob
import re

files_to_check = glob.glob("templates/settings/*.html") + ["templates/admin_base.html"]

def map_radiuses(html):
    # Mapping to polaris standard
    html = re.sub(r"\brounded-sm\b", "rounded-polaris-sm", html)
    html = re.sub(r"\brounded-md\b", "rounded-polaris-base", html)
    html = re.sub(r"\brounded-lg\b", "rounded-polaris-lg", html)
    html = re.sub(r"\brounded-xl\b", "rounded-polaris-lg", html)
    html = re.sub(r"\brounded-2xl\b", "rounded-polaris-lg", html)
    html = re.sub(r"\brounded-3xl\b", "rounded-polaris-lg", html)
    html = re.sub(r"\brounded-full\b", "rounded-polaris-full", html)
    
    # Base rounded without suffix
    # To prevent rounded-md from becoming rounded-polaris-sm-md again, we use word boundaries properly.
    # We only want to target EXACTLY "rounded"
    html = re.sub(r"(?<!-)\brounded\b(?!-)", "rounded-polaris-sm", html)
    return html

for filepath in files_to_check:
    with open(filepath, "r") as f:
        original_html = f.read()
    
    new_html = map_radiuses(original_html)
    
    with open(filepath, "w") as f:
        f.write(new_html)
