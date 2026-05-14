"""
Data Processing Pipeline for QueryQuest Project 046

This module provides advanced data processing functionality.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class ProcessingStep:
    """Represents a single processing step."""
    name: str
    func: Callable
    config: Dict[str, Any] = field(default_factory=dict)


class AdvancedDataProcessor:
    """Advanced data processing pipeline with multiple steps."""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.steps: List[ProcessingStep] = []
        self.results: Dict[str, Any] = {}
    
    def add_step(self, step_name: str, step_func: Callable, config: Optional[Dict[str, Any]] = None):
        """Add a processing step to the pipeline."""
        self.steps.append(ProcessingStep(
            name=step_name,
            func=step_func,
            config=config or {}
        ))
    
    def process(self, data: Any) -> Any:
        """Process data through all steps in the pipeline."""
        result = data
        for step in self.steps:
            result = step.func(result, **step.config)
            if isinstance(result, np.ndarray):
                result = result.tolist()
        self.results[self.name] = result
        return result
    
    def add_normalization(self, method: str = "minmax"):
        """Add normalization step to the pipeline."""
        def normalize(data, method="minmax"):
            if isinstance(data, (list, np.ndarray)):
                data = np.array(data)
                if method == "minmax":
                    min_val = np.min(data)
                    max_val = np.max(data)
                    if max_val == min_val:
                        return np.zeros_like(data)
                    return (data - min_val) / (max_val - min_val)
                elif method == "zscore":
                    mean = np.mean(data)
                    std = np.std(data)
                    if std == 0:
                        return np.zeros_like(data)
                    return (data - mean) / std
            return data
        
        self.add_step(f"normalization_{method}", normalize, {"method": method})
    
    def add_filtering(self, threshold: float = 0.5, condition: str = "greater"):
        """Add filtering step to the pipeline."""
        def filter_data(data, threshold=0.5, condition="greater"):
            if isinstance(data, (list, np.ndarray)):
                data = np.array(data)
                if condition == "greater":
                    return data[data > threshold]
                elif condition == "less":
                    return data[data < threshold]
            return data
        
        self.add_step(f"filtering_{threshold}_{condition}", filter_data, {
            "threshold": threshold,
            "condition": condition
        })
    
    def add_transformation(self, transform_func: Callable):
        """Add a custom transformation step."""
        def wrapped_transform(data, **kwargs):
            if isinstance(data, list):
                data = np.array(data)
            result = transform_func(data, **kwargs)
            if isinstance(result, np.ndarray):
                return result.tolist()
            return result
        self.add_step("custom_transform", wrapped_transform)
    
    def get_results(self) -> Dict[str, Any]:
        """Get all processing results."""
        return self.results.copy()
    
    def reset(self):
        """Reset the pipeline."""
        self.steps.clear()
        self.results.clear()


class DataPipeline:
    """High-level data pipeline for complex data processing."""
    
    def __init__(self):
        self.processors: Dict[str, AdvancedDataProcessor] = {}
        self.metadata: Dict[str, Any] = {}
    
    def add_processor(self, name: str, processor: AdvancedDataProcessor):
        """Add a processor to the pipeline."""
        self.processors[name] = processor
    
    def process_all(self, data: Any) -> Dict[str, Any]:
        """Process data through all processors."""
        results = {}
        for name, processor in self.processors.items():
            results[name] = processor.process(data)
        return results
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to the pipeline."""
        self.metadata[key] = value
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get all metadata."""
        return self.metadata.copy()
