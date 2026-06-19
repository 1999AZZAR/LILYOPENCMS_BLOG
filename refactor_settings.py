import os
import glob
import re

replacements = [
    # Remove old surface wrappers
    (r"<div class=\"space-y-8\">\n  <!-- Brand Information Section -->", "<!-- Brand Information Section -->"),
    (r"<div class=\"bg-admin-surface border border-admin-border rounded-lg shadow-lg p-6\"", "<div class=\"bg-admin-surface border border-admin-border rounded-md shadow-polaris-100 p-6 mb-8\""),
    (r"<div class=\"bg-admin-surface border border-admin-border rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6\"", "<div class=\"bg-admin-surface border border-admin-border rounded-md shadow-polaris-100 p-6\""),
    
    # Typography (Swiss style)
    (r"text-2xl font-bold text-admin-text", "text-xl font-bold tracking-tight text-admin-text"),
    (r"text-lg font-semibold text-admin-text", "text-base font-bold text-admin-text"),
    
    # Buttons (Polaris style)
    (r"bg-gradient-to-r from-admin-primary to-admin-primaryHover hover:from-admin-primaryHover hover:to-admin-primary", "bg-admin-primary hover:bg-admin-primaryHover"),
    (r"bg-gradient-to-r from-admin-accent to-admin-accentHover hover:from-admin-accentHover hover:to-admin-accent", "bg-admin-accent hover:bg-admin-accentHover"),
    (r"py-2 px-4 rounded-lg font-medium shadow-md", "px-4 h-9 rounded-md font-medium shadow-polaris-100"),
    (r"shadow-lg", "shadow-polaris-100"),
    (r"shadow-xl", "shadow-polaris-200"),
    
    # Inputs (Polaris style)
    (r"rounded-lg bg-white", "rounded-md bg-white"),
    
    # Tables (Polaris style)
    (r"rounded-lg overflow-hidden", "rounded-md overflow-hidden border border-admin-border"),
    (r"bg-admin-background", "bg-admin-surfaceHover"),
]

settings_files = glob.glob("templates/settings/*.html")

for filepath in settings_files:
    with open(filepath, "r") as f:
        html = f.read()
        
    for old, new in replacements:
        html = re.sub(old, new, html)
        
    with open(filepath, "w") as f:
        f.write(html)

print(f"Refactored {len(settings_files)} templates to use Polaris cards and Swiss typography.")
