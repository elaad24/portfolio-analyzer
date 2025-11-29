"""
Unit tests for the transaction merger.

Tests the chronological merging logic for multiple files.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from processors.merger import merge_transactions
from schemas import Purchase


class TestMerger(unittest.TestCase):
    """Test cases for transaction merging."""
    
    def test_merge_newer_append(self):
        """Test that newer transactions are appended."""
        existing = [
            Purchase(date="2023-01-15", company_symbol="AAPL", quantity=10.0, 
                    unit_price=150.0, currency="USD")
        ]
        
        new = [
            Purchase(date="2023-02-01", company_symbol="MSFT", quantity=5.0,
                    unit_price=300.0, currency="USD")
        ]
        
        merged = merge_transactions(existing, new, "purchases")
        
        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0].date, "2023-01-15")
        self.assertEqual(merged[1].date, "2023-02-01")
    
    def test_merge_older_prepend(self):
        """Test that older transactions are prepended."""
        existing = [
            Purchase(date="2023-02-01", company_symbol="AAPL", quantity=10.0,
                    unit_price=150.0, currency="USD")
        ]
        
        new = [
            Purchase(date="2023-01-15", company_symbol="MSFT", quantity=5.0,
                    unit_price=300.0, currency="USD")
        ]
        
        merged = merge_transactions(existing, new, "purchases")
        
        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0].date, "2023-01-15")
        self.assertEqual(merged[1].date, "2023-02-01")
    
    def test_merge_overlapping(self):
        """Test merging when dates overlap."""
        existing = [
            Purchase(date="2023-01-15", company_symbol="AAPL", quantity=10.0,
                    unit_price=150.0, currency="USD"),
            Purchase(date="2023-03-01", company_symbol="GOOGL", quantity=2.0,
                    unit_price=2500.0, currency="USD")
        ]
        
        new = [
            Purchase(date="2023-02-01", company_symbol="MSFT", quantity=5.0,
                    unit_price=300.0, currency="USD")
        ]
        
        merged = merge_transactions(existing, new, "purchases")
        
        self.assertEqual(len(merged), 3)
        # Should be sorted: 2023-01-15, 2023-02-01, 2023-03-01
        self.assertEqual(merged[0].date, "2023-01-15")
        self.assertEqual(merged[1].date, "2023-02-01")
        self.assertEqual(merged[2].date, "2023-03-01")
    
    def test_merge_empty_existing(self):
        """Test merging when existing list is empty."""
        existing = []
        new = [
            Purchase(date="2023-01-15", company_symbol="AAPL", quantity=10.0,
                    unit_price=150.0, currency="USD")
        ]
        
        merged = merge_transactions(existing, new, "purchases")
        
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0].date, "2023-01-15")
    
    def test_merge_empty_new(self):
        """Test merging when new list is empty."""
        existing = [
            Purchase(date="2023-01-15", company_symbol="AAPL", quantity=10.0,
                    unit_price=150.0, currency="USD")
        ]
        new = []
        
        merged = merge_transactions(existing, new, "purchases")
        
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0].date, "2023-01-15")


if __name__ == '__main__':
    unittest.main()

