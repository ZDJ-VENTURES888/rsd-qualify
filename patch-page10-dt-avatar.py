import re

PAGE = "public/pages/rsd-funnel-page-10-summary.html"

with open(PAGE, "r", encoding="utf-8") as f:
    content = f.read()

original = content
changes = 0

# --- 1. Add dt_avatar to D_PRICE ---
# Pattern: D_PRICE = {existing entries...}
# We add ",dt_avatar:9000" before the closing }
def add_to_table(content, table_name, entry, description):
    global changes
    # Find D_PRICE={...} or D_PRICE = {...}
    pattern = re.compile(rf'(\b{table_name}\s*=\s*\{{)([^}}]*)(\}})', re.DOTALL)
    
    def inject(m):
        opening = m.group(1)
        body = m.group(2)
        closing = m.group(3)
        
        # Check if entry already exists
        key = entry.split(':')[0].strip()
        if f"{key}:" in body:
            return m.group(0)  # already present, no change
        
        # Append the entry — append with leading comma if body isn't empty
        body_stripped = body.rstrip()
        if body_stripped.endswith(','):
            new_body = body_stripped + entry
        else:
            new_body = body_stripped + ',' + entry
        
        return opening + new_body + closing
    
    new_content = pattern.sub(inject, content, count=1)
    if new_content != content:
        print(f"  - {description}")
        changes += 1
    return new_content

content = add_to_table(content, 'D_PRICE', "dt_avatar:9000", "Added dt_avatar:9000 to D_PRICE")
content = add_to_table(content, 'D_TYPE',  "dt_avatar:'one'", "Added dt_avatar:'one' to D_TYPE")
content = add_to_table(content, 'D_NAME',  "dt_avatar:'RSD Digital Twin Avatar'", "Added dt_avatar:'RSD Digital Twin Avatar' to D_NAME")

# --- Write if changed ---
if content != original:
    with open(PAGE, "w", encoding="utf-8", newline="") as f:
        f.write(content)
    print(f"\n  [DONE] Page 10 patched with {changes} entries")
else:
    print("  [SKIP] No changes (dt_avatar may already be present)")

# --- Verify all three additions landed ---
print()
print("=" * 55)
print("  VERIFICATION")
print("=" * 55)

with open(PAGE, "r", encoding="utf-8") as f:
    final = f.read()

# Check D_PRICE
m = re.search(r"D_PRICE\s*=\s*\{([^}]*)\}", final, re.DOTALL)
if m:
    has_dt = "dt_avatar:9000" in m.group(1) or "dt_avatar: 9000" in m.group(1)
    print(f"  D_PRICE has dt_avatar:9000:           {'YES' if has_dt else 'NO'}")

m = re.search(r"D_TYPE\s*=\s*\{([^}]*)\}", final, re.DOTALL)
if m:
    has_dt = "dt_avatar:'one'" in m.group(1) or 'dt_avatar:"one"' in m.group(1)
    print(f"  D_TYPE has dt_avatar:'one':           {'YES' if has_dt else 'NO'}")

m = re.search(r"D_NAME\s*=\s*\{([^}]*)\}", final, re.DOTALL)
if m:
    has_dt = "dt_avatar:'RSD Digital Twin Avatar'" in m.group(1)
    print(f"  D_NAME has dt_avatar display label:   {'YES' if has_dt else 'NO'}")

# Verify all 14 critical functions still defined
print()
print("=" * 55)
print("  CRITICAL FUNCTION CHECK (must all be YES)")
print("=" * 55)
critical_fns = [
    'getState', 'buildSummary', 'renderTierBadge', 'buildQ', 'goBack',
    'resolveMonthlyItems', 'renderMonthlySupport', 'buildSuggestedNotes',
    'setupNotes', 'syncNotesPrint', 'printReport', 'copyNotes',
    'buildEmailParams', 'showError', 'clearError', 'markError', 'submitForm'
]
all_ok = True
for fn in critical_fns:
    present = f"function {fn}" in final
    status = "YES" if present else "NO "
    if not present: all_ok = False
    print(f"  [{status}] function {fn}")

print()
if all_ok:
    print("  All 17 critical functions verified intact.")
else:
    print("  WARNING: Some functions missing - DO NOT push.")
print("=" * 55)
