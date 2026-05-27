import os
import re
import glob

PAGES_DIR = os.path.join("public", "pages")
SKIP = {"rsd-funnel-page-02-qualify.html"}

# Mojibake byte sequences we expect to find (UTF-8 read as Latin-1 / Windows-1252)
MOJIBAKE_PATTERNS = [
    # Em/en dashes
    ('\u00e2\u20ac\u201d', 'em-dash (—)'),
    ('\u00e2\u20ac\u201c', 'en-dash (–)'),
    # Quotes / apostrophes
    ('\u00e2\u20ac\u2122', 'right single quote (\')'),
    ('\u00e2\u20ac\u0153', 'left double quote (")'),
    ('\u00e2\u20ac\u009d', 'right double quote (")'),
    ('\u00e2\u20ac\u009c', 'left double quote alt'),
    ('\u00e2\u20ac\u00a6', 'ellipsis (…)'),
    # Symbols
    ('\u00c2\u00b0', 'degree sign (°)'),
    ('\u00c2\u00b7', 'middle dot (·)'),
    ('\u00c2\u00a0', 'non-breaking space'),
    ('\u00c2\u00a2', 'cent sign (¢)'),
    # Trademark
    ('\u00e2\u201e\u00a2', 'trademark (™)'),
    ('\u00e2\u20ac\u017e\u00a2', 'trademark alt'),
    # Checkmarks
    ('\u00e2\u0153\u201c', 'checkmark (✓)'),
    ('\u00e2\u0153\u201d', 'checkmark alt'),
    # Arrows
    ('\u00e2\u2020\u2019', 'right arrow (→)'),
    ('\u00e2\u2020\u2018', 'left arrow (←)'),
    # Accented characters
    ('\u00c3\u20ac', 'A-grave (À)'),
    ('\u00c3\u00a0', 'a-grave (à)'),
    ('\u00c3\u00a9', 'e-acute (é)'),
    ('\u00c3\u00a8', 'e-grave (è)'),
    # Broken emoji sequences (3-byte UTF-8 read as 3 Latin-1 chars)
    ('\u00ce\u00b4\u00c3\u00af', 'broken emoji δï'),
    ('\u00ce\u00b4\u00c5\u00b8', 'broken emoji δŸ'),
    ('\u00ce\u00b1\u00c5\u00a1', 'broken emoji αš'),
]

# Simpler form using the actual mojibake byte strings as we'd type them
SIMPLE_PATTERNS = [
    ('â€"', 'em-dash'),
    ('â€"', 'en-dash'),
    ('â€™', 'right single quote'),
    ('â€œ', 'left double quote'),
    ('â€', 'right double quote'),
    ('â€¦', 'ellipsis'),
    ('Â°', 'degree sign'),
    ('Â·', 'middle dot'),
    ('Â¢', 'cent sign'),
    ('â„¢', 'trademark (™) alt-1'),
    ('â"¢', 'trademark (™) alt-2'),
    ('âœ"', 'checkmark (✓)'),
    ('Ã†\u2019', 'right arrow (→)'),
    ('Ã€', 'A-grave (À)'),
    ('Ã ', 'a-grave (à)'),
    ('Ã©', 'e-acute (é)'),
    ('Å"', 'broken oe-ligature'),
    ('δï', 'broken emoji δï'),
    ('δŸ', 'broken emoji δŸ'),
    ('αš', 'broken emoji αš'),
]

print()
print("=" * 75)
print("  DEEP AUDIT — mojibake in JavaScript strings + comments + markup")
print("=" * 75)
print()

# Regex to extract JS string content from <script> blocks
# Captures: contents between backticks, double-quotes, single-quotes, and // comments
script_block_re = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL)

def extract_js_strings_and_comments(js_code):
    """Extract content from string literals (all 3 types) and line comments."""
    extracted = []
    
    # Template literals: `...`
    for m in re.finditer(r'`([^`]*)`', js_code, re.DOTALL):
        extracted.append(('template', m.group(1)))
    
    # Double-quoted strings: "..."
    for m in re.finditer(r'"((?:[^"\\]|\\.)*)"', js_code):
        extracted.append(('dquote', m.group(1)))
    
    # Single-quoted strings: '...'
    for m in re.finditer(r"'((?:[^'\\]|\\.)*)'", js_code):
        extracted.append(('squote', m.group(1)))
    
    # Line comments: // ...
    for m in re.finditer(r'//([^\n]*)', js_code):
        extracted.append(('comment', m.group(1)))
    
    return extracted

total_per_page = {}
grand_total = 0
pages_dirty = 0

pattern = os.path.join(PAGES_DIR, "rsd-funnel-page-*.html")
for filepath in sorted(glob.glob(pattern)):
    filename = os.path.basename(filepath)
    if filename in SKIP:
        print(f"  [SKIP]    {filename}")
        continue
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # --- Section 1: Count mojibake in JS script content ---
    script_mojibake = {}
    for script_match in script_block_re.finditer(content):
        js = script_match.group(1)
        strings = extract_js_strings_and_comments(js)
        for kind, text in strings:
            for bad, desc in SIMPLE_PATTERNS:
                n = text.count(bad)
                if n > 0:
                    key = f"{desc} (in JS {kind})"
                    script_mojibake[key] = script_mojibake.get(key, 0) + n
    
    # --- Section 2: Count mojibake in markup (outside scripts and styles) ---
    markup = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    markup = re.sub(r'<style[^>]*>.*?</style>', '', markup, flags=re.DOTALL)
    
    markup_mojibake = {}
    for bad, desc in SIMPLE_PATTERNS:
        n = markup.count(bad)
        if n > 0:
            key = f"{desc} (in markup)"
            markup_mojibake[key] = markup_mojibake.get(key, 0) + n
    
    # --- Section 3: Count mojibake in CSS (style blocks) ---
    css_mojibake = {}
    for style_match in re.finditer(r'<style[^>]*>(.*?)</style>', content, re.DOTALL):
        css = style_match.group(1)
        for bad, desc in SIMPLE_PATTERNS:
            n = css.count(bad)
            if n > 0:
                key = f"{desc} (in CSS)"
                css_mojibake[key] = css_mojibake.get(key, 0) + n
    
    # --- Combine and report ---
    all_findings = {}
    all_findings.update(script_mojibake)
    all_findings.update(markup_mojibake)
    all_findings.update(css_mojibake)
    
    page_total = sum(all_findings.values())
    total_per_page[filename] = page_total
    
    if page_total > 0:
        print(f"  [DIRTY]   {filename}   ({page_total} instances)")
        for key in sorted(all_findings.keys(), key=lambda k: -all_findings[k]):
            print(f"            {all_findings[key]:>3}x  {key}")
        pages_dirty += 1
        grand_total += page_total
    else:
        print(f"  [CLEAN]   {filename}")

print()
print("=" * 75)
print(f"  GRAND TOTAL: {grand_total} mojibake instances across {pages_dirty} dirty pages")
print("=" * 75)
print()
print("  This audit checked:")
print("    - HTML markup (visible page content)")
print("    - JavaScript string literals (template, double-quote, single-quote)")
print("    - JavaScript line comments")
print("    - CSS style content")
print()
print("  Phase 2 will patch JS strings/comments + markup + CSS using ftfy + targeted map")
print("  All function definitions will be verified intact before write.")
