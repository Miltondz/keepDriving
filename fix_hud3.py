import re

with open('ui/hud.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

lines = content.split('\n')
fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Fix: Line with "class HUD:" followed by "def __init__" needs proper indent
    if i < len(lines) - 1:
        next_line = lines[i + 1] if i + 1 < len(lines) else ""
        if line.strip() == 'class HUD:' and next_line.strip().startswith('def __init__'):
            fixed_lines.append(line)  # class HUD:
            # Add 4 spaces to __init__ line
            fixed_lines.append('    ' + next_line.lstrip())
            i += 2
            continue
    
    # Fix: Extra indentation at line that should be inside method
    # If we see a line with 12 spaces that should be inside a block with 8 spaces
    if line.startswith('            ') and not line.strip().startswith('#'):
        # This is the player avatar section inside render method
        # It should have 8 spaces (inside render method at 4 spaces)
        fixed_lines.append('        ' + line.lstrip())
        i += 1
        continue
        
    fixed_lines.append(line)
    i += 1

with open('ui/hud.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print("Fixed")