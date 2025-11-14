import phonebook
from notes import Notes
from Levenshtein import distance


class BotCommands():

    done = False
    notes = Notes()

    def input_validator(func):
        def inner(self, params):
            command = func.__name__.removesuffix('_handler')
            command_params = []
            helper_name = command+"_helper"
            if helper_name in dir(self):
                command_helper = getattr(self, helper_name)
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
            try:
                return func(self, params)
            except Exception as e:
                return f"Really unexpected error occurred: {e}"
        return inner

    @input_validator
    def hello_handler(self, params):
        return "Hello, my dear! Have a nice day!"

    @input_validator
    def add_handler(self, params):
        return phonebook.add_phone(params[0], params[1])

    def add_helper(self):
        return {
            'help': "'add' command: adding new entry to phonebook",
            'name': None,
            'phone': phonebook.phone_validator,
        }

    @input_validator
    def change_handler(self, params):
        return phonebook.change_phone(params[0], params[1])

    def change_helper(self):
        return {
            'help': "'change' command: modifying existing entry in phonebook",
            'name': None,
            'phone': phonebook.phone_validator,
        }

    @input_validator
    def phone_handler(self, params):
        return phonebook.get_phone(params[0])

    def phone_helper(self):
        return {
            'help': "'phone' command: get phone number by name",
            'name': None,
        }

    @input_validator
    def all_handler(self, params):
        phone_list = ""
        for name, phone in phonebook.all_phones().items():
            phone_list += f"Name: {name}\tphone: {phone}\n"
        return phone_list

    @input_validator
    def exit_handler(self, params):
        self.done = True
        return "Bye!"

    def close_handler(self, params):
        return self.exit_handler(params)

    @input_validator
    def add_note_handler(self, params):
        if len(params) < 2:
            msg = ("'add_note' command: add new note to notes\n"
                   "Command usage: add_note <title> <content> [tags]")
            return msg

        title = params[0]

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
            msg = ("'add_note' command: add new note to notes\n"
                   "Command usage: add_note <title> <content> [tags]\n"
                   "Invalid fields: content")
            return msg

        return self.notes.add_note(title, content, tags)

    def add_note_helper(self):
        return {
            'help': "'add_note' command: add new note (tags optional)",
            'title': Notes.title_validator,
            'content': None,
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

    @input_validator
    def edit_note_handler(self, params):
        if len(params) < 2:
            msg = ("'edit_note' command: edit note content\n"
                   "Command usage: edit_note <title> <new_content>")
            return msg

        title = params[0]
        new_content = " ".join(params[1:])

        if not Notes.content_validator(new_content):
            msg = ("'edit_note' command: edit note content\n"
                   "Command usage: edit_note <title> <new_content>\n"
                   "Invalid fields: content")
            return msg

        return self.notes.edit_note(title, new_content)

    def edit_note_helper(self):
        return {
            'help': "'edit_note' command: edit note content",
            'title': Notes.title_validator,
            'content': None,
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
        return self.notes.add_tags(params[0], params[1])

    def add_tags_helper(self):
        return {
            'help': "'add_tags' command: add tags to note (comma-separated)",
            'title': Notes.title_validator,
            'tags': Notes.tags_validator,
        }

    @input_validator
    def remove_tags_handler(self, params):
        return self.notes.remove_tags(params[0], params[1])

    def remove_tags_helper(self):
        return {
            'help': ("'remove_tags' command: "
                     "remove tags from note (comma-separated)"),
            'title': Notes.title_validator,
            'tags': Notes.tags_validator,
        }

    @input_validator
    def search_tag_handler(self, params):
        return self.notes.search_by_tag(params[0])

    def search_tag_helper(self):
        return {
            'help': "'search_tag' command: search notes by single tag",
            'tag': None,
        }

    @input_validator
    def search_tags_handler(self, params):
        tags = params[0]
        match_all = len(params) > 1 and params[1].lower() == 'all'
        return self.notes.search_by_tags(tags, match_all)

    def search_tags_helper(self):
        return {
            'help': ("'search_tags' command: search notes by multiple tags "
                     "(add 'all' for AND search)"),
            'tags': None,
        }

    @input_validator
    def list_tags_handler(self, params):
        return self.notes.list_all_tags()

    @input_validator
    def sort_by_tag_handler(self, params):
        return self.notes.sort_by_tag(params[0])

    def sort_by_tag_helper(self):
        return {
            'help': ("'sort_by_tag' command: "
                     "show notes with tag sorted by date"),
            'tag': None,
        }

    @input_validator
    def help_handler(self, params):
        all_commands = self.get_avail_commands()
        return "Available comands: " + " ".join(all_commands)

    def get_avail_commands(self):
        return [
            func.replace("_handler", "")
            for func in dir(self)
            if func.endswith("_handler")
        ]

    def find_similar(self, command):
        all_commands = self.get_avail_commands()
        similarity = {
            cmd: distance(command, cmd) for cmd in all_commands
        }
        best_similarity = min(similarity.values())
        return [
            cmd for cmd, sm in similarity.items()
            if sm == best_similarity
        ]
