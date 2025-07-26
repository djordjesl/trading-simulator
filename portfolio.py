"""
Portfolio Management System
"""
import json
import csv
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from config import *

class PositionType(Enum):
    LONG = "long"
    SHORT = "short"

@dataclass
class Position:
    ticker: str
    position_type: PositionType
    entry_price: float
    quantity: float
    entry_date: datetime
    stop_loss: float
    take_profit: float
    
    def to_dict(self):
        data = asdict(self)
        data['position_type'] = self.position_type.value
        data['entry_date'] = self.entry_date.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data):
        data['position_type'] = PositionType(data['position_type'])
        data['entry_date'] = datetime.fromisoformat(data['entry_date'])
        return cls(**data)

@dataclass
class Trade:
    ticker: str
    action: str  # "BUY", "SELL", "SHORT", "COVER"
    price: float
    quantity: float
    timestamp: datetime
    profit_loss: float = 0.0
    reason: str = ""
    
    def to_dict(self):
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class Portfolio:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cash = INITIAL_BUDGET
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.load_portfolio()
    
    def load_portfolio(self):
        """Load portfolio from files"""
        try:
            # Load positions
            if POSITIONS_FILE.exists():
                with open(POSITIONS_FILE, 'r') as f:
                    data = json.load(f)
                    self.cash = data.get('cash', INITIAL_BUDGET)
                    positions_data = data.get('positions', {})
                    self.positions = {
                        ticker: Position.from_dict(pos_data)
                        for ticker, pos_data in positions_data.items()
                    }
            
            # Load trades
            if TRADES_FILE.exists():
                self.trades = []
                with open(TRADES_FILE, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        trade = Trade(
                            ticker=row['ticker'],
                            action=row['action'],
                            price=float(row['price']),
                            quantity=float(row['quantity']),
                            timestamp=datetime.fromisoformat(row['timestamp']),
                            profit_loss=float(row['profit_loss']),
                            reason=row['reason']
                        )
                        self.trades.append(trade)
                        
        except Exception as e:
            self.logger.error(f"Error loading portfolio: {e}")
    
    def save_portfolio(self):
        """Save portfolio to files"""
        try:
            # Save positions
            data = {
                'cash': self.cash,
                'positions': {
                    ticker: pos.to_dict() 
                    for ticker, pos in self.positions.items()
                }
            }
            with open(POSITIONS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Save trades
            with open(TRADES_FILE, 'w', newline='') as f:
                fieldnames = ['ticker', 'action', 'price', 'quantity', 'timestamp', 'profit_loss', 'reason']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for trade in self.trades:
                    writer.writerow(trade.to_dict())
                    
        except Exception as e:
            self.logger.error(f"Error saving portfolio: {e}")
    
    def can_open_position(self) -> bool:
        """Check if we can open a new position"""
        return self.cash >= POSITION_SIZE and len(self.positions) < MAX_POSITIONS
    
    def open_long_position(self, ticker: str, price: float) -> bool:
        """Open a long position"""
        if not self.can_open_position():
            return False
        
        if ticker in self.positions:
            return False
        
        quantity = POSITION_SIZE / price
        stop_loss = price * (1 + STOP_LOSS)  # 5% stop loss
        take_profit = price * (1 + TAKE_PROFIT)  # 3% take profit
        
        position = Position(
            ticker=ticker,
            position_type=PositionType.LONG,
            entry_price=price,
            quantity=quantity,
            entry_date=datetime.now(),
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        trade = Trade(
            ticker=ticker,
            action="BUY",
            price=price,
            quantity=quantity,
            timestamp=datetime.now(),
            reason="Price dropped 5% - buying opportunity"
        )
        
        self.positions[ticker] = position
        self.trades.append(trade)
        self.cash -= POSITION_SIZE
        
        self.logger.info(f"Opened LONG position: {ticker} at ${price:.2f}")
        return True
    
    def open_short_position(self, ticker: str, price: float) -> bool:
        """Open a short position"""
        if not self.can_open_position():
            return False
        
        if ticker in self.positions:
            return False
        
        quantity = POSITION_SIZE / price
        stop_loss = price * (1 - STOP_LOSS)  # 5% stop loss (price goes up)
        take_profit = price * (1 - TAKE_PROFIT)  # 3% take profit (price goes down)
        
        position = Position(
            ticker=ticker,
            position_type=PositionType.SHORT,
            entry_price=price,
            quantity=quantity,
            entry_date=datetime.now(),
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        trade = Trade(
            ticker=ticker,
            action="SHORT",
            price=price,
            quantity=quantity,
            timestamp=datetime.now(),
            reason="Price jumped 10% - shorting opportunity"
        )
        
        self.positions[ticker] = position
        self.trades.append(trade)
        self.cash -= POSITION_SIZE  # Reserve cash for potential losses
        
        self.logger.info(f"Opened SHORT position: {ticker} at ${price:.2f}")
        return True
    
    def close_position(self, ticker: str, current_price: float, reason: str) -> bool:
        """Close a position"""
        if ticker not in self.positions:
            return False
        
        position = self.positions[ticker]
        
        # Calculate profit/loss
        if position.position_type == PositionType.LONG:
            profit_loss = (current_price - position.entry_price) * position.quantity
            action = "SELL"
        else:  # SHORT
            profit_loss = (position.entry_price - current_price) * position.quantity
            action = "COVER"
        
        trade = Trade(
            ticker=ticker,
            action=action,
            price=current_price,
            quantity=position.quantity,
            timestamp=datetime.now(),
            profit_loss=profit_loss,
            reason=reason
        )
        
        # Update cash
        self.cash += POSITION_SIZE + profit_loss
        
        # Remove position
        del self.positions[ticker]
        self.trades.append(trade)
        
        self.logger.info(f"Closed {position.position_type.value.upper()} position: {ticker} at ${current_price:.2f}, P/L: ${profit_loss:.2f}")
        return True
    
    def should_close_position(self, ticker: str, current_price: float) -> Optional[str]:
        """Check if a position should be closed"""
        if ticker not in self.positions:
            return None
        
        position = self.positions[ticker]
        
        if position.position_type == PositionType.LONG:
            if current_price >= position.take_profit:
                return "Take profit reached"
            elif current_price <= position.stop_loss:
                return "Stop loss triggered"
        else:  # SHORT
            if current_price <= position.take_profit:
                return "Take profit reached"
            elif current_price >= position.stop_loss:
                return "Stop loss triggered"
        
        return None
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate total portfolio value"""
        total_value = self.cash
        
        for ticker, position in self.positions.items():
            if ticker in current_prices:
                current_price = current_prices[ticker]
                if position.position_type == PositionType.LONG:
                    position_value = current_price * position.quantity
                else:  # SHORT
                    # For short positions, value is entry_value + (entry_price - current_price) * quantity
                    position_value = POSITION_SIZE + (position.entry_price - current_price) * position.quantity
                
                total_value += position_value
            else:
                # If we can't get current price, assume position value = entry value
                total_value += POSITION_SIZE
        
        return total_value
    
    def get_statistics(self) -> Dict:
        """Get portfolio statistics"""
        total_trades = len(self.trades)
        profitable_trades = len([t for t in self.trades if t.profit_loss > 0])
        losing_trades = len([t for t in self.trades if t.profit_loss < 0])
        
        total_profit = sum(t.profit_loss for t in self.trades)
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'cash': self.cash,
            'active_positions': len(self.positions)
        } 