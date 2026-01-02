#!/bin/bash
# Run tests with coverage

echo "🧪 Running Tests..."
echo "===================="

# Run pytest with coverage
pytest tests/ -v --cov --cov-report=term-missing --cov-report=html

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo ""
    echo "📊 Coverage report generated: htmlcov/index.html"
else
    echo ""
    echo "❌ Some tests failed!"
    exit 1
fi