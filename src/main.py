import numpy as np
import pandas as pd

def load_data(file_path: str) -> pd.DataFrame:
    """Load data from a CSV file."""
    return pd.read_csv(file_path)

def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process the input DataFrame."""
    df['processed'] = df['value'] * 2
    return df

def analyze_data(df: pd.DataFrame) -> dict:
    """Analyze the processed data."""
    return {
        'mean': df['processed'].mean(),
        'std': df['processed'].std(),
        'min': df['processed'].min(),
        'max': df['processed'].max()
    }

def main():
    print("Hello, QueryQuest!")
    # Example usage
    data = {'value': [1, 2, 3, 4, 5]}
    df = pd.DataFrame(data)
    processed_df = process_data(df)
    analysis = analyze_data(processed_df)
    print(f"Analysis results: {analysis}")

if __name__ == "__main__":
    main()