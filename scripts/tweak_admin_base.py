"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

with open("templates/admin_base.html", "r") as f:
    content = f.read()

# Add a wrapper for the content to ensure background color stretches fully
content = content.replace("<main id=\"main-content\" class=\"w-full px-8 py-12\" role=\"main\" tabindex=\"-1\">", "<main id=\"main-content\" class=\"w-full px-8 py-12 bg-admin-background min-h-screen\" role=\"main\" tabindex=\"-1\">")
content = content.replace("bg-admin-surface border-b border-admin-border px-8 py-12 text-left", "bg-admin-surface border-b border-admin-border px-8 py-8 text-left")
content = content.replace("bg-admin-surface border-r border-admin-border shadow-lg", "bg-admin-surface border-r border-admin-border") # remove massive shadows from sidebar

with open("templates/admin_base.html", "w") as f:
    f.write(content)
