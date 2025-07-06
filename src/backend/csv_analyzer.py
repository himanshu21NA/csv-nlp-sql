import pandas as pd
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class CSVAnalyzer:
    """Analyzes CSV files and generates schema information"""
    
    def __init__(self, max_rows: int = 10000):
        self.max_rows = max_rows
        self.schema = {}
    
    def analyze_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a CSV file and generate comprehensive schema information
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dictionary containing schema information
        """
        try:
            # Read CSV with row limit
            df = pd.read_csv(file_path, nrows=self.max_rows)
            
            file_name = Path(file_path).name
            table_name = file_name.replace('.csv', '').replace(' ', '_').lower()
            
            schema = {
                "file_name": file_name,
                "table_name": table_name,
                "columns": {},
                "row_count": len(df),
                "sample_data": df.head(3).to_dict('records')
            }
            
            # Analyze each column
            for column in df.columns:
                schema["columns"][column] = self._analyze_column(df[column])
            
            logger.info(f"Successfully analyzed CSV: {file_name}")
            return schema
            
        except Exception as e:
            logger.error(f"Error analyzing CSV {file_path}: {str(e)}")
            raise
    
    def _analyze_column(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze a single column and return metadata"""
        return {
            "data_type": str(series.dtype),
            "unique_values": series.nunique(),
            "sample_values": series.dropna().unique()[:10].tolist(),
            "null_count": series.isnull().sum(),
            "is_numeric": pd.api.types.is_numeric_dtype(series),
            "is_categorical": series.nunique() < len(series) * 0.5 and series.nunique() < 20,
            "min_value": series.min() if pd.api.types.is_numeric_dtype(series) else None,
            "max_value": series.max() if pd.api.types.is_numeric_dtype(series) else None,
            "mean_value": series.mean() if pd.api.types.is_numeric_dtype(series) else None
        }
    
    def save_schema(self, schema: Dict[str, Any], output_path: str) -> None:
        """Save schema to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(schema, f, indent=2, default=str)
        
        logger.info(f"Schema saved to {output_path}")