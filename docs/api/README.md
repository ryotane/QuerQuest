# API Documentation

## Overview

This document describes the API endpoints and functions available in QueryQuest Project 046.

## Modules

### `src.ai.model`

AI model integration and data processing pipeline.

#### Classes

##### `AIModel`

Base class for AI models.

**Methods:**
- `load(params: Optional[Dict[str, Any]] = None)`: Load the AI model with optional parameters.
- `predict(input_data: Any) -> Any`: Make a prediction with the loaded model.
- `unload()`: Unload the AI model.

**Example:**
```python
from src.ai.model import AIModel

model = AIModel("my_model")
model.load({"param1": "value1"})
result = model.predict([1, 2, 3])
model.unload()
```

##### `TextAnalyzer`

Text analysis model for NLP tasks.

**Methods:**
- `load()`: Load the text analyzer.
- `analyze(text: str) -> Dict[str, Any]`: Analyze text and return statistics.
- `unload()`: Unload the text analyzer.

**Example:**
```python
from src.ai.model import TextAnalyzer

analyzer = TextAnalyzer()
analyzer.load()
result = analyzer.analyze("hello world hello")
print(result)  # {'word_count': 3, 'unique_words': 2, 'word_frequencies': {'hello': 2, 'world': 1}}
analyzer.unload()
```

##### `DataProcessor`

Data processing pipeline for AI models.

**Methods:**
- `add_step(step_name: str, step_func)`: Add a processing step to the pipeline.
- `process(data: Any) -> Any`: Process data through all steps in the pipeline.
- `add_normalization()`: Add normalization step to the pipeline.
- `add_filtering(threshold: float = 0.5)`: Add filtering step to the pipeline.

**Example:**
```python
from src.ai.model import DataProcessor

processor = DataProcessor()
processor.add_step("step1", lambda x: x * 2)
processor.add_normalization()
processor.add_filtering(5)
result = processor.process([1, 3, 5, 7, 9])
print(result)  # [5.0, 7.0, 9.0]
```

### `src.ai.pipeline`

Advanced data processing pipeline with multiple steps.

#### Classes

##### `AdvancedDataProcessor`

Advanced data processing pipeline with multiple steps.

**Methods:**
- `add_step(step_name: str, step_func: Callable, config: Optional[Dict[str, Any]] = None)`: Add a processing step to the pipeline.
- `process(data: Any) -> Any`: Process data through all steps in the pipeline.
- `add_normalization(method: str = "minmax")`: Add normalization step to the pipeline.
- `add_filtering(threshold: float = 0.5, condition: str = "greater")`: Add filtering step to the pipeline.
- `add_transformation(transform_func: Callable)`: Add a custom transformation step.
- `get_results() -> Dict[str, Any]`: Get all processing results.
- `reset()`: Reset the pipeline.

**Example:**
```python
from src.ai.pipeline import AdvancedDataProcessor

processor = AdvancedDataProcessor("my_processor")
processor.add_normalization("minmax")
processor.add_filtering(5, "greater")
result = processor.process([0, 10, 20, 30])
print(result)  # [0.5, 1.0]
```

##### `DataPipeline`

High-level data pipeline for complex data processing.

**Methods:**
- `add_processor(name: str, processor: AdvancedDataProcessor)`: Add a processor to the pipeline.
- `process_all(data: Any) -> Dict[str, Any]`: Process data through all processors.
- `add_metadata(key: str, value: Any)`: Add metadata to the pipeline.
- `get_metadata() -> Dict[str, Any]`: Get all metadata.

**Example:**
```python
from src.ai.pipeline import DataPipeline, AdvancedDataProcessor

pipeline = DataPipeline()
processor1 = AdvancedDataProcessor("proc1")
processor1.add_step("step1", lambda x: [i * 2 for i in x])

pipeline.add_processor("proc1", processor1)
results = pipeline.process_all([1, 2, 3])
print(results)  # {'proc1': [2, 4, 6]}
```

### `src.main`

Main application module.

#### Functions

##### `load_data(file_path: str) -> pd.DataFrame`

Load data from a CSV file.

**Parameters:**
- `file_path` (str): Path to the CSV file

**Returns:**
- `pd.DataFrame`: Loaded DataFrame

**Example:**
```python
from src.main import load_data

df = load_data('data/raw/sample.csv')
```

##### `process_data(df: pd.DataFrame) -> pd.DataFrame`

Process the input DataFrame.

**Parameters:**
- `df` (pd.DataFrame): Input DataFrame with 'value' column

**Returns:**
- `pd.DataFrame`: Processed DataFrame with 'processed' column

**Example:**
```python
from src.main import process_data
import pandas as pd

data = {'value': [1, 2, 3, 4, 5]}
df = pd.DataFrame(data)
processed_df = process_data(df)
```

##### `analyze_data(df: pd.DataFrame) -> dict`

Analyze the processed data.

**Parameters:**
- `df` (pd.DataFrame): Processed DataFrame with 'processed' column

**Returns:**
- `dict`: Dictionary containing mean, std, min, max values

**Example:**
```python
from src.main import analyze_data

analysis = analyze_data(processed_df)
print(analysis)
```
