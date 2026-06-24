"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

import re

with open("templates/admin_base.html", "r") as f:
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
                primary: "#202223", // Swiss Black/Polaris Ink
                primaryHover: "#000000",
                accent: "#008060", // Polaris Teal
                accentHover: "#004C3F",
                surface: "#FFFFFF",
                surfaceHover: "#F4F6F8",
                background: "#F4F6F8", // Polaris Sky
                border: "#C9CCCF", // Polaris Border
                text: "#202223", // Polaris Ink
                textMuted: "#6D7175",
                critical: "#D82C0D",
                criticalHover: "#bc2200",
                criticalSurface: "#FDEAE7"
              }
            },
            boxShadow: {
              "polaris-100": "0 1px 0 0 rgba(0,0,0,0.05)",
              "polaris-200": "0 3px 6px -3px rgba(23,24,24,0.08), 0 8px 20px -4px rgba(23,24,24,0.12)",
              "polaris-300": "0 4px 8px -2px rgba(23,24,24,0.08), 0 12px 32px -4px rgba(23,24,24,0.12)"
            }
          }
        }
      }
    </script>"""

# Replace config
content = re.sub(r"<script>\s*tailwind\.config = \{.*?\s*\}\s*</script>", config_script, content, flags=re.DOTALL)

# Refactor layout structure (Swiss x Polaris)
content = content.replace("bg-gray-100 text-gray-900", "bg-admin-background text-admin-text")
content = content.replace("bg-gradient-to-b from-slate-900 to-slate-800 border-r border-slate-700", "bg-admin-surface border-r border-admin-border")
content = content.replace("bg-gradient-to-r from-slate-900 to-slate-800", "bg-admin-primary")
content = content.replace("text-white comic-font", "text-white font-black tracking-tight")
content = content.replace("hover:text-slate-300", "hover:text-admin-textMuted")

# Sidebar links
content = content.replace("bg-admin-surface border border-admin-border rounded-xl p-4", "border-b border-admin-border p-4 rounded-none bg-transparent")
content = content.replace("text-admin-text hover:text-admin-accent hover:bg-admin-surfaceHover", "text-admin-text font-bold hover:text-admin-accent hover:bg-admin-surfaceHover")
content = content.replace("text-admin-textMuted hover:text-admin-accent hover:bg-admin-surfaceHover", "text-admin-textMuted font-medium hover:text-admin-text hover:bg-admin-surfaceHover")
content = content.replace("rounded-lg", "rounded-md")

# Hero section
content = content.replace("bg-admin-primary shadow-lg px-6 py-16 text-center cursor-pointer hover:bg-admin-primaryHover transition-all duration-300", "bg-admin-surface border-b border-admin-border px-8 py-12 text-left")
content = content.replace("text-5xl font-extrabold text-white", "text-3xl font-black text-admin-text tracking-tight")
content = content.replace("text-lg text-slate-300 max-w-2xl mx-auto mt-4", "text-base text-admin-textMuted max-w-2xl mt-2 font-medium")

# Main content area
content = content.replace("bg-admin-surface rounded-2xl shadow-lg p-10 border border-admin-border", "") # We remove the wrapper to let individual templates define their Polaris cards

with open("templates/admin_base.html", "w") as f:
    f.write(content)
