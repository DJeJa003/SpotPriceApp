import pytest
from datetime import datetime, timezone, timedelta
from data.api_client import PorssiSahkoApiClient
from domain.entities import PricePoint

class MockDateTime:
    """
    A mock datetime class used for testing time-dependent functionality.
    This class provides a fixed datetime value to ensure consistent test results.
    """
    @classmethod
    def now(cls, tz=None):
        """
        Returns a fixed datetime for testing purposes.
        This ensures that time-dependent tests are deterministic.
        """
        return datetime(2024, 3, 25, 12, 30, tzinfo=timezone.utc)
    
    @classmethod
    def fromisoformat(cls, date_string):
        """
        Parses an ISO format date string into a datetime object.
        Handles the 'Z' timezone designator by converting it to '+00:00'.
        
        Args:
            date_string (str): ISO format date string, optionally ending with 'Z'
            
        Returns:
            datetime: Parsed datetime object
        """
        # Handle the 'Z' timezone designator
        if date_string.endswith('Z'):
            date_string = date_string[:-1] + '+00:00'
        return datetime.fromisoformat(date_string)

def test_get_latest_prices(mocker):
    """
    Test the get_latest_prices method of PorssiSahkoApiClient.
    Verifies that the API response is correctly parsed into PricePoint objects.
    """
    # Mock the API response with sample price data
    mock_response = {
        "prices": [
            {
                "price": 13.494,
                "startDate": "2022-11-14T22:00:00.000Z",
                "endDate": "2022-11-14T23:00:00.000Z"
            },
            {
                "price": 17.62,
                "startDate": "2022-11-14T21:00:00.000Z",
                "endDate": "2022-11-14T22:00:00.000Z"
            }
        ]
    }
    
    # Set up the mock response object with required methods
    mock_response_obj = mocker.Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status.return_value = None
    
    # Mock the requests.get function to return our mock response
    mocker.patch('requests.get', return_value=mock_response_obj)
    
    # Create client instance and fetch prices
    client = PorssiSahkoApiClient()
    prices = client.get_latest_prices()
    
    # Verify the response
    assert len(prices) == 2  # Check number of price points
    assert isinstance(prices[0], PricePoint)  # Verify correct type
    assert prices[0].price == 13.494  # Check price value
    assert isinstance(prices[0].start_date, datetime)  # Verify datetime type
    assert isinstance(prices[0].end_date, datetime)  # Verify datetime type

def test_get_current_and_next_hour_prices(mocker):
    """
    Test the get_current_and_next_hour_prices method of PorssiSahkoApiClient.
    Verifies that the method correctly identifies and returns the current and next hour prices.
    """
    # Create test data with fixed time for deterministic testing
    current_hour = datetime(2024, 3, 25, 12, 0, tzinfo=timezone.utc)
    
    # Mock the API response with three consecutive hours of price data
    mock_response = {
        "prices": [
            {
                "price": 13.494,
                "startDate": (current_hour - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "endDate": current_hour.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            },
            {
                "price": 17.62,
                "startDate": current_hour.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "endDate": (current_hour + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            },
            {
                "price": 15.0,
                "startDate": (current_hour + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "endDate": (current_hour + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            }
        ]
    }
    
    # Set up the mock response object with required methods
    mock_response_obj = mocker.Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status.return_value = None
    
    # Mock both the API request and datetime for consistent testing
    mocker.patch('requests.get', return_value=mock_response_obj)
    mocker.patch('data.api_client.datetime', MockDateTime)
    
    # Create client instance and fetch current and next hour prices
    client = PorssiSahkoApiClient()
    current_price, next_price = client.get_current_and_next_hour_prices()
    
    # Verify the correct prices are returned
    assert current_price.price == 17.62  # Current hour price
    assert next_price.price == 15.0  # Next hour price 