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
    def __init__(self, code: str = ""):
        self.current_scope = ""
        self.last_refresh = HandleTime.get_now_timestamp()
        self.auth_credentials_filename = "authenticationCredentials.json"
        self.auth_setup_filename = "firstContactAuthenticationParameters.json"
        self.auth_refresh_filename = "refreshAuthTokenParameters.json"
        self.auth_folder_name = "authentication"

        self.session = requests.session()

        self.auth_credentials_file = lambda: JsonReader.get_json(self.auth_credentials_filename,
                                                                 self.auth_folder_name)

        self.auth_refresh_file = lambda: JsonReader.get_json(self.auth_refresh_filename,
                                                             self.auth_folder_name)

        self.auth_setup_file = lambda: JsonReader.get_json(self.auth_setup_filename,
                                                           self.auth_folder_name)

        if code:
            JsonReader.update_json(self.auth_setup_filename,
                                   self.auth_folder_name,
                                   "code",
                                   str(code)
                                   )
            response = self.talk("post", "https://accounts.zoho.com/oauth/v2/token", self.auth_setup_file())
            while response is None:
                response = self.talk("post", "https://accounts.zoho.com/oauth/v2/token", self.auth_setup_file())

            response_json = response.json()
            JsonReader.save_log(response_json, "first_auth")
            try:
                JsonReader.update_json(self.auth_refresh_filename,
                                       self.auth_folder_name,
                                       "refresh_token",
                                       response_json["refresh_token"]
                                       )
            except KeyError:
                exit("FATAL ERROR: Could not complete initial authentication with code.")
        else:
            self.authenticate()

    def authenticate(self):
        # code is used to set up first time authentication from
        response = self.talk("post", "https://accounts.zoho.com/oauth/v2/token", self.auth_refresh_file())
        response_json = response.json()
        JsonReader.save_log(response_json, "auth")

        try:
            JsonReader.update_json(self.auth_credentials_filename,
                                   self.auth_folder_name,
                                   "Authorization",
                                   "Zoho-oauth" + "token " + response_json["access_token"]
                                   )

        except KeyError:
            return 1
            # UNEXPECTED RESPONSE WHILE TRYING TO RENEW AUTHENTICATION

        self.last_refresh = HandleTime.get_now_timestamp()
        return 0

    # Used Method
    def talk(self, action: str, url: str, param: object = "") -> Union[type(requests.models.Response), None]:
        timeout = 3
        self.update_scope(url)
        if self.last_refresh - HandleTime.get_now_timestamp() > 3500:
            self.authenticate()

        self.session.headers = self.auth_credentials_file()
        self.session.params = param

        actions = {
            "get": lambda: self.session.get(url, timeout=timeout),
            "get_search": lambda: self.session.get(url, timeout=timeout),
            "post": lambda: self.session.post(url, timeout=timeout),
            "put": lambda: self.session.put(url, timeout=timeout)
        }

        try:
            return actions[action]()
        except requests.exceptions.ConnectionError:
            self.session = requests.session()
            return None

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
    try:
        response_json = response.json()
    except TypeError:
        return None
    if not response.ok():
        JsonReader.save_log(response_json, "Bad response")
        return None
    JsonReader.save_last_response(response_json)
    return response_json
