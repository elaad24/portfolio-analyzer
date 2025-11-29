"""
Transaction categorizer for portfolio rows.

Classifies rows into transaction types based on text patterns in the
"Transaction Type" column (or similar columns).
"""

import logging
from typing import Optional, Literal
import pandas as pd

logger = logging.getLogger(__name__)

# Transaction type constants for categorization
PURCHASE_KEYWORDS = ["Buy", "Purchase", "ExecutedBuy"]
SALE_KEYWORDS = ["Sell", "Sale", "ExecutedSell"]
DIVIDEND_KEYWORDS = ["Dividend"]
TAX_KEYWORDS = ["Withholding", "Tax", "Foreign Tax"]
DEPOSIT_KEYWORDS = ["Deposit", "Cash Transfer"]
FEE_KEYWORDS = ["Cash Handling Fee", "Fee", "Handling"]


def find_transaction_type_column(df: pd.DataFrame) -> Optional[str]:
    """
    Find the column that contains transaction type information.
    
    Looks for common column names like "Transaction Type", "Type", "Transaction", etc.
    
    Args:
        df: DataFrame to search
        
    Returns:
        Column name if found, None otherwise
        
    Example:
        >>> df = pd.DataFrame({"Transaction Type": ["Buy", "Sell"], "Amount": [100, 200]})
        >>> find_transaction_type_column(df)
        'Transaction Type'
    """
    # Common column names for transaction type
    possible_names = [
        "Transaction Type",
        "Type",
        "Transaction",
        "Action",
        "TransactionType",
        "transaction_type",
        "type",
    ]
    
    # Check exact matches first (case-sensitive)
    for name in possible_names:
        if name in df.columns:
            return name
    
    # Check case-insensitive matches
    df_columns_lower = [col.lower() for col in df.columns]
    for name in possible_names:
        if name.lower() in df_columns_lower:
            # Return the actual column name (preserve original case)
            idx = df_columns_lower.index(name.lower())
            return df.columns[idx]
    
    return None


def categorize_transaction(row: pd.Series, transaction_type_col: Optional[str] = None) -> Optional[str]:
    """
    Categorize a single row into a transaction type.
    
    Uses text matching on the transaction type column to determine category.
    Returns None if no match is found.
    
    Args:
        row: Pandas Series representing a single row
        transaction_type_col: Name of the column containing transaction type
        
    Returns:
        Transaction category: 'purchase', 'sale', 'dividend', 'tax', 'deposit', 'fee'
        or None if no match
        
    Example:
        >>> row = pd.Series({"Transaction Type": "Buy", "Amount": 100})
        >>> categorize_transaction(row, "Transaction Type")
        'purchase'
    """
    # If no transaction type column specified, try to find it
    if transaction_type_col is None:
        # This won't work with a single row, so we need the full DataFrame
        # For now, assume it's passed in
        return None
    
    # Get the transaction type value
    if transaction_type_col not in row.index:
        return None
    
    transaction_type = str(row[transaction_type_col]).strip()
    
    # Case-insensitive matching
    transaction_type_lower = transaction_type.lower()
    
    # Check for purchases
    for keyword in PURCHASE_KEYWORDS:
        if keyword.lower() in transaction_type_lower:
            return 'purchase'
    
    # Check for sales
    for keyword in SALE_KEYWORDS:
        if keyword.lower() in transaction_type_lower:
            return 'sale'
    
    # Check for dividends (must contain "dividend")
    for keyword in DIVIDEND_KEYWORDS:
        if keyword.lower() in transaction_type_lower:
            return 'dividend'
    
    # Check for tax withholding
    for keyword in TAX_KEYWORDS:
        if keyword.lower() in transaction_type_lower:
            return 'tax'
    
    # Check for deposits
    for keyword in DEPOSIT_KEYWORDS:
        if keyword.lower() in transaction_type_lower:
            return 'deposit'
    
    # Check for cash handling fees
    for keyword in FEE_KEYWORDS:
        if keyword.lower() in transaction_type_lower:
            return 'fee'
    
    return None


def get_company_symbol_for_dividend(row: pd.Series, transaction_type_col: str) -> Optional[str]:
    """
    Extract company symbol for dividend transactions.
    
    According to spec: "Company symbol = next column to the right"
    This means we look for the column immediately after the transaction type column.
    
    Args:
        row: Pandas Series representing a single row
        transaction_type_col: Name of the transaction type column
        
    Returns:
        Company symbol string, or None if not found
        
    Example:
        >>> row = pd.Series({"Transaction Type": "Dividend", "Company": "AAPL", "Amount": 100})
        >>> get_company_symbol_for_dividend(row, "Transaction Type")
        'AAPL'  # Assuming "Company" is the next column
    """
    if transaction_type_col not in row.index:
        return None
    
    # Get the index of the transaction type column
    cols = list(row.index)
    try:
        type_col_idx = cols.index(transaction_type_col)
        # Get the next column (if it exists)
        if type_col_idx + 1 < len(cols):
            next_col = cols[type_col_idx + 1]
            symbol = row[next_col]
            # Convert to string and clean
            if pd.notna(symbol):
                return str(symbol).strip()
    except (ValueError, IndexError):
        pass
    
    # Fallback: look for common column names
    possible_symbol_cols = [
        "Company Symbol",
        "Symbol",
        "Company",
        "Ticker",
        "company_symbol",
        "symbol",
    ]
    
    for col in possible_symbol_cols:
        if col in row.index and pd.notna(row[col]):
            return str(row[col]).strip()
    
    return None

