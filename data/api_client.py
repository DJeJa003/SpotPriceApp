"""
API client for fetching electricity spot prices from the Porssisahko API.
This module implements the PriceRepository interface to provide price data
from the external API service.
"""

import requests
from datetime import datetime, timezone, timedelta
from typing import List
from domain.entities import PricePoint
from domain.repositories import PriceRepository

class PorssiSahkoApiClient(PriceRepository):
    """
    Client for interacting with the Porssisahko electricity price API.
    Implements the PriceRepository interface to provide price data.
    """

    def __init__(self, base_url: str = "https://api.porssisahko.net/v1"):
        """
        Initialize the API client with the base URL.

        Args:
            base_url (str): The base URL for the Porssisahko API
        """
        self.base_url = base_url

    def get_latest_prices(self) -> List[PricePoint]:
        """
        Fetch the latest electricity prices from the API.
        Makes a GET request to the latest-prices endpoint and converts the response
        into PricePoint objects.

        Returns:
            List[PricePoint]: List of price points containing price and time information

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        response = requests.get(f"{self.base_url}/latest-prices.json")
        response.raise_for_status()
        
        data = response.json()
        return [
            PricePoint(
                price=price_data["price"],
                start_date=datetime.fromisoformat(price_data["startDate"].replace("Z", "+00:00")),
                end_date=datetime.fromisoformat(price_data["endDate"].replace("Z", "+00:00"))
            )
            for price_data in data["prices"]
        ]

    def get_current_and_next_hour_prices(self) -> tuple[PricePoint, PricePoint]:
        """
        Get the current hour's price and the next hour's price.
        Fetches all prices and filters for the current and next hour.

        Returns:
            tuple[PricePoint, PricePoint]: Tuple containing (current_price, next_price)

        Raises:
            ValueError: If current or next hour price cannot be found
        """
        prices = self.get_latest_prices()
        now = datetime.now(timezone.utc)
        prices.sort(key=lambda price: price.start_date)
        # Find the current price
        current_price = next(
            (price for price in prices if price.start_date <= now < price.end_date),
            None
        )

        if not current_price:
            raise ValueError("No current price found")

        # Find the next price
        next_price = next(
            (price for price in prices if price.start_date == current_price.end_date),
            None
        )

        if not next_price:
            raise ValueError("No next hour price found")

        return current_price, next_price

    def get_daily_prices(self) -> List[PricePoint]:
        """
        Get electricity prices for the current day and next day.
        Filters the latest prices to include only today's and tomorrow's prices.

        Returns:
            List[PricePoint]: List of price points for today and tomorrow
        """
        prices = self.get_latest_prices()
        now = datetime.now(timezone.utc)
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = start_of_today + timedelta(days=1) - timedelta(microseconds=1)
        start_of_tomorrow = end_of_today + timedelta(microseconds=1)
        end_of_tomorrow = start_of_tomorrow + timedelta(days=1) - timedelta(microseconds=1)

        # Filter prices for today and tomorrow
        daily_prices = [
            price for price in prices
            if (start_of_today <= price.start_date <= end_of_today) or
               (start_of_tomorrow <= price.start_date <= end_of_tomorrow)
        ]

        return daily_prices