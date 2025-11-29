"""
Excel file parser for portfolio files.

Handles XLSX and XLS file parsing with proper error handling.
"""

import logging
import pandas as pd
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def parse_excel_file(file_path: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Parse an Excel file (XLSX or XLS) into a pandas DataFrame.
    
    Uses openpyxl engine for XLSX files. Handles Excel-specific errors.
    
    Args:
        file_path: Full path to the Excel file
        
    Returns:
        Tuple of (DataFrame, error_message)
        - If successful: (DataFrame, None)
        - If failed: (None, error_message)
    """
    try:
        # Use openpyxl engine for XLSX files
        df = pd.read_excel(file_path, engine='openpyxl')
        logger.debug(f"Successfully loaded Excel file: {file_path}")
        return df, None
    
    except FileNotFoundError:
        error_msg = f"Excel file not found: {file_path}"
        logger.error(error_msg)
        return None, error_msg
    
    except pd.errors.EmptyDataError:
        error_msg = f"Excel file is empty: {file_path}"
        logger.error(error_msg)
        return None, error_msg
    
    except ValueError as e:
        # openpyxl may raise ValueError for corrupted files
        error_msg = f"Excel file appears to be corrupted: {file_path} - {str(e)}"
        logger.error(error_msg)
        return None, error_msg
    
    except Exception as e:
        error_msg = f"Unexpected error loading Excel file {file_path}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return None, error_msg

