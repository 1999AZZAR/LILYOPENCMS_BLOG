import re

with open("static/js/brand-management.js", "r") as f:
    content = f.read()

new_presets = """// Professional Color Palettes for M3 Pastel Glass
const FIXED_PRESETS = {
  "Studio Mix": {
    "--background": "210 20% 96% / 1",
    "--foreground": "215 28% 17% / 1",
    "--card": "210 20% 96% / 1",
    "--card-foreground": "215 28% 17% / 1",
    "--popover": "210 20% 96% / 1",
    "--popover-foreground": "215 28% 17% / 1",
    "--primary": "206 63% 86% / 1",
    "--primary-foreground": "206 100% 17% / 1",
    "--secondary": "264 57% 87% / 1",
    "--secondary-foreground": "264 100% 17% / 1",
    "--muted": "60 30% 96% / 1",
    "--muted-foreground": "60 10% 40% / 1",
    "--accent": "44 82% 89% / 1",
    "--accent-foreground": "44 100% 17% / 1",
    "--destructive": "356 82% 88% / 1",
    "--destructive-foreground": "356 100% 17% / 1",
    "--border": "210 20% 92% / 1",
    "--input": "210 20% 98% / 1",
    "--ring": "206 63% 86% / 1"
  },
  "Warm Blush": {
    "--background": "12 50% 95% / 1",
    "--foreground": "12 40% 15% / 1",
    "--card": "12 50% 95% / 1",
    "--card-foreground": "12 40% 15% / 1",
    "--popover": "12 50% 95% / 1",
    "--popover-foreground": "12 40% 15% / 1",
    "--primary": "9 68% 75% / 1",
    "--primary-foreground": "9 100% 15% / 1",
    "--secondary": "11 88% 90% / 1",
    "--secondary-foreground": "11 100% 15% / 1",
    "--muted": "12 30% 92% / 1",
    "--muted-foreground": "12 20% 45% / 1",
    "--accent": "28 97% 80% / 1",
    "--accent-foreground": "28 100% 15% / 1",
    "--destructive": "0 84% 60% / 1",
    "--destructive-foreground": "0 0% 100% / 1",
    "--border": "12 40% 90% / 1",
    "--input": "12 50% 98% / 1",
    "--ring": "9 68% 75% / 1"
  },
  "Soft Studio": {
    "--background": "51 20% 93% / 1",
    "--foreground": "225 30% 15% / 1",
    "--card": "51 20% 93% / 1",
    "--card-foreground": "225 30% 15% / 1",
    "--popover": "51 20% 93% / 1",
    "--popover-foreground": "225 30% 15% / 1",
    "--primary": "224 83% 93% / 1",
    "--primary-foreground": "224 100% 15% / 1",
    "--secondary": "162 30% 91% / 1",
    "--secondary-foreground": "162 100% 15% / 1",
    "--muted": "51 10% 88% / 1",
    "--muted-foreground": "51 10% 45% / 1",
    "--accent": "224 83% 90% / 1",
    "--accent-foreground": "224 100% 15% / 1",
    "--destructive": "356 82% 90% / 1",
    "--destructive-foreground": "356 100% 15% / 1",
    "--border": "51 20% 88% / 1",
    "--input": "51 30% 98% / 1",
    "--ring": "224 83% 93% / 1"
  },
  "Soft Cream": {
    "--background": "12 50% 95% / 1",
    "--foreground": "12 30% 15% / 1",
    "--card": "12 50% 95% / 1",
    "--card-foreground": "12 30% 15% / 1",
    "--popover": "12 50% 95% / 1",
    "--popover-foreground": "12 30% 15% / 1",
    "--primary": "9 97% 86% / 1",
    "--primary-foreground": "9 100% 15% / 1",
    "--secondary": "32 28% 89% / 1",
    "--secondary-foreground": "32 100% 15% / 1",
    "--muted": "12 20% 90% / 1",
    "--muted-foreground": "12 20% 45% / 1",
    "--accent": "28 97% 80% / 1",
    "--accent-foreground": "28 100% 15% / 1",
    "--destructive": "0 84% 60% / 1",
    "--destructive-foreground": "0 0% 100% / 1",
    "--border": "12 30% 90% / 1",
    "--input": "12 50% 98% / 1",
    "--ring": "9 97% 86% / 1"
  },
  "Midnight Glass": {
    "--background": "225 30% 8% / 1",
    "--foreground": "210 20% 98% / 1",
    "--card": "225 30% 8% / 1",
    "--card-foreground": "210 20% 98% / 1",
    "--popover": "225 30% 8% / 1",
    "--popover-foreground": "210 20% 98% / 1",
    "--primary": "206 63% 56% / 1",
    "--primary-foreground": "0 0% 100% / 1",
    "--secondary": "264 57% 57% / 1",
    "--secondary-foreground": "0 0% 100% / 1",
    "--muted": "225 20% 15% / 1",
    "--muted-foreground": "225 20% 70% / 1",
    "--accent": "206 63% 56% / 1",
    "--accent-foreground": "0 0% 100% / 1",
    "--destructive": "356 82% 56% / 1",
    "--destructive-foreground": "0 0% 100% / 1",
    "--border": "225 30% 15% / 1",
    "--input": "225 30% 12% / 1",
    "--ring": "206 63% 56% / 1"
  }
};

// Categorize presets
const PRESET_CATEGORIES = {
  classic: ["Studio Mix", "Warm Blush", "Soft Studio", "Soft Cream", "Midnight Glass"],
  capuchin: [],
  themed: []
};"""

content = re.sub(
    r"// Professional Color Palettes.*?const PRESET_CATEGORIES = \{[^\}]+\};",
    new_presets,
    content,
    flags=re.DOTALL
)

with open("static/js/brand-management.js", "w") as f:
    f.write(content)
