"""
CSV to JSON converter
"""
from io import StringIO
import pandas as pd
from utils.exceptions import ProcessingError


def convert_csv_to_json(csv_content: str) -> str:
    """
    Convert CSV string to JSON string
    
    Args:
        csv_content: CSV content as string
        
    Returns:
        JSON string (records-oriented format)
        
    Raises:
        ProcessingError: If conversion fails
    """
    try:
        # Use StringIO to read CSV from string
        csv_buffer = StringIO(csv_content)
        
        # Read CSV into DataFrame
        df = pd.read_csv(csv_buffer)
        
        # Convert to JSON (records-oriented)
        json_result = df.to_json(orient='records', force_ascii=False, indent=2)
        
        return json_result
    except Exception as e:
        raise ProcessingError(f"Failed to convert CSV to JSON: {str(e)}") from e

