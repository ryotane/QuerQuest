import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ai.model import AIModel, DataProcessor

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

if __name__ == '__main__':
    unittest.main()