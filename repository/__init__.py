# contact_book/repository/__init__.py

from .contact_repository import ContactRepository
from .note_repository import NoteRepository

__all__ = ["ContactRepository", "NoteRepository"]
