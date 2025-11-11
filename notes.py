import json
from pathlib import Path
from datetime import datetime
import config

def notes_keeper():
    STORAGE_FILE = config.NOTES_STORAGE

    def _load_from_file():
        if Path(STORAGE_FILE).exists():
            try:
                with open(STORAGE_FILE, 'r', encoding=config.FILE_ENCODING) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    notes = _load_from_file()
    
    def _save_to_file():
        nonlocal notes
        with open(STORAGE_FILE, 'w', encoding=config.FILE_ENCODING) as f:
            json.dump(notes, f, indent=config.JSON_INDENT, ensure_ascii=config.JSON_ENSURE_ASCII)
    
    def add_note(title, content):
        nonlocal notes
        if title not in notes:
            notes[title] = {
                "content": content,
                "created": datetime.now().strftime(config.DATETIME_FORMAT),
                "modified": datetime.now().strftime(config.DATETIME_FORMAT)
            }
            _save_to_file()
            return "Note created successfully"
        else:
            return f"Note '{title}' already exists"
    
    def get_note(title):
        title_lower = title.lower()
        found_key = None
        for key in notes.keys():
            if key.lower() == title_lower:
                found_key = key
                break
        
        if found_key:
            note = notes[found_key]
            return f"Title: {found_key}\nContent: {note['content']}\nCreated: {note['created']}\nModified: {note['modified']}"
        else:
            return f"Note '{title}' not found"
    
    def list_all_notes():
        if not notes:
            return "No notes found"
        
        note_list = "Your notes:\n"
        for title, note in notes.items():
            content_preview = note["content"][:50]
            if len(note["content"]) > 50:
                content_preview += "..."
            note_list += f"  - {title}: {content_preview}\n"
        return note_list
    
    return add_note, get_note, list_all_notes

add_note, get_note, list_all_notes = notes_keeper()

