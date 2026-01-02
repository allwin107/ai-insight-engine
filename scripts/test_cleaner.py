"""
Test data cleaning pipeline manually
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.cleaner import DataCleaner
import pandas as pd

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
    print("🧪 Testing Data Cleaner with MESSY DATA")
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
    
    # Now clean it
    print(f"\n🔧 Running Data Cleaner...")
    cleaner = DataCleaner()
    result = cleaner.clean(filepath)
    
    print(f"\n✅ Cleaning Complete!")
    print(f"   Rows: {len(result['cleaned_df'])}")
    print(f"   Quality Score: {result['quality_score']:.1f}/100")
    
    print(f"\n📋 Cleaning Log:")
    for entry in result['cleaning_log']:
        print(f"   • {entry}")
    
    print(f"\n📊 Data Quality Stats:")
    stats = result['stats']
    print(f"   • Missing cells: {stats['missing_cells']} ({stats['missing_percentage']:.1f}%)")
    print(f"   • Duplicate rows: {stats['duplicate_rows']} ({stats['duplicate_percentage']:.1f}%)")
    print(f"   • Overall quality: {stats['quality_score']:.1f}/100")
    
    print(f"\n📈 Schema Summary:")
    for col_name, col_info in result['schema']['columns'].items():
        print(f"   • {col_name}: {col_info['inferred_type']} ({col_info['unique_count']} unique, {col_info['null_percentage']:.1f}% null)")

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