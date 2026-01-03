"""
Test data cleaning pipeline manually
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.cleaner import DataCleaner
import pandas as pd
import numpy as np

def test_clean_data():
    """Test with clean data"""
    print("\n" + "="*60)
    print("🧪 Testing Data Cleaner with CLEAN DATA")
    print("="*60)
    
    filepath = "tests/fixtures/sample_sales_data.csv"
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    cleaner = DataCleaner()
    result = cleaner.clean(filepath)
    
    print(f"\n✅ Cleaning Complete!")
    print(f"   Rows: {len(result['cleaned_df'])}")
    print(f"   Columns: {len(result['cleaned_df'].columns)}")
    print(f"   Quality Score: {result['quality_score']:.1f}/100")
    
    print(f"\n📋 Cleaning Log:")
    for entry in result['cleaning_log']:
        print(f"   • {entry}")
    
    print(f"\n📊 Schema Information:")
    for col_name, col_info in result['schema']['columns'].items():
        print(f"   • {col_name}:")
        print(f"     - Type: {col_info['inferred_type']}")
        print(f"     - Nulls: {col_info['null_percentage']:.1f}%")
        print(f"     - Unique: {col_info['unique_count']}")

def test_messy_data():
    """Test with messy data"""
    print("\n" + "="*60)
    print("🧪 Testing Data Cleaner with MESSY DATA + ML CLEANING")
    print("="*60)
    
    filepath = "tests/fixtures/messy_sales_data.csv"
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    # First, show original data issues
    print(f"\n📄 Original Data Issues:")
    df_original = pd.read_csv(filepath)
    print(f"   Total rows: {len(df_original)}")
    print(f"   Missing values: {df_original.isnull().sum().sum()}")
    print(f"   Duplicate rows: {df_original.duplicated().sum()}")
    
    print(f"\n   Columns with missing data:")
    for col in df_original.columns:
        null_count = df_original[col].isnull().sum()
        if null_count > 0:
            print(f"     • {col}: {null_count} missing ({null_count/len(df_original)*100:.1f}%)")
    
    # Check for outliers
    print(f"\n   Potential outliers:")
    for col in df_original.select_dtypes(include=[np.number]).columns:
        Q1 = df_original[col].quantile(0.25)
        Q3 = df_original[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((df_original[col] < (Q1 - 1.5 * IQR)) | (df_original[col] > (Q3 + 1.5 * IQR))).sum()
        if outliers > 0:
            print(f"     • {col}: {outliers} outliers detected")
    
    # Now clean it
    print(f"\n🔧 Running ML-Powered Data Cleaner...")
    cleaner = DataCleaner()
    result = cleaner.clean(filepath)
    
    print(f"\n✅ Cleaning Complete!")
    print(f"   Rows: {len(result['cleaned_df'])}")
    print(f"   Quality Before: {result['quality_score_before']:.1f}/100")
    print(f"   Quality After: {result['quality_score_after']:.1f}/100")
    improvement = result['quality_score_after'] - result['quality_score_before']
    print(f"   Improvement: +{improvement:.1f} points! 🎯")
    
    print(f"\n📋 Cleaning Operations Performed:")
    for entry in result['cleaning_log']:
        print(f"   • {entry}")
    
    # Show data quality comparison
    print(f"\n📊 Data Quality Comparison:")
    print(f"   {'Metric':<25} {'Before':<15} {'After':<15} {'Change':<15}")
    print(f"   {'-'*70}")
    
    df_cleaned = result['cleaned_df']
    
    # Missing values
    missing_before = df_original.isnull().sum().sum()
    missing_after = df_cleaned.isnull().sum().sum()
    print(f"   {'Missing Values':<25} {missing_before:<15} {missing_after:<15} {missing_before-missing_after:<15}")
    
    # Duplicates
    dup_before = df_original.duplicated().sum()
    dup_after = df_cleaned.duplicated().sum()
    print(f"   {'Duplicate Rows':<25} {dup_before:<15} {dup_after:<15} {dup_before-dup_after:<15}")
    
    # Completeness
    completeness_before = (1 - missing_before / (len(df_original) * len(df_original.columns))) * 100
    completeness_after = (1 - missing_after / (len(df_cleaned) * len(df_cleaned.columns))) * 100
    print(f"   {'Completeness':<25} {completeness_before:<15.1f} {completeness_after:<15.1f} {completeness_after-completeness_before:<15.1f}")
    
    print(f"\n🎉 Success! Data quality improved by {improvement:.1f} points!")

def main():
    print("="*60)
    print("🚀 AI Data Insight Engine - Data Cleaner Tests")
    print("="*60)
    
    # Test with clean data
    test_clean_data()
    
    # Test with messy data
    test_messy_data()
    
    print("\n" + "="*60)
    print("✨ All Tests Complete!")
    print("="*60)
    print("\n💡 Next: Start backend and upload a file to test full pipeline")
    print("   uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()