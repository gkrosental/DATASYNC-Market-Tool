"""
Base class for all data providers
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime


class BaseDataProvider(ABC):
    """Abstract base class for data providers"""
    
    def __init__(self, name: str):
        self.name = name
        self.last_update = None
        
    @abstractmethod
    def get_stock_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Get stock price data"""
        pass
    
    @abstractmethod
    def get_real_time_price(self, symbol: str) -> Dict[str, Any]:
        """Get real-time stock price"""
        pass
    
    @abstractmethod
    def get_currency_rate(self, from_currency: str, to_currency: str) -> float:
        """Get currency exchange rate"""
        pass
    
    @abstractmethod
    def search_symbols(self, query: str) -> List[Dict[str, str]]:
        """Search for stock symbols"""
        pass
    
    def is_connected(self) -> bool:
        """Check if provider is connected"""
        return True
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information"""
        return {
            "name": self.name,
            "last_update": self.last_update,
            "connected": self.is_connected()
        }
