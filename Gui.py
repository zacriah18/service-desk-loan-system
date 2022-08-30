from tkinter import *
from tkinter import font as tk_font
from LoanSystem import LoanSystem


class Barcode(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.input = ""

        self.return_mode = False

        self.label = Label(self, text=f"Barcode: {self.input}", font=controller.title_font, fg=controller.font_colour)
        self.label.pack(expand=True, anchor=CENTER)

        self.button = Button(self, text=f"Toggle Return Mode: {self.return_mode}",
                             command=self.toggle_return)
        self.button.pack()

    def toggle_return(self):
        self.return_mode = not self.return_mode
        self.button.config(text=f"Toggle Return Mode: {self.return_mode}")

    def key_press(self, key):
        self.input = self.input + key
        self.label.config(text=f"Barcode: {self.input}")

    def submit_input(self):
        self.controller.barcode_submit(self.input, self.return_mode)
        self.input = ""
        self.label.config(text=f"Barcode: {self.input}")

    def back(self):
        self.input = self.input[:-1]
        self.label.config(text=f"Barcode: {self.input}")


class Swipe(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        self.input = ""

        self.label = Label(self, text=f"Swipe: {self.input}", font=controller.title_font, fg=controller.font_colour)
        self.label.pack(expand=True, anchor=CENTER)

        button = Button(self, text="Cancel",
                        command=self.cancel)
        button.pack()

    def cancel(self):
        self.input = ""
        self.label.config(text=f"Swipe: {self.input}")
        self.controller.show_frame("Barcode")

    def key_press(self, key):
        self.input = self.input + key
        self.label.config(text=f"Swipe: {self.input}")

    def submit_input(self):
        self.controller.swipe_submit(self.input)
        self.input = ""
        self.label.config(text=f"Swipe: {self.input}")

    def back(self):
        self.input = self.input[:-1]
        self.label.config(text=f"Swipe: {self.input}")


class Update(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.config(bg="green")

        self.label = Label(self, text="Update", font=controller.title_font, fg=controller.font_colour)
        self.label.pack(expand=True, anchor=CENTER)

    def display(self, text, colour, interval=0, frame="Barcode"):
        self.config(bg=colour)
        self.label.config(text=text, bg=colour)
        self.controller.show_frame("Update")
        if interval:
            self.controller.after(interval, lambda: self.controller.show_frame(frame))


class Gui(Tk):
    def __init__(self):
        Tk.__init__(self)
        
        self.attributes(
            '-fullscreen',
            True
        )
        self.config(bg="black")
        self.bind("<Key>", self.key_pressed)

        self.ls = LoanSystem()
        self.battery_pack = {}
        self.standard_error_interval = 2000  # 2 seconds

        self.title_font = tk_font.Font(family='Helvetica', size=24, weight="bold", slant="italic")
        self.font_colour = "white"
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (Barcode, Swipe, Update):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Barcode")
        self.current_frame = self.frames["Barcode"]

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()
        self.current_frame = frame

    def run(self):
        self.mainloop()

    def key_pressed(self, event):
        frame = self.current_frame
        if event.keysym == "Return":
            frame.submit_input()

        elif event.keysym == "Escape":
            exit("Escape was pressed")

        elif event.keysym == "BackSpace":
            frame.back()

        else:
            frame.key_press(event.keysym)

    def swipe_submit(self, swipe):
        response = self.ls.process_swipe(swipe)
        if response is None:
            self.frames["Update"].display("Bad response from user detail request.", "red", self.standard_error_interval)
            return

        try:
            user_id = response["users"][0]["id"]
        except (KeyError, IndexError) as _:
            self.frames["Update"].display("Student Card is not found.\n\
            No students with matching ID was found by the server\n\
            Please see IT to update student information", "red", self.standard_error_interval)
            return

        if self.battery_pack:
            response = self.ls.return_loan(user_id, self.battery_pack["id"])

        else:
            self.frames["Update"].display("Forgot Asset ID please try again", "red", self.standard_error_interval)
            return

        if response is None:
            self.frames["Update"].display("""Loan was not created by server\n\
            no update was made.""", "red", self.standard_error_interval)
            return

        self.frames["Update"].display(f"Battery Pack {self.battery_pack['name']} is now loaned",
                                      "green", self.standard_error_interval)

    def barcode_submit(self, barcode, return_mode):
        response = self.ls.process_barcode(barcode)

        # Check battery pack was found
        if response is None:
            self.frames["Update"].display("Bad response from battery pack request.", "red",
                                          self.standard_error_interval)
            return
        try:
            device = response["assets"][0]
            self.battery_pack = device

        # battery pack was not found
        except (KeyError, IndexError):
            self.frames["Update"].display("""Battery Pack was not found by the server\n\
            Please ensure scanned barcode matches digits on label""", "red", self.standard_error_interval)
            return

        # Check state of battery pack
        try:
            device_state = device["state"]["name"]
        except KeyError:
            self.frames["Update"].display("""Battery Pack state not found""", "red", self.standard_error_interval)
            return

        if device_state == "In Use":
            self.frames["Update"].display(f'Battery Pack {device["name"]} found.\n\
            Attempting to return.',
                                          "green", 5000)
            try:
                loaned_asset_id = device["loan"]["id"]
                loan_id = device["loan"]["loan"]["id"]
            except (KeyError, TypeError) as _:
                self.frames["Update"].display("""Device is in use but not on loan\n\
                The details for this device are not setup for loan\n\
                Please contact IT if this device should be loanable""", "red", self.standard_error_interval)
                return

            response = self.ls.get_user_loan(loaned_asset_id, loan_id)

            if response is None:
                self.frames["Update"].display("""User not found by the server""", "red", self.standard_error_interval)
            try:
                user_id = response["loaned_asset"]["received_by"]["id"]
            except KeyError:
                self.frames["Update"].display("""User not found by the server\n\
                Loan details were not returned by the server\n\
                Please ensure scanned barcode matches digits on Label""", "red", self.standard_error_interval)
                return
            # update details

            response = self.ls.return_device(user_id, loaned_asset_id, loan_id)

            if response is None:
                self.frames["Update"].display("""Loan was not returned by server\n\
                no update was made.""", "red", self.standard_error_interval)
                return

            self.frames["Update"].display(f"""Battery Pack {device["name"]} is now returned""",
                                          "green", self.standard_error_interval)

        elif device_state == "In Store":
            if return_mode:
                self.frames["Update"].display(f"""Battery Pack {device["name"]} found.\nAlready in store.""",
                                              "green", interval=1000)
            else:
                self.frames["Update"].display(f"""Battery Pack {device["name"]} found.\nAttempting to Loan.""",
                                              "green", interval=1000, frame="Swipe")

        else:
            self.frames["Update"].display(f"""Battery Pack {device["name"]} does not have a recognised state""",
                                          "red", interval=1000)
