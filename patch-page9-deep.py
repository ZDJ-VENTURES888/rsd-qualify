import re
import sys

PAGE = "public/pages/rsd-funnel-page-09-lock-rate.html"

# Targeted replacements - byte-exact mojibake -> clean Unicode
# Order matters: longer sequences first to avoid partial matches
REPLACEMENTS = [
    # Trademark
    ('â„¢', '™'),
    ('â"¢', '™'),
    # Em-dash and en-dash (em-dash is more common in this funnel's body copy)
    ('â€"', '—'),
    # Right single quote
    ('â€™', "'"),
    # Left double quote
    ('â€œ', '"'),
    # Right double quote
    ('â€', '"'),
    # Ellipsis
    ('â€¦', '…'),
    # Degree sign
    ('Â°', '°'),
    # Middle dot
    ('Â·', '·'),
    # Non-breaking space (kept as space)
    ('Â\u00a0', '\u00a0'),
    # Cent
    ('Â¢', '¢'),
    # Accented uppercase A
    ('Ã€', 'À'),
    # Accented lowercase a
    ('Ã ', 'à'),
    # Accented e
    ('Ã©', 'é'),
    ('Ã¨', 'è'),
    # Right arrow
    ('Ã†\u2019', '→'),
    ("Ã†'", '→'),
    # Checkmark
    ('âœ"', '✓'),
    ('âœ"', '✓'),
    # Broken oe-ligature
    ('Å"', '"'),
    # Generic stray Â before non-mojibake chars
    ('Â ', ' '),
]

with open(PAGE, "r", encoding="utf-8") as f:
    original = f.read()

# === Apply replacements to entire file content ===
# These specific byte sequences only appear as corruption, never as legitimate code
# So global replacement is safe (won't break syntax)
content = original
total_replacements = 0
per_pattern = {}

for bad, good in REPLACEMENTS:
    count = content.count(bad)
    if count > 0:
        content = content.replace(bad, good)
        total_replacements += count
        per_pattern[bad] = (count, good)

# === Show what changed ===
if per_pattern:
    print("  Replacements applied:")
    for bad, (count, good) in sorted(per_pattern.items(), key=lambda x: -x[1][0]):
        bad_display = repr(bad)[:30]
        good_display = repr(good)[:15]
        print(f"    {count:>3}x  {bad_display:<32} -> {good_display}")
    print()

print(f"  Total replacements: {total_replacements}")

# === Verify critical functions still defined ===
print()
print("=" * 55)
print("  CRITICAL FUNCTION VERIFICATION")
print("=" * 55)
critical_fns = [
    'function getState',
    'function buildQ',
    'function calcTotals',
    'function fmtPrice',
    'function updCart',
    'function initGateState',
    'function populatePrices',
    'function applyCheckColors',
    'function renderPkgLock',
    'function selGF',
    'function flashTiers',
    'function goBack',
    'function goNext',
]

all_ok = True
for fn in critical_fns:
    present = fn in content
    status = "OK " if present else "MISSING"
    print(f"  [{status}] {fn}")
    if not present:
        all_ok = False

print()
if all_ok:
    print("  All 13 critical functions verified intact.")
    with open(PAGE, "w", encoding="utf-8", newline="") as f:
        f.write(content)
    print(f"  [WRITTEN] {total_replacements} fixes applied to Page 9")
else:
    print("  ERROR: Function missing - NOT writing file. Investigate before retry.")
    sys.exit(1)

# === Re-check mojibake count post-patch ===
print()
print("=" * 55)
print("  POST-PATCH MOJIBAKE CHECK")
print("=" * 55)

remaining = 0
for bad, good in REPLACEMENTS:
    n = content.count(bad)
    if n > 0:
        print(f"  Still present: {n}x {repr(bad)[:25]}")
        remaining += n

if remaining == 0:
    print("  Zero mojibake byte sequences remain in Page 9.")
else:
    print(f"  WARNING: {remaining} instances still present (may need additional patterns)")
