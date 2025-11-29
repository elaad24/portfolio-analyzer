"""
Transformers for converting raw DataFrame rows into structured transaction objects.

Maps columns (A, B, C, etc.) to schema fields according to the specification.
"""

import logging
from typing import Optional
import pandas as pd

from ..schemas import Purchase, Sale, Dividend, Tax, Transfer
from ..utils import parse_date, parse_float

logger = logging.getLogger(__name__)

# Column mapping according to spec:
# Column A -> date
# Column D -> company_symbol
# Column E -> quantity
# Column F -> unit_price
# Column G -> currency
# Column H -> transaction_fee
# Column J -> proceeds_foreign
# Column K -> proceeds_ils


def get_column_by_index(df: pd.DataFrame, column_index: int) -> Optional[str]:
    """
    Get column name by 0-based index.
    
    Column A = index 0, Column B = index 1, etc.
    
    Args:
        df: DataFrame
        column_index: 0-based column index
        
    Returns:
        Column name if exists, None otherwise
    """
    if column_index < 0 or column_index >= len(df.columns):
        return None
    return df.columns[column_index]


def get_cell_value(row: pd.Series, df: pd.DataFrame, column_index: int, default=None):
    """
    Safely get cell value from a row by column index.
    
    Uses the DataFrame's column order to determine which column to access.
    
    Args:
        row: Pandas Series (single row)
        df: Full DataFrame (for column order reference)
        column_index: 0-based column index
        default: Default value if column doesn't exist
        
    Returns:
        Cell value or default
    """
    if column_index < 0 or column_index >= len(df.columns):
        return default
    
    col_name = df.columns[column_index]
    
    if col_name not in row.index:
        return default
    
    value = row[col_name]
    # Handle pandas NaN
    if pd.isna(value):
        return default
    
    return value


def transform_to_purchase(row: pd.Series, df: pd.DataFrame) -> Optional[Purchase]:
    """
    Transform a row into a Purchase transaction object.
    
    Maps columns according to spec:
    - Column A (index 0) -> date
    - Column D (index 3) -> company_symbol
    - Column E (index 4) -> quantity
    - Column F (index 5) -> unit_price
    - Column G (index 6) -> currency
    - Column H (index 7) -> transaction_fee
    - Column J (index 9) -> proceeds_foreign
    - Column K (index 10) -> proceeds_ils
    
    Args:
        row: Pandas Series (single row)
        df: Full DataFrame (for column reference)
        
    Returns:
        Purchase object or None if required fields are missing
    """
    # Extract date (Column A = index 0)
    date_str = parse_date(get_cell_value(row, df, 0))
    if date_str is None:
        return None  # Date is required
    
    # Extract company symbol (Column D = index 3)
    company_symbol = get_cell_value(row, df, 3, "")
    if not company_symbol:
        company_symbol = ""  # Allow empty but not None
    
    # Extract quantity (Column E = index 4)
    quantity = parse_float(get_cell_value(row, df, 4))
    if quantity is None:
        return None  # Quantity is required
    
    # Extract unit price (Column F = index 5)
    unit_price = parse_float(get_cell_value(row, df, 5))
    if unit_price is None:
        return None  # Unit price is required
    
    # Extract currency (Column G = index 6)
    currency = str(get_cell_value(row, df, 6, "")).strip()
    if not currency:
        currency = "USD"  # Default currency
    
    # Extract optional fields
    transaction_fee = parse_float(get_cell_value(row, df, 7))  # Column H
    proceeds_foreign = parse_float(get_cell_value(row, df, 9))  # Column J
    proceeds_ils = parse_float(get_cell_value(row, df, 10))  # Column K
    
    return Purchase(
        date=date_str,
        company_symbol=str(company_symbol),
        quantity=quantity,
        unit_price=unit_price,
        currency=currency,
        transaction_fee=transaction_fee,
        proceeds_foreign=proceeds_foreign,
        proceeds_ils=proceeds_ils,
    )


def transform_to_sale(row: pd.Series, df: pd.DataFrame) -> Optional[Sale]:
    """
    Transform a row into a Sale transaction object.
    
    Same mapping as Purchase.
    
    Args:
        row: Pandas Series (single row)
        df: Full DataFrame
        
    Returns:
        Sale object or None if required fields are missing
    """
    # Same transformation as purchase
    purchase = transform_to_purchase(row, df)
    if purchase is None:
        return None
    
    return Sale(
        date=purchase.date,
        company_symbol=purchase.company_symbol,
        quantity=purchase.quantity,
        unit_price=purchase.unit_price,
        currency=purchase.currency,
        transaction_fee=purchase.transaction_fee,
        proceeds_foreign=purchase.proceeds_foreign,
        proceeds_ils=purchase.proceeds_ils,
    )


