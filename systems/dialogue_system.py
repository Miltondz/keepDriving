"""Dialogue system for hitchhikers and NPCs."""

class DialogueLine:
    def __init__(self, speaker, text, next_id=None, avatar=None):
        self.speaker = speaker
        self.text = text
        self.next_id = next_id  # ID of the next line, or None to end
        self.avatar = avatar    # Avatar name for portraits

class DialogueTree:
    def __init__(self, lines):
        """lines: list of DialogueLine objects, first is starting node."""
        self.lines = {i: line for i, line in enumerate(lines)}
        self.current_id = 0
        self.active = True

    def current_line(self):
        return self.lines.get(self.current_id)

    def advance(self):
        """Move to the next line."""
        line = self.current_line()
        if line and line.next_id is not None:
            self.current_id = line.next_id
        else:
            self.active = False

class DialogueSystem:
    def __init__(self):
        self.active_tree = None  # tree instance or None

    def start(self, tree: DialogueTree):
        self.active_tree = tree

    def get_current(self):
        if self.active_tree and self.active_tree.active:
            return self.active_tree.current_line()
        return None

    def advance(self):
        if self.active_tree is not None:
            self.active_tree.advance()

    def is_active(self):
        return self.active_tree is not None and self.active_tree.active

    def clear(self):
        """Force clear any active dialogue."""
        if self.active_tree is not None:
            self.active_tree.active = False
        self.active_tree = None
