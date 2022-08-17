import os


class Printer:
    def __init__(self):
        try:
            self.terminal_width, self.terminal_height = os.get_terminal_size()
        except OSError:
            self.terminal_width, self.terminal_height = 100, 10

    def print_page(self, percent: float = 1) -> None:
        for i in range(int(self.terminal_height * percent)):
            print((self.terminal_width - 1) * "-")

    def print_line(self) -> None:
        print(self.terminal_width * "-")

    def center_text(self, text: str) -> None:
        if len(text) < self.terminal_width:
            length = self.terminal_width / 2 - len(text) / 2
        else:
            length = 0
        print(int(length) * " " + text)

    def print_detailed_error(self, name: str, message: str, action: str) -> None:
        self.center_text(f"ERROR: {name}")
        self.center_text(message)
        self.center_text(action)

    def print_generic_error(self, name: str, message: str):
        self.print_detailed_error(name,
                                  message,
                                  "If this error continues please contact IT")

    def print_temp_error(self, name: str) -> None:
        self.print_detailed_error(name,
                                  "Try again, this may just be a temporary error.",
                                  "If this error continues please contact IT")

    def print_no_changes_were_made(self, name):
        self.print_generic_error(name,
                                 "No changes were made")

    def print_connection_error(self, request_function_name: str) -> None:
        self.print_no_changes_were_made(f'Connection Issue Calling "{request_function_name}"')

    def print_status_update(self, text: str) -> None:
        self.center_text(f"UPDATE: {text}")

    def get_input(self, text: str) -> str:
        if len(text) < self.terminal_width:
            length = self.terminal_width / 2 - len(text) / 2
        else:
            length = 0
        return input(int(length) * " " + text)
