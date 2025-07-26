"""
Database and Logging Module
"""
import logging
import csv
import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path

from config import *

class TradingLogger:
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler()
            ]
        )
    
    def log_performance(self, portfolio_summary: Dict):
        """Log daily portfolio performance"""
        try:
            # Check if performance file exists, create with headers if not
            if not PERFORMANCE_FILE.exists():
                with open(PERFORMANCE_FILE, 'w', newline='') as f:
                    fieldnames = [
                        'timestamp', 'portfolio_value', 'cash', 'total_return', 
                        'active_positions', 'total_trades', 'win_rate', 'total_profit'
                    ]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
            
            # Append performance data
            with open(PERFORMANCE_FILE, 'a', newline='') as f:
                fieldnames = [
                    'timestamp', 'portfolio_value', 'cash', 'total_return',
                    'active_positions', 'total_trades', 'win_rate', 'total_profit'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                row = {
                    'timestamp': datetime.now().isoformat(),
                    'portfolio_value': portfolio_summary['current_value'],
                    'cash': portfolio_summary['cash'],
                    'total_return': portfolio_summary['total_return'],
                    'active_positions': portfolio_summary['active_positions'],
                    'total_trades': portfolio_summary['total_trades'],
                    'win_rate': portfolio_summary['win_rate'],
                    'total_profit': portfolio_summary['total_profit']
                }
                writer.writerow(row)
                
        except Exception as e:
            self.logger.error(f"Error logging performance: {e}")
    
    def get_performance_history(self) -> List[Dict]:
        """Get historical performance data"""
        try:
            if not PERFORMANCE_FILE.exists():
                return []
            
            performance_data = []
            with open(PERFORMANCE_FILE, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert numeric fields
                    row['portfolio_value'] = float(row['portfolio_value'])
                    row['cash'] = float(row['cash'])
                    row['total_return'] = float(row['total_return'])
                    row['active_positions'] = int(row['active_positions'])
                    row['total_trades'] = int(row['total_trades'])
                    row['win_rate'] = float(row['win_rate'])
                    row['total_profit'] = float(row['total_profit'])
                    performance_data.append(row)
            
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Error reading performance history: {e}")
            return []
    
    def backup_data(self):
        """Create backup of all trading data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = DATA_DIR / f"backup_{timestamp}"
            backup_dir.mkdir(exist_ok=True)
            
            # Copy all data files
            import shutil
            for file_path in [POSITIONS_FILE, TRADES_FILE, PERFORMANCE_FILE, COMPANIES_FILE]:
                if file_path.exists():
                    shutil.copy2(file_path, backup_dir / file_path.name)
            
            self.logger.info(f"Data backup created: {backup_dir}")
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log files"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
            
            # Clean up old backup directories
            backup_pattern = DATA_DIR.glob("backup_*")
            for backup_dir in backup_pattern:
                if backup_dir.stat().st_mtime < cutoff_date:
                    import shutil
                    shutil.rmtree(backup_dir)
                    self.logger.info(f"Cleaned up old backup: {backup_dir}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up logs: {e}") 