#!/usr/bin/env python3
"""
Trading Simulator Main Application
"""
import argparse
import sys
import time
import os
from datetime import datetime

from database import TradingLogger
from trading_logic import TradingEngine
from analyzer import PerformanceAnalyzer
from config import *

# Replit hosting mode
if __name__ == "__main__" and 'REPL_ID' in os.environ:
    print("🚀 Pokretanje u Replit modu...")
    try:
        from keep_alive import keep_alive, trading_loop
        keep_alive()
        trading_loop()
    except ImportError:
        print("❌ keep_alive.py nije pronađen, pokretanje u običnom modu...")
    except Exception as e:
        print(f"❌ Greška u Replit modu: {e}")
        sys.exit(1)

def setup_logging():
    """Initialize logging system"""
    logger = TradingLogger()
    return logger

def run_simulation():
    """Run a single trading simulation cycle"""
    logger = setup_logging()
    
    print("🚀 Pokretanje Trading Simulatora...")
    print(f"📊 Budget: ${INITIAL_BUDGET}")
    print(f"💰 Pozicija: ${POSITION_SIZE}")
    print(f"⏰ Vreme: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    try:
        # Initialize trading engine
        engine = TradingEngine()
        
        # Run trading cycle
        engine.run_trading_cycle()
        
        # Get portfolio summary
        summary = engine.get_portfolio_summary()
        
        # Log performance
        db_logger = TradingLogger()
        db_logger.log_performance(summary)
        
        # Display results
        print("\n📈 REZULTATI SIMULACIJE:")
        print(f"💵 Trenutna vrednost: ${summary['current_value']:,.2f}")
        print(f"💸 Keš: ${summary['cash']:,.2f}")
        print(f"📊 Ukupan povrat: {summary['total_return']:.2%}")
        print(f"🔢 Aktivne pozicije: {summary['active_positions']}")
        print(f"📋 Ukupno trgovina: {summary['total_trades']}")
        print(f"🎯 Win rate: {summary['win_rate']:.1%}")
        print(f"💰 Ukupan profit: ${summary['total_profit']:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Greška u simulaciji: {e}")
        return False

def run_analysis():
    """Run performance analysis and generate report"""
    print("📊 Pokretanje analize performansi...")
    
    try:
        analyzer = PerformanceAnalyzer()
        
        # Generate text report
        report = analyzer.generate_report()
        print("\n" + report)
        
        # Save report to file
        report_file = DATA_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 Izveštaj sačuvan u: {report_file}")
        
        # Generate performance plots
        analyzer.plot_performance()
        print(f"📈 Grafik sačuvan u: {DATA_DIR / 'performance_dashboard.png'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Greška u analizi: {e}")
        return False

def show_status():
    """Show current portfolio status"""
    try:
        engine = TradingEngine()
        summary = engine.get_portfolio_summary()
        
        print("💼 TRENUTNO STANJE PORTFOLIA:")
        print("-" * 40)
        print(f"💵 Ukupna vrednost: ${summary['current_value']:,.2f}")
        print(f"💸 Dostupan keš: ${summary['cash']:,.2f}")
        print(f"📊 Povrat: {summary['total_return']:.2%}")
        print(f"🔢 Aktivne pozicije: {summary['active_positions']}")
        print(f"📋 Ukupno trgovina: {summary['total_trades']}")
        
        # Show active positions
        if summary['active_positions'] > 0:
            print("\n🔍 AKTIVNE POZICIJE:")
            for ticker, position in engine.portfolio.positions.items():
                print(f"  {ticker}: {position.position_type.value.upper()} @ ${position.entry_price:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Greška pri prikazivanju statusa: {e}")
        return False

def continuous_mode():
    """Run simulator in continuous mode"""
    print("🔄 Pokretanje kontinuiranog moda...")
    print(f"⏱️  Proverava se svakih {DATA_UPDATE_INTERVAL} minuta")
    print("Pritisnite Ctrl+C za zaustavljanje\n")
    
    try:
        while True:
            print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Pokretanje ciklusa...")
            
            success = run_simulation()
            if success:
                print("✅ Ciklus uspešno završen")
            else:
                print("❌ Ciklus završen sa greškom")
            
            print(f"😴 Čekam {DATA_UPDATE_INTERVAL} minuta...")
            time.sleep(DATA_UPDATE_INTERVAL * 60)  # Convert to seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Simulator zaustavljen od strane korisnika")
    except Exception as e:
        print(f"❌ Greška u kontinuiranom modu: {e}")

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Trading Simulator - Simulacija trgovine dionica')
    parser.add_argument('command', choices=['run', 'analyze', 'status', 'continuous'], 
                      help='Komanda za izvršavanje')
    parser.add_argument('--verbose', '-v', action='store_true', 
                      help='Detaljni ispis')
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        print("🎯 TRADING SIMULATOR")
        print("=" * 50)
        print("Dostupne komande:")
        print("  python main.py run        - Pokreni jedan ciklus simulacije")
        print("  python main.py analyze    - Analiziraj performanse")
        print("  python main.py status     - Prikaži trenutno stanje")
        print("  python main.py continuous - Kontinuirani mod (svakih 30min)")
        print("\nOpcije:")
        print("  --verbose, -v             - Detaljni ispis")
        print("\nPrimer:")
        print("  python main.py run")
        print("  python main.py analyze")
        return
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    success = False
    
    if args.command == 'run':
        success = run_simulation()
    elif args.command == 'analyze':
        success = run_analysis()
    elif args.command == 'status':
        success = show_status()
    elif args.command == 'continuous':
        continuous_mode()
        success = True
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 