import requests
from datetime import datetime, timezone, timedelta
from typing import List
from domain.entities import PricePoint
from domain.repositories import PriceRepository

class PorssiSahkoApiClient(PriceRepository):
    def __init__(self, base_url: str = "https://api.porssisahko.net/v1"):
        self.base_url = base_url

    def get_latest_prices(self) -> List[PricePoint]:
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
        prices = self.get_latest_prices()
        now = datetime.now(timezone.utc)
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Filter prices for today
        daily_prices = [
            price for price in prices
            if start_of_today <= price.start_date <= end_of_today
        ]

        # Optionally, you can also fetch prices for the next day if available
        # This can be done by checking the next day's prices in the same way
        start_of_tomorrow = end_of_today + timedelta(days=1)
        end_of_tomorrow = start_of_tomorrow + timedelta(days=1) - timedelta(microseconds=1)

        tomorrow_prices = [
            price for price in prices
            if start_of_tomorrow <= price.start_date <= end_of_tomorrow
        ]

        return daily_prices + tomorrow_prices