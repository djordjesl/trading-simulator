# Replit Setup Guide - BESPLATNO HOSTING

## 🆓 Kompletno besplatan 24/7 hosting za Trading Simulator

### 1. Kreiranje Replit Account-a

1. Idite na [replit.com](https://replit.com/)
2. Kliknite "Sign up" - potpuno besplatno
3. Možete se registrovati sa GitHub, Google ili email

### 2. Kreiranje novog Repl-a

1. Kliknite "Create Repl"
2. Izaberite **Python** kao jezik
3. Nazovite ga "trading-simulator"
4. Kliknite "Create Repl"

### 3. Upload vašeg koda

#### Opcija A: Direktno kopiranje
1. U Replit editoru, obrišite `main.py`
2. Kreirajte sve vaše fajlove jedan po jedan:
   - `main.py`
   - `config.py`
   - `data_fetcher.py`
   - `portfolio.py`
   - `trading_logic.py`
   - `database.py`
   - `analyzer.py`
   - `requirements.txt`

#### Opcija B: GitHub import (preporučeno)
1. Prvo upload kod na GitHub
2. U Replit: "Import from GitHub"
3. Unesite URL vašeg repo

### 4. Instaliranje dependencies

U Replit Shell (tab "Shell"):
```bash
pip install -r requirements.txt
```

### 5. Testiranje

U Shell-u:
```bash
python main.py run
```

### 6. Podešavanje za 24/7 rad

#### A. Kreiranje `keep_alive.py`
```python
from flask import Flask
import threading
import time
from main import TradingEngine
from database import TradingLogger
from datetime import datetime

app = Flask('')

@app.route('/')
def home():
    return "Trading Simulator je aktivan! 🚀"

@app.route('/status')
def status():
    try:
        engine = TradingEngine()
        summary = engine.get_portfolio_summary()
        return f"""
        <h2>Trading Simulator Status</h2>
        <p>Portfolio vrednost: ${summary['current_value']:,.2f}</p>
        <p>Keš: ${summary['cash']:,.2f}</p>
        <p>Aktivne pozicije: {summary['active_positions']}</p>
        <p>Poslednji update: {datetime.now()}</p>
        """
    except Exception as e:
        return f"Greška: {e}"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# Trading loop
def trading_loop():
    logger = TradingLogger()
    engine = TradingEngine()
    
    while True:
        try:
            print(f"[{datetime.now()}] Pokretanje trading ciklusa...")
            engine.run_trading_cycle()
            
            # Log performance
            summary = engine.get_portfolio_summary()
            logger.log_performance(summary)
            
            print(f"Ciklus završen. Sledeći za 30 minuta...")
            time.sleep(30 * 60)  # 30 minuta
            
        except Exception as e:
            print(f"Greška u trading loop: {e}")
            time.sleep(60)  # Sačekaj 1 minut pa pokušaj ponovo

if __name__ == '__main__':
    keep_alive()
    trading_loop()
```

#### B. Modifikacija `main.py`
Dodajte na vrh fajla:
```python
# Za Replit hosting
try:
    from keep_alive import keep_alive, trading_loop
    if __name__ == "__main__" and 'REPL_ID' in os.environ:
        print("🚀 Pokretanje u Replit modu...")
        keep_alive()
        trading_loop()
except ImportError:
    pass

# Ostatak vašeg koda...
```

### 7. Pokretanje 24/7

1. Pokrenite `python keep_alive.py` u Shell-u
2. Replit će držati aplikaciju aktivnu
3. Trading će se izvršavati svakih 30 minuta automatski

### 8. Monitoring

- **Status URL**: `https://YOUR_REPL_NAME.YOUR_USERNAME.repl.co/status`
- **Logs**: Pogledajte Console u Replit-u
- **Files**: Podaci se čuvaju u `data/` folderu

### 9. Always-On funkcija (opciono)

Za garantovano 24/7 pokretanje:
1. Idite na vaš Repl
2. Kliknite "Always On" (besplatno za 1 Repl)
3. Vaš simulator će raditi neprekidno

### 10. Backup podataka

```python
# Dodati u scheduled task
import requests
import json

def backup_to_github():
    # Možete poslati podatke na GitHub ili email
    pass
```

## Prednosti Replit vs VPS:

| Svojstvo | Replit | VPS |
|----------|--------|-----|
| **Cena** | 🆓 Besplatno | 💰 $5/mesec |
| **Setup** | ⚡ 10 minuta | ⏰ 30+ minuta |
| **Održavanje** | 🔧 Automatsko | 👨‍💻 Ručno |
| **Backup** | ☁️ Automatski | 💾 Ručno |
| **Skaliranje** | 📈 Jednostavno | 🔧 Složeno |

## Ograničenja besplatnog plana:
- CPU/RAM ograničenja (dovoljno za trading simulator)
- 1 GB storage (više nego dovoljno)
- Javni kod (možete napraviti privatno za $7/mesec)

**PREPORUKA: Počnite sa besplatnim Replit-om!** 🚀 