import os
import re

PAGE = "public/pages/rsd-funnel-page-09-lock-rate.html"

with open(PAGE, "r", encoding="utf-8") as f:
    content = f.read()

# Inline SVG checkmark for .fc bullets
SVG_CHECK = '<svg class="fc-svg" viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="3,8.5 7,12.5 13,4.5"></polyline></svg>'

# SVG icons for section tier markers (in "What each tier means")
SVG_ASTRONAUT = '<svg class="tier-ico" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="8"></circle><path d="M7 11 Q12 8 17 11"></path><circle cx="9.5" cy="11" r="0.6" fill="currentColor"></circle><line x1="12" y1="4" x2="12" y2="2"></line><circle cx="12" cy="2" r="0.8" fill="currentColor"></circle></svg>'
SVG_ROCKET = '<svg class="tier-ico" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><path d="M12 2 C14 5 15 9 15 13 V17 H9 V13 C9 9 10 5 12 2 Z"></path><circle cx="12" cy="11" r="1.2"></circle><path d="M9 15 L7 18 L9 17"></path><path d="M15 15 L17 18 L15 17"></path><path d="M11 18 L11 21 M13 18 L13 21 M12 18 L12 22"></path></svg>'
SVG_LAUNCHPAD = '<svg class="tier-ico" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" aria-hidden="true"><path d="M12 3 C13.5 5.5 14 8 14 11 V14 H10 V11 C10 8 10.5 5.5 12 3 Z"></path><circle cx="12" cy="9" r="0.8" fill="currentColor"></circle><path d="M10 12 L8 14 L10 13.5"></path><path d="M14 12 L16 14 L14 13.5"></path><path d="M6 18 L8 14 M18 18 L16 14"></path><line x1="4" y1="18" x2="20" y2="18"></line><line x1="6" y1="21" x2="18" y2="21"></line><path d="M11 14 L11 17 M13 14 L13 17"></path></svg>'
SVG_BACK_ARROW = '<svg class="back-ico" viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9.5,3.5 4.5,8 9.5,12.5"></polyline><line x1="4.5" y1="8" x2="12" y2="8"></line></svg>'

CSS_BLOCK = """
/* === RSD Icon System (Page 9 cosmetic patch) === */
.fc-svg{display:inline-block;vertical-align:-2px;margin-right:8px;color:var(--gold);transition:color .35s ease,filter .35s ease,transform .35s ease;flex-shrink:0}
.tier.sel .fc-svg{color:var(--grn);filter:drop-shadow(0 0 4px rgba(92,184,92,.55))}
.tier-ico{display:inline-block;vertical-align:-4px;margin-right:8px;color:var(--gold)}
.back-ico{display:inline-block;vertical-align:-1px;margin-right:6px;color:currentColor}
"""

CSS_MARKER = "/* === RSD Icon System (Page 9 cosmetic patch) === */"

# SAFETY: Extract the <script>...</script> block, save it, and operate only on HTML around it
script_pattern = re.compile(r'(<script[^>]*>)(.*?)(</script>)', re.DOTALL)
scripts = []
def stash(m):
    scripts.append(m.group(0))
    return f'@@SCRIPT_STASH_{len(scripts)-1}@@'
content_safe = script_pattern.sub(stash, content)

changes = 0

# 1. Empty <span class="fc"></span> -> SVG checkmark
pat1 = re.compile(r'<span class="fc">\s*</span>')
n1 = len(pat1.findall(content_safe))
if n1: 
    content_safe = pat1.sub(f'<span class="fc">{SVG_CHECK}</span>', content_safe)
    changes += n1
    print(f"  - {n1} empty .fc spans -> SVG checkmark")

# 2. Dirty <span class="fc">JUNK</span> -> SVG checkmark
pat2 = re.compile(r'<span class="fc">[^<]{1,6}</span>')
n2 = len(pat2.findall(content_safe))
if n2:
    content_safe = pat2.sub(f'<span class="fc">{SVG_CHECK}</span>', content_safe)
    changes += n2
    print(f"  - {n2} dirty .fc spans -> SVG checkmark")

# 3. Tier section icons in "What each tier actually means"
tier_pat = re.compile(
    r'(<div class="tg-ico">)([^<]{0,8})(</div>\s*<div class="tg-body">\s*<div class="tg-lbl">)(Starter Lock|Growth Lock|Dominate Lock)',
    re.DOTALL
)
def rep_tier(m):
    name = m.group(4)
    svg = SVG_ASTRONAUT if 'Starter' in name else (SVG_ROCKET if 'Growth' in name else SVG_LAUNCHPAD)
    return f'{m.group(1)}{svg}{m.group(3)}{name}'

n3 = len(tier_pat.findall(content_safe))
if n3:
    content_safe = tier_pat.sub(rep_tier, content_safe)
    changes += n3
    print(f"  - {n3} tier section icons -> astronaut/rocket/launchpad SVG")

# 4. Back button: replace any junk char before " Back</button>"
back_pat = re.compile(r'>([^<>]{0,4})\s*Back</button>')
n4 = len(back_pat.findall(content_safe))
if n4:
    content_safe = back_pat.sub(f'>{SVG_BACK_ARROW} Back</button>', content_safe)
    changes += n4
    print(f"  - {n4} Back buttons -> SVG arrow")

# 5. Clean common visible-text mojibake (safe, HTML-only)
mojibake_map = {
    'Tour2Bookingâ"¢': 'Tour2Booking™',
    'Tour2Bookingâ„¢': 'Tour2Booking™',
    '360Â°': '360°',
    'â€"': '—',
    'â€"': '–',
    'â€™': "'",
    'â€œ': '"',
    'â€': '"',
    '3â€"9 min': '3–9 min',
    '2â€"3 weeks': '2–3 weeks',
    '90â€"120s': '90–120s',
    '3â€"4 weeks': '3–4 weeks',
    '5Â%': '5%',
    'lockedâ€"': 'locked—',
    'â€"  Rate locked': '—  Rate locked',
    'youâ€™re': 'you\'re',
}
for bad, good in mojibake_map.items():
    n = content_safe.count(bad)
    if n:
        content_safe = content_safe.replace(bad, good)
        changes += n
        print(f"  - {n}x replaced {bad[:20]!r} -> {good[:20]!r}")

# 6. Inject CSS if not present
if CSS_MARKER not in content_safe and changes > 0:
    if '</style>' in content_safe:
        content_safe = content_safe.replace('</style>', CSS_BLOCK + '\n</style>', 1)
        changes += 1
        print(f"  - CSS block injected")

# Restore script blocks UNTOUCHED
for i, script in enumerate(scripts):
    content_safe = content_safe.replace(f'@@SCRIPT_STASH_{i}@@', script)

# Write only if changed
if content_safe != content:
    with open(PAGE, "w", encoding="utf-8", newline="") as f:
        f.write(content_safe)
    print(f"\n  [DONE] Page 9 updated with {changes} cosmetic fixes")
    print(f"  [SAFE] JavaScript block was stashed and restored untouched")
else:
    print("  [SKIP] No changes needed")
