# Created BY: Zack Bailey
# Company: St Andrews Cathedral School
# Called BY: main
# Dependencies: json, os
# Accesses: files in jsonData
# Description:
#    The functions outlined in this document \
#    are used to simplify json operations for \
#    other files in this project

import json
import os
import HandleTime


# Used Function in Talk.
def get_json(file_name: str, folder_name: str) -> object:
    json_folder = "jsonData"
    path = os.path.join(os.getcwd(), json_folder, folder_name, file_name)

    with open(path) as file:
        return json.load(file)


# SAVING JSONS
def overwrite_json(path: str, response: object) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    with open(path, "w") as file:
        json.dump(response, file, indent=4)
        file.truncate()


# UPDATING JSONS
# Used Function by loanSystem.handle_response, loanSystem.first_time_authentication
def save_last_response(response: object) -> None:
    json_folder = "jsonData"
    response_folder = "connectionInfo"
    path = os.path.join(os.getcwd(), json_folder, response_folder, "lastResponse.json")

    overwrite_json(path, response)


def save_log(response: object, log_type: str) -> None:
    json_folder = "jsonData"
    response_folder = "logs"
    # ["Error", "Auth", "First_Auth"]
    path = os.path.join(os.getcwd(), json_folder, response_folder, f"{log_type} at {HandleTime.get_now_timestamp()}.json")

    overwrite_json(path, response)


# Used Function by Talk.refresh
def save_last_refresh(response: object) -> None:
    json_folder = "jsonData"
    response_folder = "connectionInfo"
    path = os.path.join(os.getcwd(), json_folder, response_folder, "lastRefresh.json")

    overwrite_json(path, response)


# CREATING JSONS

# Used Function by handleTime.update_time_search_input
def update_since_last_monday_input_data(time: int) -> None:
    json_folder = "jsonData"
    param_folder = "searchParam"
    path = os.path.join(os.getcwd(), json_folder, param_folder, "lastMonday.json")

    save = {
        "input_data":
            '''{
                "list_info": {
                    "row_count": 100,
                    "search_criteria": {
                        "field": "created_time.value",
                        "condition": "greater than",
                        "value": ''' + str(time) + '''
                    }
                }
            }'''
    }

    overwrite_json(path, save)


# Used Function by loanSystem.trigger_return_battery_pack
def update_return_asset_data(time: int, comment: str, user_id: int):
    json_folder = "jsonData"
    param_folder = "postParam"
    path = os.path.join(os.getcwd(), json_folder, param_folder, "returnAsset.json")

    save = {
        "input_data":
            '''{
                "loaned_asset": {
                    "returned_time": {
                        "value": ''' + str(time) + '''
                    },
                    "comments": ''' + str(comment) + ''',
                    "returned_by": {
                        "id": ''' + str(user_id) + '''
                    }
                }
            }'''
    }

    overwrite_json(path, save)


def update_laptop_barcode(laptop_serial: str) -> None:
    json_folder = "jsonData"
    param_folder = "searchParam"
    path = os.path.join(os.getcwd(), json_folder, param_folder, "laptopBarcode.json")

    save = {
        "input_data":
            '''{
                "list_info": {
                    "start_index": 0,
                    "row_count": 1,
                    "fields_required": ["id", "barcode"],
                    "search_criteria": {
                        "field": "product.product_type.name",
                        "condition": "is",
                        "value": "Student Device",
                        "children" : [ 
                            {
                                "field": "barcode",
                                "condition": "is",
                                "value": ''' + str(laptop_serial) + ''',
                                "logical_operator" : "AND"
                            } 
                        ]
                    }
                }
            }'''
    }

    overwrite_json(path, save)


def update_user_data(swipe_number: str) -> None:
    json_folder = "jsonData"
    param_folder = "searchParam"
    path = os.path.join(os.getcwd(), json_folder, param_folder, "userData.json")

    save = {
        "input_data":
            '''{
                "list_info": {
                    "start_index": 0,
                    "row_count": 1,
                    "fields_required": ["id", "name", "employee_id"],
                    "search_criteria": {
                        "field": "employee_id",
                        "condition": "is",
                        "value": ''' + str(swipe_number) + '''
                    }
                }
            }'''
    }

    overwrite_json(path, save)


def update_asset_data(barcode_number: str) -> None:
    json_folder = "jsonData"
    param_folder = "searchParam"
    path = os.path.join(os.getcwd(), json_folder, param_folder, "assetData.json")

    save = {
        "input_data":
            '''{
                "list_info": {
                    "start_index": 0,
                    "row_count": 1,
                    "fields_required": ["id", "name", "barcode", "state", "loan.id", "loan.loan.id"],
                    "search_criteria": {
                        "field": "barcode",
                        "condition": "is",
                        "value": ''' + str(barcode_number) + '''
                    }
                }
            }'''
    }

    overwrite_json(path, save)


# Used Function in loanSystem.state_decision
def update_loan_creation(start_time: int, due_time: int, user_id: int, asset_id: int) -> None:
    json_folder = "jsonData"
    param_folder = "postParam"
    path = os.path.join(os.getcwd(), json_folder, param_folder, "createLoan.json")

    save = {
        "input_data":
            '''{
                   "asset_loan": {
                       "loaned_assets": [{
                    "asset": {
                        "id": ''' + str(asset_id) + '''
                    }
                }],
                "due_by_time": {
                    "value": ''' + str(due_time) + '''
                },
                "start_time": {
                    "value": ''' + str(start_time) + '''
                },
                "site": null,
                "received_by": {
                    "id": ''' + str(user_id) + '''
                },
                "loaned_to_user": {
                    "id": ''' + str(user_id) + '''
                }
            }
        }'''
    }

    overwrite_json(path, save)


# Used Function in JsonReader.update_parameter_code, JsonReader.update_refresh_token, JsonReader.update_auth_token,
#                  JsonReader.update_scope,
def update_json(file_name: str, folder_name: str, element_id: str, value: str) -> int:
    json_folder = "jsonData"
    path = os.path.join(os.getcwd(), json_folder, folder_name, file_name)

    try:
        with open(path, 'r') as file:
            data = json.load(file)
            data[element_id] = value

        os.remove(path)

        with open(path, 'w') as file:
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()
        return 1

    except FileNotFoundError:
        return 0


# Used Function in loanSystem.__init__, loanSystem.state_decision
def update_scope(*scopes) -> None:
    if not scopes:
        raise ValueError("Expected one input")
    scope_options = {
        "requests": "SDPOnDemand.requests.ALL",
        "problems": "SDPOnDemand.problems.ALL",
        "changes": "SDPOnDemand.changes.ALL",
        "projects": "SDPOnDemand.projects.ALL",
        "assets": "SDPOnDemand.assets.ALL",
        "cmdb": "SDPOnDemand.cmdb.ALL",
        "setup": "SDPOnDemand.setup.ALL",
        "general": "SDPOnDemand.general.ALL",
        "users": "SDPOnDemand.users.All"
    }

    request_scopes = scope_options[scopes[0]]
    scopes = scopes[1:]

    for scope in scopes:
        request_scopes = request_scopes + ", " + scope_options[scope]

    update_json("refreshAuthTokenParameters.json", "authentication", "scope", request_scopes)
