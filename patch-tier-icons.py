import os
import re
import glob

PAGES_DIR = os.path.join("public", "pages")
SKIP = {"rsd-funnel-page-02-qualify.html"}

# ============================================================
# RSD CUSTOM SVG ICONS — Astronaut/Rocket/Launchpad theme
# ============================================================

# Astronaut helmet - "suited up, ready"
SVG_ASTRONAUT = '<svg class="tier-ico" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="8"></circle><path d="M7 11 Q12 8 17 11"></path><circle cx="9.5" cy="11" r="0.6" fill="currentColor"></circle><line x1="12" y1="4" x2="12" y2="2"></line><circle cx="12" cy="2" r="0.8" fill="currentColor"></circle></svg>'

# Rocket ascending - "lifting off, gaining momentum"
SVG_ROCKET = '<svg class="tier-ico" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><path d="M12 2 C14 5 15 9 15 13 V17 H9 V13 C9 9 10 5 12 2 Z"></path><circle cx="12" cy="11" r="1.2"></circle><path d="M9 15 L7 18 L9 17"></path><path d="M15 15 L17 18 L15 17"></path><path d="M11 18 L11 21 M13 18 L13 21 M12 18 L12 22"></path></svg>'

# Launchpad with rocket - "fully operational, in command"
SVG_LAUNCHPAD = '<svg class="tier-ico" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><path d="M12 3 C13.5 5.5 14 8 14 11 V14 H10 V11 C10 8 10.5 5.5 12 3 Z"></path><circle cx="12" cy="9" r="0.8" fill="currentColor"></circle><path d="M10 12 L8 14 L10 13.5"></path><path d="M14 12 L16 14 L14 13.5"></path><path d="M6 18 L8 14 M18 18 L16 14"></path><line x1="4" y1="18" x2="20" y2="18"></line><line x1="6" y1="21" x2="18" y2="21"></line><path d="M11 14 L11 17 M13 14 L13 17"></path></svg>'

# Clean left-arrow for Back buttons
SVG_BACK_ARROW = '<svg class="back-ico" viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9.5,3.5 4.5,8 9.5,12.5"></polyline><line x1="4.5" y1="8" x2="12" y2="8"></line></svg>'

CSS_BLOCK = """
/* === RSD Tier & Back Icons (added by patch) === */
.tier-ico{display:inline-block;vertical-align:-4px;margin-right:8px;color:var(--gold);transition:color .35s ease,filter .35s ease,transform .35s ease}
.tier-card.act .tier-ico,.tier.act .tier-ico,.tg-row:hover .tier-ico{color:var(--grn);filter:drop-shadow(0 0 5px rgba(92,184,92,.55));transform:scale(1.05)}
.back-ico{display:inline-block;vertical-align:-1px;margin-right:6px;color:currentColor}
"""

CSS_MARKER = "/* === RSD Tier & Back Icons (added by patch) === */"

files_changed = 0
total_replacements = 0

pattern = os.path.join(PAGES_DIR, "rsd-funnel-page-*.html")
for filepath in sorted(glob.glob(pattern)):
    filename = os.path.basename(filepath)
    if filename in SKIP:
        print(f"  [SKIP]  {filename} (Page 2 excluded)")
        continue
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    original = content
    file_changes = 0
    
    # ------------------------------------------------------------
    # 1. Fix Back button - replace any broken char before "Back</button"
    # Pattern: >X Back</button where X is any non-ASCII junk
    # ------------------------------------------------------------
    pattern_back = re.compile(r'>([^<>]{0,3})\s*Back</button>')
    def fix_back(m):
        nonlocal_count = 1
        return f'>{SVG_BACK_ARROW} Back</button>'
    
    back_matches = pattern_back.findall(content)
    if back_matches:
        content = pattern_back.sub(f'>{SVG_BACK_ARROW} Back</button>', content)
        file_changes += len(back_matches)
        print(f"    - {len(back_matches)} Back buttons -> SVG arrow")
    
    # ------------------------------------------------------------
    # 2. Tier heading icons in "What each tier actually means" section
    #    Replace garbage chars inside <div class="tg-ico"> for each tier
    # ------------------------------------------------------------
    # Pattern: <div class="tg-ico">JUNK</div> followed by tier name in tg-lbl
    # We need to inject the right SVG based on which tier follows
    
    # Strategy: find tg-row blocks and replace their tg-ico content based on tg-lbl
    tier_pattern = re.compile(
        r'(<div class="tg-ico">)([^<]{0,8})(</div>\s*<div class="tg-body">\s*<div class="tg-lbl">)(Starter Lock|Growth Lock|Dominate Lock)',
        re.DOTALL
    )
    
    def replace_tier_ico(m):
        tier_name = m.group(4)
        if "Starter" in tier_name:
            svg = SVG_ASTRONAUT
        elif "Growth" in tier_name:
            svg = SVG_ROCKET
        elif "Dominate" in tier_name:
            svg = SVG_LAUNCHPAD
        else:
            svg = SVG_ASTRONAUT
        return f'{m.group(1)}{svg}{m.group(3)}{tier_name}'
    
    tier_matches = tier_pattern.findall(content)
    if tier_matches:
        content = tier_pattern.sub(replace_tier_ico, content)
        file_changes += len(tier_matches)
        print(f"    - {len(tier_matches)} tier section icons -> astronaut/rocket/launchpad SVG")
    
    # ------------------------------------------------------------
    # 3. Inject CSS if not already present
    # ------------------------------------------------------------
    if CSS_MARKER not in content and file_changes > 0:
        if "</style>" in content:
            content = content.replace("</style>", CSS_BLOCK + "\n</style>", 1)
            print(f"    - CSS injected")
            file_changes += 1
    
    if content != original:
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        print(f"  [DONE]  {filename}: {file_changes} changes")
        files_changed += 1
        total_replacements += file_changes
    else:
        print(f"  [SKIP]  {filename}: nothing to change")

print()
print("=" * 55)
print(f"  Files changed: {files_changed}")
print(f"  Total fixes:   {total_replacements}")
print("=" * 55)
