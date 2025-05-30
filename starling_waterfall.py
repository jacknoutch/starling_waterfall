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


# load_dotenv()
# api = StarlingAPI(
#     os.environ.get("ACCESS_TOKEN"),
#     os.environ.get("ACCOUNT_UID")
#     )
# print(api.get_balance())
# savings_goals = api.get_savings_goals()

# for goal in savings_goals:
#     print(api.get_recurring_transfer(goal.get("savingsGoalUid")))