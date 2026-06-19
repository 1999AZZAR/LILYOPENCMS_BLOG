import os
import glob
import re

replacements = [
    # Critical (Reds/Pinks)
    (r"bg-red-500", "bg-admin-critical"),
    (r"bg-red-600", "bg-admin-criticalHover"),
    (r"hover:bg-red-600", "hover:bg-admin-criticalHover"),
    (r"text-red-500", "text-admin-critical"),
    (r"text-red-600", "text-admin-critical"),
    (r"text-red-700", "text-admin-criticalHover"),
    (r"border-red-200", "border-admin-criticalSurface"),
    (r"border-red-300", "border-admin-critical"),
    (r"border-red-500", "border-admin-critical"),
    (r"ring-red-300", "ring-admin-criticalSurface"),
    (r"ring-red-400", "ring-admin-critical"),
    (r"ring-red-500", "ring-admin-critical"),
    (r"bg-red-50", "bg-admin-criticalSurface"),
    (r"bg-red-100", "bg-admin-criticalSurface"),
    (r"bg-red-200", "bg-admin-criticalSurface"),
    
    # Success (Greens/Emeralds)
    (r"bg-green-500", "bg-admin-success"),
    (r"bg-green-600", "bg-admin-successHover"),
    (r"hover:bg-green-600", "hover:bg-admin-successHover"),
    (r"text-green-500", "text-admin-success"),
    (r"text-green-600", "text-admin-success"),
    (r"text-green-700", "text-admin-successHover"),
    (r"border-green-200", "border-admin-successSurface"),
    (r"border-green-500", "border-admin-success"),
    (r"ring-green-300", "ring-admin-successSurface"),
    (r"ring-green-400", "ring-admin-success"),
    (r"ring-green-500", "ring-admin-success"),
    (r"bg-green-50", "bg-admin-successSurface"),
    (r"bg-green-100", "bg-admin-successSurface"),
    (r"bg-green-200", "bg-admin-successSurface"),

    # Warning (Yellows)
    (r"bg-yellow-500", "bg-admin-warning"),
    (r"bg-yellow-600", "bg-admin-warningHover"),
    (r"hover:bg-yellow-600", "hover:bg-admin-warningHover"),
    (r"text-yellow-500", "text-admin-warning"),
    (r"text-yellow-600", "text-admin-warning"),
    (r"text-yellow-700", "text-admin-warningHover"),
    (r"border-yellow-200", "border-admin-warningSurface"),
    (r"ring-yellow-300", "ring-admin-warningSurface"),
    (r"bg-yellow-50", "bg-admin-warningSurface"),
    (r"bg-yellow-100", "bg-admin-warningSurface"),

    # Remaining Blues (Primary/Accent mappings)
    (r"bg-blue-300", "bg-admin-surfaceHover"),
    (r"hover:bg-blue-400", "hover:bg-admin-border"),
    (r"bg-blue-200", "bg-admin-surfaceHover"),
    (r"hover:bg-blue-300", "hover:bg-admin-border"),
    (r"ring-blue-400", "ring-admin-accent"),
    
    # Catching hover:to and hover:from leftovers if any exist
    (r"hover:to-pink-600", ""),
    (r"hover:to-emerald-600", ""),
    (r"hover:to-indigo-400", ""),
]

settings_files = glob.glob("templates/settings/*.html")

for filepath in settings_files:
    with open(filepath, "r") as f:
        html = f.read()
        
    for old, new in replacements:
        html = re.sub(old, new, html)
        
    with open(filepath, "w") as f:
        f.write(html)

print(f"Refactored {len(settings_files)} templates to remove arbitrary status colors.")