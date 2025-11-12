from phonebook import Contact, Phonebook
from notes import Notes
from Levenshtein import distance
from colorama import Fore, Style

class BotCommands():

    done = False
    notes = Notes()
    phonebook = Phonebook()

    def input_validator(func):
        def inner(self, params):
            command = func.__name__.removesuffix('_handler')
            command_params = []
            command_helper = self.get_helper(command)
            if command_helper != None:
                command_params = command_helper()
                params_validation = {}
                help_string = ""
                i = 0
                for param_name, value in command_params.items():
                    if param_name != 'help':
                        if type(value) is func:
                            params_validation[param_name] = value(params[i]) if len(params) > i else False
                        else:
                            params_validation[param_name] = True if len(params) > i else False
                        i += 1
                    else:
                        help_string = value

                validation_errors = [field for field, value in params_validation.items() if not value]
                if validation_errors:
                    error_in_fields = f"Invalid fields: " + " ".join(validation_errors)
                    return f"{help_string}\nCommand usage: {command} <" + "> <".join(params_validation.keys()) + f">\n{error_in_fields}"
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
        return self.phonebook.add_contact(params[0])

    def add_contact_helper(self):
        return {
            'help' : "'add_contact' command: add new entry into phonebook",
            'name' : None,
        }

    @input_validator
    def change_contact_handler(self, params):
        return self.phonebook.change_contact(params[0], params[1])

    def change_contact_helper(self):
        return {
            'help' : "'change_contact' command: modify existing entry in phonebook",
            'name' : None,
            'phone': Contact.phone_validator,
        }

    @input_validator
    def get_contact_handler(self, params):
        return self.phonebook.get_contact(params[0])

    def get_contact_helper(self):
        return {
            'help' : "'get_contact' command: get contact from phonebook by name",
            'name' : None,
        }

    @input_validator
    def del_contact_handler(self, params):
        return self.phonebook.del_contact(params[0])

    def del_contact_helper(self):
        return {
            'help' : "'del_contact' command: delete contact from phonebook by name",
            'name' : None,
        }

    @input_validator
    def all_contacts_handler(self, params):
        phone_list = ""
        for name, phone in self.phonebook.all_contacts().items():
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
        return self.notes.add_note(params[0], params[1])

    def add_note_helper(self):
        return {
            'help' : "'add_note' command: add new note to notes",
            'title' : Notes.title_validator,
            'content': Notes.content_validator,
        }

    @input_validator
    def show_note_handler(self, params):
        return self.notes.get_note(params[0])

    def show_note_helper(self):
        return {
            'help' : "'show_note' command: get note from notes by title",
            'title' : Notes.title_validator,
        }

    @input_validator
    def list_notes_handler(self, params):
        return self.notes.list_all_notes()

    @input_validator
    def help_handler(self, params):
        all_commands = sorted(self.get_avail_commands())
        help = {}
        for command in all_commands:
            helper = self.get_helper(command)
            if helper != None:
                params = helper()
                help[command] = params['help'] if 'help' in params else ""
            else:
                help[command] = ""

        txt = ""
        for command, help_txt in help.items():
            txt += f"    {Fore.RED}{command.ljust(20)}{Style.RESET_ALL}{help_txt}\n"
        return f"Available comands:\n{txt}"

    def get_avail_commands(self):
        return [func.replace("_handler", "") for func in dir(self) if func.endswith("_handler")]

    def get_helper(self, command):
        helper_name = command + "_helper"
        if helper_name in dir(self):
            return getattr(self, helper_name)
        return None

    def find_similar(self, command):
        all_commands = self.get_avail_commands()
        similarity = {cmd : (1 if cmd.startswith(command) else (2 if command in cmd else distance(command, cmd))) for cmd in all_commands}
        best_similarity = min(similarity.values())
        if len(command) < best_similarity:
            return []
        return [cmd for cmd, sm in similarity.items() if sm == best_similarity]

