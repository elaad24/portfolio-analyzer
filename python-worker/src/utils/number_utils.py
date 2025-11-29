"""
Number utility functions for safe parsing of numeric values.

Handles various number formats from CSV/Excel files and converts them
to float, handling edge cases like commas, currency symbols, etc.
"""

import re
from typing import Optional


def parse_float(value: any) -> Optional[float]:
    """
    Safely parse a value to float.
    
    Handles:
    - String numbers with commas (1,234.56)
    - String numbers with currency symbols ($1,234.56)
    - Already numeric values
    - Empty strings and None values
    
    Args:
        value: Value to parse (string, int, float, None, etc.)
        
    Returns:
        Float value, or None if parsing fails
        
    Example:
        >>> parse_float("1,234.56")
        1234.56
        >>> parse_float("$1,234.56")
        1234.56
        >>> parse_float(None)
        None
    """
    if value is None:
        return None
    
    # If already a number, convert and return
    if isinstance(value, (int, float)):
        return float(value)
    
    # If it's a string, clean it first
    if isinstance(value, str):
        # Remove whitespace
        cleaned = value.strip()
        
        # Empty string returns None
        if not cleaned or cleaned == '':
            return None
        
        # Remove currency symbols and commas
        # This regex removes $, €, £, commas, and spaces
        cleaned = re.sub(r'[$€£,\s]', '', cleaned)
        
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    
    return None


def parse_int(value: any) -> Optional[int]:
    """
    Safely parse a value to integer.
    
    Similar to parse_float but returns int.
    Useful for quantity fields.
    
    Args:
        value: Value to parse
        
    Returns:
        Integer value, or None if parsing fails
        
    Example:
        >>> parse_int("123")
        123
        >>> parse_int("123.45")
        123
    """
    float_value = parse_float(value)
    if float_value is None:
        return None
    
    try:
        return int(float_value)
    except (ValueError, TypeError):
        return None


def safe_divide(numerator: float, denominator: float) -> Optional[float]:
    """
    Safely divide two numbers, handling division by zero.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        
    Returns:
        Division result, or None if denominator is zero or invalid
        
    Example:
        >>> safe_divide(10, 2)
        5.0
        >>> safe_divide(10, 0)
        None
    """
    if denominator is None or denominator == 0:
        return None
    
    try:
        return float(numerator) / float(denominator)
    except (ValueError, TypeError, ZeroDivisionError):
        return None

