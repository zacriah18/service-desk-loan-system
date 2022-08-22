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
            # Get Battery Pack

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
                battery_pack = response["assets"][0]
            # battery pack was not found
            except (KeyError, IndexError):
                self.printer.print_detailed_error("Battery Pack not found",
                                                  "No Battery Packs were returned by the server",
                                                  "Please ensure scanned barcode matches digits on Label")
                continue

            # Check state of battery pack
            try:
                battery_pack_state = battery_pack["state"]["name"]
            except KeyError:
                self.printer.print_temp_error("Battery Pack state not found")
                continue

            self.printer.center_text(f'Battery Pack {battery_pack["name"]} is {battery_pack_state}')

            if battery_pack_state == "In Use":

                self.printer.print_status_update("Attempting to return Battery Pack")

                try:
                    loaned_asset_id = battery_pack["loan"]["id"]
                    loan_id = battery_pack["loan"]["loan"]["id"]
                except KeyError:
                    self.printer.print_detailed_error("Battery Pack is in use but not on loan",
                                                      "The details for this battery pack are not setup for loan",
                                                      "Please contact IT if this battery pack should be loanable")
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

                self.printer.print_status_update(f'Battery Pack {battery_pack["name"]} is now "In Store"')

            elif battery_pack_state == "In Store":
                self.printer.print_status_update("Attempting to loan Battery Pack")

                self.get_swipe()

                if self.swipe == "skip":
                    continue

                response = Talk.handle_response(
                    self.authenticator.talk("get_search",
                                            "https://sacs.sdpondemand.manageengine.com/app/itdesk/api/v3/users/",
                                            JsonReader.get_json("userData.json", "searchParam")))

                if response is None:
                    self.printer.print_connection_error("request_user_details")
                    continue

                try:
                    user_id = response["users"][0]["id"]
                except KeyError:
                    self.printer.print_detailed_error("Student Card is not found",
                                                      "No students with matching ID was found by the server",
                                                      "Please see IT to update student information")
                    continue

                asset_id = battery_pack["id"]

                JsonReader.update_loan_creation(HandleTime.get_today_timestamp(True),
                                                HandleTime.get_today_timestamp(False), user_id, asset_id)

                response = Talk.handle_response(self.authenticator.talk(
                        "post",
                        "https://sacs.sdpondemand.manageengine.com/app/itdesk/api/v3/asset_loans/",
                        JsonReader.get_json("createLoan.json", "postParam")
                    ))

                if response is None:
                    self.printer.print_connection_error("Put request create loan")
                    continue

                self.printer.print_status_update(f'Successfully loaned Battery Pack {battery_pack["name"]} to User')
            else:
                self.printer.print_temp_error("Battery Pack state not recognized")

    def get_barcode(self) -> None:
        self.barcode = ""
        while not self.barcode:
            self.barcode = self.printer.get_input("Enter Barcode: ")
        JsonReader.update_asset_data(self.barcode)

    def get_swipe(self) -> None:
        self.swipe = ""
        while not self.swipe:
            self.swipe = self.printer.get_input("Enter swipe: ")
        JsonReader.update_user_data(self.swipe)

    def process_barcode(self) -> None:
        battery_pack = None
        battery_pack_list = Talk.handle_response(
            self.authenticator.talk("get_search",
                                    "https://sacs.sdpondemand.manageengine.com/app/itdesk/api/v3/assets/",
                                    JsonReader.get_json("batteryPackSearchParam.json", "searchParam")))["assets"]
        if battery_pack_list:
            # if not empty iterator over assets in response
            for asset in battery_pack_list:
                if asset["name"] == self.barcode:
                    # find battery back associated to barcode
                    battery_pack = asset
        return battery_pack
