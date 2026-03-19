with open('world/locations.py', 'rb') as f:
    lines = f.readlines()

# Check indentation from line 98 to 115
for i in range(97, 116):
    line = lines[i]
    spaces = len(line) - len(line.lstrip())
    print(f"Line {i+1}: {spaces} spaces: {line[:60].decode('utf-8', errors='ignore')}")