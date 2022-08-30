# Created BY: Zack Bailey
# Company: St Andrews Cathedral School
# Called BY:
# Dependencies: jsonReader, talk,
# Accesses: main
# Description:
# Manager for the loan system

import Talk
import JsonReader
import HandleTime
import Printer
from typing import Union

# Called from main.main()
# Defines the class for the loan system and handles long use variables
class LoanSystem:
    def __init__(self, code: str = "") -> None:
        # Declare class instances
        self.printer = Printer.Printer()
        # setup authenticator class and if needed conducts first time authentication process
        self.authenticator = Talk.Authenticator(code)
        self.authenticator.authenticate()

        # Declare class variables
        self.barcode = ""
        self.swipe = ""

    # Defines the method to call the loan system process
    def run(self) -> None:
        while True:
            # Get Barcode
            self.get_barcode()
            # Get Device

            if self.barcode == "exit":
                exit("User terminated program")

            response = Talk.handle_response(
                self.authenticator.talk("get_search",
                                        "https://sacs.sdpondemand.manageengine.com/app/itdesk/api/v3/assets/",
                                        JsonReader.get_json("assetData.json", "searchParam")))

            # Check battery pack was found
            if response is None:
                self.printer.print_connection_error("Request Battery Pack Details")
                continue
            try:
                device = response["assets"][0]
            # battery pack was not found
            except (KeyError, IndexError):
                self.printer.print_detailed_error("Battery Pack not found",
                                                  "No Battery Packs were returned by the server",
                                                  "Please ensure scanned barcode matches digits on Label")
                continue

            # Check state of battery pack
            try:
                device_state = device["state"]["name"]
            except KeyError:
                self.printer.print_temp_error("Battery Pack state not found")
                continue

            self.printer.center_text(f'Battery Pack {device["name"]} is {device_state}')

            if device_state == "In Use":

                self.printer.print_status_update("Attempting to return Device")

                try:
                    loaned_asset_id = device["loan"]["id"]
                    loan_id = device["loan"]["loan"]["id"]
                except (KeyError, TypeError) as _:
                    self.printer.print_detailed_error("Device is in use but not on loan",
                                                      "The details for this device are not setup for loan",
                                                      "Please contact IT if this device should be loanable")
                    continue

                # get user ID associated with the loan
                response = Talk.handle_response(
                    self.authenticator.talk("get",
                                            "https://sacs.sdpondemand.manageengine.com/app/itdesk/api/v3"
                                            "/asset_loans/" + str(loan_id) + "/loaned_assets/" +
                                            str(loaned_asset_id) + "/"))
                if response is None:
                    self.printer.print_connection_error("Request Loan from Asset Details")
                try:
                    user_id = response["loaned_asset"]["received_by"]["id"]
                except KeyError:
                    self.printer.print_detailed_error("Loan ID not found",
                                                      "Loan details were not returned by the server",
                                                      "Please ensure scanned barcode matches digits on Label")
                    continue
                # update details
                JsonReader.update_return_asset_data(HandleTime.get_now_timestamp(), "loan system", user_id)

                response = Talk.handle_response(self.authenticator.talk(
                        "put",
                        "https://sacs.sdpondemand.manageengine.com/app/itdesk/api/v3/asset_loans/" + str(loan_id) +
                        "/loaned_assets/" + str(loaned_asset_id) + "/",
                        JsonReader.get_json("returnAsset.json", "postParam")
                    ))
                if response is None:
                    self.printer.print_connection_error("Put request loan details to returned")
                    continue

                self.printer.print_status_update(f'Battery Pack {device["name"]} is now "In Store"')

            elif device_state == "In Store":
                self.printer.print_status_update(f'{device["name"]} is currently In store')
            else:
                self.printer.print_temp_error("Battery Pack state not recognized")

    def get_barcode(self) -> None:
        self.barcode = ""
        while not self.barcode:
            self.barcode = self.printer.get_input("Enter Barcode: ")
        JsonReader.update_asset_data(self.barcode)

    def process_swipe(self, swipe) -> Union[dict, None]:
        JsonReader.update_user_data(swipe)

        response = Talk.handle_response(
            self.authenticator.talk("get_search",
                                    "https://sacs.sdpondemand.manageengine.com/app/itdesk/api/v3/users/",
                                    JsonReader.get_json("userData.json", "searchParam")))

        return response

    def return_loan(self, user_id, asset_id) -> Union[dict, None]:
        JsonReader.update_loan_creation(HandleTime.get_today_timestamp(True),
                                        HandleTime.get_today_timestamp(False), user_id, asset_id)

        response = Talk.handle_response(self.authenticator.talk(
            "post",
            "https://sacs.sdpondemand.manageengine.com/app/itdesk/api/v3/asset_loans/",
            JsonReader.get_json("createLoan.json", "postParam")
        ))

        return response

    def process_barcode(self, barcode) -> Union[dict, None]:
        self.barcode = barcode

        if self.barcode == "exit":
            exit("User terminated program")

        JsonReader.update_asset_data(self.barcode)
        response = Talk.handle_response(
            self.authenticator.talk("get_search",
                                    "https://sacs.sdpondemand.manageengine.com/app/itdesk/api/v3/assets/",
                                    JsonReader.get_json("assetData.json", "searchParam")))
        return response

    def get_user_loan(self, loaned_asset_id, loan_id) -> Union[dict, None]:

        response = Talk.handle_response(
            self.authenticator.talk("get",
                                    "https://sacs.sdpondemand.manageengine.com/app/itdesk/api/v3"
                                    "/asset_loans/" + str(loan_id) + "/loaned_assets/" +
                                    str(loaned_asset_id) + "/"))
        return response

    def return_device(self, user_id, loaned_asset_id, loan_id) -> Union[dict, None]:
        JsonReader.update_return_asset_data(HandleTime.get_now_timestamp(), "loan system", user_id)

        response = Talk.handle_response(self.authenticator.talk(
            "put",
            "https://sacs.sdpondemand.manageengine.com/app/itdesk/api/v3/asset_loans/" + str(loan_id) +
            "/loaned_assets/" + str(loaned_asset_id) + "/",
            JsonReader.get_json("returnAsset.json", "postParam")
        ))

        return response
