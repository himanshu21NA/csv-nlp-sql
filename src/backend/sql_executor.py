import sqlite3
import pandas as pd
import logging
from typing import Any, Dict, List
from io import StringIO
import tempfile
import os

logger = logging.getLogger(__name__)

class SQLExecutor:
    """Executes SQL queries against CSV data"""
    
    def __init__(self):
        self.temp_db_path = None
        self.connection = None
    
    def execute_query(self, df: pd.DataFrame, sql_query: str, table_name: str) -> pd.DataFrame:
        """
        Execute SQL query against DataFrame
        
        Args:
            df: DataFrame containing the data
            sql_query: SQL query to execute
            table_name: Name of the table
            
        Returns:
            DataFrame with query results
        """
        try:
            # Create temporary SQLite database
            self._create_temp_db(df, table_name)
            
            # Execute query
            result_df = pd.read_sql_query(sql_query, self.connection)
            
            logger.info(f"Successfully executed query, returned {len(result_df)} rows")
            return result_df
            
        except Exception as e:
            logger.error(f"Error executing SQL query: {str(e)}")
            raise
        finally:
            self._cleanup()
    
    def _create_temp_db(self, df: pd.DataFrame, table_name: str) -> None:
        """Create temporary SQLite database from DataFrame"""
        # Create temporary database file
        temp_fd, self.temp_db_path = tempfile.mkstemp(suffix='.db')
        os.close(temp_fd)
        
        # Connect to database
        self.connection = sqlite3.connect(self.temp_db_path)
        
        # Load DataFrame into SQLite
        df.to_sql(table_name, self.connection, index=False, if_exists='replace')
        
        logger.info(f"Created temporary database with table: {table_name}")
    
    def _cleanup(self) -> None:
        """Clean up temporary resources"""
        if self.connection:
            self.connection.close()
        
        if self.temp_db_path and os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)
            
        logger.info("Cleaned up temporary resources")
    
    def validate_sql(self, sql_query: str) -> bool:
        """
        Validate SQL query syntax
        
        Args:
            sql_query: SQL query to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Try to parse the query
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute(f"EXPLAIN QUERY PLAN {sql_query}")
                return True
        except Exception as e:
            logger.warning(f"SQL validation failed: {str(e)}")
            return False
        
        return False