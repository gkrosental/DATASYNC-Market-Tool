"""
DATASYNC Market Tool - Demo Script
Quick demonstration of key features
"""
import os
import sys

# Add paths
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

try:
    from src.data_providers.data_manager import DataProviderManager
    from src.analyzers.technical_analyzer import TechnicalAnalyzer
    from src.utils.helpers import *
    from colorama import init, Fore, Style
    
    init(autoreset=True)
    
    print(f"{Fore.CYAN}")
    print("██████╗  █████╗ ████████╗ █████╗ ███████╗██╗   ██╗███╗   ██╗ ██████╗")
    print("██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔════╝╚██╗ ██╔╝████╗  ██║██╔════╝")
    print("██║  ██║███████║   ██║   ███████║███████╗ ╚████╔╝ ██╔██╗ ██║██║     ")
    print("██║  ██║██╔══██║   ██║   ██╔══██║╚════██║  ╚██╔╝  ██║╚██╗██║██║     ")
    print("██████╔╝██║  ██║   ██║   ██║  ██║███████║   ██║   ██║ ╚████║╚██████╗")
    print("╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝")
    print(f"{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Market Analysis Tool v2.0.0 - DEMO{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Developed by Guilherme Rosental{Style.RESET_ALL}")
    print(f"{Fore.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}🚀 Initializing DATASYNC components...{Style.RESET_ALL}")
    
    # Initialize components
    dm = DataProviderManager()
    ta = TechnicalAnalyzer()
    
    print(f"{Fore.GREEN}✓ Data providers initialized{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Technical analyzer ready{Style.RESET_ALL}")
    
    # Demo 1: Market Overview
    print(f"\n{Fore.CYAN}📈 MARKET OVERVIEW{Style.RESET_ALL}")
    print("Getting major indices...")
    
    indices = ['^GSPC', '^DJI', '^IXIC']
    index_names = ['S&P 500', 'Dow Jones', 'NASDAQ']
    
    for symbol, name in zip(indices, index_names):
        try:
            data = dm.get_real_time_price(symbol)
            color = Fore.GREEN if data['change'] >= 0 else Fore.RED
            arrow = "↗" if data['change'] >= 0 else "↘"
            
            print(f"{name}: {data['price']:.2f} {color}{arrow} {data['change']:+.2f} ({data['change_percent']:+.2f}%){Style.RESET_ALL}")
        except Exception as e:
            print(f"{name}: Error - {str(e)}")
    
    # Demo 2: Stock Analysis
    print(f"\n{Fore.CYAN}📊 STOCK ANALYSIS DEMO{Style.RESET_ALL}")
    
    demo_stocks = ['AAPL', 'TSLA', 'MSFT']
    
    for symbol in demo_stocks:
        try:
            print(f"\n{Fore.BLUE}Analyzing {symbol}...{Style.RESET_ALL}")
            
            # Get real-time data
            real_time = dm.get_real_time_price(symbol)
            color = Fore.GREEN if real_time['change'] >= 0 else Fore.RED
            arrow = "↗" if real_time['change'] >= 0 else "↘"
            
            print(f"Price: ${real_time['price']:.2f} {color}{arrow} {real_time['change']:+.2f} ({real_time['change_percent']:+.2f}%){Style.RESET_ALL}")
            print(f"Volume: {format_volume(real_time['volume'])}")
            
            # Get company info
            try:
                company = dm.get_company_info(symbol)
                print(f"Company: {company.get('company_name', 'N/A')}")
                print(f"Market Cap: {format_market_cap(company.get('market_cap', 0))}")
                print(f"P/E Ratio: {company.get('pe_ratio', 'N/A')}")
            except:
                print("Company info not available")
            
            # Technical analysis
            try:
                df = dm.get_stock_data(symbol, "3mo", "1d")
                analysis = ta.analyze_stock(df)
                signals = ta.generate_signals(analysis)
                
                print("Technical Signals:")
                for indicator, signal in list(signals.items())[:3]:  # Show first 3
                    signal_color = Fore.GREEN if signal == "BULLISH" else Fore.RED if signal == "BEARISH" else Fore.YELLOW
                    print(f"  {indicator}: {signal_color}{signal}{Style.RESET_ALL}")
            except:
                print("Technical analysis not available")
                
        except Exception as e:
            print(f"Error analyzing {symbol}: {str(e)}")
    
    # Demo 3: Currency Exchange
    print(f"\n{Fore.CYAN}💱 CURRENCY EXCHANGE DEMO{Style.RESET_ALL}")
    
    currency_pairs = [('USD', 'EUR'), ('USD', 'BRL'), ('USD', 'GBP')]
    
    for from_curr, to_curr in currency_pairs:
        try:
            rate = dm.get_currency_rate(from_curr, to_curr)
            print(f"{from_curr}/{to_curr}: {rate:.4f}")
        except Exception as e:
            print(f"{from_curr}/{to_curr}: Error - {str(e)}")
    
    # Demo 4: News Headlines
    print(f"\n{Fore.CYAN}📰 LATEST MARKET NEWS{Style.RESET_ALL}")
    
    try:
        news = dm.get_market_news(5)
        for i, article in enumerate(news, 1):
            print(f"{i}. {article['title'][:80]}...")
            print(f"   Source: {article['source']} | {article['published'].strftime('%Y-%m-%d %H:%M')}")
    except Exception as e:
        print(f"News not available: {str(e)}")
    
    print(f"\n{Fore.GREEN}🎉 Demo completed successfully!{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}To use the full application:{Style.RESET_ALL}")
    print(f"• Console Interface: {Fore.CYAN}python datasync_new.py{Style.RESET_ALL}")
    print(f"• Web Interface: {Fore.CYAN}streamlit run streamlit_launcher.py{Style.RESET_ALL}")
    
    print(f"\n{Fore.BLUE}Features Available:{Style.RESET_ALL}")
    print("• Real-time stock quotes and analysis")
    print("• Technical indicators (RSI, MACD, Bollinger Bands, etc.)")
    print("• Portfolio management and optimization")
    print("• Currency exchange rates")
    print("• Market news and trends")
    print("• Interactive charts and visualizations")
    
    print(f"\n{Fore.RED}Disclaimer:{Style.RESET_ALL}")
    print("This tool is for educational purposes only. Not financial advice.")
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install requirements: pip install -r requirements.txt")
except Exception as e:
    print(f"Error: {e}")

input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
