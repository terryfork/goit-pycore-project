import phonebook
import notes

class BotCommands():

    done = False

    def input_validator(func):
        def inner(self, params):
            command = func.__name__.removesuffix('_handler')
            command_params = []
            helper_name = command+"_helper"
            if helper_name in dir(self):
                command_helper = getattr(self, helper_name)
                command_params = command_helper()
                if len(params) != len(command_params):
                    return f"Usage: {command} <" + "> <".join(command_params) + ">"
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
        return ['name', 'phone']

    @input_validator
    def change_handler(self, params):
        return phonebook.change_phone(params[0], params[1])

    def change_helper(self):
        return ['name', 'phone']

    @input_validator
    def phone_handler(self, params):
        return phonebook.get_phone(params[0])

    def phone_helper(self):
        return ['name']

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

    @input_validator
    def close_handler(self, params):
        return self.exit_handler(params)

    @input_validator
    def add_note_handler(self, params):
        return notes.add_note(params[0], params[1])

    def add_note_helper(self):
        return ['title', 'content']

    @input_validator
    def show_note_handler(self, params):
        return notes.get_note(params[0])

    def show_note_helper(self):
        return ['title']

    @input_validator
    def list_notes_handler(self, params):
        return notes.list_all_notes()

    @input_validator
    def help_handler(self, params):
        all_commands = [func.replace("_handler", "") for func in dir(self) if func.endswith("_handler")]
        return "Available comands: " + " ".join(all_commands)
