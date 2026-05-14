import unittest
import sys
import os
import numpy as np

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ai.pipeline import AdvancedDataProcessor, DataPipeline

class TestAdvancedDataProcessor(unittest.TestCase):
    def test_add_step(self):
        processor = AdvancedDataProcessor("test")
        processor.add_step("step1", lambda x: x * 2)
        self.assertEqual(len(processor.steps), 1)
    
    def test_process(self):
        processor = AdvancedDataProcessor("test")
        processor.add_step("step1", lambda x: x * 2)
        processor.add_step("step2", lambda x: x + 1)
        result = processor.process(5)
        self.assertEqual(result, 11)  # 5 * 2 + 1 = 11
    
    def test_add_normalization_minmax(self):
        processor = AdvancedDataProcessor("test")
        processor.add_normalization("minmax")
        result = processor.process([0, 10, 20])
        self.assertAlmostEqual(result[0], 0.0)
        self.assertAlmostEqual(result[1], 0.5)
        self.assertAlmostEqual(result[2], 1.0)
    
    def test_add_normalization_zscore(self):
        processor = AdvancedDataProcessor("test")
        processor.add_normalization("zscore")
        result = processor.process([10, 20, 30])
        mean = np.mean(result)
        std = np.std(result)
        self.assertAlmostEqual(mean, 0.0, places=5)
        self.assertAlmostEqual(std, 1.0, places=5)
    
    def test_add_filtering_greater(self):
        processor = AdvancedDataProcessor("test")
        processor.add_filtering(5, "greater")
        result = processor.process([1, 3, 5, 7, 9])
        self.assertEqual(result, [7, 9])
    
    def test_add_filtering_less(self):
        processor = AdvancedDataProcessor("test")
        processor.add_filtering(5, "less")
        result = processor.process([1, 3, 5, 7, 9])
        self.assertEqual(result, [1, 3])
    
    def test_add_transformation(self):
        processor = AdvancedDataProcessor("test")
        processor.add_transformation(lambda x: x ** 2)
        result = processor.process([1, 2, 3])
        self.assertEqual(result, [1, 4, 9])
    
    def test_get_results(self):
        processor = AdvancedDataProcessor("test")
        processor.add_step("step1", lambda x: x * 2)
        processor.process([1, 2, 3])
        results = processor.get_results()
        self.assertIn("test", results)
    
    def test_reset(self):
        processor = AdvancedDataProcessor("test")
        processor.add_step("step1", lambda x: x * 2)
        processor.reset()
        self.assertEqual(len(processor.steps), 0)
        self.assertEqual(len(processor.results), 0)

class TestDataPipeline(unittest.TestCase):
    def test_add_processor(self):
        pipeline = DataPipeline()
        processor = AdvancedDataProcessor("test")
        pipeline.add_processor("test", processor)
        self.assertIn("test", pipeline.processors)
    
    def test_process_all(self):
        pipeline = DataPipeline()
        processor1 = AdvancedDataProcessor("proc1")
        processor1.add_step("step1", lambda x: [i * 2 for i in x])
        
        processor2 = AdvancedDataProcessor("proc2")
        processor2.add_step("step1", lambda x: [i + 1 for i in x])
        
        pipeline.add_processor("proc1", processor1)
        pipeline.add_processor("proc2", processor2)
        
        results = pipeline.process_all([1, 2, 3])
        self.assertEqual(results["proc1"], [2, 4, 6])
        self.assertEqual(results["proc2"], [2, 3, 4])
    
    def test_add_metadata(self):
        pipeline = DataPipeline()
        pipeline.add_metadata("key1", "value1")
        metadata = pipeline.get_metadata()
        self.assertEqual(metadata["key1"], "value1")
    
    def test_get_metadata(self):
        pipeline = DataPipeline()
        pipeline.add_metadata("key1", "value1")
        pipeline.add_metadata("key2", "value2")
        metadata = pipeline.get_metadata()
        self.assertEqual(len(metadata), 2)
        self.assertEqual(metadata["key1"], "value1")
        self.assertEqual(metadata["key2"], "value2")

if __name__ == '__main__':
    unittest.main()