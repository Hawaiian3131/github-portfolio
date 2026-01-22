"""
Quick ML Integration Script
Run this to add ML tab to your GUI
"""
import sys
from pathlib import Path

# Check if scikit-learn is installed
try:
    import sklearn
    print("✅ scikit-learn is installed")
except ImportError:
    print("❌ scikit-learn NOT installed")
    print("Run: pip install scikit-learn numpy pandas --break-system-packages")
    sys.exit(1)

# Check if ml_ai_module.py exists
ml_module = Path("ml_ai_module.py")
if not ml_module.exists():
    print("❌ ml_ai_module.py NOT found")
    print("Download ml_ai_module.py to this folder")
    sys.exit(1)
else:
    print("✅ ml_ai_module.py found")

# Check if GUI file exists
gui_file = Path("organizer_gui_advanced.py")
if not gui_file.exists():
    print("❌ organizer_gui_advanced.py NOT found")
    sys.exit(1)
else:
    print("✅ organizer_gui_advanced.py found")

# Check if ML already integrated
with open(gui_file, 'r', encoding='utf-8') as f:
    content = f.read()

if 'from ml_ai_module import' in content:
    print("✅ ML import already in GUI")
else:
    print("⚠ ML import missing - needs manual integration")

if 'def create_ml_tab' in content:
    print("✅ ML tab already in GUI")
else:
    print("⚠ ML tab missing - needs manual integration")

print("\n" + "="*50)
print("INTEGRATION STATUS:")
print("="*50)

if 'def create_ml_tab' in content and 'from ml_ai_module import' in content:
    print("✅ ML FULLY INTEGRATED!")
    print("\nRun: python organizer_gui_advanced.py")
else:
    print("⚠ ML NEEDS MANUAL INTEGRATION")
    print("\nFollow the manual steps in the guide")

print("="*50)