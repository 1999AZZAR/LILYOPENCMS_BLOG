import glob
import re

# 1. Update admin_base.html to include tailwind.config
admin_base_path = "templates/admin_base.html"
with open(admin_base_path, "r") as f:
    content = f.read()

config_script = """    <script src="https://cdn.tailwindcss.com?plugins=forms,typography"></script>
    <script>
      tailwind.config = {
        theme: {
          extend: {
            colors: {
              admin: {
                primary: "#0f172a", // slate-900
                primaryHover: "#1e293b", // slate-800
                accent: "#3b82f6", // blue-500
                accentHover: "#2563eb", // blue-600
                surface: "#ffffff",
                surfaceHover: "#f8fafc",
                background: "#f1f5f9", // slate-100
                border: "#e2e8f0", // slate-200
                text: "#0f172a", // slate-900
                textMuted: "#64748b" // slate-500
              }
            }
          }
        }
      }
    </script>"""

if "tailwind.config =" not in content:
    content = content.replace("<script src=\"https://cdn.tailwindcss.com?plugins=forms,typography\"></script>", config_script)

with open(admin_base_path, "w") as f:
    f.write(content)

# 2. Refactor all settings templates
replacements = [
    # Backgrounds and Gradients
    (r"bg-gradient-to-br from-blue-50 to-indigo-50", "bg-admin-surface"),
    (r"bg-gradient-to-r from-blue-100 to-indigo-100", "bg-admin-background"),
    (r"bg-gradient-to-r from-blue-50 to-indigo-50", "bg-admin-surface"),
    (r"bg-gradient-to-r from-blue-500 to-indigo-500", "bg-admin-primary"),
    (r"hover:from-blue-600 hover:to-indigo-600", "hover:bg-admin-primaryHover"),
    
    # Background Solid
    (r"bg-blue-50", "bg-admin-surface"),
    (r"bg-blue-100", "bg-admin-background"),
    (r"bg-blue-500", "bg-admin-accent"),
    (r"bg-blue-600", "bg-admin-accentHover"),
    (r"hover:bg-blue-100", "hover:bg-admin-surfaceHover"),
    (r"hover:bg-blue-200", "hover:bg-admin-border"),
    
    # Text
    (r"text-blue-900", "text-admin-text"),
    (r"text-blue-800", "text-admin-text"),
    (r"text-blue-700", "text-admin-textMuted"),
    (r"text-blue-600", "text-admin-textMuted"),
    (r"text-blue-500", "text-admin-accent"),
    (r"hover:text-blue-600", "hover:text-admin-text"),
    
    # Borders & Rings
    (r"border-blue-200", "border-admin-border"),
    (r"border-blue-300", "border-admin-border"),
    (r"focus:border-blue-500", "focus:border-admin-accent"),
    (r"focus:ring-blue-500", "focus:ring-admin-accent"),
    (r"focus:ring-blue-300", "focus:ring-admin-border"),
    (r"divide-blue-200", "divide-admin-border"),
    (r"ring-blue-500", "ring-admin-accent"),
]

settings_files = glob.glob("templates/settings/*.html")

for filepath in settings_files:
    with open(filepath, "r") as f:
        html = f.read()
        
    for old, new in replacements:
        html = re.sub(old, new, html)
        
    with open(filepath, "w") as f:
        f.write(html)

print(f"Refactored {len(settings_files)} templates to use semantic admin colors.")
