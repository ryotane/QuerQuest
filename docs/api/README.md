# API Documentation

## Overview

This document describes the API endpoints and functions available in QueryQuest Project 046.

## Functions

### `load_data(file_path: str) -> pd.DataFrame`

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

### `process_data(df: pd.DataFrame) -> pd.DataFrame`

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

### `analyze_data(df: pd.DataFrame) -> dict`

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
