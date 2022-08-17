from tkinter import *


def run_window():
    root = Tk()
    root.attributes(
        '-fullscreen',
        True
    )

    # Title
    root.title('Loan System')

    # Label
    my_label1 = Label(
        root,
        text="Scan Barcode"
    )
    my_label1.pack()

    # button = Button(
    #     root,
    #     text="End All",
    #     width=50,
    #     height=10,
    #     bg="white",
    #     fg="black",
    # )

    barcode_input = Text(
        root,
        width=50
    )
    barcode_input.pack()

    root.mainloop()
