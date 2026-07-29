import uuid
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.models.schema import Portfolio, Position, Order, Transaction, OrderType, OrderSide, OrderStatus, TransactionType
from app.schemas.trading import PortfolioSummary, PositionSchema, TransactionSchema

class TradingEngine:
    
    @staticmethod
    async def execute_buy(session: AsyncSession, portfolio_id: uuid.UUID, symbol: str, quantity: float, price: float) -> Order:
        # Fetch portfolio
        portfolio = await session.get(Portfolio, portfolio_id)
        if not portfolio:
            raise ValueError("Portfolio not found")
            
        cost = quantity * price
        if float(portfolio.cash_balance) < cost:
            raise ValueError(f"Insufficient funds. Required: {cost}, Available: {portfolio.cash_balance}")
            
        # Deduct cash
        portfolio.cash_balance = float(portfolio.cash_balance) - cost
        
        # Create Order
        order = Order(
            portfolio_id=portfolio_id,
            symbol=symbol,
            order_type=OrderType.MARKET,
            side=OrderSide.BUY,
            quantity=quantity,
            price=price,
            status=OrderStatus.FILLED
        )
        session.add(order)
        await session.flush()
        
        # Record Transaction
        transaction = Transaction(
            portfolio_id=portfolio_id,
            order_id=order.id,
            transaction_type=TransactionType.BUY,
            amount=-cost
        )
        session.add(transaction)
        
        # Update Position
        stmt = select(Position).where(Position.portfolio_id == portfolio_id, Position.symbol == symbol)
        result = await session.execute(stmt)
        position = result.scalar_one_or_none()
        
        if position:
            # Weighted average cost
            old_value = float(position.quantity) * float(position.average_price)
            new_value = quantity * price
            position.quantity = float(position.quantity) + quantity
            position.average_price = (old_value + new_value) / float(position.quantity)
        else:
            position = Position(
                portfolio_id=portfolio_id,
                symbol=symbol,
                quantity=quantity,
                average_price=price
            )
            session.add(position)
            
        return order

    @staticmethod
    async def execute_sell(session: AsyncSession, portfolio_id: uuid.UUID, symbol: str, quantity: float, price: float) -> Order:
        # Fetch portfolio & position
        portfolio = await session.get(Portfolio, portfolio_id)
        if not portfolio:
            raise ValueError("Portfolio not found")
            
        stmt = select(Position).where(Position.portfolio_id == portfolio_id, Position.symbol == symbol)
        result = await session.execute(stmt)
        position = result.scalar_one_or_none()
        
        if not position or float(position.quantity) < quantity:
            raise ValueError(f"Insufficient position. Owned: {position.quantity if position else 0}, Attempted to sell: {quantity}")
            
        revenue = quantity * price
        
        # Add cash
        portfolio.cash_balance = float(portfolio.cash_balance) + revenue
        
        # Create Order
        order = Order(
            portfolio_id=portfolio_id,
            symbol=symbol,
            order_type=OrderType.MARKET,
            side=OrderSide.SELL,
            quantity=quantity,
            price=price,
            status=OrderStatus.FILLED
        )
        session.add(order)
        await session.flush()
        
        # Record Transaction
        transaction = Transaction(
            portfolio_id=portfolio_id,
            order_id=order.id,
            transaction_type=TransactionType.SELL,
            amount=revenue
        )
        session.add(transaction)
        
        # Realized PnL is revenue - cost basis
        # Cost basis of the sold shares: quantity * average_price
        # In a real system, you might record this PnL explicitly.
        
        # Update Position
        position.quantity = float(position.quantity) - quantity
        if float(position.quantity) == 0:
            session.delete(position)
            
        return order

    @staticmethod
    async def get_portfolio_summary(session: AsyncSession, portfolio_id: uuid.UUID, current_prices: Dict[str, float]) -> PortfolioSummary:
        portfolio = await session.get(Portfolio, portfolio_id)
        if not portfolio:
            raise ValueError("Portfolio not found")
            
        stmt = select(Position).where(Position.portfolio_id == portfolio_id)
        result = await session.execute(stmt)
        positions = result.scalars().all()
        
        pos_schemas = []
        total_unrealized_pnl = 0.0
        total_equity = float(portfolio.cash_balance)
        
        for p in positions:
            curr_price = current_prices.get(p.symbol, float(p.average_price)) # Fallback to avg price if not found
            unrealized = float(p.quantity) * (curr_price - float(p.average_price))
            total_unrealized_pnl += unrealized
            equity = float(p.quantity) * curr_price
            total_equity += equity
            
            pos_schemas.append(PositionSchema(
                symbol=p.symbol,
                quantity=float(p.quantity),
                average_cost=float(p.average_price),
                current_price=curr_price,
                unrealized_pnl=unrealized
            ))
            
        # Calculate Realized PnL by scanning transactions
        # Realized PnL = Total Sell Revenue - Total Buy Cost of Sold Shares
        # A simpler formula: Total Deposits - Total Withdrawals + Current Equity = Total Realized + Total Unrealized
        # But we'll just return 0 for now as it requires parsing all transactions or adding a column.
        # Let's add total_realized_pnl logic based on total buys/sells
        
        stmt = select(Transaction).where(Transaction.portfolio_id == portfolio_id)
        result = await session.execute(stmt)
        transactions = result.scalars().all()
        
        # Net cash generated by trading (Sells - Buys)
        net_cash_from_trades = sum(float(t.amount) for t in transactions if t.transaction_type in (TransactionType.BUY, TransactionType.SELL))
        
        # Realized PnL = Net Cash from Trades + Value of Current Positions (At Cost)
        value_at_cost = sum(float(p.quantity) * float(p.average_price) for p in positions)
        total_realized_pnl = net_cash_from_trades + value_at_cost
        
        return PortfolioSummary(
            portfolio_id=portfolio_id,
            cash_balance=float(portfolio.cash_balance),
            total_equity=total_equity,
            total_unrealized_pnl=total_unrealized_pnl,
            total_realized_pnl=total_realized_pnl,
            positions=pos_schemas
        )

    @staticmethod
    async def get_transaction_history(session: AsyncSession, portfolio_id: uuid.UUID) -> List[TransactionSchema]:
        stmt = select(Transaction).options(joinedload(Transaction.order)).where(Transaction.portfolio_id == portfolio_id).order_by(Transaction.created_at.desc())
        result = await session.execute(stmt)
        transactions = result.scalars().all()
        
        return [
            TransactionSchema(
                id=t.id,
                transaction_type=t.transaction_type,
                symbol=t.order.symbol if t.order else None,
                amount=float(t.amount),
                created_at=t.created_at
            ) for t in transactions
        ]
