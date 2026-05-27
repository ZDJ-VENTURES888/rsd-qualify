import os
import re
import json
import glob

PAGES_DIR = os.path.join("public", "pages")
SKIP = {"rsd-funnel-page-02-qualify.html"}

# ============================================================
# CANONICAL PRICING — single source of truth
# This file gets written to public/pricing.js
# Every funnel page will import this instead of having local copies
# ============================================================

CANONICAL_PRICING_JS = """// ============================================================
// RSD Funnel — Canonical Pricing Tables
// Single source of truth. All funnel pages import from here.
// Edit prices ONLY in this file. Pages auto-pick up changes.
// ============================================================

// Package prices (one-time, base before any tier discount)
window.PKG_PRICE = {
  pkg_t2b: 5549,   // Tour2Booking
  pkg_ao:  6549,   // AlwaysOn Tour2Booking
  pkg_os:  9549    // AlwaysOn Digital Twin Conversion OS
};

// A la carte item prices
window.D_PRICE = {
  // Page 03 - Capture
  scan_base: 1299, scan_guided: 1799, vid_single: 500, vid_pack: 1200,
  drone_half: 350, drone_full: 600,
  vid_authority: 1800, vid_testimonial: 1800,
  photo_half: 400, photo_full: 800,
  lp_prem: 3500, lp_extra_page: 450,
  photo_1_3: 350, photo_6_9: 850, photo_9_12: 1300,
  photo_vol20: 2200, photo_21_30: 1995,
  // Page 04 - Web Presence
  seas_spring: 1850, seas_summer: 1850, seas_harvest: 2150,
  seas_winter: 1650, seas_annual: 6800, seas_extra: 1450,
  lp_base: 1800, lp_conv: 2800, lp_about: 500,
  vt_250: 0,
  // Page 04/05 additions
  ao_page: 1499, ao_ai_base: 1995, ao_ai_voice: 2495, ao_ai_full: 2995,
  // Page 06 - Social
  soc1: 750, soc2: 1500, soc3: 2250,
  ad_mgmt: 1495, ad_local: 995, ad_meta: 1295,
  // Page 07 - Rapid Response
  rr_basic: 495, rr_full: 995, rr_premium: 1495,
  // Page 08 - Digital Twin Avatar (added per user request)
  dt_avatar: 9000
};

// Item billing type: 'one' (one-time) or 'mo' (monthly recurring)
window.D_TYPE = {
  // One-time items
  scan_base: 'one', scan_guided: 'one', vid_single: 'one', vid_pack: 'one',
  drone_half: 'one', drone_full: 'one',
  vid_authority: 'one', vid_testimonial: 'one',
  photo_half: 'one', photo_full: 'one',
  lp_prem: 'one', lp_extra_page: 'one',
  photo_1_3: 'one', photo_6_9: 'one', photo_9_12: 'one',
  photo_vol20: 'one', photo_21_30: 'one',
  seas_spring: 'one', seas_summer: 'one', seas_harvest: 'one',
  seas_winter: 'one', seas_annual: 'one', seas_extra: 'one',
  lp_base: 'one', lp_conv: 'one', lp_about: 'one',
  vt_250: 'one',
  // Monthly recurring
  ao_page: 'mo', ao_ai_base: 'mo', ao_ai_voice: 'mo', ao_ai_full: 'mo',
  soc1: 'mo', soc2: 'mo', soc3: 'mo',
  ad_mgmt: 'mo', ad_local: 'mo', ad_meta: 'mo',
  rr_basic: 'mo', rr_full: 'mo', rr_premium: 'mo',
  // One-time (Digital Twin Avatar)
  dt_avatar: 'one'
};

// Founder lock tier discount rates
window.GF_DISC = {
  gf1: 0.05,   // Starter Lock: 5% off
  gf2: 0.10,   // Growth Lock: 10% off + priority fee
  gf3: 0.15    // Dominate Lock: 15% off
};

// Growth Lock one-time priority access fee
window.PRIORITY_FEE = 497;

console.log('[RSD] Pricing loaded:', Object.keys(window.D_PRICE).length, 'items');
"""

