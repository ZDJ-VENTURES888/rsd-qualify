import os
import re
import glob

PAGES_DIR = os.path.join("public", "pages")
SKIP = {"rsd-funnel-page-02-qualify.html"}

# Patterns that are definitely mojibake (UTF-8 byte sequences interpreted as Latin-1)
MOJIBAKE_PATTERNS = [
    (r'â€"', 'em/en dash corruption'),
    (r'â€™', 'right single quote corruption'),
    (r'â€œ', 'left double quote corruption'),
    (r'â€', 'right double quote corruption'),
    (r'Ã€', 'A-grave corruption (À)'),
    (r'Ã ', 'a-grave corruption (à)'),
    (r'Â°', 'degree sign corruption (°)'),
    (r'Â·', 'middle dot corruption (·)'),
    (r'Â¢', 'cent sign corruption'),
    (r'â"¢', 'trademark corruption (™)'),
    (r'â„¢', 'trademark corruption alt (™)'),
    (r'âœ"', 'checkmark corruption (✓)'),
    (r'Ã†', 'AE-ligature corruption'),
    (r'â†', 'arrow corruption'),
    (r'â‡', 'double arrow corruption'),
    (r'Ã©', 'e-acute corruption (é)'),
    (r'Ã¨', 'e-grave corruption (è)'),
    (r'Ã³', 'o-acute corruption (ó)'),
    (r'Ã¼', 'u-umlaut corruption (ü)'),
    (r'δï', 'broken emoji sequence (δï)'),
    (r'δŸ', 'broken emoji sequence (δŸ)'),
    (r'αš', 'broken emoji sequence (αš)'),
    (r'@"', 'broken bullet in span'),
    (r'@\u201c', 'broken bullet variant'),
    (r'Å"', 'O-ligature corruption'),
    (r'â–º', 'play arrow corruption'),
    (r'â–²', 'up triangle corruption'),
    (r'â–¼', 'down triangle corruption'),
]

# Stash script/style blocks so we only audit visible markup
script_pattern = re.compile(r'<script[^>]*>.*?</script>', re.DOTALL)
style_pattern = re.compile(r'<style[^>]*>.*?</style>', re.DOTALL)

print()
print("=" * 70)
print("  MOJIBAKE AUDIT — visible HTML markup only (scripts/styles excluded)")
print("=" * 70)
print()

pattern = os.path.join(PAGES_DIR, "rsd-funnel-page-*.html")
total_per_page = {}

for filepath in sorted(glob.glob(pattern)):
    filename = os.path.basename(filepath)
    if filename in SKIP:
        print(f"  [SKIP]   {filename}")
        continue
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Strip scripts and styles for audit (don't change file - just analyze)
    markup_only = script_pattern.sub('', content)
    markup_only = style_pattern.sub('', markup_only)
    
    page_total = 0
    page_breakdown = []
    
    for pat, desc in MOJIBAKE_PATTERNS:
        count = len(re.findall(pat, markup_only))
        if count > 0:
            page_total += count
            page_breakdown.append((count, desc))
    
    # Empty .fc spans (would-be checkmarks)
    empty_fc = len(re.findall(r'<span class="fc">\s*</span>', markup_only))
    if empty_fc > 0:
        page_breakdown.append((empty_fc, 'empty .fc bullet spans'))
        page_total += empty_fc
    
    # Empty tg-ico containers
    empty_ico = len(re.findall(r'<div class="tg-ico">\s*</div>', markup_only))
    if empty_ico > 0:
        page_breakdown.append((empty_ico, 'empty .tg-ico containers'))
        page_total += empty_ico
    
    # Raw mojibake byte detection (catch-all)
    raw_mojibake = len(re.findall(r'[\u00C0-\u00FF][\u0080-\u00BF]', markup_only))
    if raw_mojibake > 0 and raw_mojibake > sum(c for c, _ in page_breakdown):
        extra = raw_mojibake - sum(c for c, d in page_breakdown if 'corruption' in d)
        if extra > 0:
            page_breakdown.append((extra, '(other mojibake byte pairs)'))
            page_total += extra
    
    total_per_page[filename] = page_total
    
    if page_total > 0:
        print(f"  [DIRTY] {filename:<48} {page_total} issues")
        for count, desc in sorted(page_breakdown, reverse=True):
            print(f"          - {count:>3}x  {desc}")
    else:
        print(f"  [CLEAN] {filename:<48} (no mojibake found)")

print()
print("=" * 70)
total_all = sum(total_per_page.values())
print(f"  TOTAL ISSUES ACROSS ALL PAGES: {total_all}")
print(f"  PAGES NEEDING REPAIR: {sum(1 for v in total_per_page.values() if v > 0)}")
print("=" * 70)
