import os
import re
import ftfy

PAGE = "public/pages/rsd-funnel-page-09-lock-rate.html"

with open(PAGE, "r", encoding="utf-8") as f:
    original = f.read()

# === SAFETY: Stash <script> and <style> blocks ===
script_pattern = re.compile(r'(<script[^>]*>.*?</script>)', re.DOTALL)
style_pattern = re.compile(r'(<style[^>]*>.*?</style>)', re.DOTALL)

scripts = []
styles = []

def stash_script(m):
    scripts.append(m.group(1))
    return f'@@SCRIPT_STASH_{len(scripts)-1}@@'

def stash_style(m):
    styles.append(m.group(1))
    return f'@@STYLE_STASH_{len(styles)-1}@@'

content = script_pattern.sub(stash_script, original)
content = style_pattern.sub(stash_style, content)

# === INLINE SVG ICONS ===

# Bullet checkmark — gold default, animatable to green via CSS .tier.sel .fc-svg
SVG_CHECK = '<svg class="fc-svg" viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="3,8.5 7,12.5 13,4.5"></polyline></svg>'

# === MINIMALIST GEOMETRIC LOCK ICONS (your spec: lock / lock-plus / lock-crown) ===

# Tier 1: Plain padlock — Starter Lock
SVG_LOCK = '<svg class="tier-ico" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="1.5"></rect><path d="M8 11 V7.5 A4 4 0 0 1 16 7.5 V11"></path><circle cx="12" cy="16" r="0.9" fill="currentColor"></circle></svg>'

# Tier 2: Padlock with upward chevron — Growth Lock
SVG_LOCK_PLUS = '<svg class="tier-ico" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="1.5"></rect><path d="M8 11 V7.5 A4 4 0 0 1 16 7.5 V11"></path><polyline points="9,17 12,14 15,17"></polyline></svg>'

# Tier 3: Padlock with crown — Dominate Lock
SVG_LOCK_CROWN = '<svg class="tier-ico" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="13" width="14" height="9" rx="1.5"></rect><path d="M8 13 V9.5 A4 4 0 0 1 16 9.5 V13"></path><circle cx="12" cy="17.5" r="0.8" fill="currentColor"></circle><polyline points="7,5 9,8 12,3 15,8 17,5 17,8 7,8 Z"></polyline></svg>'

# Right-arrow for button text
SVG_RIGHT_ARROW = '<svg class="btn-arrow" viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="display:inline-block;vertical-align:-1px;margin-left:4px"><polyline points="6.5,3.5 11,8 6.5,12.5"></polyline><line x1="4" y1="8" x2="11" y2="8"></line></svg>'

# Back left-arrow
SVG_BACK_ARROW = '<svg class="back-ico" viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9.5,3.5 4.5,8 9.5,12.5"></polyline><line x1="4.5" y1="8" x2="12" y2="8"></line></svg>'

CSS_BLOCK = """
/* === RSD Page 9 Cosmetic Icon System === */
.fc-svg{display:inline-block;vertical-align:-2px;margin-right:8px;color:var(--gold);transition:color .35s ease,filter .35s ease,transform .35s ease;flex-shrink:0}
.tier.sel .fc-svg{color:var(--grn);filter:drop-shadow(0 0 4px rgba(92,184,92,.55))}
.tier-ico{display:inline-block;vertical-align:-4px;margin-right:10px;color:var(--gold)}
.back-ico{display:inline-block;vertical-align:-1px;margin-right:6px;color:currentColor}
"""

CSS_MARKER = "/* === RSD Page 9 Cosmetic Icon System === */"

changes = 0

# === Pass 1: ftfy on the markup ===
ftfy_fixed = ftfy.fix_text(content)
if ftfy_fixed != content:
    diff = sum(1 for a, b in zip(content, ftfy_fixed) if a != b) + abs(len(content) - len(ftfy_fixed))
    print(f"  - ftfy repaired ~{diff} characters in markup")
    content = ftfy_fixed
    changes += diff

# === Pass 2: Targeted mojibake patterns (catches what ftfy didn't) ===
mojibake_map = [
    # Trademark variants
    ('Tour2Bookingâ€žÂ¢', 'Tour2Booking™'),
    ('Tour2Bookingâ„¢', 'Tour2Booking™'),
    ('Tour2Bookingâ"¢', 'Tour2Booking™'),
    ('â€žÂ¢', '™'),
    ('â„¢', '™'),
    ('â"¢', '™'),
    # Degree
    ('Â°', '°'),
    # Middle dot
    ('Ã·', '·'),
    ('Â·', '·'),
    # Accented A
    ('Ã€', 'À'),
    ('Ã ', 'à '),
    # Right arrow (in REVIEW MY PACKAGE button)
    ('Ã†\u2019', '→'),
    ('Ã†â€™', '→'),
    ("Ã†'", '→'),
    # Various em/en dash corruptions
    ('â€"', '—'),
    ('â€"', '–'),
    ('â€™', "'"),
    ('â€œ', '"'),
    ('â€', '"'),
    # Checkmark in green banner
    ('âœ"', '✓'),
    ('âœ“', '✓'),
    # Broken tier emojis (specific 3-byte mojibake from Greek block)
    ('δï""', '@@TIER_ICON_1@@'),
    ('δï"', '@@TIER_ICON_1@@'),
    ('αš¡', '@@TIER_ICON_2@@'),
    ('αš', '@@TIER_ICON_2@@'),
    ('δŸ¦Ž†', '@@TIER_ICON_3@@'),
    ('δŸ¦Ž', '@@TIER_ICON_3@@'),
    ('δŸ', '@@TIER_ICON_3@@'),
]

