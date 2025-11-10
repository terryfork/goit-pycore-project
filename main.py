from commands import BotCommands

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
            print(handler(params))
        else:
            print("Command not recognized. Type 'help' to print available commands")


def parse_input(line):
    words = line.split(" ")
    command = words.pop(0).lower()
    return command, words


if __name__ == "__main__":
    main()
