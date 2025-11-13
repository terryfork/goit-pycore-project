
class Note:

    def __init__(self, title: str, content: str, tags=None):
        self.title = title
        self.content = content
        self.tags = set(tags) if tags else set()

    def add_tag(self, tag: str):
        self.tags.add(tag)

    def remove_tag(self, tag: str):
        self.tags.discard(tag)
