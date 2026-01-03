"""
Tests for data cleaning service
"""
import pytest
import pandas as pd
import os
from pathlib import Path

from app.services.cleaner import DataCleaner

@pytest.fixture
def sample_csv_path():
    """Path to sample CSV file"""
    return "tests/fixtures/sample_sales_data.csv"

@pytest.fixture
def messy_csv_path():
    """Path to messy CSV file"""
    return "tests/fixtures/messy_sales_data.csv"

@pytest.mark.unit
class TestDataCleaner:
    """Test data cleaning functionality"""
    
    def test_cleaner_initialization(self):
        """Test DataCleaner can be initialized"""
        cleaner = DataCleaner()
        assert cleaner.cleaning_log == []
        assert cleaner.df_original is None
        assert cleaner.df_cleaned is None
        assert cleaner.schema is None
        assert cleaner.quality_score == 0.0
    
    def test_load_csv_file(self, sample_csv_path):
        """Test loading a CSV file"""
        cleaner = DataCleaner()
        df = cleaner._load_file(sample_csv_path)
        
        assert df is not None
        assert len(df) > 0
        assert len(df.columns) > 0
    
    def test_infer_schema(self, sample_csv_path):
        """Test schema inference"""
        cleaner = DataCleaner()
        df = cleaner._load_file(sample_csv_path)
        schema = cleaner._infer_schema(df)
        
        assert 'columns' in schema
        assert 'row_count' in schema
        assert 'column_count' in schema
        assert len(schema['columns']) == len(df.columns)
    
    def test_column_type_inference_numeric(self):
        """Test numeric column type inference"""
        cleaner = DataCleaner()
        series = pd.Series([1, 2, 3, 4, 5])
        col_type = cleaner._infer_column_type(series)
        assert col_type == 'numeric'
    
    def test_column_type_inference_categorical(self):
        """Test categorical column type inference"""
        cleaner = DataCleaner()
        series = pd.Series(['A', 'B', 'A', 'C', 'B', 'A'])
        col_type = cleaner._infer_column_type(series)
        assert col_type == 'categorical'
    
    def test_column_type_inference_boolean(self):
        """Test boolean column type inference"""
        cleaner = DataCleaner()
        series = pd.Series(['Yes', 'No', 'Yes', 'No'])
        col_type = cleaner._infer_column_type(series)
        assert col_type == 'boolean'
    
    def test_profile_data(self, sample_csv_path):
        """Test data profiling"""
        cleaner = DataCleaner()
        df = cleaner._load_file(sample_csv_path)
        stats = cleaner._profile_data(df)
        
        assert 'row_count' in stats
        assert 'column_count' in stats
        assert 'quality_score' in stats
        assert 0 <= stats['quality_score'] <= 100
    
    def test_clean_pipeline_clean_data(self, sample_csv_path):
        """Test cleaning pipeline with clean data"""
        cleaner = DataCleaner()
        result = cleaner.clean(sample_csv_path)
        
        assert 'cleaned_df' in result
        assert 'cleaning_log' in result
        assert 'quality_score' in result
        assert 'schema' in result
        assert 'stats' in result
        
        # Clean data should have high quality score
        assert result['quality_score'] > 80
    
    def test_clean_pipeline_messy_data(self, messy_csv_path):
        """Test cleaning pipeline with messy data"""
        cleaner = DataCleaner()
        result = cleaner.clean(messy_csv_path)
        
        assert 'cleaned_df' in result
        assert 'cleaning_log' in result
        assert len(result['cleaning_log']) > 0
        
        # Should have quality scores before and after
        assert 'quality_score_before' in result
        assert 'quality_score_after' in result
        
        # Quality should improve or stay same
        assert result['quality_score_after'] >= result['quality_score_before']
        
        # Missing values should be reduced
        missing_after = result['cleaned_df'].isnull().sum().sum()
        assert missing_after == 0 or missing_after < result['stats']['missing_cells']
    
    def test_missing_value_imputation(self):
        """Test ML-based missing value imputation"""
        cleaner = DataCleaner()
        
        # Create DataFrame with missing values
        df = pd.DataFrame({
            'A': [1, 2, None, 4, 5, 6, 7, 8],
            'B': [10, 20, 30, None, 50, 60, 70, 80],
            'C': ['x', 'y', None, 'z', 'x', 'y', 'z', 'x']
        })
        
        # Infer schema first
        cleaner.schema = cleaner._infer_schema(df)
        
        # Apply imputation
        df_imputed = cleaner._handle_missing_values(df)
        
        # Check that missing values are filled
        assert df_imputed['A'].isnull().sum() == 0
        assert df_imputed['B'].isnull().sum() == 0
        assert df_imputed['C'].isnull().sum() == 0
    
    def test_outlier_detection(self):
        """Test outlier detection and handling"""
        cleaner = DataCleaner()
        
        # Create DataFrame with outliers
        df = pd.DataFrame({
            'Sales': [100, 105, 98, 102, 9999, 103, 101, 104],  # 9999 is outlier
            'Quantity': [10, 12, 11, 999, 13, 11, 12, 10]  # 999 is suspicious
        })
        
        # Infer schema
        cleaner.schema = cleaner._infer_schema(df)
        
        # Handle outliers
        df_cleaned = cleaner._handle_outliers(df)
        
        # Extreme values should be capped
        assert df_cleaned['Sales'].max() < 9999
        assert df_cleaned['Quantity'].max() < 999
    
    def test_business_rules(self):
        """Test business rule application"""
        cleaner = DataCleaner()
        
        # Create DataFrame with business rule violations
        df = pd.DataFrame({
            'Revenue': [1000, -500, 2000, 3000],  # Negative revenue
            'Quantity': [10, 999, 12, 15]  # 999 is error code
        })
        
        # Infer schema
        cleaner.schema = cleaner._infer_schema(df)
        
        # Apply business rules
        corrections = cleaner._apply_business_rules(df)
        
        # Negative revenue should be corrected
        assert (df['Revenue'] >= 0).all()
        
        # Suspicious quantity should be replaced
        assert 999 not in df['Quantity'].values
        
        # Should have made corrections
        assert corrections > 0
    
    def test_duplicate_removal(self):
        """Test duplicate row removal"""
        cleaner = DataCleaner()
        
        # Create DataFrame with duplicates
        df = pd.DataFrame({
            'A': [1, 2, 1, 4, 2],
            'B': ['x', 'y', 'x', 'z', 'y']
        })
        
        df_dedup = cleaner._remove_duplicates(df)
        
        # Duplicates should be removed
        assert len(df_dedup) == 3  # Only unique rows
        assert df_dedup.duplicated().sum() == 0
    
    def test_analyze_column(self, sample_csv_path):
        """Test column analysis"""
        cleaner = DataCleaner()
        df = cleaner._load_file(sample_csv_path)
        
        for col in df.columns:
            col_info = cleaner._analyze_column(df[col], col)
            
            assert 'name' in col_info
            assert 'dtype' in col_info
            assert 'null_count' in col_info
            assert 'null_percentage' in col_info
            assert 'unique_count' in col_info
            assert 'inferred_type' in col_info
    
    def test_missing_data_detection(self):
        """Test detection of missing data"""
        cleaner = DataCleaner()
        
        # Create DataFrame with missing values
        df = pd.DataFrame({
            'A': [1, 2, None, 4, 5],
            'B': ['x', 'y', 'z', None, 'w']
        })
        
        stats = cleaner._profile_data(df)
        
        assert stats['missing_cells'] == 2
        assert stats['missing_percentage'] > 0
    
    def test_duplicate_detection(self):
        """Test detection of duplicate rows"""
        cleaner = DataCleaner()
        
        # Create DataFrame with duplicates
        df = pd.DataFrame({
            'A': [1, 2, 1, 4],
            'B': ['x', 'y', 'x', 'z']
        })
        
        stats = cleaner._profile_data(df)
        
        assert stats['duplicate_rows'] == 1
        assert stats['duplicate_percentage'] > 0