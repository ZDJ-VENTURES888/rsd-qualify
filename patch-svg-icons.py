import os
import re
import glob

PAGES_DIR = os.path.join("public", "pages")
SKIP = {"rsd-funnel-page-02-qualify.html"}

# Inline SVG checkmark - gold by default, will turn green via CSS
SVG_CHECK = '<svg class="fc-svg" viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="3,8.5 7,12.5 13,4.5"></polyline></svg>'

# SVG icons for section markers
SVG_SHIELD = '<svg class="sec-ico" viewBox="0 0 20 20" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><path d="M10 2 L17 5 V10 C17 14 13.5 17 10 18 C6.5 17 3 14 3 10 V5 Z"></path><polyline points="7,10 9.5,12.5 13.5,8"></polyline></svg>'
SVG_BOLT = '<svg class="sec-ico" viewBox="0 0 20 20" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true"><polygon points="11,2 4,11 9.5,11 8,18 16,8 10.5,8 12,2"></polygon></svg>'
SVG_LOCK = '<svg class="sec-ico" viewBox="0 0 20 20" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4.5" y="9" width="11" height="8" rx="1.2"></rect><path d="M7 9 V6.5 A3 3 0 0 1 13 6.5 V9"></path></svg>'

# CSS to add (idempotent - only added once per file)
CSS_BLOCK = """
/* === RSD SVG Icon System (added by patch) === */
.fc-svg{display:inline-block;vertical-align:-2px;margin-right:8px;color:var(--gold);transition:color .35s ease,filter .35s ease,transform .35s ease;flex-shrink:0}
.tier.act .fc-svg,.tier.selected .fc-svg,.tier:hover .fc-svg{color:var(--grn);filter:drop-shadow(0 0 4px rgba(92,184,92,.55))}
.tier.act .fc-svg{transform:scale(1.08)}
.sec-ico{display:inline-block;vertical-align:-3px;margin-right:10px;color:var(--gold)}
.sec-ico-shield{color:var(--grn)}
.tg-ico .sec-ico{margin-right:0}
/* Cascade animation when tier becomes active */
@keyframes fcCascade{0%{color:var(--gold);transform:scale(1)}50%{color:#7fd97f;transform:scale(1.15);filter:drop-shadow(0 0 6px rgba(92,184,92,.7))}100%{color:var(--grn);transform:scale(1.08);filter:drop-shadow(0 0 4px rgba(92,184,92,.55))}}
.tier.act .fc-svg{animation:fcCascade .6s ease-out forwards}
.tier.act li:nth-child(1) .fc-svg{animation-delay:0s}
.tier.act li:nth-child(2) .fc-svg{animation-delay:.08s}
.tier.act li:nth-child(3) .fc-svg{animation-delay:.16s}
.tier.act li:nth-child(4) .fc-svg{animation-delay:.24s}
.tier.act li:nth-child(5) .fc-svg{animation-delay:.32s}
.tier.act li:nth-child(6) .fc-svg{animation-delay:.40s}
.tier.act li:nth-child(7) .fc-svg{animation-delay:.48s}
"""

CSS_MARKER = "/* === RSD SVG Icon System (added by patch) === */"

# What to look for in markup and how to replace it
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
    
    # 1. Replace empty <span class="fc"></span> with SVG checkmark
    pattern_fc_empty = re.compile(r'<span class="fc">\s*</span>')
    matches = len(pattern_fc_empty.findall(content))
    if matches > 0:
        content = pattern_fc_empty.sub(f'<span class="fc">{SVG_CHECK}</span>', content)
        file_changes += matches
        print(f"    - {matches} empty .fc spans -> SVG checkmark")
    
    # 2. Handle .fc spans that still have garbage character in them
    pattern_fc_dirty = re.compile(r'<span class="fc">[^<]{1,3}</span>')
    matches = len(pattern_fc_dirty.findall(content))
    if matches > 0:
        content = pattern_fc_dirty.sub(f'<span class="fc">{SVG_CHECK}</span>', content)
        file_changes += matches
        print(f"    - {matches} dirty .fc spans -> SVG checkmark")
    
    # 3. Empty .tg-ico containers (section icons)
    pattern_ico_empty = re.compile(r'<div class="tg-ico">\s*</div>')
    matches = len(pattern_ico_empty.findall(content))
    if matches > 0:
        # Default to bolt (most common - "speed" / "prosperity" type)
        content = pattern_ico_empty.sub(f'<div class="tg-ico">{SVG_BOLT}</div>', content)
        file_changes += matches
        print(f"    - {matches} empty .tg-ico -> bolt SVG")
    
    # 4. Dirty .tg-ico containers  
    pattern_ico_dirty = re.compile(r'<div class="tg-ico">[^<]{1,5}</div>')
    matches = len(pattern_ico_dirty.findall(content))
    if matches > 0:
        content = pattern_ico_dirty.sub(f'<div class="tg-ico">{SVG_BOLT}</div>', content)
        file_changes += matches
        print(f"    - {matches} dirty .tg-ico -> bolt SVG")
    
    # 5. Context-aware: shield for guarantee sections
    content = content.replace(
        f'<div class="tg-ico">{SVG_BOLT}</div>\n        <div class="tg-body">\n          <div class="tg-lbl">You\'re Guarantee Qualified',
        f'<div class="tg-ico">{SVG_SHIELD}</div>\n        <div class="tg-body">\n          <div class="tg-lbl">You\'re Guarantee Qualified'
    )
    
    # 6. Add CSS block if not already present
    if CSS_MARKER not in content and file_changes > 0:
        # Insert before closing </style>
        if "</style>" in content:
            content = content.replace("</style>", CSS_BLOCK + "\n</style>", 1)
            print(f"    - CSS block injected")
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
