with open('world/locations.py', 'rb') as f:
    lines = f.readlines()

# Check indentation around RoadSegment class
for i in range(68, 75):
    line = lines[i]
    spaces = len(line) - len(line.lstrip())
    print(f"Line {i+1}: {spaces} spaces: {line[:60].decode('utf-8', errors='ignore')}")