def transform_to_dividend(row: pd.Series, df: pd.DataFrame, company_symbol: Optional[str] = None) -> Optional[Dividend]:
    """
    Transform a row into a Dividend transaction object.
    
    Dividends have simpler schema: date, company_symbol, amount, currency.
    
    Args:
        row: Pandas Series (single row)
        df: Full DataFrame
        company_symbol: Company symbol (may be extracted from next column)
        
    Returns:
        Dividend object or None if required fields are missing
    """
    # Extract date (Column A = index 0)
    date_str = parse_date(get_cell_value(row, df, 0))
    if date_str is None:
        return None
    
    # Use provided company symbol or extract from Column D
    if company_symbol is None:
        company_symbol = str(get_cell_value(row, df, 3, "")).strip()
    
    if not company_symbol:
        company_symbol = ""  # Allow empty
    
    # For dividends, amount might be in different columns
    # Try Column J (proceeds_foreign) or Column K (proceeds_ils) or Column F (unit_price)
    amount = parse_float(get_cell_value(row, df, 9))  # Try Column J first
    if amount is None:
        amount = parse_float(get_cell_value(row, df, 10))  # Try Column K
    if amount is None:
        amount = parse_float(get_cell_value(row, df, 5))  # Try Column F (unit_price)
    
    if amount is None:
        return None  # Amount is required
    
    # Extract currency (Column G = index 6)
    currency = str(get_cell_value(row, df, 6, "")).strip()
    if not currency:
        currency = "USD"  # Default currency
    
    return Dividend(
        date=date_str,
        company_symbol=company_symbol,
        amount=amount,
        currency=currency,
    )


def transform_to_tax(row: pd.Series, df: pd.DataFrame, company_symbol: Optional[str] = None) -> Optional[Tax]:
    """
    Transform a row into a Tax transaction object.
    
    Args:
        row: Pandas Series (single row)
        df: Full DataFrame
        company_symbol: Company symbol (optional for taxes)
        
    Returns:
        Tax object or None if required fields are missing
    """
    # Extract date (Column A = index 0)
    date_str = parse_date(get_cell_value(row, df, 0))
    if date_str is None:
        return None
    
    # Company symbol is optional for taxes
    if company_symbol is None:
        company_symbol = str(get_cell_value(row, df, 3, "")).strip()
        if not company_symbol:
            company_symbol = None  # Allow None for taxes
    
    # Extract amount (try multiple columns)
    amount = parse_float(get_cell_value(row, df, 9))  # Column J
    if amount is None:
        amount = parse_float(get_cell_value(row, df, 10))  # Column K
    if amount is None:
        amount = parse_float(get_cell_value(row, df, 5))  # Column F
    
    if amount is None:
        return None  # Amount is required
    
    # Extract currency (Column G = index 6)
    currency = str(get_cell_value(row, df, 6, "")).strip()
    if not currency:
        currency = "USD"
    
    return Tax(
        date=date_str,
        company_symbol=company_symbol,
        amount=amount,
        currency=currency,
    )


def transform_to_transfer(row: pd.Series, df: pd.DataFrame, transfer_type: str) -> Optional[Transfer]:
    """
    Transform a row into a Transfer transaction object (deposit or fee).
    
    Args:
        row: Pandas Series (single row)
        df: Full DataFrame
        transfer_type: Either "deposit" or "cash_handling_fee"
        
    Returns:
        Transfer object or None if required fields are missing
    """
    # Extract date (Column A = index 0)
    date_str = parse_date(get_cell_value(row, df, 0))
    if date_str is None:
        return None
    
    # Extract amount (try multiple columns)
    amount = parse_float(get_cell_value(row, df, 9))  # Column J
    if amount is None:
        amount = parse_float(get_cell_value(row, df, 10))  # Column K
    if amount is None:
        amount = parse_float(get_cell_value(row, df, 5))  # Column F
    
    if amount is None:
        return None  # Amount is required
    
    # Extract currency (Column G = index 6)
    currency = str(get_cell_value(row, df, 6, "")).strip()
    if not currency:
        currency = "USD"
    
    return Transfer(
        date=date_str,
        type=transfer_type,
        amount=amount,
        currency=currency,
    )

