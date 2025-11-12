from commands import BotCommands
from colorama import Fore, Style
from typing import Generator

def main():
    print("Hello! This is CLI bot. Please enter command.")
    command_processor = BotCommands()
    while not command_processor.done:
        console_line = ""
        while console_line == "":
            console_line = input(">")
        command, params = parse_input(console_line)
        handler_name = command+"_handler"
        if handler_name in dir(command_processor):
            handler = getattr(command_processor, handler_name)
            result = handler(params)
            if isinstance(result, Generator):
                try:
                    answ = next(result)
                    while True:
                        answ = result.send(input(answ))
                except StopIteration as done:
                    print(done)
            else:
                print(result)
        else:
            possible_commands = command_processor.find_similar(command)
            suggest = "Did you mean " + Fore.RED + " or ".join(possible_commands) + Style.RESET_ALL + "? " if possible_commands else ""
            print(f"Command not recognized. {suggest}Type 'help' to print available commands")


def parse_input(line):
    params = []
    for i, block in enumerate(line.split('"')):
        params += block.strip().split(" ") if not i % 2 else [block]

    command = params.pop(0).lower()
    command = command.replace("-", "_")

    if command == "add_note" and len(words) >= 2:
        title = words[0]
        content = " ".join(words[1:])
        return command, [title, content]

    return command, params


if __name__ == "__main__":
    main()
