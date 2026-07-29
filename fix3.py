#!/usr/bin/env python3
"""Remove ALL white backgrounds from a draw.io SVG, every variant."""
import html, re

filepath = '/home/rs/Development/hal-architecture/hal-architecture.svg'

with open(filepath) as f:
    c = f.read()

# --- mxGraphModel ---
start = c.index('content="') + len('content="')
end = start
while True:
    end = c.index('"', end + 1)
    rest = c[end+1:end+50].strip()
    if rest.startswith('>'):
        break

model = html.unescape(c[start:end])
removed = 0
for pat in ['labelBackgroundColor=#ffffff;', ';labelBackgroundColor=#ffffff', 'labelBackgroundColor=#ffffff']:
    removed += model.count(pat)
    model = model.replace(pat, '')
print(f'mxGraphModel: removed {removed} labelBackgroundColor=#ffffff')

c = c[:start] + html.escape(model, quote=True) + c[end:]

# --- SVG body ---
switch_match = re.search(r'</switch>\s*(.*)</svg>', c, re.DOTALL)
if switch_match:
    body = switch_match.group(1)

    def count_all(s):
        return {
            'plain': len(re.findall(r'background-color:\s*#ffffff', s, re.IGNORECASE)),
            'light-dark': len(re.findall(r'background-color:\s*light-dark\(\s*#ffffff', s, re.IGNORECASE)),
            'var': len(re.findall(r'background-color:\s*var\(--ge-adaptive-bg,\s*#ffffff\)', s, re.IGNORECASE)),
        }

    before = count_all(body)

    # Remove all three variants in one pass
    body = re.sub(r'background-color:\s*#ffffff\s*;?\s*', '', body, flags=re.IGNORECASE)
    body = re.sub(r'background-color:\s*light-dark\(\s*#ffffff\s*,\s*#121212\s*\)\s*;?\s*', '', body, flags=re.IGNORECASE)
    body = re.sub(r'background-color:\s*var\(--ge-adaptive-bg,\s*#ffffff\)\s*;?\s*', '', body, flags=re.IGNORECASE)

    # Clean up double semicolons and trailing semicolons before closing quote
    body = re.sub(r';\s*;', ';', body)
    body = re.sub(r';\s*"', '"', body)

    after = count_all(body)

    print(f"SVG plain #ffffff:     {before['plain']} -> {after['plain']} (removed {before['plain'] - after['plain']})")
    print(f"SVG light-dark:        {before['light-dark']} -> {after['light-dark']} (removed {before['light-dark'] - after['light-dark']})")
    print(f"SVG var(--ge-adaptive): {before['var']} -> {after['var']} (removed {before['var'] - after['var']})")

    c = c.replace(switch_match.group(1), body)

with open(filepath, 'w') as f:
    f.write(c)

# Final sweep
total = sum(count_all(switch_match.group(1)).values()) if switch_match else 0
print(f'\nTotal white backgrounds remaining: {total}')
print('All clean!' if total == 0 else 'Still some left!')
