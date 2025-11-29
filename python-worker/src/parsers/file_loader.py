"""
File loader for CSV and XLSX portfolio files.

Handles safe file opening, type detection, and error handling.
Delegates to specialized parsers for CSV and Excel files.
"""

import os
import logging
import pandas as pd
from typing import Optional, Tuple
from pathlib import Path

from .csv_parser import parse_csv_file
from .excel_parser import parse_excel_file

logger = logging.getLogger(__name__)


def detect_file_type(file_path: str) -> Optional[str]:
    """
    Detect if file is CSV or XLSX based on extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        'csv', 'xlsx', or None if unknown type
        
    Example:
        >>> detect_file_type("data.csv")
        'csv'
        >>> detect_file_type("data.xlsx")
        'xlsx'
    """
    path = Path(file_path)
    extension = path.suffix.lower()
    
    if extension == '.csv':
        return 'csv'
    elif extension in ['.xlsx', '.xls']:
        return 'xlsx'
    else:
        return None


def load_file(directory: str, filename: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Safely load a CSV or XLSX file into a pandas DataFrame.
    
    This function:
    - Detects file type automatically
    - Handles encoding issues (tries UTF-8, then other encodings)
    - Catches and logs errors without crashing
    - Returns None if file cannot be loaded
    
    Args:
        directory: Directory path where file is stored
        filename: Name of the file to load
        
    Returns:
        Tuple of (DataFrame, error_message)
        - If successful: (DataFrame, None)
        - If failed: (None, error_message)
        
    Example:
        >>> df, error = load_file("/uploads", "portfolio.csv")
        >>> if df is not None:
        ...     print(f"Loaded {len(df)} rows")
    """
    file_path = os.path.join(directory, filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        error_msg = f"File not found: {filename}"
        logger.error(error_msg)
        return None, error_msg
    
    # Detect file type
    file_type = detect_file_type(file_path)
    if file_type is None:
        error_msg = f"Unsupported file type: {filename} (must be .csv or .xlsx)"
        logger.error(error_msg)
        return None, error_msg
    
    # Delegate to specialized parsers
        if file_type == 'csv':
        df, error = parse_csv_file(file_path)
    elif file_type == 'xlsx':
        df, error = parse_excel_file(file_path)
                else:
        # This shouldn't happen due to earlier check, but handle it anyway
        error_msg = f"Unsupported file type: {filename}"
        logger.error(error_msg)
        return None, error_msg
    
    # If parsing failed, return error
    if df is None:
        return None, error
    
    # Log success
        logger.info(f"Successfully loaded {filename}: {len(df)} rows, {len(df.columns)} columns")
        return df, None


def validate_dataframe(df: pd.DataFrame, filename: str) -> Tuple[bool, Optional[str]]:
    """
    Basic validation of loaded DataFrame.
    
    Checks:
    - DataFrame is not empty
    - Has at least some columns
    
    Args:
        df: DataFrame to validate
        filename: Name of the file (for error messages)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if df is None:
        return False, f"{filename}: DataFrame is None"
    
    if df.empty:
        return False, f"{filename}: File is empty (no rows)"
    
    if len(df.columns) == 0:
        return False, f"{filename}: File has no columns"
    
    return True, None

