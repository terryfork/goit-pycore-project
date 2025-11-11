import json
from pathlib import Path
from datetime import datetime
import config

class Notes:
    def __init__(self):
        self.storage_file = config.NOTES_STORAGE
        self.notes = self._load_from_file()
    
    def _load_from_file(self):
        if Path(self.storage_file).exists():
            try:
                with open(self.storage_file, 'r', encoding=config.FILE_ENCODING) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def _save_to_file(self):
        with open(self.storage_file, 'w', encoding=config.FILE_ENCODING) as f:
            json.dump(self.notes, f, indent=config.JSON_INDENT, ensure_ascii=config.JSON_ENSURE_ASCII)
    
    def add_note(self, title, content):
        if title not in self.notes:
            self.notes[title] = {
                "content": content,
                "created": datetime.now().strftime(config.DATETIME_FORMAT),
                "modified": datetime.now().strftime(config.DATETIME_FORMAT)
            }
            self._save_to_file()
            return "Note created successfully"
        else:
            return f"Note '{title}' already exists"
    
    def get_note(self, title):
        title_lower = title.lower()
        found_key = None
        for key in self.notes.keys():
            if key.lower() == title_lower:
                found_key = key
                break
        
        if found_key:
            note = self.notes[found_key]
            return f"Title: {found_key}\nContent: {note['content']}\nCreated: {note['created']}\nModified: {note['modified']}"
        else:
            return f"Note '{title}' not found"
    
    def list_all_notes(self):
        if not self.notes:
            return "No notes found"
        
        note_list = "Your notes:\n"
        for title, note in self.notes.items():
            content_preview = note["content"][:50]
            if len(note["content"]) > 50:
                content_preview += "..."
            note_list += f"  - {title}: {content_preview}\n"
        return note_list
