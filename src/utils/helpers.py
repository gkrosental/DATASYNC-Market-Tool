"""
Utility functions for data formatting, caching, and helper methods
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
import pickle
import os
from functools import wraps
import time


class Cache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 300):
        self.cache = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            value, expiry = self.cache[key]
            if datetime.now() < expiry:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        if ttl is None:
            ttl = self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = (value, expiry)
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
    
    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)


# Global cache instance
cache = Cache()


def cached(ttl: int = 300):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator


def format_currency(value: float, currency: str = "USD", decimal_places: int = 2) -> str:
    """Format currency value with appropriate symbol"""
    if pd.isna(value) or value is None:
        return "N/A"
    
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'BRL': 'R$',
        'CAD': 'C$',
        'AUD': 'A$',
        'CHF': 'CHF ',
        'CNY': '¥',
        'INR': '₹'
    }
    
    symbol = symbols.get(currency, currency + ' ')
    
    if currency == 'JPY':
        decimal_places = 0  # JPY typically doesn't use decimal places
    
    if symbol in ['$', '€', '£', '¥', '₹']:
        return f"{symbol}{value:,.{decimal_places}f}"
    else:
        return f"{symbol}{value:,.{decimal_places}f}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format percentage value"""
    if pd.isna(value) or value is None:
        return "N/A"
    
    return f"{value:.{decimal_places}f}%"


def format_number(value: Union[int, float], decimal_places: int = 2, 
                 abbreviate: bool = False) -> str:
    """Format large numbers with abbreviations"""
    if pd.isna(value) or value is None:
        return "N/A"
    
    if not abbreviate:
        return f"{value:,.{decimal_places}f}"
    
    # Abbreviate large numbers
    if abs(value) >= 1e12:
        return f"{value/1e12:.{decimal_places}f}T"
    elif abs(value) >= 1e9:
        return f"{value/1e9:.{decimal_places}f}B"
    elif abs(value) >= 1e6:
        return f"{value/1e6:.{decimal_places}f}M"
    elif abs(value) >= 1e3:
        return f"{value/1e3:.{decimal_places}f}K"
    else:
        return f"{value:.{decimal_places}f}"


def format_market_cap(value: float) -> str:
    """Format market capitalization"""
    return format_number(value, decimal_places=1, abbreviate=True)


def format_volume(value: int) -> str:
    """Format trading volume"""
    return format_number(value, decimal_places=0, abbreviate=True)


def calculate_color_for_change(change: float) -> str:
    """Get color based on price change"""
    if change > 0:
        return "green"
    elif change < 0:
        return "red"
    else:
        return "gray"


def get_arrow_for_change(change: float) -> str:
    """Get arrow symbol based on price change"""
    if change > 0:
        return "↗"
    elif change < 0:
        return "↘"
    else:
        return "→"


def calculate_performance_metrics(data: pd.Series) -> Dict[str, float]:
    """Calculate basic performance metrics for a price series"""
    if len(data) < 2:
        return {}
    
    returns = data.pct_change().dropna()
    
    return {
        'total_return': (data.iloc[-1] / data.iloc[0] - 1) * 100,
        'daily_volatility': returns.std() * 100,
        'annualized_volatility': returns.std() * np.sqrt(252) * 100,
        'max_gain': returns.max() * 100,
        'max_loss': returns.min() * 100,
        'avg_daily_return': returns.mean() * 100,
        'positive_days': (returns > 0).sum(),
        'negative_days': (returns < 0).sum(),
        'win_rate': (returns > 0).mean() * 100
    }


def validate_symbol(symbol: str) -> bool:
    """Validate stock symbol format"""
    if not symbol or not isinstance(symbol, str):
        return False
    
    symbol = symbol.strip().upper()
    
    # Basic validation - letters, numbers, dots, hyphens
    allowed_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-=^')
    return all(c in allowed_chars for c in symbol) and len(symbol) <= 20


