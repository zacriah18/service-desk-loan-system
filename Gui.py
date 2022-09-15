import os
from tkinter import *
from tkinter import font as tk_font
from PIL import ImageTk, Image

from LoanSystem import LoanSystem


class Test(Frame):
    def __init__(self, parent, controller, width, height):
        Frame.__init__(self, parent, width=width, height=height)

        self.controller = controller
        self.config(bg=controller.background_colour)

        image_height = 128
        image_width = 100

        # # Import Image | separate image import for better config
        logo_image_raw = Image.open(os.path.join(os.getcwd(), "images", "only_sacs_logo.png"))
        #   .resize((image_width, image_height), Image.ANTIALIAS)
        logo_image_tk = ImageTk.PhotoImage(logo_image_raw)

        # IMAGE LABEL
        self.logo_label = Label(self, image=logo_image_tk)
        self.logo_label.image = logo_image_tk
        self.logo_label.config(borderwidth=0, highlightthickness=0)
        self.logo_label.grid(row=1, column=1)

        # # TEXT LABEL
        self.label = Label(self, text=f"{self.winfo_geometry()}")
        self.label.config(font=controller.title_font, bg=controller.background_colour, fg=controller.font_colour)
        self.label.grid(row=2, column=2)

        #
        # # SETTINGS BUTTON
        # self.button = Button(self, text="BUTTON")
        # self.button.config(width=controller.width-image_width, height=int(controller.height / 2))
        # self.button.config(font=controller.button_font, bg=controller.background_colour)
        #
        # # Logo
        # self.logo_label.grid(row=1, column=1, rowspan=2)
        #
        # # Label
        # self.label.grid(row=1, column=2, sticky=NE)
        #
        # # Button
        # self.button.grid(row=2, column=2, sticky=SE)

    def refresh(self):
        print(f"Controller: {self.controller.winfo_geometry()}\nContainer: {self.parent.winfo_geometry()}\nFrame: {self.winfo_geometry()}")
        self.controller.after(1000, self.refresh)


class Barcode(Frame):

    def __init__(self, parent, controller, width, height):
        Frame.__init__(self, parent, width=width, height=height)
        self.parent = parent
        self.controller = controller
        self.config(bg=controller.background_colour)

        #  -------------------------------------------------------------------------------------------------------------
        #  Class variables
        self.input = ""
        self.return_mode = False

        #  -------------------------------------------------------------------------------------------------------------
        #  Class Graphics

        self.grid_columnconfigure(0, weight=0)
        self.grid_rowconfigure(0, weight=2)

        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=2)

        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(2, weight=0)

        #  Import Image | separate image import for better config
        image_height = 128
        image_width = 100
        logo_image_raw = Image.open(os.path.join(os.getcwd(), "images", "only_sacs_logo.png"))
        logo_image_raw.resize((image_width, image_height), Image.ANTIALIAS)
        logo_image_tk = ImageTk.PhotoImage(logo_image_raw)

        # IMAGE LABEL
        self.logo_label = Label(self, image=logo_image_tk)
        self.logo_label.image = logo_image_tk
        self.logo_label.config(borderwidth=0, highlightthickness=0)
        self.logo_label.grid(row=0, column=0, rowspan=2, sticky='w')

        # Label
        self.label = Label(self, text=f"Barcode: {self.input}")
        self.label.config(font=controller.title_font, fg=controller.font_colour, bg=controller.background_colour)
        self.label.grid(row=0, column=1, rowspan=2, columnspan=2, sticky='w')

        # Button
        self.button = Button(self, text=f"Toggle Return Mode: {self.return_mode}",
                             command=self.toggle_return)
        self.button.config(font=controller.button_font, fg=controller.font_colour, bg=controller.button_colour)
        self.button.grid(row=2, column=0, columnspan=3, rowspan=2, sticky='news')

        self.logging()

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

    def logging(self):
        print(f"Controller: {self.controller.winfo_geometry()}\n\
        Container: {self.parent.winfo_geometry()}\nFrame: {self.winfo_geometry()}")
        self.controller.after(1000, self.logging)


class LaptopSerial(Frame):
    def __init__(self, parent, controller, width, height):
        Frame.__init__(self, parent, width=width, height=height)
        self.controller = controller

        self.input = ""
        self.config(bg=controller.background_colour)

        self.label = Label(self, text=f"Laptop Serial: {self.input}", font=controller.title_font, fg=controller.font_colour,
                           bg=controller.background_colour)
        self.label.grid(row=1, column=1)

        button = Button(self, text="Cancel", command=self.cancel, font=controller.button_font)
        button.config(height=5, width=30, fg=controller.font_colour, bg=controller.button_colour)
        button.grid(row=2, column=1)

    def cancel(self):
        self.input = ""
        self.label.config(text=f"Laptop Serial: {self.input}")
        self.controller.show_frame("Barcode")

    def key_press(self, key):
        self.input = self.input + key
        self.label.config(text=f"Laptop Serial: {self.input}")

    def submit_input(self):
        self.controller.laptop_serial_submit(self.input)
        self.input = ""
        self.label.config(text=f"Laptop Serial: {self.input}")

    def back(self):
        self.input = self.input[:-1]
        self.label.config(text=f"Laptop Serial: {self.input}")


