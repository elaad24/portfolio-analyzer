"""
Data schemas for portfolio transactions.

This module defines the strict structure that all parsed transactions must follow.
Each transaction type has its own schema to ensure data consistency.
"""

from typing import Optional, Literal
from dataclasses import dataclass
from datetime import date


@dataclass
class Purchase:
    """
    Purchase transaction schema.
    
    Represents a stock/asset purchase with all financial details.
    """
    date: str  # YYYY-MM-DD format
    company_symbol: str
    quantity: float
    unit_price: float
    currency: str
    transaction_fee: Optional[float] = None
    proceeds_foreign: Optional[float] = None
    proceeds_ils: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "date": self.date,
            "company_symbol": self.company_symbol,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "currency": self.currency,
            "transaction_fee": self.transaction_fee,
            "proceeds_foreign": self.proceeds_foreign,
            "proceeds_ils": self.proceeds_ils,
        }


@dataclass
class Sale:
    """
    Sale transaction schema.
    
    Same structure as Purchase - represents a stock/asset sale.
    """
    date: str  # YYYY-MM-DD format
    company_symbol: str
    quantity: float
    unit_price: float
    currency: str
    transaction_fee: Optional[float] = None
    proceeds_foreign: Optional[float] = None
    proceeds_ils: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "date": self.date,
            "company_symbol": self.company_symbol,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "currency": self.currency,
            "transaction_fee": self.transaction_fee,
            "proceeds_foreign": self.proceeds_foreign,
            "proceeds_ils": self.proceeds_ils,
        }


@dataclass
class Dividend:
    """
    Dividend transaction schema.
    
    Represents dividend payments received from companies.
    Simpler schema than purchases/sales - only needs amount.
    """
    date: str  # YYYY-MM-DD format
    company_symbol: str
    amount: float
    currency: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "date": self.date,
            "company_symbol": self.company_symbol,
            "amount": self.amount,
            "currency": self.currency,
        }


@dataclass
class Tax:
    """
    Tax withholding transaction schema.
    
    Represents tax deductions (withholding, foreign tax, etc.).
    Company symbol may be null if tax is general.
    """
    date: str  # YYYY-MM-DD format
    company_symbol: Optional[str]
    amount: float
    currency: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "date": self.date,
            "company_symbol": self.company_symbol,
            "amount": self.amount,
            "currency": self.currency,
        }


@dataclass
class Transfer:
    """
    Transfer transaction schema (deposits + cash handling fees).
    
    Represents cash movements: deposits into account or fees charged.
    Type field distinguishes between deposit and fee.
    """
    date: str  # YYYY-MM-DD format
    type: Literal["deposit", "cash_handling_fee"]
    amount: float
    currency: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "date": self.date,
            "type": self.type,
            "amount": self.amount,
            "currency": self.currency,
        }


@dataclass
class ParsedJobResult:
    """
    Final unified output schema.
    
    Contains all categorized transactions from all processed files,
    plus any errors encountered during processing.
    """
    jobId: str
    purchases: list[Purchase]
    sales: list[Sale]
    dividends: list[Dividend]
    taxes: list[Tax]
    transfers: list[Transfer]
    errors: list[str]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "jobId": self.jobId,
            "purchases": [p.to_dict() for p in self.purchases],
            "sales": [s.to_dict() for s in self.sales],
            "dividends": [d.to_dict() for d in self.dividends],
            "taxes": [t.to_dict() for t in self.taxes],
            "transfers": [tr.to_dict() for tr in self.transfers],
            "errors": self.errors,
        }

