import unittest
import pandas as pd
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import process_data, analyze_data

class TestProcessData(unittest.TestCase):
    def test_process_data(self):
        data = {'value': [1, 2, 3, 4, 5]}
        df = pd.DataFrame(data)
        processed_df = process_data(df)
        self.assertIn('processed', processed_df.columns)
        self.assertTrue((processed_df['processed'] == df['value'] * 2).all())

class TestAnalyzeData(unittest.TestCase):
    def test_analyze_data(self):
        data = {'value': [1, 2, 3, 4, 5]}
        df = pd.DataFrame(data)
        processed_df = process_data(df)
        analysis = analyze_data(processed_df)
        self.assertIn('mean', analysis)
        self.assertIn('std', analysis)
        self.assertIn('min', analysis)
        self.assertIn('max', analysis)
        self.assertEqual(analysis['mean'], 6.0)
        self.assertEqual(analysis['min'], 2.0)
        self.assertEqual(analysis['max'], 10.0)

if __name__ == '__main__':
    unittest.main()