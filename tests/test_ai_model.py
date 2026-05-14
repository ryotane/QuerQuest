import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ai.model import AIModel, TextAnalyzer, DataProcessor

class TestAIModel(unittest.TestCase):
    def test_load_and_unload(self):
        model = AIModel("test_model")
        self.assertFalse(model.is_loaded)
        model.load()
        self.assertTrue(model.is_loaded)
        model.unload()
        self.assertFalse(model.is_loaded)
    
    def test_predict_without_load(self):
        model = AIModel("test_model")
        with self.assertRaises(RuntimeError):
            model.predict([1, 2, 3])
    
    def test_predict_after_load(self):
        model = AIModel("test_model")
        model.load()
        result = model.predict([1, 2, 3])
        self.assertEqual(result, [1, 2, 3])
        model.unload()

class TestTextAnalyzer(unittest.TestCase):
    def test_load_and_unload(self):
        analyzer = TextAnalyzer()
        self.assertFalse(analyzer.is_loaded)
        analyzer.load()
        self.assertTrue(analyzer.is_loaded)
        analyzer.unload()
        self.assertFalse(analyzer.is_loaded)
    
    def test_analyze_text(self):
        analyzer = TextAnalyzer()
        analyzer.load()
        result = analyzer.analyze("hello world hello")
        self.assertEqual(result['word_count'], 3)
        self.assertEqual(result['unique_words'], 2)
        self.assertEqual(result['word_frequencies']['hello'], 2)
        self.assertEqual(result['word_frequencies']['world'], 1)
        analyzer.unload()

class TestDataProcessor(unittest.TestCase):
    def test_add_step(self):
        processor = DataProcessor()
        processor.add_step("step1", lambda x: x * 2)
        self.assertEqual(len(processor.steps), 1)
    
    def test_process(self):
        processor = DataProcessor()
        processor.add_step("step1", lambda x: x * 2)
        processor.add_step("step2", lambda x: x + 1)
        result = processor.process(5)
        self.assertEqual(result, 11)  # 5 * 2 + 1 = 11
    
    def test_add_normalization(self):
        processor = DataProcessor()
        processor.add_normalization()
        result = processor.process([0, 10, 20])
        self.assertAlmostEqual(result[0], 0.0)
        self.assertAlmostEqual(result[1], 0.5)
        self.assertAlmostEqual(result[2], 1.0)
    
    def test_add_filtering(self):
        processor = DataProcessor()
        processor.add_filtering(5)
        result = processor.process([1, 3, 5, 7, 9])
        self.assertEqual(result, [5, 7, 9])

if __name__ == '__main__':
    unittest.main()