"""
Main parser orchestration logic.

Coordinates file loading, categorization, transformation, sorting, and merging.
This is the core processing pipeline that implements all 5 mandatory steps.
"""

import logging
from typing import List
import pandas as pd

from .schemas import (
    ParsedJobResult,
    Purchase,
    Sale,
    Dividend,
    Tax,
    Transfer,
)
from .parsers import load_file, validate_dataframe
from .processors import (
    find_transaction_type_column,
    categorize_transaction,
    get_company_symbol_for_dividend,
    transform_to_purchase,
    transform_to_sale,
    transform_to_dividend,
    transform_to_tax,
    transform_to_transfer,
    merge_transactions,
)
from .utils import parse_date

logger = logging.getLogger(__name__)


class PortfolioParser:
    """
    Main parser class that orchestrates the entire parsing pipeline.
    
    Processes multiple files, categorizes transactions, and merges them
    into a unified chronological dataset.
    """
    
    def __init__(self, job_id: str):
        """
        Initialize parser with a job ID.
        
        Args:
            job_id: Unique job identifier
        """
        self.job_id = job_id
        # Accumulated results (global state for merging)
        self.purchases: List[Purchase] = []
        self.sales: List[Sale] = []
        self.dividends: List[Dividend] = []
        self.taxes: List[Tax] = []
        self.transfers: List[Transfer] = []
        self.errors: List[str] = []
    
    def parse_job(self, directory: str, files: List[str]) -> ParsedJobResult:
        """
        Parse all files for a job and return unified result.
        
        This is the main entry point that implements the 5-step pipeline:
        1. Load each file
        2. Iterate rows and categorize
        3. Sort each category by date
        4. Merge with global accumulated data
        5. Return unified object
        
        Args:
            directory: Directory path where files are stored
            files: List of filenames to process
            
        Returns:
            ParsedJobResult with all transactions and errors
        """
        logger.info(f"Starting job {self.job_id}: processing {len(files)} files")
        
        # Process each file one by one
        for filename in files:
            logger.info(f"Processing file: {filename}")
            self._process_file(directory, filename)
        
        # Return final unified result
        result = ParsedJobResult(
            jobId=self.job_id,
            purchases=self.purchases,
            sales=self.sales,
            dividends=self.dividends,
            taxes=self.taxes,
            transfers=self.transfers,
            errors=self.errors,
        )
        
        logger.info(
            f"Job {self.job_id} complete: "
            f"{len(self.purchases)} purchases, "
            f"{len(self.sales)} sales, "
            f"{len(self.dividends)} dividends, "
            f"{len(self.taxes)} taxes, "
            f"{len(self.transfers)} transfers, "
            f"{len(self.errors)} errors"
        )
        
        return result
    
    def _process_file(self, directory: str, filename: str):
        """
        Process a single file through the pipeline.
        
        Steps:
        1. Load file
        2. Iterate rows and categorize
        3. Transform to schema objects
        4. Sort by date
        5. Merge with accumulated data
        
        Args:
            directory: Directory path
            filename: Filename to process
        """
        # Step 1: Load file
        df, error = load_file(directory, filename)
        if df is None:
            self.errors.append(f"File {filename} failed to load: {error}")
            return
        
        # Validate DataFrame
        is_valid, validation_error = validate_dataframe(df, filename)
        if not is_valid:
            self.errors.append(f"File {filename} validation failed: {validation_error}")
            return
        
        # Find transaction type column
        transaction_type_col = find_transaction_type_column(df)
        if transaction_type_col is None:
            self.errors.append(
                f"File {filename}: Could not find transaction type column. "
                f"Available columns: {list(df.columns)}"
            )
            # Continue anyway - might be able to infer from other columns
        
        # Step 2: Iterate rows and categorize
        file_purchases: List[Purchase] = []
        file_sales: List[Sale] = []
        file_dividends: List[Dividend] = []
        file_taxes: List[Tax] = []
        file_transfers: List[Transfer] = []
        
        for idx, row in df.iterrows():
            try:
                # Categorize the row
                category = categorize_transaction(row, transaction_type_col)
                
                if category == 'purchase':
                    purchase = transform_to_purchase(row, df)
                    if purchase:
                        file_purchases.append(purchase)
                    else:
                        self.errors.append(
                            f"File {filename}, row {idx + 1}: Failed to transform purchase"
                        )
                
                elif category == 'sale':
                    sale = transform_to_sale(row, df)
                    if sale:
                        file_sales.append(sale)
                    else:
                        self.errors.append(
                            f"File {filename}, row {idx + 1}: Failed to transform sale"
                        )
                
                elif category == 'dividend':
                    # Get company symbol from next column
                    company_symbol = get_company_symbol_for_dividend(row, transaction_type_col or "")
                    dividend = transform_to_dividend(row, df, company_symbol)
                    if dividend:
                        file_dividends.append(dividend)
                    else:
                        self.errors.append(
                            f"File {filename}, row {idx + 1}: Failed to transform dividend"
                        )
                
                elif category == 'tax':
                    tax = transform_to_tax(row, df)
                    if tax:
                        file_taxes.append(tax)
                    else:
                        self.errors.append(
                            f"File {filename}, row {idx + 1}: Failed to transform tax"
                        )
                
                elif category == 'deposit':
                    transfer = transform_to_transfer(row, df, "deposit")
                    if transfer:
                        file_transfers.append(transfer)
                    else:
                        self.errors.append(
                            f"File {filename}, row {idx + 1}: Failed to transform deposit"
                        )
                
                elif category == 'fee':
                    transfer = transform_to_transfer(row, df, "cash_handling_fee")
                    if transfer:
                        file_transfers.append(transfer)
                    else:
                        self.errors.append(
                            f"File {filename}, row {idx + 1}: Failed to transform fee"
                        )
                
                # If category is None, skip the row (not a recognized transaction type)
                # This is normal - not all rows are transactions
                
            except Exception as e:
                self.errors.append(
                    f"File {filename}, row {idx + 1}: Error processing row: {str(e)}"
                )
                logger.error(f"Error processing row {idx + 1} in {filename}: {e}", exc_info=True)
        
        # Step 3: Sort each category by date (within this file)
        file_purchases.sort(key=lambda x: x.date)
        file_sales.sort(key=lambda x: x.date)
        file_dividends.sort(key=lambda x: x.date)
        file_taxes.sort(key=lambda x: x.date)
        file_transfers.sort(key=lambda x: x.date)
        
        # Step 4: Merge with global accumulated data
        self.purchases = merge_transactions(self.purchases, file_purchases, "purchases")
        self.sales = merge_transactions(self.sales, file_sales, "sales")
        self.dividends = merge_transactions(self.dividends, file_dividends, "dividends")
        self.taxes = merge_transactions(self.taxes, file_taxes, "taxes")
        self.transfers = merge_transactions(self.transfers, file_transfers, "transfers")
        
        logger.info(
            f"File {filename} processed: "
            f"{len(file_purchases)} purchases, "
            f"{len(file_sales)} sales, "
            f"{len(file_dividends)} dividends, "
            f"{len(file_taxes)} taxes, "
            f"{len(file_transfers)} transfers"
        )

