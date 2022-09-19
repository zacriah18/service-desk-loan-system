# Created BY: Zack Bailey
# Company: St Andrews Cathedral School
# Called BY:
# Dependencies: jsonReader,
# Access:
# Description:
#    This document is the main program file for \
#    the serviceDesk project and contains functions \
#    that serve major processes
# from typing import Union

import Gui
import LoanSystem

# Main function
def main():
    ls = LoanSystem.LoanSystem()
    ls.run()
    gui = Gui.Gui()
    gui.run()


if __name__ == "__main__":
    main()
