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

    def edit_note(self, title, new_content=None, new_tags=None):
        found_key = self._find_note_key(title)

        if not found_key:
            return f"Note '{title}' not found"

        note = self.notes[found_key]

        if new_content is not None:
            note['content'] = new_content

        if new_tags is not None:
            tags_list = [
                tag.strip() for tag in new_tags.split(',') if tag.strip()
            ]
            note['tags'] = tags_list

        note['modified'] = datetime.now().strftime(config.DATETIME_FORMAT)
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