class Update(Frame):
    def __init__(self, parent, controller, width, height):
        Frame.__init__(self, parent, width=width, height=height)
        self.controller = controller
        self.config(bg="green")

        self.label = Label(self, text="Update", font=controller.error_font, fg=controller.font_colour)
        self.label.grid(row=0, column=0)

    def display(self, text, colour, interval=0, frame="Barcode"):
        self.config(bg=colour)
        self.label.config(text=text, bg=colour)
        self.controller.show_frame("Update")
        if interval:
            self.controller.after(interval, lambda: self.controller.show_frame(frame))


class Gui(Tk):
    def __init__(self):
        Tk.__init__(self)

        #  -------------------------------------------------------------------------------------------------------------
        #  GUI

        # self.attributes(
        #     '-fullscreen',
        #     True
        # )

        self.current_frame = None

        self.width = 320
        self.height = 240
        self.geom = str(self.width) + "x" + str(self.height)
        self.geometry(self.geom)
        self.bind("<Key>", self.key_pressed)
        # self.config(cursor="none")

        self.ls = LoanSystem()
        self.battery_pack = {}
        self.standard_error_interval = 2000  # 2 seconds

        self.title_font = tk_font.Font(family='Helvetica', size=16, weight="bold", slant="italic")
        self.button_font = tk_font.Font(family='Helvetica', size=14, weight="bold", slant="italic")
        self.error_font = tk_font.Font(family='Helvetica', size=12, weight="bold", slant="italic")
        self.font_colour = "white"
        self.background_colour = "#082042"
        self.button_colour = "#847355"
        self.config(bg=self.background_colour, width=self.width, height=self.height)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        self.container = Frame(self, width=self.width, height=self.height)

        self.container.grid(row=0, column=0, sticky='news')
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.grid()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (Test, Barcode, LaptopSerial, Update):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self, width=self.width, height=self.height)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="news")
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_rowconfigure(0, weight=1)

        self.show_frame("Barcode")

    def geom_controller(self):
        self.container.config(width=self.width, height=self.height)
        self.after(5000, self.geom_controller)

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

    def laptop_serial_submit(self, laptop_serial):
        response = self.ls.search_device(laptop_serial)
        if response is None:
            self.frames["Update"].display(f"{laptop_serial} Laptop barcode not Found", "red",
                                          self.standard_error_interval)
            return

        try:
            laptop_id = response["assets"][0]["id"]
        except (KeyError, IndexError) as _:
            self.frames["Update"].display(f"{laptop_serial} Laptop ID not found", "red", self.standard_error_interval)
            return

        response = self.ls.get_asset_details(laptop_id)
        if response is None:
            self.frames["Update"].display(f"{laptop_serial} Laptop details not Found", "red",
                                          self.standard_error_interval)
            return

        try:
            user_id = response["asset"]["user"]["id"]
        except (KeyError, IndexError) as _:
            self.frames["Update"].display(f"{laptop_serial} not assigned to user", "red", self.standard_error_interval)
            return

        if self.battery_pack:
            response = self.ls.return_loan(str(user_id), str(self.battery_pack["id"]))
        else:
            self.frames["Update"].display("Forgot Asset ID please try again", "red", self.standard_error_interval)
            return
        if response is None:
            self.frames["Update"].display("""Loan was not created by server\n\
no update was made.""", "red", self.standard_error_interval)
            return

        self.frames["Update"].display(f"{self.battery_pack['name']} is now loaned",
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
            self.frames["Update"].display(f"""{barcode} Not Found\n\
Please ensure scanned barcode \nmatches digits on label""", "red", self.standard_error_interval)
            return

        # Check state of battery pack
        try:
            device_state = device["state"]["name"]
        except KeyError:
            self.frames["Update"].display("""Battery Pack state not found""", "red", self.standard_error_interval)
            return

        if device_state == "In Use":
            self.frames["Update"].display(f'Battery Pack {device["name"]} found.\n\
                Attempting to return.', "green", 5000)
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
                                              "green", interval=1000, frame="LaptopSerial")

        else:
            self.frames["Update"].display(f"""Battery Pack {device["name"]} does not have a recognised state""",
                                          "red", interval=1000)
