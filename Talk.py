# Created BY: Zack Bailey
# Company: St Andrews Cathedral School
# Called BY: main
# Dependencies: requests, jsonReader
# Accesses:
# Description:
#    The functions outlined in this document \
#    communicate with the service-desk API \
#    for the SACS help-desk system.

import requests
import JsonReader
import HandleTime
from typing import Union


# Used class in loanSystem.__init__
class Authenticator:
    def __init__(self):
        self.current_scope = ""
        self.last_refresh = HandleTime.get_now_timestamp()
        self.auth_credentials_filename = "authenticationCredentials.json"
        self.auth_setup_filename = "firstContactAuthenticationParameters.json"
        self.auth_refresh_filename = "refreshAuthTokenParameters.json"
        self.auth_folder_name = "authentication"

        self.auth_credentials_file = lambda: JsonReader.get_json(self.auth_credentials_filename,
                                                                 self.auth_folder_name)

        self.auth_refresh_file = lambda: JsonReader.get_json(self.auth_refresh_filename,
                                                             self.auth_folder_name)

        self.auth_setup_file = lambda: JsonReader.get_json(self.auth_setup_filename,
                                                           self.auth_folder_name)

    def authenticate(self, code: str = ""):
        # code is used to set up first time authentication from
        if code:
            JsonReader.update_json(self.auth_setup_filename, self.auth_folder_name, "code", str(code))
            response = self.talk("post", "https://accounts.zoho.com/oauth/v2/token", self.auth_setup_file())
        else:
            response = self.talk("post", "https://accounts.zoho.com/oauth/v2/token", self.auth_refresh_file())

        response_json = response.json()
        JsonReader.save_last_refresh(response_json)
        try:
            if code:
                JsonReader.update_json(self.auth_refresh_filename, self.auth_folder_name, "refresh_token",
                                       response_json["refresh_token"])

            JsonReader.update_json(self.auth_credentials_filename, self.auth_folder_name, "Authorization",
                                   "Zoho-oauth" + "token " + response_json["access_token"])
        except KeyError:
            if code:
                return 2
                # UNEXPECTED RESPONSE WHILE TRYING TO INITIATE AUTHENTICATION
            else:
                return 1
                # UNEXPECTED RESPONSE WHILE TRYING TO RENEW AUTHENTICATION
        self.last_refresh = HandleTime.get_now_timestamp()
        return 0

    # Used Method
    def talk(self, action: str, url: str, param: object = "") -> type(requests.models.Response):
        self.update_scope(url)
        if self.last_refresh - HandleTime.get_now_timestamp() > 3500:
            self.authenticate()

        auth_header = self.auth_credentials_file()

        actions = {
            "get": lambda: requests.get(url, headers=auth_header),
            "get_search": lambda: requests.get(url, param, headers=auth_header),
            "post": lambda: requests.post(url, param, headers=auth_header),
            "put": lambda: requests.put(url, param, headers=auth_header)
        }
        return actions[action]()

    def update_scope(self, url: str) -> None:
        # possible scopes = ["requests", "problems", "changes", "projects", "assets", "cmdb", "setup", "general"]
        if "user" in url:
            new_scope = "users"
        elif "asset" in url:
            new_scope = "assets"
        else:
            new_scope = "general"

        if self.current_scope == new_scope or "token" in url:
            return

        JsonReader.update_scope(new_scope)
        self.current_scope = new_scope
        # force authentication not check_auth because of scope change
        self.authenticate()


# Used Function by loanSystem.trigger_return_battery_pack
def handle_response(response: type(requests.models.Response)) -> Union[dict, None]:
    if response.status_code != 200:
        print(response)
        print(response.status_code)
        return None
    response_json = response.json()
    JsonReader.save_last_response(response_json)
    return response_json
