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

    def run(self) -> None:
        self.search_device("003819714453")

    def search_device(self, serial: str) -> Union[dict, None]:
        JsonReader.update_laptop_barcode(serial)
        response = Talk.handle_response(
            self.authenticator.talk("get_search",
                                    "https://sacs.sdpondemand.manageengine.com/app/itdesk/api/v3/assets/",
                                    JsonReader.get_json("laptopBarcode.json", "searchParam")))
        return response

    def get_asset_details(self, asset_id: str) -> Union[dict, None]:
        response = Talk.handle_response(
            self.authenticator.talk("get",
                                    "https://sacs.sdpondemand.manageengine.com/app/itdesk/api/v3/assets/" +
                                    str(asset_id)))
        return response

    def return_loan(self, user_id: str, asset_id: str) -> Union[dict, None]:
        JsonReader.update_loan_creation(HandleTime.get_today_timestamp(True),
                                        HandleTime.get_today_timestamp(False), user_id, asset_id)

        response = Talk.handle_response(
            self.authenticator.talk("post",
                                    "https://sacs.sdpondemand.manageengine.com/app/itdesk/api/v3/asset_loans/",
                                    JsonReader.get_json("createLoan.json", "postParam")))
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
                                    "https://sacs.sdpondemand.manageengine.com/app/itdesk/api/v3" +
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
