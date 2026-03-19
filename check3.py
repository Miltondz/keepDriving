with open('world/locations.py', 'rb') as f:
    lines = f.readlines()

# Find where SETTLEMENTS is defined
for i in range(50, 70):
    line = lines[i]
    if b'SETTLEMENTS' in line:
        spaces = len(line) - len(line.lstrip())
        print(f"Line {i+1}: {spaces} spaces: {line[:60].decode('utf-8', errors='ignore')}")