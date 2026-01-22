# Smart File Renaming Guide

## 📝 What It Does

The Smart Renamer cleans up messy filenames and standardizes naming across all your files.

---

## 🎯 Features

### 1. **Sanitize Filenames**
Remove special characters and clean up names
- Before: `My Photo!@#$%^&*.jpg`
- After: `My Photo.jpg`

### 2. **Add Date Prefixes**
Add dates from file creation/modification
- Before: `vacation.jpg`
- After: `2026-01-21_vacation.jpg`

### 3. **Standardize Case**
- **Title Case**: `Vacation Photo.jpg`
- **lowercase**: `vacation photo.jpg`
- **UPPERCASE**: `VACATION PHOTO.JPG`
- **snake_case**: `vacation_photo.jpg`
- **camelCase**: `vacationPhoto.jpg`

### 4. **Remove Patterns**
Strip common junk from names
- Before: `Copy of IMG_1234.jpg`
- After: `1234.jpg`

### 5. **Replace Text**
Find and replace in filenames
- Before: `old_name_file.txt`
- After: `new_name_file.txt`

### 6. **Add Suffixes**
Add text before extension
- Before: `document.pdf`
- After: `document_backup.pdf`

### 7. **Sequential Numbering**
Add numbers to multiple files
- `Photo_001.jpg`
- `Photo_002.jpg`
- `Photo_003.jpg`

---

## 🚀 Quick Start

### Python Usage

```python
from smart_renamer import SmartRenamer
from pathlib import Path

renamer = SmartRenamer()

# Clean a single filename
clean = renamer.sanitize_filename("My File!@#$.txt")
# Result: "My File.txt"

# Add date prefix
dated = renamer.add_date_prefix("photo.jpg")
# Result: "2026-01-21_photo.jpg"

# Standardize case
title = renamer.standardize_case("my file name.txt", "title")
# Result: "My File Name.txt"

# Remove patterns
clean = renamer.remove_patterns("Copy of IMG_1234.jpg", ["Copy of ", "IMG_"])
# Result: "1234.jpg"

# Replace text
new = renamer.replace_text("old_name.txt", "old", "new")
# Result: "new_name.txt"
```

---

## 📦 Bulk Rename

### Preview Changes First

```python
from smart_renamer import SmartRenamer, RENAME_RECIPES
from pathlib import Path

renamer = SmartRenamer()

# Get files to rename
files = list(Path("C:/Downloads").glob("*.jpg"))

# Use a preset recipe
operations = RENAME_RECIPES["photos"]

# Preview what will happen
preview = renamer.bulk_rename_preview(files, operations)

for file_path, old_name, new_name in preview:
    print(f"{old_name} → {new_name}")
```

### Execute Renames

```python
# Dry run first (safe - doesn't actually rename)
success, errors, messages = renamer.execute_renames(dry_run=True)

# If looks good, do it for real
success, errors, messages = renamer.execute_renames(dry_run=False)

print(f"Renamed {success} files")
```

---

## 🎨 Preset Recipes

### Photos Recipe
```python
operations = RENAME_RECIPES["photos"]
# - Adds date prefix
# - Removes IMG_, DSC_, DCIM_
# - Title Case
```

### Documents Recipe
```python
operations = RENAME_RECIPES["documents"]
# - Sanitizes
# - Removes "Copy of"
# - Title Case
```

### Downloads Recipe
```python
operations = RENAME_RECIPES["downloads"]
# - Sanitizes
# - Removes (1), (2), - Copy
# - Title Case
```

### Clean All Recipe
```python
operations = RENAME_RECIPES["clean_all"]
# - Sanitizes
# - Title Case
```

---

## 🔧 Custom Operations

### Build Your Own Recipe

```python
custom_operations = [
    {"type": "sanitize"},                           # Clean special chars
    {"type": "add_date", "format": "%Y-%m-%d"},    # Add date
    {"type": "remove", "patterns": ["IMG_", "DSC_"]},  # Remove patterns
    {"type": "replace", "find": "old", "replace": "new"},  # Replace text
    {"type": "case", "style": "title"},            # Title Case
    {"type": "suffix", "suffix": "_backup"}        # Add suffix
]

preview = renamer.bulk_rename_preview(files, custom_operations)
```

### Operation Types

| Type | Options | Example |
|------|---------|---------|
| `sanitize` | None | Removes special chars |
| `add_date` | `format` | Adds date prefix |
| `case` | `style` (title/lower/upper/snake/camel) | Changes case |
| `remove` | `patterns` (list) | Removes text |
| `replace` | `find`, `replace` | Replaces text |
| `suffix` | `suffix` | Adds before extension |

---

## 💡 Examples

### Clean Camera Photos

```python
operations = [
    {"type": "add_date", "format": "%Y-%m-%d"},
    {"type": "remove", "patterns": ["IMG_", "DSC_"]},
    {"type": "case", "style": "title"}
]

# IMG_1234.jpg → 2026-01-21_1234.jpg → 2026-01-21_1234.Jpg
```

### Standardize Documents

```python
operations = [
    {"type": "sanitize"},
    {"type": "remove", "patterns": ["Copy of ", "- Copy"]},
    {"type": "case", "style": "snake"}
]

# Copy of My Document!.pdf → my_document.pdf
```

### Add Version Numbers

```python
operations = [
    {"type": "sanitize"},
    {"type": "suffix", "suffix": "_v1"}
]

# document.pdf → document_v1.pdf
```

---

## ⚠️ Safety Tips

1. **Always preview first** - Use `bulk_rename_preview()` before executing
2. **Test with dry_run** - Set `dry_run=True` first
3. **Backup important files** - Have backups before bulk operations
4. **Check for conflicts** - The renamer will skip existing files

---

## 🎯 Common Use Cases

### Organize Downloads
```python
files = Path("C:/Users/Noble/Downloads").glob("*")
operations = RENAME_RECIPES["downloads"]
preview = renamer.bulk_rename_preview(files, operations)
```

### Date Your Photos
```python
files = Path("C:/Photos").glob("*.jpg")
operations = [{"type": "add_date", "format": "%Y-%m-%d"}]
preview = renamer.bulk_rename_preview(files, operations)
```

### Clean Up Copied Files
```python
files = Path("C:/Documents").glob("*Copy*")
operations = [{"type": "remove", "patterns": ["Copy of ", " - Copy"]}]
preview = renamer.bulk_rename_preview(files, operations)
```

---

## 🔗 Integration with File Organizer

The Smart Renamer can be used with the File Organizer to:
1. Clean filenames BEFORE organizing
2. Standardize names in organized folders
3. Batch rename files in specific categories

---

Built by Tyler Noble
Keiser University - IT Cybersecurity
Smart File Renaming - January 2026
