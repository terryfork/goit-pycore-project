from service import BotService


def main():
    bot = BotService()

    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            continue

        command, *args = __parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add-contact":
            print(bot.save_contact(args))
        # more cases
        else:
            print("Invalid command.")


def __parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


if __name__ == "__main__":
    main()
