from dataclasses import dataclass
from datetime import datetime

@dataclass
class PricePoint:
    price: float
    start_date: datetime
    end_date: datetime

@dataclass
class PriceLimits:
    lower_limit: float
    upper_limit: float

    def is_price_within_limits(self, price: float) -> bool:
        return self.lower_limit <= price <= self.upper_limit 