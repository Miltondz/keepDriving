with open('world/locations.py', 'rb') as f:
    lines = f.readlines()

# Check class definitions
for i in range(0, 160):
    line = lines[i]
    stripped = line.decode('utf-8', errors='ignore').strip()
    if stripped.startswith('class ') or stripped.startswith('def '):
        spaces = len(line) - len(line.lstrip())
        print(f"Line {i+1}: {spaces} spaces: {stripped[:50]}")