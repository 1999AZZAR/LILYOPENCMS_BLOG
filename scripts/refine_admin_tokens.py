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
            }
          }
        }
      }
    </script>"""

content = re.sub(r"<script>\s*tailwind\.config = \{.*?\s*\}\s*</script>", config_script, content, flags=re.DOTALL)

with open("templates/admin_base.html", "w") as f:
    f.write(content)
