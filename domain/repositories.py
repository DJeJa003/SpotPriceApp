from abc import ABC, abstractmethod
from typing import List
from .entities import PricePoint

class PriceRepository(ABC):
    @abstractmethod
    def get_latest_prices(self) -> List[PricePoint]:
        """Fetch the latest electricity prices from the API."""
        pass

    @abstractmethod
    def get_current_and_next_hour_prices(self) -> tuple[PricePoint, PricePoint]:
        """Get the current hour's price and the next hour's price."""
        pass 