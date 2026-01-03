"""
Data Cleaning Service
Handles automated data cleaning for business datasets with ML-based techniques
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import chardet
from pathlib import Path
import logging
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder

from app.utils.logging import logger

class DataCleaner:
    """
    Automated data cleaning pipeline for business data with ML techniques
    """
    
    def __init__(self):
        self.cleaning_log: List[str] = []
        self.df_original: Optional[pd.DataFrame] = None
        self.df_cleaned: Optional[pd.DataFrame] = None
        self.schema: Optional[Dict] = None
        self.quality_score: float = 0.0
        self.quality_score_before: float = 0.0
        self.quality_score_after: float = 0.0
        
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
            
            # Stage 3: Profile data (before cleaning)
            stats_before = self._profile_data(self.df_original)
            self.quality_score_before = stats_before['quality_score']
            self._log("Initial data quality", f"{self.quality_score_before:.1f}/100")
            
            # Initialize cleaned dataframe
            self.df_cleaned = self.df_original.copy()
            
            # Stage 4: Handle missing values (ML-based imputation)
            if stats_before['missing_cells'] > 0:
                self.df_cleaned = self._handle_missing_values(self.df_cleaned)
            
            # Stage 5: Detect and handle outliers
            self.df_cleaned = self._handle_outliers(self.df_cleaned)
            
            # Stage 6: Remove duplicates
            duplicates_before = self.df_cleaned.duplicated().sum()
            if duplicates_before > 0:
                self.df_cleaned = self._remove_duplicates(self.df_cleaned)
            
            # Stage 7: Profile data (after cleaning)
            stats_after = self._profile_data(self.df_cleaned)
            self.quality_score_after = stats_after['quality_score']
            self._log("Final data quality", f"{self.quality_score_after:.1f}/100")
            
            # Calculate improvement
            improvement = self.quality_score_after - self.quality_score_before
            if improvement > 0:
                self._log("Quality improvement", f"+{improvement:.1f} points")
            
            # Use final quality score
            self.quality_score = self.quality_score_after
            
            logger.info("cleaning_complete", 
                       rows=len(self.df_cleaned),
                       quality_before=self.quality_score_before,
                       quality_after=self.quality_score_after)
            
            return {
                'cleaned_df': self.df_cleaned,
                'cleaning_log': self.cleaning_log,
                'quality_score': self.quality_score,
                'quality_score_before': self.quality_score_before,
                'quality_score_after': self.quality_score_after,
                'schema': self.schema,
                'stats': stats_after
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
    
    def _log(self, action: str, details: str = "", confidence: str = ""):
        """Add entry to cleaning log with optional confidence level"""
        if confidence:
            entry = f"{action}: {details} [Confidence: {confidence}]" if details else f"{action} [Confidence: {confidence}]"
        else:
            entry = f"{action}: {details}" if details else action
        
        self.cleaning_log.append(entry)
        logger.info("cleaning_step", action=action, details=details, confidence=confidence)
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values using ML-based imputation
        
        Strategy:
        - Numeric columns: KNN imputation (considers similar rows)
        - Categorical columns: Most frequent value
        - Business rules: Special handling for revenue, dates, etc.
        """
        df_imputed = df.copy()
        missing_before = df.isnull().sum().sum()
        
        if missing_before == 0:
            return df_imputed
        
        imputed_columns = []
        
        # Separate numeric and categorical columns
        numeric_cols = []
        categorical_cols = []
        
        for col in df.columns:
            if df[col].isnull().sum() == 0:
                continue  # Skip columns with no missing values
            
            col_type = self.schema['columns'][col]['inferred_type']
            
            if col_type == 'numeric':
                numeric_cols.append(col)
            elif col_type in ['categorical', 'text', 'boolean']:
                categorical_cols.append(col)
        
        # Impute numeric columns with KNN
        if numeric_cols:
            try:
                imputer = KNNImputer(n_neighbors=min(5, len(df)-1))
                df_imputed[numeric_cols] = imputer.fit_transform(df[numeric_cols])
                imputed_columns.extend(numeric_cols)
                self._log("KNN imputation applied", 
                         f"{len(numeric_cols)} numeric columns, {sum(df[numeric_cols].isnull().sum())} values filled",
                         confidence="medium")
            except Exception as e:
                logger.warning("knn_imputation_failed", error=str(e))
                # Fallback to mean imputation
                for col in numeric_cols:
                    df_imputed[col].fillna(df[col].mean(), inplace=True)
                    imputed_columns.append(col)
                self._log("Mean imputation applied", 
                         f"{len(numeric_cols)} numeric columns (KNN failed)",
                         confidence="low")
        
        # Impute categorical columns with mode (most frequent)
        if categorical_cols:
            for col in categorical_cols:
                mode_value = df[col].mode()
                if len(mode_value) > 0:
                    df_imputed[col].fillna(mode_value[0], inplace=True)
                    imputed_columns.append(col)
            
            self._log("Mode imputation applied", 
                     f"{len(categorical_cols)} categorical columns",
                     confidence="high")
        
        missing_after = df_imputed.isnull().sum().sum()
        filled_count = missing_before - missing_after
        
        if filled_count > 0:
            self._log("Missing values handled", 
                     f"{filled_count} values imputed across {len(imputed_columns)} columns")
        
        return df_imputed
    
    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect and handle outliers using multiple methods
        
        Methods:
        1. IsolationForest (ML-based anomaly detection)
        2. IQR (Interquartile Range for statistical outliers)
        3. Business rules (domain-specific constraints)
        """
        df_cleaned = df.copy()
        outliers_detected = 0
        outliers_handled = 0
        
        # Get numeric columns only
        numeric_cols = [col for col, info in self.schema['columns'].items() 
                       if info['inferred_type'] == 'numeric']
        
        if len(numeric_cols) == 0:
            return df_cleaned
        
        # Method 1: IsolationForest for multivariate outliers
        try:
            # Prepare data (only numeric columns without nulls)
            numeric_data = df_cleaned[numeric_cols].dropna()
            
            if len(numeric_data) > 10:  # Need enough data for IsolationForest
                iso_forest = IsolationForest(
                    contamination=0.1,  # Expect 10% outliers
                    random_state=42
                )
                
                outlier_labels = iso_forest.fit_predict(numeric_data)
                outlier_count = (outlier_labels == -1).sum()
                
                if outlier_count > 0:
                    outliers_detected += outlier_count
                    self._log("IsolationForest outliers detected", 
                             f"{outlier_count} anomalous rows identified",
                             confidence="medium")
        
        except Exception as e:
            logger.warning("isolation_forest_failed", error=str(e))
        
        # Method 2: IQR method for each numeric column
        for col in numeric_cols:
            try:
                Q1 = df_cleaned[col].quantile(0.25)
                Q3 = df_cleaned[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Count outliers
                outlier_mask = (df_cleaned[col] < lower_bound) | (df_cleaned[col] > upper_bound)
                col_outliers = outlier_mask.sum()
                
                if col_outliers > 0:
                    outliers_detected += col_outliers
                    
                    # Cap outliers (Winsorization)
                    df_cleaned.loc[df_cleaned[col] < lower_bound, col] = lower_bound
                    df_cleaned.loc[df_cleaned[col] > upper_bound, col] = upper_bound
                    
                    outliers_handled += col_outliers
                    
                    self._log(f"IQR outliers capped in {col}", 
                             f"{col_outliers} values capped to [{lower_bound:.2f}, {upper_bound:.2f}]",
                             confidence="high")
            
            except Exception as e:
                logger.warning("iqr_outlier_detection_failed", column=col, error=str(e))
        
        # Method 3: Business rules
        business_rules_applied = self._apply_business_rules(df_cleaned)
        outliers_handled += business_rules_applied
        
        if outliers_handled > 0:
            self._log("Outliers handled", 
                     f"{outliers_handled} outliers detected and capped/corrected")
        
        return df_cleaned
    
    def _apply_business_rules(self, df: pd.DataFrame) -> int:
        """
        Apply business-specific rules to detect and fix data issues
        
        Returns: Number of values corrected
        """
        corrections = 0
        
        # Rule 1: Negative values in revenue/sales/price columns
        revenue_like_cols = [col for col in df.columns 
                           if any(term in col.lower() for term in ['revenue', 'sales', 'price', 'cost', 'amount'])]
        
        for col in revenue_like_cols:
            if df[col].dtype in [np.float64, np.int64]:
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    df.loc[df[col] < 0, col] = 0
                    corrections += negative_count
                    self._log(f"Business rule applied to {col}", 
                             f"{negative_count} negative values set to 0",
                             confidence="high")
        
        # Rule 2: Suspicious quantity values (999, 9999 often error codes)
        quantity_like_cols = [col for col in df.columns 
                            if any(term in col.lower() for term in ['quantity', 'qty', 'count'])]
        
        for col in quantity_like_cols:
            if df[col].dtype in [np.float64, np.int64]:
                suspicious = df[col].isin([999, 9999, 99999])
                suspicious_count = suspicious.sum()
                if suspicious_count > 0:
                    # Replace with median
                    median_val = df.loc[~suspicious, col].median()
                    df.loc[suspicious, col] = median_val
                    corrections += suspicious_count
                    self._log(f"Suspicious values in {col}", 
                             f"{suspicious_count} values (999/9999) replaced with median",
                             confidence="medium")
        
        return corrections
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate rows
        
        Strategy:
        1. Exact duplicates: Remove all but first occurrence
        2. Keep first occurrence (usually the original entry)
        """
        duplicates_before = df.duplicated().sum()
        
        if duplicates_before == 0:
            return df
        
        df_dedup = df.drop_duplicates(keep='first')
        
        duplicates_removed = duplicates_before
        
        self._log("Duplicates removed", 
                 f"{duplicates_removed} duplicate rows removed, {len(df_dedup)} rows remaining",
                 confidence="high")
        
        return df_dedup