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

from LoanSystem import LoanSystem


# Main function
def main():
    ls = LoanSystem()
    ls.run()


if __name__ == "__main__":
    main()
