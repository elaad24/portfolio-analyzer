"""
Unit tests for the portfolio parser.

Tests the core parsing logic, categorization, and merging functionality.
"""

import unittest
import os
import tempfile
import pandas as pd
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orchestrator import PortfolioParser
from schemas import ParsedJobResult


class TestPortfolioParser(unittest.TestCase):
    """Test cases for PortfolioParser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.job_id = "test-job-123"
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_csv(self, filename: str, rows: list):
        """
        Helper to create a test CSV file.
        
        Args:
            filename: Name of the file
            rows: List of dictionaries representing rows
        """
        df = pd.DataFrame(rows)
        filepath = os.path.join(self.temp_dir, filename)
        df.to_csv(filepath, index=False)
        return filepath
    
    def test_parse_single_file(self):
        """Test parsing a single CSV file."""
        # Create test CSV with purchase transaction
        rows = [
            {
                'Date': '2023-01-15',
                'Transaction Type': 'Buy',
                'Company': 'AAPL',
                'Symbol': 'AAPL',
                'Quantity': '10',
                'Price': '150.50',
                'Currency': 'USD',
                'Fee': '1.00',
                'Proceeds Foreign': '1505.00',
                'Proceeds ILS': '5500.00'
            }
        ]
        
        self.create_test_csv('test.csv', rows)
        
        # Parse
        parser = PortfolioParser(self.job_id)
        result = parser.parse_job(self.temp_dir, ['test.csv'])
        
        # Assertions
        self.assertEqual(result.jobId, self.job_id)
        self.assertEqual(len(result.purchases), 1)
        self.assertEqual(result.purchases[0].company_symbol, 'AAPL')
        self.assertEqual(result.purchases[0].quantity, 10.0)
    
    def test_categorize_purchase(self):
        """Test that purchases are correctly categorized."""
        rows = [
            {
                'Date': '2023-01-15',
                'Transaction Type': 'Buy',
                'Symbol': 'AAPL',
                'Quantity': '10',
                'Price': '150.50',
                'Currency': 'USD'
            }
        ]
        
        self.create_test_csv('purchase.csv', rows)
        
        parser = PortfolioParser(self.job_id)
        result = parser.parse_job(self.temp_dir, ['purchase.csv'])
        
        self.assertEqual(len(result.purchases), 1)
        self.assertEqual(len(result.sales), 0)
    
    def test_categorize_sale(self):
        """Test that sales are correctly categorized."""
        rows = [
            {
                'Date': '2023-02-01',
                'Transaction Type': 'Sell',
                'Symbol': 'AAPL',
                'Quantity': '5',
                'Price': '160.00',
                'Currency': 'USD'
            }
        ]
        
        self.create_test_csv('sale.csv', rows)
        
        parser = PortfolioParser(self.job_id)
        result = parser.parse_job(self.temp_dir, ['sale.csv'])
        
        self.assertEqual(len(result.sales), 1)
        self.assertEqual(len(result.purchases), 0)
    
    def test_merge_multiple_files(self):
        """Test merging transactions from multiple files chronologically."""
        # File 1: Older transactions
        rows1 = [
            {
                'Date': '2023-02-01',
                'Transaction Type': 'Buy',
                'Symbol': 'AAPL',
                'Quantity': '10',
                'Price': '150.00',
                'Currency': 'USD'
            }
        ]
        
        # File 2: Newer transactions
        rows2 = [
            {
                'Date': '2023-01-15',
                'Transaction Type': 'Buy',
                'Symbol': 'MSFT',
                'Quantity': '5',
                'Price': '300.00',
                'Currency': 'USD'
            }
        ]
        
        self.create_test_csv('file1.csv', rows1)
        self.create_test_csv('file2.csv', rows2)
        
        parser = PortfolioParser(self.job_id)
        result = parser.parse_job(self.temp_dir, ['file1.csv', 'file2.csv'])
        
        # Should have 2 purchases, sorted chronologically
        self.assertEqual(len(result.purchases), 2)
        # First purchase should be from file2 (older date)
        self.assertEqual(result.purchases[0].date, '2023-01-15')
        self.assertEqual(result.purchases[0].company_symbol, 'MSFT')
        # Second purchase should be from file1 (newer date)
        self.assertEqual(result.purchases[1].date, '2023-02-01')
        self.assertEqual(result.purchases[1].company_symbol, 'AAPL')
    
    def test_handle_missing_file(self):
        """Test error handling for missing files."""
        parser = PortfolioParser(self.job_id)
        result = parser.parse_job(self.temp_dir, ['nonexistent.csv'])
        
        # Should have errors
        self.assertGreater(len(result.errors), 0)
        self.assertTrue(any('nonexistent.csv' in error for error in result.errors))


if __name__ == '__main__':
    unittest.main()

