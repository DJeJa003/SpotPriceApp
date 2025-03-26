import pytest
from datetime import datetime, timezone, timedelta
from data.api_client import PorssiSahkoApiClient
from domain.entities import PricePoint

class MockDateTime:
    @classmethod
    def now(cls, tz=None):
        return datetime(2024, 3, 25, 12, 30, tzinfo=timezone.utc)
    
    @classmethod
    def fromisoformat(cls, date_string):
        # Handle the 'Z' timezone designator
        if date_string.endswith('Z'):
            date_string = date_string[:-1] + '+00:00'
        return datetime.fromisoformat(date_string)

def test_get_latest_prices(mocker):
    # Mock the API response
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
    
    mock_response_obj = mocker.Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status.return_value = None
    
    mocker.patch('requests.get', return_value=mock_response_obj)
    
    client = PorssiSahkoApiClient()
    prices = client.get_latest_prices()
    
    assert len(prices) == 2
    assert isinstance(prices[0], PricePoint)
    assert prices[0].price == 13.494
    assert isinstance(prices[0].start_date, datetime)
    assert isinstance(prices[0].end_date, datetime)

def test_get_current_and_next_hour_prices(mocker):
    # Create test data with fixed time
    current_hour = datetime(2024, 3, 25, 12, 0, tzinfo=timezone.utc)
    
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
    
    mock_response_obj = mocker.Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status.return_value = None
    
    mocker.patch('requests.get', return_value=mock_response_obj)
    mocker.patch('data.api_client.datetime', MockDateTime)
    
    client = PorssiSahkoApiClient()
    current_price, next_price = client.get_current_and_next_hour_prices()
    
    assert current_price.price == 17.62
    assert next_price.price == 15.0 