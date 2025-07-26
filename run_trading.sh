#!/bin/bash

# Trading Simulator Cron Script
# Add this to crontab: */30 * * * * /path/to/your/project/run_trading.sh

# Change to the project directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run the trading simulator
python main.py run

# Log the execution
echo "$(date): Trading cycle completed" >> data/cron.log 