import pytest
from datetime import datetime, timezone
from domain.entities import PricePoint, PriceLimits

def test_price_point():
    start_date = datetime(2022, 11, 14, 22, 0, tzinfo=timezone.utc)
    end_date = datetime(2022, 11, 14, 23, 0, tzinfo=timezone.utc)
    
    price_point = PricePoint(price=13.494, start_date=start_date, end_date=end_date)
    
    assert price_point.price == 13.494
    assert price_point.start_date == start_date
    assert price_point.end_date == end_date

def test_price_limits():
    limits = PriceLimits(lower_limit=10.0, upper_limit=20.0)
    
    assert limits.is_price_within_limits(15.0) == True
    assert limits.is_price_within_limits(10.0) == True
    assert limits.is_price_within_limits(20.0) == True
    assert limits.is_price_within_limits(9.99) == False
    assert limits.is_price_within_limits(20.01) == False 