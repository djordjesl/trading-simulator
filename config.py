"""
Trading Simulator Configuration
"""
import os
from pathlib import Path

# Trading Parameters
INITIAL_BUDGET = 1000.0  # $1000 total budget
POSITION_SIZE = 10.0     # $10 per position
MAX_POSITIONS = int(INITIAL_BUDGET / POSITION_SIZE)  # 100 positions max

# Trading Triggers
SHORT_TRIGGER = 0.10     # Short if stock jumped 10% in 7 days
BUY_TRIGGER = -0.05      # Buy if stock dropped 5% in 7 days
TAKE_PROFIT = 0.03       # Take profit at 3%
STOP_LOSS = -0.05        # Stop loss at -5%

# Data Parameters
LOOKBACK_DAYS = 7        # Days to look back for price changes
MAX_COMPANIES = 1000     # Maximum companies to track
DATA_UPDATE_INTERVAL = 30 # Minutes between updates

# File Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
POSITIONS_FILE = DATA_DIR / "positions.json"
TRADES_FILE = DATA_DIR / "trades.csv"
PERFORMANCE_FILE = DATA_DIR / "performance.csv"
COMPANIES_FILE = DATA_DIR / "sp500_companies.json"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# API Settings
YFINANCE_TIMEOUT = 10    # Seconds timeout for API calls
BATCH_SIZE = 50          # Number of stocks to fetch at once

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = DATA_DIR / "trading.log" 