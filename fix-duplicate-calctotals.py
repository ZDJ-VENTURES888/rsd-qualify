import re

PAGE = "public/pages/rsd-funnel-page-09-lock-rate.html"

with open(PAGE, "r", encoding="utf-8") as f:
    content = f.read()

# Remove my injected calcTotals (the multi-line version)
# It looks like: "\n// Calculate cart totals from URL state — restored\nfunction calcTotals(S){...}\n"
injected = """
// Calculate cart totals from URL state — restored
function calcTotals(S){
  let o = 0, m = 0;
  // Package price (one-time)
  if(S.pkg && PKG_PRICE[S.pkg]){
    o += PKG_PRICE[S.pkg];
  }
  // A la carte items
  if(S.items && S.items.length){
    for(const id of S.items){
      const price = D_PRICE[id];
      if(!price) continue;
      if(D_TYPE[id] === 'mo'){
        m += price;
      } else {
        o += price;
      }
    }
  }
  return {o: o, m: m};
}

"""

if injected in content:
    content = content.replace(injected, "")
    with open(PAGE, "w", encoding="utf-8", newline="") as f:
        f.write(content)
    print("  [DONE] Removed duplicate calcTotals injection")
else:
    print("  [SKIP] Injected version not found - searching for variant...")
    # Try regex match for any "Restored" comment followed by function
    pattern = re.compile(r'\n\s*// Calculate cart totals.*?return\s*\{o:\s*o,\s*m:\s*m\};\s*\}\s*\n', re.DOTALL)
    if pattern.search(content):
        content = pattern.sub("", content)
        with open(PAGE, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        print("  [DONE] Removed via regex variant")
    else:
        print("  [SKIP] No duplicate found - file may already be clean")

# Confirm only one calcTotals remains
matches = len(re.findall(r"function calcTotals", content))
print(f"\n  calcTotals function count: {matches}")
print(f"  Expected: 1")
