"""
Transaction processing module.

Handles categorization, transformation, and merging of transactions.
"""

from .categorizer import (
    find_transaction_type_column,
    categorize_transaction,
    get_company_symbol_for_dividend,
)
from .transformer import (
    transform_to_purchase,
    transform_to_sale,
    transform_to_dividend,
    transform_to_tax,
    transform_to_transfer,
)
from .merger import merge_transactions

__all__ = [
    'find_transaction_type_column',
    'categorize_transaction',
    'get_company_symbol_for_dividend',
    'transform_to_purchase',
    'transform_to_sale',
    'transform_to_dividend',
    'transform_to_tax',
    'transform_to_transfer',
    'merge_transactions',
]