# Write canonical pricing file
os.makedirs("public", exist_ok=True)
with open("public/pricing.js", "w", encoding="utf-8", newline="\n") as f:
    f.write(CANONICAL_PRICING_JS)
print("  [WRITE] public/pricing.js (canonical pricing)")

# ============================================================
# AUDIT: walk all funnel pages
# ============================================================

# Stash patterns to separate JS/CSS from markup
script_pattern = re.compile(r'<script[^>]*>.*?</script>', re.DOTALL)
style_pattern = re.compile(r'<style[^>]*>.*?</style>', re.DOTALL)

# Critical functions every funnel page should have
CRITICAL_FUNCTIONS = ['getState', 'buildQ']
PAGE_SPECIFIC = {
    'rsd-funnel-page-09-lock-rate.html': ['calcTotals', 'selGF', 'goNext', 'populatePrices', 'fmtPrice', 'updCart'],
    'rsd-funnel-page-08-packages.html': ['selPkg', 'goNext'],
    'rsd-funnel-page-10-summary.html': ['calcTotals', 'goNext'],
}

# Premium-allowed Unicode characters (these are fine, not mojibake)
ALLOWED_UNICODE = set([
    '\u00a0',  # non-breaking space
    '\u2013',  # en-dash –
    '\u2014',  # em-dash —
    '\u2018', '\u2019',  # smart quotes ' '
    '\u201c', '\u201d',  # smart quotes " "
    '\u00b0',  # degree °
    '\u00b7',  # middle dot ·
    '\u00bd',  # 1/2
    '\u2122',  # trademark ™
    '\u00ae',  # registered ®
    '\u00a9',  # copyright ©
    '\u2713', '\u2714',  # checkmarks ✓ ✔
    '\u2192', '\u2190',  # arrows → ←
    '\u00e0', '\u00e1', '\u00e8', '\u00e9', '\u00ec', '\u00ed', '\u00f2', '\u00f3', '\u00f9', '\u00fa',  # accented lowercase
    '\u00c0', '\u00c1', '\u00c8', '\u00c9', '\u00cc', '\u00cd', '\u00d2', '\u00d3', '\u00d9', '\u00da',  # accented uppercase
    '\u00f1', '\u00d1',  # ñ Ñ
    '\u00fc', '\u00dc', '\u00f6', '\u00d6',  # umlauts
    '\u20ac',  # euro €
    '\u00a3', '\u00a5',  # £ ¥
])

# Mojibake byte sequences (UTF-8 read as Latin-1)
MOJIBAKE_INDICATORS = [
    'â€"', 'â€"', 'â€™', 'â€œ', 'â€', 'â€¦',
    'Ã€', 'Ã¡', 'Ã©', 'Ã¨', 'Ã³',
    'Â°', 'Â·', 'Â¢', 'Â£', 'Â¥', 'Â®',
    'â"¢', 'â„¢',
    'âœ"', 'âœ"',
    'Ã†', 'â†', 'â‡',
    'δï', 'δŸ', 'αš',
    '@"', '@"',
    'Å"', 'Å"',
]

print()
print("=" * 70)
print("  AUDIT REPORT")
print("=" * 70)
print()

audit = {}
pattern = os.path.join(PAGES_DIR, "rsd-funnel-page-*.html")

