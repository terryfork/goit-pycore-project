from commands import BotCommands
from colorama import Fore, Style
from typing import Generator


def main():
    print(
        "Hello! This is CLI bot. Please enter command.\n"
        "Type 'help' for available commands list"
    )
    command_processor = BotCommands()
    while not command_processor.done:
        console_line = ""
        while console_line == "":
            console_line = input(">")
        command, params = parse_input(console_line)
        handler_name = command + "_handler"
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
            if possible_commands:
                cmd_list = " or ".join(possible_commands)
                suggest = (
                    f"Did you mean {Fore.RED}{cmd_list}"
                    f"{Style.RESET_ALL}? "
                )
            else:
                suggest = ""
            print(
                f"Command not recognized. {suggest}"
                f"Type 'help' to print available commands"
            )


def parse_input(line):
    params = []
    for i, block in enumerate(line.split('"')):
        if not i % 2:
            params += [p for p in block.strip().split(" ") if p]
        else:
            if block:
                params.append(block)

    command = params.pop(0).lower()
    command = command.replace("-", "_")
    return command, params


if __name__ == "__main__":
    main()
