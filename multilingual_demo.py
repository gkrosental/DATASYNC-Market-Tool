"""
DATASYNC Market Tool - Multilingual Demo
Demonstração com suporte a múltiplos idiomas
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
    from src.localization import get_text, set_language, get_language, get_available_languages
    from src.utils.helpers import *
    from colorama import init, Fore, Style
    
    init(autoreset=True)
    
    def show_banner(language='en'):
        """Show banner in selected language"""
        print(f"{Fore.CYAN}")
        print("██████╗  █████╗ ████████╗ █████╗ ███████╗██╗   ██╗███╗   ██╗ ██████╗")
        print("██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔════╝╚██╗ ██╔╝████╗  ██║██╔════╝")
        print("██║  ██║███████║   ██║   ███████║███████╗ ╚████╔╝ ██╔██╗ ██║██║     ")
        print("██║  ██║██╔══██║   ██║   ██╔══██║╚════██║  ╚██╔╝  ██║╚██╗██║██║     ")
        print("██████╔╝██║  ██║   ██║   ██║  ██║███████║   ██║   ██║ ╚████║╚██████╗")
        print("╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝")
        print(f"{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{get_text('app.subtitle')} {get_text('app.version')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{get_text('app.developer')}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
    
    def language_selection():
        """Language selection menu"""
        print(f"\n{Fore.CYAN}🌐 LANGUAGE SELECTION / SELEÇÃO DE IDIOMA / SELECCIÓN DE IDIOMA{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Please select your language / Por favor selecione seu idioma / Por favor seleccione su idioma:{Style.RESET_ALL}")
        print("1. 🇧🇷 Português")
        print("2. 🇺🇸 English")
        print("3. 🇪🇸 Español")
        
        choice = input(f"\n{Fore.YELLOW}Choose / Escolha / Elija (1-3): {Style.RESET_ALL}").strip()
        
        if choice == "1":
            set_language('pt')
        elif choice == "2":
            set_language('en')
        elif choice == "3":
            set_language('es')
        else:
            set_language('en')  # Default to English
    
    def demo_market_data():
        """Demo with market data in selected language"""
        print(f"\n{Fore.YELLOW}🚀 {get_text('input.processing')}...{Style.RESET_ALL}")
        
        # Initialize components
        dm = DataProviderManager()
        ta = TechnicalAnalyzer()
        
        print(f"{Fore.GREEN}✓ {get_text('success.data_loaded')}{Style.RESET_ALL}")
        
        # Demo 1: Market Overview
        print(f"\n{Fore.CYAN}📈 {get_text('market.overview').upper()}{Style.RESET_ALL}")
        
        indices = ['^GSPC', '^DJI', '^IXIC']
        index_names = ['S&P 500', 'Dow Jones', 'NASDAQ']
        
        for symbol, name in zip(indices, index_names):
            try:
                data = dm.get_real_time_price(symbol)
                color = Fore.GREEN if data['change'] >= 0 else Fore.RED
                arrow = "↗" if data['change'] >= 0 else "↘"
                
                print(f"{name}: {data['price']:.2f} {color}{arrow} {data['change']:+.2f} ({data['change_percent']:+.2f}%){Style.RESET_ALL}")
            except Exception as e:
                print(f"{name}: {get_text('errors.api_error')}")
        
        # Demo 2: Stock Analysis
        print(f"\n{Fore.CYAN}📊 {get_text('stock.analysis').upper()}{Style.RESET_ALL}")
        
        demo_stocks = ['AAPL', 'MSFT', 'TSLA']
        
        for symbol in demo_stocks:
            try:
                print(f"\n{Fore.BLUE}{get_text('stock.fetching_data', symbol=symbol)}{Style.RESET_ALL}")
                
                # Get real-time data
                real_time = dm.get_real_time_price(symbol)
                color = Fore.GREEN if real_time['change'] >= 0 else Fore.RED
                arrow = "↗" if real_time['change'] >= 0 else "↘"
                
                print(f"{get_text('stock.price')}: ${real_time['price']:.2f} {color}{arrow} {real_time['change']:+.2f} ({real_time['change_percent']:+.2f}%){Style.RESET_ALL}")
                print(f"{get_text('stock.volume')}: {format_volume(real_time['volume'])}")
                
                # Technical analysis
                try:
                    df = dm.get_stock_data(symbol, "3mo", "1d")
                    analysis = ta.analyze_stock(df)
                    signals = ta.generate_signals(analysis)
                    
                    print(f"{get_text('technical.signals')}:")
                    for indicator, signal in list(signals.items())[:3]:  # Show first 3
                        signal_color = Fore.GREEN if signal == "BULLISH" else Fore.RED if signal == "BEARISH" else Fore.YELLOW
                        signal_text = get_text(f'technical.{signal.lower()}') if signal.lower() in ['bullish', 'bearish', 'neutral'] else signal
                        print(f"  {get_text(f'technical.{indicator}')}: {signal_color}{signal_text}{Style.RESET_ALL}")
                except:
                    print(f"  {get_text('technical.analysis')}: {get_text('errors.api_error')}")
                    
            except Exception as e:
                print(f"{get_text('errors.invalid_symbol', symbol=symbol)}")
        
        # Demo 3: Currency Exchange
        print(f"\n{Fore.CYAN}💱 {get_text('currency.converter').upper()}{Style.RESET_ALL}")
        
        currency_pairs = [('USD', 'EUR'), ('USD', 'BRL'), ('USD', 'GBP')]
        
        for from_curr, to_curr in currency_pairs:
            try:
                rate = dm.get_currency_rate(from_curr, to_curr)
                print(f"{from_curr}/{to_curr}: {rate:.4f}")
            except Exception as e:
                print(f"{from_curr}/{to_curr}: {get_text('errors.api_error')}")
        
        # Demo 4: News Headlines
        print(f"\n{Fore.CYAN}📰 {get_text('news.latest').upper()}{Style.RESET_ALL}")
        
        try:
            news = dm.get_market_news(5)
            for i, article in enumerate(news, 1):
                print(f"{i}. {article['title'][:80]}...")
                print(f"   {get_text('news.source')}: {article['source']} | {article['published'].strftime('%Y-%m-%d %H:%M')}")
        except Exception as e:
            print(f"{get_text('news.no_news')}")
    
    def main():
        """Main function"""
        # Language selection
        language_selection()
        
        # Show banner in selected language
        show_banner()
        
        print(f"\n{Fore.GREEN}🎉 {get_text('success.language_changed', language=get_available_languages()[get_language()])}{Style.RESET_ALL}")
        
        # Run demo
        demo_market_data()
        
        print(f"\n{Fore.GREEN}🎉 Demo concluído!{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}{get_text('web.launching')}:{Style.RESET_ALL}")
        print(f"• {get_text('menu.main.stock_analysis')}: {Fore.CYAN}python datasync_new.py{Style.RESET_ALL}")
        print(f"• {get_text('menu.main.web_interface')}: {Fore.CYAN}streamlit run streamlit_launcher.py{Style.RESET_ALL}")
        
        print(f"\n{Fore.BLUE}{get_text('app.disclaimer')}{Style.RESET_ALL}")
    
    if __name__ == "__main__":
        main()
        input(f"\n{Fore.YELLOW}{get_text('input.press_enter')}{Style.RESET_ALL}")

except ImportError as e:
    print(f"Import error: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    input("Press Enter to exit...")
except Exception as e:
    print(f"Error: {e}")
    input("Press Enter to exit...")
