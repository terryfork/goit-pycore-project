from contactbook import Contactbook
from notes import Notes
from Levenshtein import distance
from colorama import Fore, Style


class BotCommands():

    done = False

    def __init__(self):
        self.notes = Notes()
        self.contactbook = Contactbook()

    def input_validator(func):
        def inner(self, params):
            command = func.__name__.removesuffix('_handler')
            command_params = []
            command_helper = self.get_helper(command)
            if command_helper is not None:
                command_params = command_helper()
                params_validation = {}
                help_string = ""
                i = 0
                for param_name, value in command_params.items():
                    if param_name != 'help':
                        if type(value) is func:
                            params_validation[param_name] = (
                                value(params[i]) if len(params) > i
                                else False
                            )
                        else:
                            params_validation[param_name] = (
                                True if len(params) > i else False
                            )
                        i += 1
                    else:
                        help_string = (
                            f"{Fore.RED}{command}{Style.RESET_ALL} "
                            f"command: {value}"
                        )

                validation_errors = [
                    field for field, value in params_validation.items()
                    if not value
                ]
                if validation_errors:
                    error_in_fields = (
                        "Invalid fields: " + " ".join(validation_errors)
                    )
                    usage = (
                        f"{help_string}\nCommand usage: {command} <"
                        + "> <".join(params_validation.keys())
                        + f">\n{error_in_fields}"
                    )
                    return usage
            else:
                if len(params) > 1:
                    return f"Usage: {command}"
            return func(self, params)
        return inner

    @input_validator
    def add_contact_handler(self, params):
        return self.contactbook.add_contact(params[0])

    def add_contact_helper(self):
        return {
            'help': "add new contact",
            'name': None,
        }

    @input_validator
    def upcoming_birthdays_handler(self, params):
        try:
            days = int(params[0])
        except ValueError:
            return "Invalid days format"
        return self.contactbook.upcoming_birthdays(days)

    def upcoming_birthdays_helper(self):
        return {
            'help': "get upcoming contact's birthdays",
            'days': None,
        }

    @input_validator
    def edit_contact_handler(self, params):
        return self.contactbook.edit_by_name(params[0])

    def edit_contact_helper(self):
        return {
            'help': "edit existing contact by name",
            'name': None,
        }

    @input_validator
    def edit_contact_id_handler(self, params):
        try:
            id = int(params[0])
        except ValueError:
            return "Invalid id format"
        return self.contactbook.edit_by_id(id)

    def edit_contact_id_helper(self):
        return {
            'help': "edit existing contact by id",
            'id': None,
        }

    @input_validator
    def edit_last_contact_handler(self, params):
        return self.contactbook.edit_last_contact()

    def edit_last_contact_helper(self):
        return {
            'help': "edit last contact",
        }

    @input_validator
    def get_contact_handler(self, params):
        return self.contactbook.get_contact(params[0])

    def get_contact_helper(self):
        return {
            'help': "get contact by name",
            'name': None,
        }

    @input_validator
    def del_contact_handler(self, params):
        return self.contactbook.del_contact(params[0])

    def del_contact_helper(self):
        return {
            'help': "delete contact by name",
            'name': None,
        }

    def del_contact_id_handler(self, params):
        return self.contactbook.del_by_id(params[0])

    def del_contact_id_helper(self):
        return {
            'help': "delete contact by id",
            'id': None,
        }

    def del_last_contact_handler(self, params):
        return self.contactbook.del_last()

    def del_last_contact_helper(self):
        return {
            'help': "delete last contact",
        }

    @input_validator
    def all_contacts_handler(self, params):
        return self.contactbook.all_contacts()

    def all_contacts_helper(self):
        return {
            'help': "print all contacts",
        }

    @input_validator
    def exit_handler(self, params):
        self.done = True
        return "Bye!"

    def exit_helper(self):
        return {
            'help': "exit application",
        }

    def close_handler(self, params):
        return self.exit_handler(params)

    def close_helper(self):
        return self.exit_helper()

    def add_note_handler(self, params):
        return self.notes.add_note_from_command(params)

    def add_note_helper(self):
        return {
            'help': (
                "add note (interactive mode). "
                "Usage: add_note OR add_note <title> OR "
                "add_note <title> <content> [tags]"
            ),
        }

    @input_validator
    def show_note_handler(self, params):
        return self.notes.get_note(params[0])

    def show_note_helper(self):
        return {
            'help': "get note from notes by title",
            'title': Notes.title_validator,
        }

    @input_validator
    def list_notes_handler(self, params):
        return self.notes.list_all_notes()

    def list_notes_helper(self):
        return {
            'help': "list all notes",
        }

    @input_validator
    def edit_note_handler(self, params):
        return self.notes.edit_note_from_command(params)

    def edit_note_helper(self):
        return {
            'help': "edit existing note (interactive mode available)",
            'title': Notes.title_validator,
        }

    @input_validator
    def delete_note_handler(self, params):
        return self.notes.delete_note(params[0])

    def delete_note_helper(self):
        return {
            'help': "delete note by title",
            'title': Notes.title_validator,
        }

    @input_validator
    def add_tags_handler(self, params):
        return self.notes.add_tags_from_command(params)

    def add_tags_helper(self):
        return {
            'help': "add tags to note",
            'title': Notes.title_validator,
            'tags': None,
        }

    @input_validator
    def remove_tags_handler(self, params):
        return self.notes.remove_tags_from_command(params)

    def remove_tags_helper(self):
        return {
            'help': "remove tags from note",
            'title': Notes.title_validator,
            'tags': None,
        }

    @input_validator
    def search_by_tag_handler(self, params):
        return self.notes.search_by_tag(params[0])

    def search_by_tag_helper(self):
        return {
            'help': "search notes by single tag",
            'tag': None,
        }

    @input_validator
    def search_by_tags_handler(self, params):
        return self.notes.search_by_tags_from_command(params)

    def search_by_tags_helper(self):
        return {
            'help': (
                "search notes by multiple tags "
                "(use --all for AND logic)"
            ),
            'tags': None,
        }

    @input_validator
    def list_all_tags_handler(self, params):
        return self.notes.list_all_tags()

    def list_all_tags_helper(self):
        return {
            'help': "list all tags with counts",
        }

    @input_validator
    def sort_by_tag_handler(self, params):
        return self.notes.sort_by_tag(params[0])

    def sort_by_tag_helper(self):
        return {
            'help': "sort notes by tag",
            'tag': None,
        }

    @input_validator
    def help_handler(self, params):
        all_commands = sorted(self.get_avail_commands())
        help = {}
        for command in all_commands:
            helper = self.get_helper(command)
            if helper is not None:
                params = helper()
                help[command] = params['help'] if 'help' in params else ""
            else:
                help[command] = ""

        txt = ""
        for command, help_txt in help.items():
            txt += (
                f"    {Fore.RED}{command.ljust(20)}"
                f"{Style.RESET_ALL}{help_txt}\n"
            )
        return f"Available comands:\n{txt}"

    def help_helper(self):
        return {
            'help': "list available commands",
        }

    def get_avail_commands(self):
        return [
            func.replace("_handler", "")
            for func in dir(self)
            if func.endswith("_handler")
        ]

    def get_helper(self, command):
        helper_name = command + "_helper"
        if helper_name in dir(self):
            return getattr(self, helper_name)
        return None

    def find_similar(self, command):
        all_commands = self.get_avail_commands()
        similarity = {
            cmd: (
                1 if cmd.startswith(command)
                else (2 if command in cmd else distance(command, cmd))
            )
            for cmd in all_commands
        }
        best_similarity = min(similarity.values())
        if len(command) < best_similarity:
            return []
        return [
            cmd for cmd, sm in similarity.items()
            if sm == best_similarity
        ]
