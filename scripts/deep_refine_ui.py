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

# 1. Update Tailwind config in admin_base.html
admin_base_path = "templates/admin_base.html"
with open(admin_base_path, "r") as f:
    content = f.read()

config_script = """    <script>
      tailwind.config = {
        theme: {
          extend: {
            fontFamily: {
              sans: ["-apple-system", "BlinkMacSystemFont", "San Francisco", "Segoe UI", "Roboto", "Helvetica Neue", "sans-serif"]
            },
            colors: {
              admin: {
                primary: "#202223", // Ink
                primaryHover: "#000000",
                accent: "#008060", // Teal
                accentHover: "#004C3F",
                surface: "#FFFFFF",
                surfaceHover: "#F4F6F8",
                background: "#F4F6F8",
                border: "#C9CCCF",
                text: "#202223",
                textMuted: "#6D7175",
                critical: "#D82C0D",
                criticalHover: "#bc2200",
                criticalSurface: "#FDEAE7",
                warning: "#FFC453",
                warningHover: "#FFB320",
                warningSurface: "#FFFBED",
                success: "#008060",
                successHover: "#006e52",
                successSurface: "#F1F8F5"
              }
            },
            boxShadow: {
              "polaris-100": "0 1px 0 0 rgba(0,0,0,0.05)",
              "polaris-200": "0 3px 6px -3px rgba(23,24,24,0.08), 0 8px 20px -4px rgba(23,24,24,0.12)",
              "polaris-300": "0 4px 8px -2px rgba(23,24,24,0.08), 0 12px 32px -4px rgba(23,24,24,0.12)"
            },
            borderRadius: {
              "polaris-sm": "4px",
              "polaris-base": "8px",
              "polaris-lg": "12px",
              "polaris-full": "9999px"
            }
          }
        }
      }
    </script>"""

content = re.sub(r"<script>\s*tailwind\.config = \{.*?\s*\}\s*</script>", config_script, content, flags=re.DOTALL)
with open(admin_base_path, "w") as f:
    f.write(content)

# 2. Refactor shadows and rounded classes across all files
replacements = [
    # Shadows
    (r"\bshadow-sm\b", "shadow-polaris-100"),
    (r"\bshadow-md\b", "shadow-polaris-100"),
    (r"\bshadow-lg\b", "shadow-polaris-200"),
    (r"\bshadow-xl\b", "shadow-polaris-300"),
    (r"\bshadow-2xl\b", "shadow-polaris-300"),
    (r"\bshadow-inner\b", ""),
    
    # Border Radiuses
    (r"\brounded\b", "rounded-polaris-sm"),
    (r"\brounded-sm\b", "rounded-polaris-sm"),
    (r"\brounded-md\b", "rounded-polaris-base"),
    (r"\brounded-lg\b", "rounded-polaris-base"),
    (r"\brounded-xl\b", "rounded-polaris-lg"),
    (r"\brounded-2xl\b", "rounded-polaris-lg"),
    (r"\brounded-3xl\b", "rounded-polaris-lg"),
    (r"\brounded-full\b", "rounded-polaris-full"),
    (r"\brounded-t-lg\b", "rounded-t-polaris-base"),
    (r"\brounded-t-md\b", "rounded-t-polaris-base"),
    (r"\brounded-b-lg\b", "rounded-b-polaris-base"),
    (r"\brounded-b-md\b", "rounded-b-polaris-base"),
]

settings_files = glob.glob("templates/settings/*.html") + ["templates/admin_base.html"]
total_replacements = 0

for filepath in settings_files:
    with open(filepath, "r") as f:
        html = f.read()
        
    for old, new in replacements:
        html, count = re.subn(old, new, html)
        total_replacements += count
        
    with open(filepath, "w") as f:
        f.write(html)

print(f"Made {total_replacements} structural replacements (shadows & radiuses) across {len(settings_files)} files.")
