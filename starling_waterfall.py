import os

import json, requests
from dotenv import load_dotenv
from functools import wraps


def api_request(method):
    """
    Decorator for methods to handle HTTP requests with standardized error handling.

    Args:
        method (str): The HTTP method to use for the request (e.g. 'GET', 'POST),

    Returns:
        function: A wrapper function that executes the decorated method to obtain the request
            URL and data, performs the HTTP request, and returns the parsed JSON response
            or None if an error occurs.

    The decorated method should return a tuple (url, data), where 'data' may be None for methods
    that do not send a request body.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):

            url, data = func(self, *args, **kwargs)

            try:
                response = requests.request(method, url, headers=self.headers, data=data)
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.RequestException as error:
                print(f"API request failed: {error}")
                return None
            
        return wrapper
    
    return decorator


class StarlingAPI:
    """Handles the interaction with Starling Bank's API"""

    BASE_URL = "https://api.starlingbank.com/api/v2"

    def __init__(self, api_token, account_uid):
        self.api_token = api_token
        self.account_uid = account_uid
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }


    @api_request('GET')
    def _get_balance_data(self):
        url = f"{self.BASE_URL}/accounts/{self.account_uid}/balance"
        return url, None

    
    def get_balance(self):
        data = self._get_balance_data()
        if data:
            return data.get("effectiveBalance").get("minorUnits")
        return None
        

    @api_request('GET')
    def _get_savings_goals_data(self):
        url = f"{self.BASE_URL}/account/{self.account_uid}/savings-goals"
        return url, None
    

    def get_savings_goals(self):
        data = self._get_savings_goals_data()
        if data:
            return data.get("savingsGoalList")
        return None


    @api_request('GET')
    def get_recurring_transfer(self, savings_goal_id):
        url = f"{self.BASE_URL}/account/{self.account_uid}/savings-goals/{savings_goal_id}/recurring-transfer"
        return url, None
        

    @api_request('PUT')
    def set_recurring_transfer(self, savings_goal_id, data):
        """
        Sets a recurring transfer for a specified savings goal.

        Args:
            savings_goal_id (str): The ID of the savings goal.
            data (dict): The data for the recurring transfer.

        Returns:
            dict: The response from the API containing the updated recurring transfer details.
        """
        url = f"{self.BASE_URL}/account/{self.account_uid}/savings-goals/{savings_goal_id}/recurring-transfer"
        return url, json.dumps(data)


class RecurrenceRule:

    def __init__(self, start_date: str):
        self.start_date = start_date
        self.frequency = "MONTHLY"

    def to_dict(self):
        return {
            "startDate": self.start_date,
            "frequency": self.frequency,
        }
    

class Amount:

    def __init__(self, minorUnits: int, currency: str ="GBP"):
        self.currency = currency
        self.minorUnits = minorUnits

    def to_dict(self):
        return {
            "currency": self.currency,
            "minorUnits": self.minorUnits
        }


class RecurringTransfer:

    def __init__(self, transfer_uid: str, recurrence_rule: RecurrenceRule, amount: Amount, top_up: bool):
        self.transfer_uid = transfer_uid
        self.recurrence_rule = recurrence_rule
        self.amount = amount
        self.top_up = top_up
    
    def to_dict(self):
        return {
            "transfer_uid": self.transfer_uid,
            "recurrenceRule": self.recurrence_rule.to_dict(),
            "amount": self.amount.to_dict(),
            "topUp": self.top_up
        }
    
    def to_json(self):
        return json.dumps(self.to_dict())
    

class Application:

    def __init__(self, api_token, account_uid):
        self.api = StarlingAPI(api_token, account_uid)

    def run(self):
        self.print_balance()

        self.print_savings_goals()

        self.print_recurring_transfers()
        

    def print_balance(self):
        balance = self.api.get_balance()
        print(f"{'Main balance:':<30} £ {balance / 100:>10}")


    def print_savings_goals(self):
        savings_goals = self.api.get_savings_goals()
        print(f"{'Savings Goals':<30}   {'Balance':>10}")
        print("-" * 43)

        if not savings_goals:
            print("No savings goals found.")
            return

        for goal in savings_goals:
            name = goal.get("name", "Unnamed Goal")
            balance = goal.get("totalSaved").get("minorUnits")
            print(f"{name:<30} £ {balance / 100:>10.2f}")



    def print_recurring_transfer(self, transfer_json):
        name = transfer_json.get("name", transfer_json["transferUid"])
        amount = transfer_json.get("currencyAndAmount").get("minorUnits")
        next_payment_date = transfer_json.get("nextPaymentDate")
        print(f"{name:<16} - {next_payment_date} - £ {amount / 100:>10.02f}")



    def print_recurring_transfers(self):

        savings_goals = self.api.get_savings_goals()

        if not savings_goals:
            print("No savings goals found.")
            return
        
        for goal in savings_goals:
            goal_id = goal.get("savingsGoalUid")
            
            try:
                recurring_transfer = self.api.get_recurring_transfer(goal_id)
                self.print_recurring_transfer(recurring_transfer)
            
            except Exception as e:
                # print(e)
                pass



if __name__ == "__main__":
    load_dotenv()
    api_token = os.getenv("ACCESS_TOKEN")
    account_uid = os.getenv("ACCOUNT_UID")
    app = Application(api_token, account_uid)
    app.run()

# load_dotenv()
# api = StarlingAPI(
#     os.environ.get("ACCESS_TOKEN"),
#     os.environ.get("ACCOUNT_UID")
#     )
# print(api.get_balance())
# savings_goals = api.get_savings_goals()

# for goal in savings_goals:

#     goal_id = goal.get("savingsGoalUid")
    
#     try:
#         recurring_transfer = api.get_recurring_transfer(goal_id)
#         recurrenceRule = recurring_transfer.get("recurrenceRule")
#         recurrenceRule["startDate"] = "2025-07-01"
#         # print(recurring_transfer)

#         data = {
#             "recurrenceRule": recurrenceRule,
#             "amount": recurring_transfer.get("currencyAndAmount"),
#             "topUp": recurring_transfer.get("topUp"),
#         }

#         data = json.dumps(data)

    #     print(data)
    #     new_recurring_transfer = api.set_recurring_transfer(goal_id, data)
    #     print(new_recurring_transfer)

    # except AttributeError as error:
    #     print(error)
    
