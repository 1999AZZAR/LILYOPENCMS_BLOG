import glob
import re

files_to_check = glob.glob("templates/settings/*.html") + ["templates/admin_base.html"]

def fix_content(html):
    # Fix malformed rounded classes
    html = html.replace("rounded-polaris-sm-none", "rounded-none")
    html = html.replace("rounded-polaris-sm-sm", "rounded-sm")
    html = html.replace("rounded-polaris-sm-md", "rounded-md")
    html = html.replace("rounded-polaris-sm-lg", "rounded-lg")
    html = html.replace("rounded-polaris-sm-xl", "rounded-xl")
    html = html.replace("rounded-polaris-sm-2xl", "rounded-2xl")
    html = html.replace("rounded-polaris-sm-3xl", "rounded-3xl")
    html = html.replace("rounded-polaris-sm-full", "rounded-full")
    html = html.replace("rounded-polaris-base", "rounded-md") # Reverting back to native tailwind standard for now to be safe, then mapping cleanly
    html = html.replace("rounded-polaris-lg", "rounded-lg")
    html = html.replace("rounded-polaris-sm", "rounded-sm")
    html = html.replace("rounded-polaris-full", "rounded-full")
    
    # Strip any lingering from- and to- classes
    html = re.sub(r"\b(from|to|via|hover:from|hover:to|hover:via)-[a-zA-Z0-9-]+\b", "", html)
    
    # Map divide to admin borders
    html = re.sub(r"\bdivide-(gray|slate|zinc|neutral|stone)-[0-9]+\b", "divide-admin-border", html)
    
    # Fix weird double spaces caused by deletion
    html = re.sub(r" {2,}", " ", html)
    
    return html

total_changed = 0
for filepath in files_to_check:
    with open(filepath, "r") as f:
        original_html = f.read()
    
    new_html = fix_content(original_html)
    
    if new_html != original_html:
        with open(filepath, "w") as f:
            f.write(new_html)
        total_changed += 1

print(f"Fixed anomalies in {total_changed} files.")
