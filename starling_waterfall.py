# Standard library imports
import json, os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

# Local imports
from utils import *


class StarlingAPI:
    """
    A class to interact with the Starling Bank API.
    """

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


class RecurrenceRule(BaseModel):
    startDate: str
    frequency: str = "MONTHLY"


class Amount(BaseModel):
    currency: str = "GBP"
    minorUnits: int


class RecurringTransfer(BaseModel):
    description: Optional[str] = None
    transferUid: str
    recurrenceRule: RecurrenceRule
    currencyAndAmount: Amount
    # top_up: bool
    reference: Optional[str] = None


class SavingsSpace(BaseModel):
    savingsGoalUid: str
    name: str
    target: Optional[Amount] = None
    totalSaved: Amount
    savedPercentage: Optional[int] = None
    # target_date: str = None
    # recurring_transfer: RecurringTransfer = None
    state: str
    recurringTransfer: Optional[RecurringTransfer] = None


class Application():

    def __init__(self, api_token, account_uid):
        self.api = StarlingAPI(api_token, account_uid)
        self.balance = Amount.model_validate(self.api._get_balance_data()["effectiveBalance"])
        self.spaces = []

        self.refresh_spaces()  # Load savings goals on initialization


    def run(self):
        self.print_balance()

        self.print_savings_goals()

        self.print_recurring_transfers()

        self.print_waterfall_total()

        user_input = input("Would you like to proceed with the waterfall process? (y/n): ").strip().lower()

        if user_input == "y":
            self.execute_waterfall()
        else:
            print("Waterfall process aborted.")


    def execute_waterfall(self):
        """
        Executes the waterfall process by distributing the respective amount to each savings goal according to its
        recurring transfer settings and putting back the date of the next transfer to the first of the next month.
        """
        self.spaces = self._refresh_spaces_if_needed()

        if not self.spaces:
            print("No savings goals found.")
            return

        total_recurring = self.calculate_waterfall_total()

        if total_recurring == 0:
            print("No recurring payments found. Nothing to distribute.")
            return

        # Make sure there is a balance to distribute
        if self.balance.minorUnits < total_recurring:
            print(f"Insufficient balance to distribute. Available: £ {self.balance.minorUnits / 100:.2f}, Required: £ {total_recurring / 100:.2f}")
            return

        print("Starting waterfall process...")

        for space in self.spaces:
            if space.recurringTransfer:
                transfer_amount = space.recurringTransfer.currencyAndAmount.minorUnits
                if transfer_amount > 0:
                    print(f"Distributing £ {transfer_amount / 100:.2f} to {space.name}")
                    self.api.set_recurring_transfer(space.savingsGoalUid, space.recurringTransfer.model_dump())
                else:
                    print(f"No recurring transfer set for {space.name}")

        print("Waterfall process completed.")


    def calculate_waterfall_total(self):
        """
        Calculates the total amount of money available for the waterfall process.
        This is the sum of all recurring payments.
        """
        total_recurring = sum(space.recurringTransfer.currencyAndAmount.minorUnits for space in self.spaces if space.recurringTransfer)
        return total_recurring
    

    def print_waterfall_total(self):
        """
        Prints the total amount of money available for the waterfall process.
        """
        total = self.calculate_waterfall_total()
        print("=" * 53)
        print(f"{'Waterfall Total':<40}   {'Amount':>10}")
        print("-" * 53)
        print(f"{'Total recurring payments:':<40} £ {total / 100:>10.2f}")
        print("=" * 53)
        print()


    def refresh_spaces(self):
        """
        Refreshes the data for savings goals (spaces) from the API, returning them as a list of SavingsSpace objects.
        """
        savings_goals = self.api.get_savings_goals()

        for goal in savings_goals:
            totalSaved = Amount.model_validate(goal.get("totalSaved"))
            goal["totalSaved"] = totalSaved
            savings_space = SavingsSpace.model_validate(goal)
            
            recurring_transfer = self.api.get_recurring_transfer(savings_space.savingsGoalUid)
            
            if recurring_transfer:
                transform_childs_class(recurring_transfer, "recurrenceRule", RecurrenceRule)
                transform_childs_class(recurring_transfer, "currencyAndAmount", Amount)
                savings_space.recurringTransfer = RecurringTransfer.model_validate(recurring_transfer)
            
            self.spaces.append(savings_space)

        return self.spaces


    def _refresh_spaces_if_needed(self):
        """
        Checks if the spaces list is empty and refreshes it if necessary.
        """
        if not self.spaces:
            print("Refreshing savings goals...")
            self.refresh_spaces()
        return self.spaces


    def print_balance(self):
        print("=" * 53)
        print(f"{'Savings Goals':<40}   {'Balance':>10}")
        print("-" * 53)
        print(f"{'Main balance:':<40} £ {self.balance.minorUnits / 100:>10}")
        print("=" * 53)
        print()


    def print_savings_goals(self):
        """
        Prints the savings goals and their balances.
        """

        self.spaces = self._refresh_spaces_if_needed()

        if not self.spaces:
            print("No savings goals found.")
            return

        print("=" * 53)
        print(f"{'Savings Goals':<40}   {'Balance':>10}")
        print("-" * 53)

        for goal in self.spaces:
            name = goal.name if goal.name else "Unnamed Goal"
            balance = goal.totalSaved.minorUnits
            print(f"{name:<40} £ {balance / 100:>10.2f}")

        print("=" * 53)
        print()


    def print_recurring_transfer(self, transfer_json):
        name = transfer_json.get("name", transfer_json["transferUid"])
        amount = transfer_json.get("currencyAndAmount").get("minorUnits")
        next_payment_date = transfer_json.get("nextPaymentDate")
        print(f"{name:<26} - {next_payment_date} - £ {amount / 100:>10.02f}")



    def print_recurring_transfers(self):

        self.spaces = self._refresh_spaces_if_needed()

        if not self.spaces:
            print("No savings goals found.")
            return
        
        print("=" * 53)
        print(f"{'Savings Goals':<29}{'Next Date'}{'Amount':>15}")
        print("-" * 53)

        for goal in self.spaces:
            if goal.recurringTransfer:
                next_payment_date = goal.recurringTransfer.recurrenceRule.startDate
                amount = goal.recurringTransfer.currencyAndAmount.minorUnits
                print(f"{goal.name:<29}{next_payment_date}  £ {amount / 100:>10.02f}")
            else:
                print(f"{goal.name:<29}   {'No recurring transfer':>21}")

        print("=" * 53)
        print()


if __name__ == "__main__":
    load_dotenv()
    api_token = os.getenv("ACCESS_TOKEN")
    account_uid = os.getenv("ACCOUNT_UID")
    app = Application(api_token, account_uid)
    app.run()