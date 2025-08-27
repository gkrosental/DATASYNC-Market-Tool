"""
DATASYNC Market Tool - Simple Launcher
Test the core functionality
"""
import os
import sys

# Add paths
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

try:
    from src.data_providers.yahoo_finance import YahooFinanceProvider
    from colorama import init, Fore, Style
    init(autoreset=True)
    
    print(f"{Fore.CYAN}=== DATASYNC Market Tool Test ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Testing Yahoo Finance provider...{Style.RESET_ALL}")
    
    # Test Yahoo Finance provider
    provider = YahooFinanceProvider()
    
    # Test basic stock data
    symbol = "AAPL"
    print(f"\n{Fore.BLUE}Fetching data for {symbol}...{Style.RESET_ALL}")
    
    try:
        real_time_data = provider.get_real_time_price(symbol)
        print(f"{Fore.GREEN}✓ Successfully fetched real-time data for {symbol}{Style.RESET_ALL}")
        print(f"Price: ${real_time_data['price']:.2f}")
        print(f"Change: {real_time_data['change']:+.2f} ({real_time_data['change_percent']:+.2f}%)")
        
        # Test historical data
        hist_data = provider.get_stock_data(symbol, "1mo", "1d")
        print(f"{Fore.GREEN}✓ Successfully fetched historical data for {symbol}{Style.RESET_ALL}")
        print(f"Data points: {len(hist_data)}")
        
        # Test currency
        print(f"\n{Fore.BLUE}Testing currency exchange...{Style.RESET_ALL}")
        rate = provider.get_currency_rate("USD", "EUR")
        print(f"{Fore.GREEN}✓ USD/EUR rate: {rate:.4f}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}🎉 All tests passed! DATASYNC is ready to use.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Run 'python datasync_new.py' to start the full application.{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}✗ Error testing {symbol}: {str(e)}{Style.RESET_ALL}")
        
except ImportError as e:
    print(f"{Fore.RED}Import error: {e}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Make sure all dependencies are installed: pip install -r requirements.txt{Style.RESET_ALL}")
    
except Exception as e:
    print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
