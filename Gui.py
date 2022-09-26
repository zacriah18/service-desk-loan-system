import os
import platform
from tkinter import *
from tkinter import font as tk_font
from PIL import ImageTk, Image

from LoanSystem import LoanSystem


class ServiceDeskFrame(Frame):

    def __init__(self, parent, controller, width, height, bg_color=""):
        Frame.__init__(self, parent, width=width, height=height)
        self.controller = controller
        self.parent = parent

        if not bg_color:
            self.config(bg=controller.background_colour)
        else:
            self.config(bg=bg_color)


class Test(ServiceDeskFrame):

    def __init__(self, parent, controller, width, height):
        ServiceDeskFrame.__init__(self, parent, controller, width=width, height=height)
        pass

    def refresh(self):
        print(f"Controller: {self.controller.winfo_geometry()}\nContainer: {self.parent.winfo_geometry()}\n\
Frame: {self.winfo_geometry()}")
        self.controller.after(1000, self.refresh)


class Barcode(ServiceDeskFrame):

    def __init__(self, parent, controller, width, height):
        ServiceDeskFrame.__init__(self, parent, controller, width=width, height=height)
        self.input = ""
        self.return_mode = False

        self.grid_columnconfigure(0, weight=0)
        self.grid_rowconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(2, weight=1)

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
        self.logo_label.grid(row=0, column=0, sticky='nw')

        # Label
        self.label = Label(self, text=f"Barcode: {self.input}")
        self.label.config(font=controller.title_font, fg=controller.font_colour, bg=controller.background_colour)
        self.label.grid(row=1, column=0, rowspan=2, columnspan=2, sticky='n')

        # Button
        self.button = Button(self, text=f"Toggle Return Mode: {self.return_mode}",
                             command=self.toggle_return)
        self.button.config(font=controller.button_font, fg=controller.font_colour, bg=controller.button_colour)
        self.button.grid(row=2, column=0, columnspan=3, rowspan=2, sticky='news')

    # toggles return mode and updates button text
    def toggle_return(self):
        self.return_mode = not self.return_mode
        self.button.config(text=f"Toggle Return Mode: {self.return_mode}")

    # function called when a key is pressed and this frame is active
    def key_press(self, key):
        self.input = self.input + key
        self.label.config(text=f"Barcode: {self.input}")

    # when the key pressed is the return button
    def submit_input(self):
        submit = self.input
        self.input = ""
        self.controller.battery_serial_submit(submit, self.return_mode)
        self.label.config(text=f"Barcode: {self.input}")

    def back(self):
        self.input = self.input[:-1]
        self.label.config(text=f"Barcode: {self.input}")

    def logging(self):
        print(f"Controller: {self.controller.winfo_geometry()}\n\
        Container: {self.parent.winfo_geometry()}\nFrame: {self.winfo_geometry()}")
        self.controller.after(1000, self.logging)


class LaptopSerial(ServiceDeskFrame):

    def __init__(self, parent, controller, width, height):
        ServiceDeskFrame.__init__(self, parent, controller, width=width, height=height)
        self.controller = controller

        self.input = ""
        self.config(bg=controller.background_colour)

        self.grid_columnconfigure(0, weight=0)
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=0)

        self.label = Label(self, text=f"Laptop Serial: {self.input}", font=controller.title_font, fg=controller.font_colour,
                           bg=controller.background_colour)
        self.label.grid(row=0, column=0)

        button = Button(self, text="Cancel", command=self.cancel, font=controller.button_font)
        button.config(height=5, width=30, fg=controller.font_colour, bg=controller.button_colour)
        button.grid(row=1, column=0, sticky='news')

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


class Update(ServiceDeskFrame):

    def __init__(self, parent, controller, width, height):
        ServiceDeskFrame.__init__(self, parent, controller, width=width, height=height, bg_color="green")

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

        # windows are only used for test devices and non-windows for deployment
        if platform.system() != "Windows":
            self.attributes(
                '-fullscreen',
                True
            )
            self.config(cursor="none")

        self.current_frame = None

        self.width = 800
        self.height = 480
        self.geom = str(self.width) + "x" + str(self.height)

        self.bind("<Key>", self.key_pressed)

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

        self.grid()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.container = Frame(self, width=self.width, height=self.height)
        self.container.grid(row=0, column=0, sticky='news')
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (Test, Barcode, LaptopSerial, Update):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self, width=self.width, height=self.height)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="news")
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_rowconfigure(0, weight=1)

        self.show_frame("Barcode")

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()
        self.current_frame = frame

    def run(self):
        self.mainloop()

    def key_pressed(self, event):
        if event.keysym == "Return":
            self.current_frame.submit_input()

        elif event.keysym == "Escape":
            exit("Escape was pressed")

        elif event.keysym == "BackSpace":
            self.current_frame.back()

        else:
            self.current_frame.key_press(event.keysym)

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

    def battery_serial_submit(self, barcode, return_mode):
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

        # device is in use
        if device_state == "In Use":
            # update
            self.frames["Update"].display(f'Battery Pack {device["name"]} found.\n\
Attempting to return.', "green", 3000)
            # get device details from response
            try:
                loaned_asset_id = device["loan"]["id"]
                loan_id = device["loan"]["loan"]["id"]

            # details not present
            except (KeyError, TypeError) as _:
                self.frames["Update"].display("""Device is in use but not on loan\n\
The details for this device are not setup for loan\n\
Please contact IT if this device should be loanable""", "red", self.standard_error_interval)
                return

            # get user details from loan
            response = self.ls.get_user_loan(loaned_asset_id, loan_id)

            # check bad response
            if response is None:
                self.frames["Update"].display("""User not found by the server\n\
Valid user ID not assigned to battery pack""", "red", self.standard_error_interval)
            try:
                user_id = response["loaned_asset"]["received_by"]["id"]
            except KeyError:
                self.frames["Update"].display("""User not found by the server\n\
Loan details were not returned by the server\n\
Please ensure scanned barcode matches digits on Label""", "red", self.standard_error_interval)
                return

            # update details
            response = self.ls.return_device(user_id, loaned_asset_id, loan_id)

            # check bad response
            if response is None:
                self.frames["Update"].display("""Loan was not returned by server\n\
no update was made.""", "red", self.standard_error_interval)
                return

            self.frames["Update"].display(f"""Battery Pack {device["name"]} is now returned""", "green",
                                          self.standard_error_interval)

        # device is in store
        elif device_state == "In Store":
            if return_mode:
                self.frames["Update"].display(f"""Battery Pack {device["name"]} found.\nAlready in store.""",
                                              "green", interval=1000)
            else:
                self.frames["Update"].display(f"""Battery Pack {device["name"]} found.\nAttempting to Loan.""",
                                              "green", interval=1000, frame="LaptopSerial")

        # unknown state
        else:
            self.frames["Update"].display(f"""Battery Pack {device["name"]} does not have a recognised state""",
                                          "red", interval=1000)
