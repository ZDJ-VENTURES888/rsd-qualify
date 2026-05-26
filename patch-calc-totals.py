import os
import re

PAGE = os.path.join("public", "pages", "rsd-funnel-page-09-lock-rate.html")

with open(PAGE, "r", encoding="utf-8") as f:
    content = f.read()

# The function to inject
CALC_TOTALS_FN = """
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

# Inject calcTotals BEFORE populatePrices IIFE
marker = "(function populatePrices()"
if marker in content:
    if "function calcTotals" in content:
        print("  [SKIP] calcTotals already exists")
    else:
        content = content.replace(marker, CALC_TOTALS_FN + marker, 1)
        with open(PAGE, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        print("  [DONE] calcTotals injected before populatePrices")
else:
    print("  [FAIL] Could not find populatePrices marker")
