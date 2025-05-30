import unittest
from unittest.mock import patch, MagicMock

from starling_waterfall import StarlingAPI


class TestStarlingAPI(unittest.TestCase):


    def setUp(self):
        """Initialise API instance with mock token."""
        self.api = StarlingAPI("fake_access_token", "fake_account_uid")
        self.balance = {
            "clearedBalance": {
                "currency": "GBP",
                "minorUnits": 123450
            },
            "effectiveBalance": {
                "currency": "GBP",
                "minorUnits": 123451
            },
            "pendingTransactions": {
                "currency": "GBP",
                "minorUnits": 123452
            },
            "acceptedOverdraft": {
                "currency": "GBP",
                "minorUnits": 123453
            },
            "amount": {
                "currency": "GBP",
                "minorUnits": 123454
            },
            "totalClearedBalance": {
                "currency": "GBP",
                "minorUnits": 123455
            },
            "totalEffectiveBalance": {
                "currency": "GBP",
                "minorUnits": 123456
            }
        }
        self.savings_goals = {
            "savingsGoalList": [
                {
                "savingsGoalUid": "77887788-7788-7788-7788-778877887788",
                "name": "Trip to Paris",
                "target": {
                    "currency": "GBP",
                    "minorUnits": 100000
                },
                "totalSaved": {
                    "currency": "GBP",
                    "minorUnits": 50000
                },
                "savedPercentage": 50,
                "state": "ACTIVE"
                },
                {
                "savingsGoalUid": "77887788-7788-7788-7788-778877887789",
                "name": "Rainy Day Fund",
                "target": {
                    "currency": "GBP",
                    "minorUnits": 10000
                },
                "totalSaved": {
                    "currency": "GBP",
                    "minorUnits": 2000
                },
                "savedPercentage": 20,
                "state": "ACTIVE"
                },
            ]
        }
        self.savings_goal_id = "abcdefghij"
        self.recurring_transfer = {
            "transferUid": "88998899-8899-8899-8899-889988998899",
            "recurrenceRule": {
                "startDate": "2023-01-01",
                "frequency": "DAILY",
                "interval": 2,
                "count": 10,
                "untilDate": "2023-01-01",
                "days": [
                "MONDAY"
                ]
            },
            "currencyAndAmount": {
                "currency": "GBP",
                "minorUnits": 123456
            },
            "nextPaymentDate": "2023-01-01"
            }


    @patch("starling_waterfall.requests.get")
    def test_get_balance(self, mock_get):

        mock_response = MagicMock()
        mock_response.json.return_value = self.balance
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        balance = self.api.get_balance()

        self.assertIsInstance(balance, int)
        self.assertEqual(balance, self.balance.get("effectiveBalance").get("minorUnits"))


    @patch("starling_waterfall.requests.get")
    def test_get_savings_goals(self, mock_get):

        mock_response = MagicMock()
        mock_response.json.return_value = self.savings_goals
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        savings_goals = self.api.get_savings_goals()

        self.assertIsInstance(savings_goals, list)
        self.assertIsInstance(savings_goals[0], dict)

        number_of_goals = len(savings_goals)
        self.assertEqual(number_of_goals, 2)
        
        first_savings_goal = self.savings_goals.get("savingsGoalList")[0]
        self.assertDictEqual(first_savings_goal, savings_goals[0])


    @patch("starling_waterfall.requests.get")    
    def test_get_recurring_transfer(self, mock_get):

        mock_response = MagicMock()
        mock_response.json.return_value = self.recurring_transfer
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        recurring_transfer = self.api.get_recurring_transfer(self.savings_goal_id)

        self.assertDictEqual(self.recurring_transfer, recurring_transfer)

    