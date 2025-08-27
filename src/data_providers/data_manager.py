"""
Data Provider Manager
Manages all data providers and provides unified interface
"""
from typing import Dict, List, Optional, Any, Union
import pandas as pd
from datetime import datetime
from .yahoo_finance import YahooFinanceProvider
from .news_provider import NewsProvider


class DataProviderManager:
    """Manages all data providers with unified interface"""
    
    def __init__(self):
        self.providers = {}
        self.news_provider = None
        self._initialize_providers()
        
    def _initialize_providers(self):
        """Initialize all available data providers"""
        # Initialize Yahoo Finance (primary provider)
        try:
            self.providers['yahoo'] = YahooFinanceProvider()
            print("✓ Yahoo Finance provider initialized")
        except Exception as e:
            print(f"✗ Failed to initialize Yahoo Finance: {e}")
        
        # Initialize News provider
        try:
            self.news_provider = NewsProvider()
            print("✓ News provider initialized")
        except Exception as e:
            print(f"✗ Failed to initialize News provider: {e}")
    
    def get_stock_data(self, symbol: str, period: str = "1y", interval: str = "1d", provider: str = "yahoo") -> pd.DataFrame:
        """Get stock data from specified provider"""
        if provider not in self.providers:
            raise ValueError(f"Provider '{provider}' not available")
        
        return self.providers[provider].get_stock_data(symbol, period, interval)
    
    def get_real_time_price(self, symbol: str, provider: str = "yahoo") -> Dict[str, Any]:
        """Get real-time stock price"""
        if provider not in self.providers:
            raise ValueError(f"Provider '{provider}' not available")
        
        return self.providers[provider].get_real_time_price(symbol)
    
    def get_multiple_prices(self, symbols: List[str], provider: str = "yahoo") -> Dict[str, Dict[str, Any]]:
        """Get real-time prices for multiple symbols"""
        results = {}
        
        for symbol in symbols:
            try:
                results[symbol] = self.get_real_time_price(symbol, provider)
            except Exception as e:
                results[symbol] = {'error': str(e)}
        
        return results
    
    def get_currency_rate(self, from_currency: str, to_currency: str, provider: str = "yahoo") -> float:
        """Get currency exchange rate"""
        if provider not in self.providers:
            raise ValueError(f"Provider '{provider}' not available")
        
        return self.providers[provider].get_currency_rate(from_currency, to_currency)
    
    def get_currency_rates(self, base_currency: str, target_currencies: List[str], provider: str = "yahoo") -> Dict[str, float]:
        """Get multiple currency exchange rates"""
        rates = {}
        
        for currency in target_currencies:
            try:
                rates[currency] = self.get_currency_rate(base_currency, currency, provider)
            except Exception as e:
                rates[currency] = None
        
        return rates
    
    def search_symbols(self, query: str, provider: str = "yahoo") -> List[Dict[str, str]]:
        """Search for stock symbols"""
        if provider not in self.providers:
            raise ValueError(f"Provider '{provider}' not available")
        
        return self.providers[provider].search_symbols(query)
    
    def get_company_info(self, symbol: str, provider: str = "yahoo") -> Dict[str, Any]:
        """Get detailed company information"""
        if provider not in self.providers:
            raise ValueError(f"Provider '{provider}' not available")
        
        if hasattr(self.providers[provider], 'get_company_info'):
            return self.providers[provider].get_company_info(symbol)
        else:
            raise NotImplementedError(f"Provider '{provider}' does not support company info")
    
    def get_financial_data(self, symbol: str, provider: str = "yahoo") -> Dict[str, pd.DataFrame]:
        """Get financial statements data"""
        if provider not in self.providers:
            raise ValueError(f"Provider '{provider}' not available")
        
        if hasattr(self.providers[provider], 'get_financial_data'):
            return self.providers[provider].get_financial_data(symbol)
        else:
            raise NotImplementedError(f"Provider '{provider}' does not support financial data")
    
    def get_market_news(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get latest market news"""
        if not self.news_provider:
            raise ValueError("News provider not available")
        
        return self.news_provider.get_market_news(limit)
    
    def search_news(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for news containing specific keywords"""
        if not self.news_provider:
            raise ValueError("News provider not available")
        
        return self.news_provider.search_news(query, limit)
    
    def get_trending_topics(self) -> List[Dict[str, Any]]:
        """Get trending topics from news"""
        if not self.news_provider:
            raise ValueError("News provider not available")
        
        return self.news_provider.get_trending_topics()
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers"""
        status = {}
        
        for name, provider in self.providers.items():
            status[name] = provider.get_provider_info()
        
        if self.news_provider:
            status['news'] = self.news_provider.get_source_info()
        
        return status
    
    def is_provider_available(self, provider: str) -> bool:
        """Check if a specific provider is available"""
        return provider in self.providers and self.providers[provider].is_connected()
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        available = []
        for name, provider in self.providers.items():
            if provider.is_connected():
                available.append(name)
        return available
    
    def refresh_providers(self):
        """Refresh all provider connections"""
        self._initialize_providers()
    
    def get_market_overview(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Get market overview with key indices and currencies"""
        if symbols is None:
            # Default major indices and currencies
            symbols = [
                '^GSPC',   # S&P 500
                '^DJI',    # Dow Jones
                '^IXIC',   # NASDAQ
                '^BVSP',   # Bovespa
                '^FTSE',   # FTSE 100
                '^N225',   # Nikkei 225
                'EURUSD=X', # EUR/USD
                'GBPUSD=X', # GBP/USD
                'USDBRL=X', # USD/BRL
            ]
        
        overview = {
            'indices': {},
            'currencies': {},
            'timestamp': datetime.now()
        }
        
        for symbol in symbols:
            try:
                data = self.get_real_time_price(symbol)
                
                if '=X' in symbol:  # Currency pair
                    overview['currencies'][symbol] = data
                else:  # Index
                    overview['indices'][symbol] = data
                    
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
        
        return overview