for bad, good in mojibake_map:
    n = content.count(bad)
    if n > 0:
        content = content.replace(bad, good)
        print(f"  - {n}x  {repr(bad[:25])} -> {repr(good[:25])}")
        changes += n

# === Pass 3: Tier section icons via class context (replace placeholders + any remaining empty .tg-ico) ===
# Replace placeholders with correct SVG based on adjacent tier name
def inject_tier_svg(content_str):
    nonlocal_count = 0
    # For each placeholder, find the surrounding context to determine which tier
    placeholders_found = 0
    for placeholder, svg_set in [
        ('@@TIER_ICON_1@@', (SVG_LOCK, SVG_LOCK_PLUS, SVG_LOCK_CROWN)),
        ('@@TIER_ICON_2@@', (SVG_LOCK, SVG_LOCK_PLUS, SVG_LOCK_CROWN)),
        ('@@TIER_ICON_3@@', (SVG_LOCK, SVG_LOCK_PLUS, SVG_LOCK_CROWN)),
    ]:
        # Find each placeholder, look ahead ~200 chars to find tier name
        idx = 0
        while True:
            pos = content_str.find(placeholder, idx)
            if pos == -1:
                break
            window = content_str[pos:pos+300]
            if 'Starter Lock' in window:
                content_str = content_str[:pos] + SVG_LOCK + content_str[pos+len(placeholder):]
                placeholders_found += 1
            elif 'Growth Lock' in window:
                content_str = content_str[:pos] + SVG_LOCK_PLUS + content_str[pos+len(placeholder):]
                placeholders_found += 1
            elif 'Dominate Lock' in window:
                content_str = content_str[:pos] + SVG_LOCK_CROWN + content_str[pos+len(placeholder):]
                placeholders_found += 1
            else:
                # Default to lock if context unclear
                content_str = content_str[:pos] + SVG_LOCK + content_str[pos+len(placeholder):]
                placeholders_found += 1
            idx = pos + len(SVG_LOCK)
    return content_str, placeholders_found

content, tier_count = inject_tier_svg(content)
if tier_count > 0:
    print(f"  - {tier_count} tier section icons -> geometric lock SVGs")
    changes += tier_count

# Also handle empty <div class="tg-ico"></div> via context
tg_pattern = re.compile(
    r'(<div class="tg-ico">)\s*([^<]{0,8})\s*(</div>\s*<div class="tg-body">\s*<div class="tg-lbl">)(Starter Lock|Growth Lock|Dominate Lock)',
    re.DOTALL
)
def replace_tg(m):
    name = m.group(4)
    svg = SVG_LOCK if 'Starter' in name else (SVG_LOCK_PLUS if 'Growth' in name else SVG_LOCK_CROWN)
    return f'{m.group(1)}{svg}{m.group(3)}{name}'

tg_matches = len(tg_pattern.findall(content))
if tg_matches > 0:
    content = tg_pattern.sub(replace_tg, content)
    print(f"  - {tg_matches} .tg-ico containers cleaned/upgraded to lock SVGs")
    changes += tg_matches

# === Pass 4: Bullet checkmarks in .fc spans ===
pat_fc_empty = re.compile(r'<span class="fc">\s*</span>')
n_empty = len(pat_fc_empty.findall(content))
if n_empty > 0:
    content = pat_fc_empty.sub(f'<span class="fc">{SVG_CHECK}</span>', content)
    print(f"  - {n_empty} empty .fc spans -> SVG checkmark")
    changes += n_empty

pat_fc_dirty = re.compile(r'<span class="fc">[^<]{1,6}</span>')
n_dirty = len(pat_fc_dirty.findall(content))
if n_dirty > 0:
    content = pat_fc_dirty.sub(f'<span class="fc">{SVG_CHECK}</span>', content)
    print(f"  - {n_dirty} dirty .fc spans -> SVG checkmark")
    changes += n_dirty

# === Pass 5: Back button arrow ===
back_pat = re.compile(r'>([^<>]{0,4})\s*Back</button>')
n_back = len(back_pat.findall(content))
if n_back > 0:
    content = back_pat.sub(f'>{SVG_BACK_ARROW} Back</button>', content)
    print(f"  - {n_back} Back buttons -> SVG left-arrow")
    changes += n_back

# === Pass 6: Inject CSS (only once) — restore styles first, then add ===
for i, style in enumerate(styles):
    content = content.replace(f'@@STYLE_STASH_{i}@@', style)

if CSS_MARKER not in content:
    if '</style>' in content:
        content = content.replace('</style>', CSS_BLOCK + '\n</style>', 1)
        print(f"  - CSS icon system injected")
        changes += 1

# === Restore scripts UNTOUCHED (this is the critical safety step) ===
for i, script in enumerate(scripts):
    content = content.replace(f'@@SCRIPT_STASH_{i}@@', script)

# === Write file ===
if content != original:
    with open(PAGE, "w", encoding="utf-8", newline="") as f:
        f.write(content)
    print(f"\n  [DONE] Page 9 updated with {changes} total fixes")
    print(f"  [SAFE] JavaScript block stashed/restored untouched")
else:
    print("  [SKIP] No changes needed")

# === Verify critical functions still defined ===
print()
print("=" * 55)
print("  POST-PATCH JAVASCRIPT VERIFICATION")
print("=" * 55)
checks = ['function calcTotals', 'function selGF', 'function goNext', 'populatePrices']
all_ok = True
for fn in checks:
    present = fn in content
    status = "OK " if present else "MISSING"
    print(f"  [{status}] {fn}")
    if not present:
        all_ok = False
print()
if all_ok:
    print("  All JavaScript functions verified intact.")
else:
    print("  WARNING: Some functions missing - DO NOT push.")
print("=" * 55)
