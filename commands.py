from contactbook import Contact, Contactbook
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
                        help_string = value

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
    def hello_handler(self, params):
        return "Hello, my dear! Have a nice day!"

    @input_validator
    def add_contact_handler(self, params):
        return self.contactbook.add_contact(params[0])

    def add_contact_helper(self):
        return {
            'help': "'add_contact' command: add new entry",
            'name': None,
        }

    @input_validator
    def change_contact_handler(self, params):
        return self.contactbook.change_contact(params[0], params[1])

    def change_contact_helper(self):
        return {
            'help': "'change_contact' command: modify existing entry",
            'name': None,
            'phone': Contact.phone_validator,
        }

    @input_validator
    def get_contact_handler(self, params):
        return self.contactbook.get_contact(params[0])

    def get_contact_helper(self):
        return {
            'help': "'get_contact' command: get contact by name",
            'name': None,
        }

    @input_validator
    def del_contact_handler(self, params):
        return self.contactbook.del_contact(params[0])

    def del_contact_helper(self):
        return {
            'help': "'del_contact' command: delete contact by name",
            'name': None,
        }

    @input_validator
    def all_contacts_handler(self, params):
        phone_list = ""
        for name, phone in self.contactbook.all_contacts().items():
            phone_list += f"Name: {name}\tphone: {phone}\n"
        return phone_list

    @input_validator
    def exit_handler(self, params):
        self.done = True
        return "Bye!"

    def close_handler(self, params):
        return self.exit_handler(params)

    def _add_note_fully_interactive(self):
        title = yield ("Enter note title: ")
        if not Notes.title_validator(title):
            return "Error: Invalid title format."
        content = yield ("Enter note content: ")
        if not Notes.content_validator(content):
            return "Error: Invalid content format."
        tags = yield (
            "Enter tags (separated by comma or space, "
            "or press Enter to skip): "
        )
        if tags and not Notes.tags_validator(tags):
            return "Error: Invalid tags format."
        return self.notes.add_note(title, content, tags)

    def add_note_handler(self, params):
        if len(params) == 0:
            return self._add_note_fully_interactive()

        if len(params) == 1:
            if not Notes.title_validator(params[0]):
                return "Error: Invalid title format."
            return self.notes.add_note_interactive(params[0])

        title = params[0]

        if not Notes.title_validator(title):
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

        if not Notes.content_validator(content):
            msg = (
                "'add_note' command: add new note to notes\n"
                "Command usage: add_note [<title>] [<content>] [tags]\n"
                "Invalid fields: content"
            )
            return msg

        if tags and not Notes.tags_validator(tags):
            msg = (
                "'add_note' command: add new note to notes\n"
                "Command usage: add_note [<title>] [<content>] [tags]\n"
                "Invalid fields: tags"
            )
            return msg

        return self.notes.add_note(title, content, tags)

    def add_note_helper(self):
        return {
            'help': (
                "'add_note' command: add note (interactive mode). "
                "Usage: add_note OR add_note <title> OR "
                "add_note <title> <content> [tags]"
            ),
        }

    @input_validator
    def show_note_handler(self, params):
        return self.notes.get_note(params[0])

    def show_note_helper(self):
        return {
            'help': "'show_note' command: get note from notes by title",
            'title': Notes.title_validator,
        }

    @input_validator
    def list_notes_handler(self, params):
        return self.notes.list_all_notes()

    def list_notes_helper(self):
        return {
            'help': "'list_notes' command: list all notes",
        }

    @input_validator
    def edit_note_handler(self, params):
        if len(params) < 1:
            msg = (
                "'edit_note' command: edit existing note\n"
                "Command usage: edit_note <title> [new_content] [new_tags]"
            )
            return msg

        title = params[0]
        new_content = params[1] if len(params) > 1 else None
        new_tags = params[2] if len(params) > 2 else None

        if new_content is not None:
            if not Notes.content_validator(new_content):
                msg = (
                    "'edit_note' command: edit existing note\n"
                    "Command usage: edit_note <title> [new_content] "
                    "[new_tags]\n"
                    "Invalid fields: new_content"
                )
                return msg

        if new_tags is not None and not Notes.tags_validator(new_tags):
            msg = (
                "'edit_note' command: edit existing note\n"
                "Command usage: edit_note <title> [new_content] [new_tags]\n"
                "Invalid fields: new_tags"
            )
            return msg

        return self.notes.edit_note(title, new_content, new_tags)

    def edit_note_helper(self):
        return {
            'help': "'edit_note' command: edit existing note",
            'title': Notes.title_validator,
        }

    @input_validator
    def delete_note_handler(self, params):
        return self.notes.delete_note(params[0])

    def delete_note_helper(self):
        return {
            'help': "'delete_note' command: delete note by title",
            'title': Notes.title_validator,
        }

    @input_validator
    def add_tags_handler(self, params):
        if len(params) < 2:
            msg = (
                "'add_tags' command: add tags to note\n"
                "Command usage: add_tags <title> <tags>"
            )
            return msg

        title = params[0]
        tags_str = " ".join(params[1:])

        if not Notes.tags_validator(tags_str):
            msg = (
                "'add_tags' command: add tags to note\n"
                "Command usage: add_tags <title> <tags>\n"
                "Invalid fields: tags"
            )
            return msg

        return self.notes.add_tags(title, tags_str)

    def add_tags_helper(self):
        return {
            'help': "'add_tags' command: add tags to note",
            'title': Notes.title_validator,
            'tags': None,
        }

    @input_validator
    def remove_tags_handler(self, params):
        if len(params) < 2:
            msg = (
                "'remove_tags' command: remove tags from note\n"
                "Command usage: remove_tags <title> <tags>"
            )
            return msg

        title = params[0]
        tags_str = " ".join(params[1:])

        return self.notes.remove_tags(title, tags_str)

    def remove_tags_helper(self):
        return {
            'help': "'remove_tags' command: remove tags from note",
            'title': Notes.title_validator,
            'tags': None,
        }

    @input_validator
    def search_by_tag_handler(self, params):
        return self.notes.search_by_tag(params[0])

    def search_by_tag_helper(self):
        return {
            'help': "'search_by_tag' command: search notes by single tag",
            'tag': None,
        }

    @input_validator
    def search_by_tags_handler(self, params):
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

        return self.notes.search_by_tags(tags_str, match_all)

    def search_by_tags_helper(self):
        return {
            'help': (
                "'search_by_tags' command: search notes by multiple tags "
                "(use --all for AND logic)"
            ),
            'tags': None,
        }

    @input_validator
    def list_all_tags_handler(self, params):
        return self.notes.list_all_tags()

    def list_all_tags_helper(self):
        return {
            'help': "'list_all_tags' command: list all tags with counts",
        }

    @input_validator
    def sort_by_tag_handler(self, params):
        return self.notes.sort_by_tag(params[0])

    def sort_by_tag_helper(self):
        return {
            'help': "'sort_by_tag' command: sort notes by tag",
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
