"""
Domain entities for the Electricity Spot Price Monitor application.
This module defines the core data structures used throughout the application.
"""

from dataclasses import dataclass
from datetime import datetime

@dataclass
class PricePoint:
    """
    Represents a single electricity price point with its time period.
    
    Attributes:
        price (float): The electricity price in cents per kilowatt-hour
        start_date (datetime): The start time of the price period
        end_date (datetime): The end time of the price period
    """
    price: float
    start_date: datetime
    end_date: datetime

@dataclass
class PriceLimits:
    """
    Represents the upper and lower price limits for notifications.
    
    Attributes:
        lower_limit (float): The lower price limit in cents per kilowatt-hour
        upper_limit (float): The upper price limit in cents per kilowatt-hour
    """

    lower_limit: float
    upper_limit: float

    def is_price_within_limits(self, price: float) -> bool:
        """
        Check if a given price is within the set limits.

        Args:
            price (float): The price to check in cents per kilowatt-hour

        Returns:
            bool: True if the price is within limits, False otherwise
        """
        return self.lower_limit <= price <= self.upper_limit 