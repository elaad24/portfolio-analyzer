"""
Date utility functions for parsing and formatting dates.

Handles various date formats from CSV/Excel files and normalizes them
to YYYY-MM-DD format required by the schema.
"""

import re
from datetime import datetime
from typing import Optional


def parse_date(date_value: any) -> Optional[str]:
    """
    Parse a date value into YYYY-MM-DD format.
    
    Handles multiple input types:
    - String dates in various formats
    - Pandas Timestamp objects
    - Python datetime objects
    - Excel serial dates (if passed as float)
    
    Args:
        date_value: Date value from CSV/Excel (can be string, datetime, Timestamp, etc.)
        
    Returns:
        Date string in YYYY-MM-DD format, or None if parsing fails
        
    Example:
        >>> parse_date("2023-01-15")
        '2023-01-15'
        >>> parse_date("01/15/2023")
        '2023-01-15'
    """
    if date_value is None:
        return None
    
    # If it's already a string in YYYY-MM-DD format, return as-is
    if isinstance(date_value, str):
        # Check if it's already in the correct format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_value):
            return date_value
        
        # Try common date formats
        formats = [
            '%Y-%m-%d',      # 2023-01-15
            '%m/%d/%Y',      # 01/15/2023
            '%d/%m/%Y',      # 15/01/2023
            '%Y/%m/%d',      # 2023/01/15
            '%d-%m-%Y',      # 15-01-2023
            '%m-%d-%Y',      # 01-15-2023
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_value.strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
    
    # Handle pandas Timestamp objects
    if hasattr(date_value, 'strftime'):
        try:
            return date_value.strftime('%Y-%m-%d')
        except (AttributeError, ValueError):
            pass
    
    # Handle datetime objects directly
    if isinstance(date_value, datetime):
        try:
            return date_value.strftime('%Y-%m-%d')
        except (ValueError, AttributeError):
            pass
    
    return None


def compare_dates(date1: str, date2: str) -> int:
    """
    Compare two date strings in YYYY-MM-DD format.
    
    Args:
        date1: First date string
        date2: Second date string
        
    Returns:
        -1 if date1 < date2, 0 if equal, 1 if date1 > date2
        
    Example:
        >>> compare_dates("2023-01-15", "2023-02-01")
        -1
    """
    try:
        d1 = datetime.strptime(date1, '%Y-%m-%d')
        d2 = datetime.strptime(date2, '%Y-%m-%d')
        
        if d1 < d2:
            return -1
        elif d1 > d2:
            return 1
        else:
            return 0
    except (ValueError, TypeError):
        # If dates are invalid, treat as equal to avoid sorting issues
        return 0


def get_date_boundaries(dates: list[str]) -> tuple[Optional[str], Optional[str]]:
    """
    Get the earliest and latest dates from a list.
    
    Useful for determining merge strategy (prepend vs append).
    
    Args:
        dates: List of date strings in YYYY-MM-DD format
        
    Returns:
        Tuple of (earliest_date, latest_date), or (None, None) if empty
        
    Example:
        >>> get_date_boundaries(["2023-01-15", "2023-02-01", "2023-01-20"])
        ('2023-01-15', '2023-02-01')
    """
    if not dates:
        return None, None
    
    # Filter out None values
    valid_dates = [d for d in dates if d is not None]
    
    if not valid_dates:
        return None, None
    
    # Sort to get min and max
    sorted_dates = sorted(valid_dates)
    return sorted_dates[0], sorted_dates[-1]

