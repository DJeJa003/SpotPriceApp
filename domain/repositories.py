"""
Repository interface definitions for the Electricity Spot Price Monitor application.
This module defines the abstract base classes that specify the contract for
price data access implementations.
"""

from abc import ABC, abstractmethod
from typing import List
from .entities import PricePoint

class PriceRepository(ABC):
    """
    Abstract base class defining the interface for price data access.
    Concrete implementations must provide methods for fetching price data
    from various sources (e.g., API, database, etc.).
    """

    @abstractmethod
    def get_latest_prices(self) -> List[PricePoint]:
        """
        Fetch the latest electricity prices from the data source.

        Returns:
            List[PricePoint]: List of price points containing price and time information
        """
        pass

    @abstractmethod
    def get_current_and_next_hour_prices(self) -> tuple[PricePoint, PricePoint]:
        """
        Get the current hour's price and the next hour's price.

        Returns:
            tuple[PricePoint, PricePoint]: Tuple containing (current_price, next_price)

        Raises:
            ValueError: If current or next hour price cannot be found
        """
        pass 