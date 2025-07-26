"""
Keep Alive Server za Replit 24/7 Hosting
"""
from flask import Flask
import threading
import time
import os
from datetime import datetime

# Import trading components
try:
    from trading_logic import TradingEngine
    from database import TradingLogger
    from config import DATA_UPDATE_INTERVAL
except ImportError as e:
    print(f"Greška pri importu: {e}")

app = Flask('')

@app.route('/')
def home():
    return """
    <html>
        <head><title>Trading Simulator</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1>🚀 Trading Simulator je aktivan!</h1>
            <p>Simulator radi 24/7 na Replit-u</p>
            <a href="/status" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Pogledaj Status
            </a>
        </body>
    </html>
    """

@app.route('/status')
def status():
    try:
        engine = TradingEngine()
        summary = engine.get_portfolio_summary()
        
        # Format active positions
        positions_html = ""
        if summary['active_positions'] > 0:
            positions_html = "<h3>Aktivne pozicije:</h3><ul>"
            for ticker, position in engine.portfolio.positions.items():
                positions_html += f"<li>{ticker}: {position.position_type.value.upper()} @ ${position.entry_price:.2f}</li>"
            positions_html += "</ul>"
        
        return f"""
        <html>
            <head>
                <title>Trading Simulator Status</title>
                <meta http-equiv="refresh" content="60">
            </head>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h1>📊 Trading Simulator Status</h1>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h2>Portfolio Pregled</h2>
                    <p><strong>Ukupna vrednost:</strong> ${summary['current_value']:,.2f}</p>
                    <p><strong>Dostupan keš:</strong> ${summary['cash']:,.2f}</p>
                    <p><strong>Ukupan povrat:</strong> {summary['total_return']:.2%}</p>
                    <p><strong>Aktivne pozicije:</strong> {summary['active_positions']}</p>
                    <p><strong>Ukupno trgovina:</strong> {summary['total_trades']}</p>
                    <p><strong>Win rate:</strong> {summary['win_rate']:.1%}</p>
                    <p><strong>Ukupan profit:</strong> ${summary['total_profit']:,.2f}</p>
                    <p><strong>Poslednji update:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                {positions_html}
                <div style="margin-top: 30px;">
                    <a href="/" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Nazad
                    </a>
                </div>
            </body>
        </html>
        """
    except Exception as e:
        return f"""
        <html>
            <head><title>Greška</title></head>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h1>❌ Greška u sistemu</h1>
                <p>Greška: {e}</p>
                <p>Vreme: {datetime.now()}</p>
                <a href="/" style="background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    Nazad
                </a>
            </body>
        </html>
        """

def run_server():
    """Pokreni Flask server"""
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    """Pokreni server u background thread-u"""
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()
    print("🌐 Web server pokrenuto za keep-alive")

def trading_loop():
    """Glavna trading petlja"""
    print("🚀 Pokretanje Trading Simulator petlje...")
    
    try:
        logger = TradingLogger()
        engine = TradingEngine()
        
        while True:
            try:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Pokretanje trading ciklusa...")
                
                # Pokreni trading ciklus
                engine.run_trading_cycle()
                
                # Log performance
                summary = engine.get_portfolio_summary()
                logger.log_performance(summary)
                
                print(f"✅ Ciklus završen uspešno!")
                print(f"💼 Portfolio: ${summary['current_value']:,.2f} | Pozicije: {summary['active_positions']}")
                print(f"😴 Sledeći ciklus za {DATA_UPDATE_INTERVAL} minuta...")
                
                # Čekaj do sledećeg ciklusa
                time.sleep(DATA_UPDATE_INTERVAL * 60)
                
            except Exception as e:
                print(f"❌ Greška u trading ciklusu: {e}")
                print("⏳ Pokušavam ponovo za 5 minuta...")
                time.sleep(5 * 60)  # Sačekaj 5 minuta pa pokušaj ponovo
                
    except Exception as e:
        print(f"💥 Kritična greška u trading petlji: {e}")
        print("🔄 Restart-ovanje za 1 minut...")
        time.sleep(60)
        trading_loop()  # Restart petlje

if __name__ == '__main__':
    print("🎯 TRADING SIMULATOR - REPLIT MODE")
    print("=" * 50)
    
    # Pokreni keep-alive server
    keep_alive()
    
    # Sačekaj da se server pokrene
    time.sleep(2)
    
    # Pokreni trading petlju
    trading_loop() 