def clean_symbol(symbol: str) -> str:
    """Clean and standardize symbol format"""
    if not symbol:
        return ""
    
    return symbol.strip().upper()


def parse_period(period_str: str) -> str:
    """Parse and validate period string"""
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    
    if period_str in valid_periods:
        return period_str
    
    # Try to map common inputs
    period_map = {
        '1day': '1d',
        '1week': '5d',
        '1month': '1mo',
        '3months': '3mo',
        '6months': '6mo',
        '1year': '1y',
        '2years': '2y',
        '5years': '5y',
        '10years': '10y'
    }
    
    return period_map.get(period_str.lower(), '1y')


def parse_interval(interval_str: str) -> str:
    """Parse and validate interval string"""
    valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
    
    if interval_str in valid_intervals:
        return interval_str
    
    # Try to map common inputs
    interval_map = {
        '1min': '1m',
        '5min': '5m',
        '15min': '15m',
        '30min': '30m',
        '1hour': '1h',
        '1hr': '1h',
        'daily': '1d',
        'weekly': '1wk',
        'monthly': '1mo'
    }
    
    return interval_map.get(interval_str.lower(), '1d')


def save_to_file(data: Any, filename: str, format: str = 'json') -> bool:
    """Save data to file in various formats"""
    try:
        if format.lower() == 'json':
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        elif format.lower() == 'pickle':
            with open(filename, 'wb') as f:
                pickle.dump(data, f)
        elif format.lower() == 'csv' and isinstance(data, pd.DataFrame):
            data.to_csv(filename, index=True)
        else:
            return False
        
        return True
    except Exception as e:
        print(f"Error saving file {filename}: {e}")
        return False


def load_from_file(filename: str, format: str = 'json') -> Optional[Any]:
    """Load data from file"""
    try:
        if not os.path.exists(filename):
            return None
        
        if format.lower() == 'json':
            with open(filename, 'r') as f:
                return json.load(f)
        elif format.lower() == 'pickle':
            with open(filename, 'rb') as f:
                return pickle.load(f)
        elif format.lower() == 'csv':
            return pd.read_csv(filename, index_col=0)
        else:
            return None
    except Exception as e:
        print(f"Error loading file {filename}: {e}")
        return None


def get_trading_days(start_date: datetime, end_date: datetime) -> int:
    """Calculate number of trading days between two dates"""
    # Simple approximation: 252 trading days per year
    total_days = (end_date - start_date).days
    return int(total_days * 252 / 365)


def is_market_hours(timezone: str = 'US/Eastern') -> bool:
    """Check if it's market hours (simplified for US markets)"""
    now = datetime.now()
    
    # Simple check for US market hours (9:30 AM - 4:00 PM ET)
    # This is a simplified version - real implementation would need proper timezone handling
    weekday = now.weekday()  # 0 = Monday, 6 = Sunday
    
    if weekday >= 5:  # Weekend
        return False
    
    hour = now.hour
    return 9 <= hour <= 16


def calculate_age_of_data(timestamp: datetime) -> str:
    """Calculate and format age of data"""
    if not isinstance(timestamp, datetime):
        return "Unknown"
    
    now = datetime.now()
    if timestamp.tzinfo and not now.tzinfo:
        now = now.replace(tzinfo=timestamp.tzinfo)
    elif not timestamp.tzinfo and now.tzinfo:
        timestamp = timestamp.replace(tzinfo=now.tzinfo)
    
    diff = now - timestamp
    
    if diff.total_seconds() < 60:
        return "Just now"
    elif diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = diff.days
        return f"{days} day{'s' if days != 1 else ''} ago"


def benchmark_function(func):
    """Decorator to benchmark function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"{func.__name__} executed in {execution_time:.4f} seconds")
        return result
    return wrapper


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division that handles division by zero"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default


def extract_company_ticker(full_symbol: str) -> str:
    """Extract base ticker from full symbol (e.g., 'AAPL' from 'AAPL.US')"""
    if '.' in full_symbol:
        return full_symbol.split('.')[0]
    return full_symbol
