"""
JSON to CSV converter
"""
from typing import List, Dict, Any
from io import StringIO
import pandas as pd
from utils.exceptions import ProcessingError, ValidationError


def convert_json_to_csv(json_content: str) -> str:
    """
    Convert JSON string to CSV string
    
    Args:
        json_content: JSON content as string
        
    Returns:
        CSV string
        
    Raises:
        ValidationError: If JSON format is invalid
        ProcessingError: If conversion fails
    """
    import json
    
    try:
        # Parse JSON
        data = json.loads(json_content)
        
        # Create DataFrame from JSON
        # If it's a list of dictionaries (array of objects)
        if isinstance(data, list):
            if not data:
                raise ValidationError("JSON array is empty")
            df = pd.DataFrame(data)
        # If it's a single object
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            raise ValidationError("Invalid JSON format. Expected object or array of objects.")
        
        # Convert to CSV
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_result = csv_buffer.getvalue()
        
        return csv_result
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON format: {str(e)}") from e
    except Exception as e:
        raise ProcessingError(f"Failed to convert JSON to CSV: {str(e)}") from e