for filepath in sorted(glob.glob(pattern)):
    filename = os.path.basename(filepath)
    if filename in SKIP:
        print(f"  [SKIP]  {filename}")
        continue
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Stash JS/CSS so we audit only the markup
    markup = script_pattern.sub('', content)
    markup = style_pattern.sub('', markup)
    
    report = {
        'mojibake_count': 0,
        'mojibake_types': [],
        'empty_fc_spans': 0,
        'empty_tg_ico': 0,
        'missing_critical_fns': [],
        'has_pricing_js_import': '<script src="/pricing.js"' in content or '<script src="../pricing.js"' in content or '<script src="pricing.js"' in content,
        'has_local_pkg_price': 'PKG_PRICE' in content and 'window.PKG_PRICE' not in content,
        'has_local_d_price': 'D_PRICE' in content and 'window.D_PRICE' not in content,
        'has_dt_avatar': 'dt_avatar' in content,
    }
    
    # Count mojibake in markup
    for pattern_str in MOJIBAKE_INDICATORS:
        n = markup.count(pattern_str)
        if n > 0:
            report['mojibake_count'] += n
            report['mojibake_types'].append((n, pattern_str))
    
    # Count empty visual containers
    report['empty_fc_spans'] = len(re.findall(r'<span class="fc">\s*</span>', markup))
    report['empty_tg_ico'] = len(re.findall(r'<div class="tg-ico">\s*</div>', markup))
    
    # Check for critical functions (in full content, including scripts)
    expected_fns = CRITICAL_FUNCTIONS + PAGE_SPECIFIC.get(filename, [])
    for fn in expected_fns:
        if f'function {fn}' not in content and f'{fn}=' not in content and f'function populatePrices' not in content:
            # populatePrices is an IIFE check
            if fn == 'populatePrices' and 'populatePrices' in content:
                continue
            report['missing_critical_fns'].append(fn)
    
    audit[filename] = report
    
    # Print per-page summary
    has_issues = (report['mojibake_count'] > 0 or 
                  report['empty_fc_spans'] > 0 or 
                  report['empty_tg_ico'] > 0 or
                  len(report['missing_critical_fns']) > 0)
    
    status = "DIRTY" if has_issues else "CLEAN"
    color_indicator = "!" if has_issues else " "
    print(f"  [{status}]{color_indicator} {filename}")
    
    if report['mojibake_count'] > 0:
        print(f"          mojibake: {report['mojibake_count']} instances")
        for n, p in sorted(report['mojibake_types'], reverse=True)[:5]:
            print(f"            {n}x  {repr(p)}")
    
    if report['empty_fc_spans'] > 0:
        print(f"          empty .fc spans (need SVG checkmarks): {report['empty_fc_spans']}")
    
    if report['empty_tg_ico'] > 0:
        print(f"          empty .tg-ico (need lock icons): {report['empty_tg_ico']}")
    
    if report['missing_critical_fns']:
        print(f"          MISSING FUNCTIONS: {', '.join(report['missing_critical_fns'])}")
    
    if report['has_local_pkg_price']:
        print(f"          has local PKG_PRICE (should import from pricing.js)")
    
    if report['has_local_d_price']:
        print(f"          has local D_PRICE (should import from pricing.js)")
    
    if 'dt_avatar' in content and report['has_local_d_price']:
        # Check if dt_avatar is in their local D_PRICE
        if 'dt_avatar:' not in content and 'dt_avatar :' not in content:
            print(f"          local D_PRICE missing dt_avatar entry")

print()
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
total_mojibake = sum(r['mojibake_count'] for r in audit.values())
total_empty = sum(r['empty_fc_spans'] + r['empty_tg_ico'] for r in audit.values())
total_missing_fns = sum(len(r['missing_critical_fns']) for r in audit.values())
pages_with_local_pricing = sum(1 for r in audit.values() if r['has_local_pkg_price'] or r['has_local_d_price'])

print(f"  Total mojibake instances:      {total_mojibake}")
print(f"  Total empty visual containers: {total_empty}")
print(f"  Total missing functions:       {total_missing_fns}")
print(f"  Pages with local pricing:      {pages_with_local_pricing}")
print()
print("  Saving audit to: audit-results.json")

# Save machine-readable for Phase 2 to consume
with open("audit-results.json", "w") as f:
    json.dump(audit, f, indent=2, default=str)

print("=" * 70)
