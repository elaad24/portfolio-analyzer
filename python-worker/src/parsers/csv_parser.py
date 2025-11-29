"""
CSV file parser for portfolio files.

Handles CSV-specific parsing logic including encoding detection and error handling.
"""

import logging
import pandas as pd
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def parse_csv_file(file_path: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Parse a CSV file into a pandas DataFrame.
    
    Handles multiple encodings:
    - Tries UTF-8 first (most common)
    - Falls back to latin-1, iso-8859-1, cp1252 if UTF-8 fails
    
    Args:
        file_path: Full path to the CSV file
        
    Returns:
        Tuple of (DataFrame, error_message)
        - If successful: (DataFrame, None)
        - If failed: (None, error_message)
    """
    try:
        # Try UTF-8 first (most common)
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            logger.debug(f"Loaded CSV with UTF-8 encoding: {file_path}")
            return df, None
        except UnicodeDecodeError:
            # Try other common encodings
            encodings = ['latin-1', 'iso-8859-1', 'cp1252']
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    logger.info(f"Loaded CSV with {encoding} encoding: {file_path}")
                    return df, None
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail
            error_msg = f"Could not decode CSV file with any supported encoding: {file_path}"
            logger.error(error_msg)
            return None, error_msg
    
    except pd.errors.EmptyDataError:
        error_msg = f"CSV file is empty: {file_path}"
        logger.error(error_msg)
        return None, error_msg
    
    except pd.errors.ParserError as e:
        error_msg = f"CSV parsing error in {file_path}: {str(e)}"
        logger.error(error_msg)
        return None, error_msg
    
    except Exception as e:
        error_msg = f"Unexpected error loading CSV file {file_path}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return None, error_msg

