import ftfy
import os
import glob

PAGES_DIR = os.path.join("public", "pages")
SKIP_FILES = {"rsd-funnel-page-02-qualify.html"}

pattern = os.path.join(PAGES_DIR, "rsd-funnel-page-*.html")
files = sorted(glob.glob(pattern))

print()
print("=" * 60)
print("  ftfy mojibake repair (skipping Page 2 per user request)")
print("=" * 60)
print()

total_changed = 0
total_files_changed = 0
skipped = 0

for filepath in files:
    filename = os.path.basename(filepath)

    if filename in SKIP_FILES:
        print(f"  [SKIP]  {filename:<48} (user excluded)")
        skipped += 1
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        original = f.read()

    fixed = ftfy.fix_text(original)

    if fixed != original:
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            f.write(fixed)
        diff = sum(1 for a, b in zip(original, fixed) if a != b)
        diff += abs(len(original) - len(fixed))
        print(f"  [FIXED] {filename:<48} ~{diff} chars repaired")
        total_changed += diff
        total_files_changed += 1
    else:
        print(f"  [CLEAN] {filename:<48} no mojibake found")

print()
print("=" * 60)
print(f"  Files changed: {total_files_changed}")
print(f"  Files skipped: {skipped}")
print(f"  Total repairs: ~{total_changed} characters")
print("=" * 60)
