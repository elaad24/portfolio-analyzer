"""
Merger for chronologically merging transactions from multiple files.

Implements the merge strategy:
- If new file dates are older → prepend
- If new file dates are newer → append
- If overlapping → merge while maintaining sorted order
"""

import logging
from typing import TypeVar, List
from ..utils import get_date_boundaries, compare_dates

logger = logging.getLogger(__name__)

# Generic type for transaction objects
T = TypeVar('T')


def get_transaction_date(transaction: any) -> str:
    """
    Extract date from a transaction object.
    
    Works with all transaction types (Purchase, Sale, Dividend, Tax, Transfer).
    
    Args:
        transaction: Transaction object with a 'date' attribute
        
    Returns:
        Date string in YYYY-MM-DD format
    """
    return transaction.date


def merge_transactions(
    existing: List[T],
    new: List[T],
    category_name: str = "transactions"
) -> List[T]:
    """
    Merge two sorted lists of transactions chronologically.
    
    Strategy:
    1. If new list is empty → return existing
    2. If existing list is empty → return new
    3. Compare date boundaries:
       - If all new dates < all existing dates → prepend new
       - If all new dates > all existing dates → append new
       - If overlapping → merge while maintaining sorted order
    
    Args:
        existing: Existing sorted list of transactions
        new: New sorted list of transactions to merge
        category_name: Name of category (for logging)
        
    Returns:
        Merged sorted list of transactions
        
    Example:
        >>> existing = [Purchase(date="2023-02-01", ...), Purchase(date="2023-03-01", ...)]
        >>> new = [Purchase(date="2023-01-01", ...), Purchase(date="2023-01-15", ...)]
        >>> merged = merge_transactions(existing, new)
        >>> # Result: [new[0], new[1], existing[0], existing[1]]
    """
    # If new list is empty, return existing
    if not new:
        return existing
    
    # If existing list is empty, return new
    if not existing:
        return new
    
    # Get date boundaries for both lists
    existing_dates = [get_transaction_date(t) for t in existing]
    new_dates = [get_transaction_date(t) for t in new]
    
    existing_min, existing_max = get_date_boundaries(existing_dates)
    new_min, new_max = get_date_boundaries(new_dates)
    
    # If we can't determine boundaries, fall back to simple merge
    if existing_min is None or existing_max is None or new_min is None or new_max is None:
        logger.warning(f"Could not determine date boundaries for {category_name}, using simple merge")
        return _simple_merge(existing, new)
    
    # Strategy 1: All new dates are older than all existing dates → prepend
    if compare_dates(new_max, existing_min) < 0:
        logger.debug(f"{category_name}: New data is older, prepending")
        return new + existing
    
    # Strategy 2: All new dates are newer than all existing dates → append
    if compare_dates(new_min, existing_max) > 0:
        logger.debug(f"{category_name}: New data is newer, appending")
        return existing + new
    
    # Strategy 3: Dates overlap → merge while maintaining sorted order
    logger.debug(f"{category_name}: Dates overlap, performing sorted merge")
    return _sorted_merge(existing, new)


def _simple_merge(existing: List[T], new: List[T]) -> List[T]:
    """
    Simple merge: combine lists and sort by date.
    
    Used as fallback when date boundaries cannot be determined.
    
    Args:
        existing: Existing list
        new: New list
        
    Returns:
        Combined and sorted list
    """
    combined = existing + new
    # Sort by date
    combined.sort(key=get_transaction_date)
    return combined


def _sorted_merge(existing: List[T], new: List[T]) -> List[T]:
    """
    Merge two sorted lists while maintaining sorted order.
    
    Uses a two-pointer merge algorithm (like merge sort).
    Both lists are assumed to be already sorted by date.
    
    Args:
        existing: Existing sorted list
        new: New sorted list
        
    Returns:
        Merged sorted list
    """
    result = []
    i = 0  # Pointer for existing
    j = 0  # Pointer for new
    
    while i < len(existing) and j < len(new):
        existing_date = get_transaction_date(existing[i])
        new_date = get_transaction_date(new[j])
        
        # Compare dates and add the earlier one
        if compare_dates(existing_date, new_date) <= 0:
            result.append(existing[i])
            i += 1
        else:
            result.append(new[j])
            j += 1
    
    # Add remaining elements
    result.extend(existing[i:])
    result.extend(new[j:])
    
    return result

