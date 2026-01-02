"""
Data Cleaning Service
Handles automated data cleaning for business datasets
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import chardet
from pathlib import Path
import logging

from app.utils.logging import logger

class DataCleaner:
    """
    Automated data cleaning pipeline for business data
    """
    
    def __init__(self):
        self.cleaning_log: List[str] = []
        self.df_original: Optional[pd.DataFrame] = None
        self.df_cleaned: Optional[pd.DataFrame] = None
        self.schema: Optional[Dict] = None
        self.quality_score: float = 0.0
        
    def clean(self, filepath: str) -> Dict:
        """
        Main cleaning pipeline
        
        Args:
            filepath: Path to CSV/Excel file
            
        Returns:
            Dictionary containing:
                - cleaned_df: Cleaned DataFrame
                - cleaning_log: List of operations performed
                - quality_score: Overall data quality (0-100)
                - schema: Inferred schema information
                - stats: Dataset statistics
        """
        logger.info("cleaning_started", filepath=filepath)
        
        try:
            # Stage 1: Load and parse
            self.df_original = self._load_file(filepath)
            self._log("File loaded successfully", f"{len(self.df_original)} rows, {len(self.df_original.columns)} columns")
            
            # Stage 2: Infer schema
            self.schema = self._infer_schema(self.df_original)
            self._log("Schema inferred", f"{len(self.schema['columns'])} columns analyzed")
            
            # Stage 3: Profile data
            stats = self._profile_data(self.df_original)
            self._log("Data profiled", f"Quality score: {stats['quality_score']:.1f}/100")
            
            # Initialize cleaned dataframe
            self.df_cleaned = self.df_original.copy()
            
            # Calculate quality score
            self.quality_score = stats['quality_score']
            
            logger.info("cleaning_complete", 
                       rows=len(self.df_cleaned),
                       quality_score=self.quality_score)
            
            return {
                'cleaned_df': self.df_cleaned,
                'cleaning_log': self.cleaning_log,
                'quality_score': self.quality_score,
                'schema': self.schema,
                'stats': stats
            }
            
        except Exception as e:
            logger.error("cleaning_failed", error=str(e))
            raise
    
    def _load_file(self, filepath: str) -> pd.DataFrame:
        """
        Load CSV or Excel file with automatic encoding detection
        
        Args:
            filepath: Path to file
            
        Returns:
            pandas DataFrame
        """
        file_path = Path(filepath)
        file_ext = file_path.suffix.lower()
        
        try:
            if file_ext == '.csv':
                # Detect encoding
                with open(filepath, 'rb') as f:
                    result = chardet.detect(f.read(10000))
                    encoding = result['encoding'] or 'utf-8'
                
                # Try to read CSV
                df = pd.read_csv(filepath, encoding=encoding)
                
            elif file_ext in ['.xlsx', '.xls']:
                # Read Excel
                df = pd.read_excel(filepath)
                
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # Basic validation
            if df.empty:
                raise ValueError("File is empty")
            
            if len(df.columns) == 0:
                raise ValueError("No columns found")
            
            return df
            
        except Exception as e:
            logger.error("file_load_failed", filepath=filepath, error=str(e))
            raise
    
    def _infer_schema(self, df: pd.DataFrame) -> Dict:
        """
        Infer schema and data types for each column
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with schema information
        """
        schema = {
            'columns': {},
            'row_count': len(df),
            'column_count': len(df.columns)
        }
        
        for col in df.columns:
            col_info = self._analyze_column(df[col], col)
            schema['columns'][col] = col_info
        
        return schema
    
    def _analyze_column(self, series: pd.Series, col_name: str) -> Dict:
        """
        Analyze a single column to determine its characteristics
        
        Args:
            series: pandas Series
            col_name: Column name
            
        Returns:
            Dictionary with column information
        """
        info = {
            'name': col_name,
            'dtype': str(series.dtype),
            'null_count': int(series.isnull().sum()),
            'null_percentage': float(series.isnull().sum() / len(series) * 100),
            'unique_count': int(series.nunique()),
            'inferred_type': None,
            'sample_values': []
        }
        
        # Get sample non-null values
        non_null = series.dropna()
        if len(non_null) > 0:
            info['sample_values'] = non_null.head(3).tolist()
        
        # Infer semantic type
        info['inferred_type'] = self._infer_column_type(series)
        
        # Add type-specific statistics
        if info['inferred_type'] == 'numeric':
            info['min'] = float(series.min()) if not series.empty else None
            info['max'] = float(series.max()) if not series.empty else None
            info['mean'] = float(series.mean()) if not series.empty else None
            info['std'] = float(series.std()) if not series.empty else None
            
        elif info['inferred_type'] == 'categorical':
            info['categories'] = series.value_counts().head(10).to_dict()
            info['cardinality'] = 'high' if info['unique_count'] > 50 else 'low'
        
        return info
    
    def _infer_column_type(self, series: pd.Series) -> str:
        """
        Infer semantic type of a column
        
        Returns: 'numeric', 'categorical', 'datetime', 'text', 'boolean', 'id'
        """
        # Remove nulls for analysis
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return 'unknown'
        
        # Check for datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return 'datetime'
        
        # Try parsing as datetime
        if series.dtype == 'object':
            try:
                pd.to_datetime(non_null.head(100))
                return 'datetime'
            except:
                pass
        
        # Check for numeric
        if pd.api.types.is_numeric_dtype(series):
            return 'numeric'
        
        # Try converting to numeric
        if series.dtype == 'object':
            try:
                pd.to_numeric(non_null.head(100))
                return 'numeric'
            except:
                pass
        
        # Check for boolean
        unique_vals = set(str(v).lower() for v in non_null.unique())
        bool_vals = {'true', 'false', 'yes', 'no', 'y', 'n', '1', '0', 't', 'f'}
        if unique_vals.issubset(bool_vals) and len(unique_vals) <= 2:
            return 'boolean'
        
        # Check for ID column (high uniqueness)
        uniqueness = series.nunique() / len(series)
        if uniqueness > 0.95:
            return 'id'
        
        # Check cardinality for categorical vs text
        cardinality = series.nunique()
        if cardinality < 50:  # Low cardinality = categorical
            return 'categorical'
        else:
            return 'text'
    
    def _profile_data(self, df: pd.DataFrame) -> Dict:
        """
        Profile dataset and calculate quality metrics
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with profiling statistics
        """
        stats = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'total_cells': len(df) * len(df.columns),
            'missing_cells': int(df.isnull().sum().sum()),
            'duplicate_rows': int(df.duplicated().sum()),
            'memory_usage': df.memory_usage(deep=True).sum(),
        }
        
        # Calculate missing percentage
        stats['missing_percentage'] = (stats['missing_cells'] / stats['total_cells'] * 100) if stats['total_cells'] > 0 else 0
        
        # Calculate duplicate percentage
        stats['duplicate_percentage'] = (stats['duplicate_rows'] / stats['row_count'] * 100) if stats['row_count'] > 0 else 0
        
        # Calculate completeness score (inverse of missing %)
        completeness = 100 - stats['missing_percentage']
        
        # Calculate uniqueness score (inverse of duplicate %)
        uniqueness = 100 - stats['duplicate_percentage']
        
        # Overall quality score (weighted average)
        stats['quality_score'] = (
            completeness * 0.6 +  # Completeness is most important
            uniqueness * 0.4      # Uniqueness matters too
        )
        
        return stats
    
    def _log(self, action: str, details: str = ""):
        """Add entry to cleaning log"""
        entry = f"{action}: {details}" if details else action
        self.cleaning_log.append(entry)
        logger.info("cleaning_step", action=action, details=details)