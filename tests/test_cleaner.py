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
        
        # Messy data should have lower quality score before cleaning
        # But pipeline should still complete
        assert result['quality_score'] >= 0
    
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