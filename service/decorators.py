

def input_error(func):
    def inner(*args, **kwargs):
        function = func.__name__

        try:
            return func(*args, **kwargs)
        except IndexError:
            if function == "add_contact":
                return "Usage: add <name> <phone> [email] [address]"  # [] optional
            # more cases
            return "Enter the argument for the command"
        except ValueError as e:
            return str(e)

    return inner
