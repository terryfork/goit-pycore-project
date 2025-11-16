import json
from pathlib import Path
from datetime import datetime
import config


class Notes:
    def __init__(self):
        self.storage_file = config.NOTES_STORAGE
        self.notes = self._load_from_file()
        self._migrate_notes()

    @staticmethod
    def title_validator(title):
        if not title or not title.strip():
            return False
        if len(title) > 100:
            return False
        return True

    @staticmethod
    def content_validator(content):
        if not content or not content.strip():
            return False
        return True

    @staticmethod
    def normalize_tags(tags_str):
        if not tags_str or not tags_str.strip():
            return []

        tags = []
        for part in tags_str.split(','):
            tags.extend(
                [tag.strip() for tag in part.split() if tag.strip()]
            )

        return [tag for tag in tags if tag and len(tag) <= 20]

    @staticmethod
    def tags_validator(tags_str):
        if not tags_str or not tags_str.strip():
            return True

        tags = Notes.normalize_tags(tags_str)
        return all(tag and len(tag) <= 20 for tag in tags)

    def _load_from_file(self):
        if Path(self.storage_file).exists():
            try:
                with open(
                    self.storage_file, 'r', encoding=config.FILE_ENCODING
                ) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_to_file(self):
        with open(
            self.storage_file, 'w', encoding=config.FILE_ENCODING
        ) as f:
            json.dump(
                self.notes, f,
                indent=config.JSON_INDENT,
                ensure_ascii=config.JSON_ENSURE_ASCII
            )

    def _migrate_notes(self):
        migrated = False
        for title, note in self.notes.items():
            if 'tags' not in note:
                note['tags'] = []
                migrated = True
        if migrated:
            self._save_to_file()

    def _find_note_key(self, title):
        title_lower = title.lower()
        for key in self.notes.keys():
            if key.lower() == title_lower:
                return key
        return None

    def add_note(self, title, content, tags=""):
        if title not in self.notes:
            tags_list = self.normalize_tags(tags)

            self.notes[title] = {
                "content": content,
                "created": datetime.now().strftime(config.DATETIME_FORMAT),
                "modified": datetime.now().strftime(config.DATETIME_FORMAT),
                "tags": tags_list
            }
            self._save_to_file()
            return "Note created successfully"
        else:
            return f"Note '{title}' already exists"

    def add_note_interactive(self, title):
        content = yield ("Enter note content: ")
        tags = yield (
            "Enter tags (separated by comma or space, "
            "or press Enter to skip): "
        )

        if not self.content_validator(content):
            return "Error: Invalid content format."

        if tags and not self.tags_validator(tags):
            msg = (
                "Error: Invalid tags format. "
                "Each tag must be <= 20 characters."
            )
            return msg

        return self.add_note(title, content, tags)

    def add_note_fully_interactive(self):
        title = yield ("Enter note title: ")
        if not self.title_validator(title):
            return "Error: Invalid title format."
        content = yield ("Enter note content: ")
        if not self.content_validator(content):
            return "Error: Invalid content format."
        tags = yield (
            "Enter tags (separated by comma or space, "
            "or press Enter to skip): "
        )
        if tags and not self.tags_validator(tags):
            return "Error: Invalid tags format."
        return self.add_note(title, content, tags)

    def edit_note_interactive(self, title):
        found_key = self._find_note_key(title)
        if not found_key:
            return f"Note '{title}' not found"

        note = self.notes[found_key]

        new_title = yield (
            f"Current title: {found_key}\n"
            "New title (press Enter to skip): "
        )
        new_title = new_title.strip() if new_title else ""
        if new_title and new_title != found_key:
            if not self.title_validator(new_title):
                return "Error: Invalid title format."
            if self._find_note_key(new_title):
                return f"Note '{new_title}' already exists"
        else:
            new_title = None

        new_content = yield (
            f"Current content: {note['content']}\n"
            "New content (press Enter to skip): "
        )
        new_content = new_content.strip() if new_content else ""
        if new_content:
            if not self.content_validator(new_content):
                return "Error: Invalid content format."
        else:
            new_content = None

        current_tags_str = (
            ", ".join(note.get('tags', []))
            if note.get('tags') else "none"
        )
        new_tags = yield (
            f"Current tags: {current_tags_str}\n"
            "New tags (comma or space separated, press Enter to skip): "
        )
        new_tags = new_tags.strip() if new_tags else ""
        if new_tags:
            if not self.tags_validator(new_tags):
                return "Error: Invalid tags format."
        else:
            new_tags = None

        return self.edit_note(found_key, new_title, new_content, new_tags)

    def edit_note_fully_interactive(self):
        title = yield ("Enter note title to edit: ")
        if not title or not title.strip():
            return "Error: Title cannot be empty."
        title = title.strip()

        found_key = self._find_note_key(title)
        if not found_key:
            return f"Note '{title}' not found"

        return (yield from self.edit_note_interactive(found_key))

    def add_note_from_command(self, params):
        if len(params) == 0:
            return self.add_note_fully_interactive()

        if len(params) == 1:
            if not self.title_validator(params[0]):
                return "Error: Invalid title format."
            return self.add_note_interactive(params[0])

        title = params[0]

        if not self.title_validator(title):
            msg = (
                "'add_note' command: add new note to notes\n"
                "Command usage: add_note [<title>] [<content>] [tags]\n"
                "Invalid fields: title"
            )
            return msg

        if len(params) == 3:
            content = params[1]
            tags = params[2]
        elif len(params) >= 3 and ',' in params[-1]:
            content = " ".join(params[1:-1])
            tags = params[-1]
        else:
            content = " ".join(params[1:])
            tags = ""

        if not self.content_validator(content):
            msg = (
                "'add_note' command: add new note to notes\n"
                "Command usage: add_note [<title>] [<content>] [tags]\n"
                "Invalid fields: content"
            )
            return msg

        if tags and not self.tags_validator(tags):
            msg = (
                "'add_note' command: add new note to notes\n"
                "Command usage: add_note [<title>] [<content>] [tags]\n"
                "Invalid fields: tags"
            )
            return msg

        return self.add_note(title, content, tags)

    def edit_note_from_command(self, params):
        if len(params) == 0:
            return self.edit_note_fully_interactive()

        if len(params) == 1:
            if not self.title_validator(params[0]):
                return "Error: Invalid title format."
            return self.edit_note_interactive(params[0])

        title = params[0]
        new_content = params[1] if len(params) > 1 else None
        new_tags = params[2] if len(params) > 2 else None

        if new_content is not None:
            if not self.content_validator(new_content):
                msg = (
                    "'edit_note' command: edit existing note\n"
                    "Command usage: edit_note [<title>] [new_content] "
                    "[new_tags]\n"
                    "Invalid fields: new_content"
                )
                return msg

        if new_tags is not None and not self.tags_validator(new_tags):
            msg = (
                "'edit_note' command: edit existing note\n"
                "Command usage: edit_note [<title>] [new_content] [new_tags]\n"
                "Invalid fields: new_tags"
            )
            return msg

        return self.edit_note(title, None, new_content, new_tags)

    def add_tags_from_command(self, params):
        if len(params) < 2:
            msg = (
                "'add_tags' command: add tags to note\n"
                "Command usage: add_tags <title> <tags>"
            )
            return msg

        title = params[0]
        tags_str = " ".join(params[1:])

        if not self.tags_validator(tags_str):
            msg = (
                "'add_tags' command: add tags to note\n"
                "Command usage: add_tags <title> <tags>\n"
                "Invalid fields: tags"
            )
            return msg

        return self.add_tags(title, tags_str)

    def remove_tags_from_command(self, params):
        if len(params) < 2:
            msg = (
                "'remove_tags' command: remove tags from note\n"
                "Command usage: remove_tags <title> <tags>"
            )
            return msg

        title = params[0]
        tags_str = " ".join(params[1:])

        return self.remove_tags(title, tags_str)

    def search_by_tags_from_command(self, params):
        if len(params) < 1:
            msg = (
                "'search_by_tags' command: search notes by multiple tags\n"
                "Command usage: search_by_tags <tags> [--all]"
            )
            return msg

        match_all = False
        tags_params = params

        if '--all' in params:
            match_all = True
            tags_params = [p for p in params if p != '--all']

        tags_str = " ".join(tags_params)

        return self.search_by_tags(tags_str, match_all)

    def get_note(self, title):
        found_key = self._find_note_key(title)

        if found_key:
            note = self.notes[found_key]
            if note.get('tags'):
                tags_str = ", ".join(note.get('tags', []))
            else:
                tags_str = "none"
            return (
                f"Title: {found_key}\n"
                f"Content: {note['content']}\n"
                f"Tags: {tags_str}\n"
                f"Created: {note['created']}\n"
                f"Modified: {note['modified']}"
            )
        else:
            return f"Note '{title}' not found"

    def edit_note(self, title, new_title=None, new_content=None, new_tags=None):
        found_key = self._find_note_key(title)

        if not found_key:
            return f"Note '{title}' not found"

        note = self.notes[found_key]

        if new_title is not None and new_title != found_key:
            if self._find_note_key(new_title):
                return f"Note '{new_title}' already exists"
            self.notes[new_title] = note.copy()
            del self.notes[found_key]
            found_key = new_title

        if new_content is not None:
            self.notes[found_key]['content'] = new_content

        if new_tags is not None:
            tags_list = self.normalize_tags(new_tags)
            self.notes[found_key]['tags'] = tags_list

        self.notes[found_key]['modified'] = (
            datetime.now().strftime(config.DATETIME_FORMAT)
        )
        self._save_to_file()
        return "Note updated successfully"

    def delete_note(self, title):
        found_key = self._find_note_key(title)

        if found_key:
            del self.notes[found_key]
            self._save_to_file()
            return "Note deleted successfully"
        else:
            return f"Note '{title}' not found"

    def add_tags(self, title, tags_str):
        found_key = self._find_note_key(title)

        if not found_key:
            return f"Note '{title}' not found"

        note = self.notes[found_key]
        new_tags = [
            tag.strip() for tag in tags_str.split(',') if tag.strip()
        ]

        existing_tags = set(note.get('tags', []))
        for tag in new_tags:
            existing_tags.add(tag)

        note['tags'] = list(existing_tags)
        note['modified'] = datetime.now().strftime(config.DATETIME_FORMAT)
        self._save_to_file()

        tags_display = ', '.join(note['tags'])
        return f"Tags updated. Current tags: {tags_display}"

    def remove_tags(self, title, tags_str):
        found_key = self._find_note_key(title)

        if not found_key:
            return f"Note '{title}' not found"

        note = self.notes[found_key]
        tags_to_remove = set(
            tag.strip() for tag in tags_str.split(',') if tag.strip()
        )

        current_tags = set(note.get('tags', []))
        current_tags -= tags_to_remove

        note['tags'] = list(current_tags)
        note['modified'] = datetime.now().strftime(config.DATETIME_FORMAT)
        self._save_to_file()

        tags_display = ', '.join(note['tags']) if note['tags'] else 'none'
        return f"Tags removed. Current tags: {tags_display}"

    def search_by_tag(self, tag):
        tag_lower = tag.lower()
        found_notes = []

        for title, note in self.notes.items():
            note_tags = [t.lower() for t in note.get('tags', [])]
            if tag_lower in note_tags:
                content_preview = note["content"][:50]
                if len(note["content"]) > 50:
                    content_preview += "..."
                found_notes.append(
                    (title, content_preview, note.get('tags', []))
                )

        if found_notes:
            result = (
                f"Found {len(found_notes)} note(s) with tag '{tag}':\n"
            )
            for title, preview, tags in found_notes:
                tags_str = ', '.join(tags) if tags else 'none'
                result += (
                    f"  - {title}: {preview}\n"
                    f"    Tags: {tags_str}\n"
                )
            return result
        else:
            return f"No notes found with tag '{tag}'"

    def search_by_tags(self, tags_str, match_all=False):
        search_tags = set(
            tag.strip().lower()
            for tag in tags_str.split(',') if tag.strip()
        )
        found_notes = []

        for title, note in self.notes.items():
            note_tags = set(t.lower() for t in note.get('tags', []))

            if match_all:
                if search_tags.issubset(note_tags):
                    found_notes.append((title, note))
            else:
                if search_tags & note_tags:
                    found_notes.append((title, note))

        if found_notes:
            match_type = "all" if match_all else "any"
            result = (
                f"Found {len(found_notes)} note(s) with {match_type} "
                f"tags '{tags_str}':\n"
            )
            for title, note in found_notes:
                content_preview = note["content"][:50]
                if len(note["content"]) > 50:
                    content_preview += "..."
                if note.get('tags'):
                    tags_str_display = ', '.join(note.get('tags', []))
                else:
                    tags_str_display = 'none'
                result += (
                    f"  - {title}: {content_preview}\n"
                    f"    Tags: {tags_str_display}\n"
                )
            return result
        else:
            return "No notes found with specified tags"

    def list_all_tags(self):
        tag_counts = {}

        for note in self.notes.values():
            for tag in note.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        if not tag_counts:
            return "No tags found"

        sorted_tags = sorted(tag_counts.items())

        result = "All tags:\n"
        for tag, count in sorted_tags:
            result += f"  - {tag} ({count})\n"

        return result

    def sort_by_tag(self, tag):
        tag_lower = tag.lower()
        found_notes = []

        for title, note in self.notes.items():
            note_tags = [t.lower() for t in note.get('tags', [])]
            if tag_lower in note_tags:
                found_notes.append((title, note))

        if not found_notes:
            return f"No notes found with tag '{tag}'"

        found_notes.sort(key=lambda x: x[1]['modified'], reverse=True)

        result = f"Notes with tag '{tag}' (sorted by date):\n"
        for title, note in found_notes:
            content_preview = note["content"][:50]
            if len(note["content"]) > 50:
                content_preview += "..."
            result += (
                f"  - {title} (modified: {note['modified']})\n"
                f"    {content_preview}\n"
            )

        return result

    def list_all_notes(self):
        if not self.notes:
            return "No notes found"

        note_list = "Your notes:\n"
        for title, note in self.notes.items():
            content_preview = note["content"][:50]
            if len(note["content"]) > 50:
                content_preview += "..."
            if note.get('tags'):
                tags_str = ', '.join(note.get('tags', []))
            else:
                tags_str = 'none'
            note_list += (
                f"  - {title}: {content_preview}\n"
                f"    Tags: {tags_str}\n"
            )
        return note_list
