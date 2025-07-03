import os

import json, requests
from dotenv import load_dotenv


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


    def get_balance(self):
        url = f"{self.BASE_URL}/accounts/{self.account_uid}/balance"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            effectiveBalance = response.json().get("effectiveBalance").get("minorUnits")
            return effectiveBalance
        
        except requests.exceptions.RequestException as error:
            print(error)
            return None
        
    
    def get_savings_goals(self):
        url = f"{self.BASE_URL}/account/{self.account_uid}/savings-goals"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            savings_goals = response.json().get("savingsGoalList")
            return savings_goals

        except requests.exceptions.RequestException as error:
            print(error)
            return None


    def get_recurring_transfer(self, savings_goal_id):
        
        url = f"{self.BASE_URL}/account/{self.account_uid}/savings-goals/{savings_goal_id}/recurring-transfer"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            recurring_transfer = response.json()
            return recurring_transfer

        except requests.exceptions.RequestException as error:
            print(error)
            return error
        

    def set_recurring_transfer(self, savings_goal_id, data):

        url = f"{self.BASE_URL}/account/{self.account_uid}/savings-goals/{savings_goal_id}/recurring-transfer"

        try:
            response = requests.put(url, headers=self.headers, data=data)
            response.raise_for_status()
            recurring_transfer = response.json()
            return recurring_transfer
        
        except requests.exceptions.RequestException as error:
            print(error)
            return error


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
        balance = self.api.get_balance()
        print(f"Balance: {balance}")

        savings_goals = self.api.get_savings_goals()
        print(f"Savings Goals: {savings_goals}")

        for goal in savings_goals:
            goal_id = goal.get("savingsGoalUid")
            try:
                recurring_transfer = self.api.get_recurring_transfer(goal_id)
                print(f"Recurring Transfer for {goal_id}: {recurring_transfer}")
            except Exception as e:
                print(f"Error fetching recurring transfer for {goal_id}: {e}")


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
    