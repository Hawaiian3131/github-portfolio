from ml_ai_module import MLFileCategorizer
from pathlib import Path

# Test ML module
ml = MLFileCategorizer()
print("✅ ML Module loaded successfully!")

# Test prediction (works without training)
test_file = Path("test.txt")
category, confidence = ml.predict(test_file)
print(f"Prediction: {category} ({confidence:.1%})")