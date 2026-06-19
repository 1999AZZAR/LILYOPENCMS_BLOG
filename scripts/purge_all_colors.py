import glob
import re

def replace_color_class(match):
    full_class = match.group(0)
    # Group 1 can be just prefix or pseudo:prefix (e.g. hover:bg)
    prefix_full = match.group(1)
    color = match.group(2)
    weight = int(match.group(3))
    
    # Determine base prefix vs pseudo class
    pseudo = ""
    prefix = prefix_full
    if ":" in prefix_full:
        pseudo, prefix = prefix_full.split(":")
        pseudo += ":"
    
    semantic_color = ""
    
    if color in ["gray", "slate", "zinc", "neutral", "stone"]:
        if prefix == "text":
            semantic_color = "textMuted" if weight < 700 else "text"
        elif prefix == "bg":
            semantic_color = "surfaceHover" if weight < 300 else ("border" if weight < 500 else "primaryHover")
        elif prefix == "border":
            semantic_color = "border" if weight < 500 else "textMuted"
        elif prefix == "ring":
            semantic_color = "border"
        elif prefix == "shadow":
            semantic_color = "polaris-100" if weight < 300 else "polaris-200"
            return f"{pseudo}shadow-{semantic_color}" # shadow uses different token system
    elif color in ["red", "rose", "pink"]:
        if prefix == "bg":
            semantic_color = "criticalSurface" if weight < 400 else ("critical" if weight < 600 else "criticalHover")
        elif prefix == "text":
            semantic_color = "critical" if weight < 700 else "criticalHover"
        else:
            semantic_color = "critical"
    elif color in ["green", "emerald", "lime"]:
        if prefix == "bg":
            semantic_color = "successSurface" if weight < 400 else ("success" if weight < 600 else "successHover")
        elif prefix == "text":
            semantic_color = "success" if weight < 700 else "successHover"
        else:
            semantic_color = "success"
    elif color in ["yellow", "amber", "orange"]:
        if prefix == "bg":
            semantic_color = "warningSurface" if weight < 400 else ("warning" if weight < 600 else "warningHover")
        elif prefix == "text":
            semantic_color = "warning" if weight < 700 else "warningHover"
        else:
            semantic_color = "warning"
    elif color in ["blue", "indigo", "cyan", "sky", "teal", "purple", "violet", "fuchsia"]:
        if prefix == "bg":
            semantic_color = "surfaceHover" if weight < 400 else ("accent" if weight < 600 else "accentHover")
        elif prefix == "text":
            semantic_color = "accent" if weight < 700 else "accentHover"
        else:
            semantic_color = "accent"

    if not semantic_color:
        return full_class

    return f"{pseudo}{prefix}-admin-{semantic_color}"

pattern = re.compile(r"\b(bg|text|border|ring|hover:bg|hover:text|focus:ring|focus:border|shadow)-(gray|slate|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-([0-9]{2,3})\b")

files_to_check = glob.glob("templates/settings/*.html") + ["templates/admin_base.html"]
total_replacements = 0

for filepath in files_to_check:
    with open(filepath, "r") as f:
        html = f.read()
    
    new_html, count = pattern.subn(replace_color_class, html)
    total_replacements += count
    
    if count > 0:
        with open(filepath, "w") as f:
            f.write(new_html)

print(f"Made {total_replacements} semantic color replacements across {len(files_to_check)} files.")
