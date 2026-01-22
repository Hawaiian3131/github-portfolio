"""
Smart File Renaming Module
Bulk rename files with patterns, clean names, add dates, standardize
"""
import re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict


class SmartRenamer:
    def __init__(self):
        self.rename_preview = []
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Remove special characters and clean filename
        
        Args:
            filename: Original filename
            
        Returns:
            Cleaned filename
        """
        # Get name and extension
        name = Path(filename).stem
        ext = Path(filename).suffix
        
        # Remove special characters (keep alphanumeric, spaces, hyphens, underscores)
        name = re.sub(r'[^\w\s\-]', '', name)
        
        # Replace multiple spaces with single space
        name = re.sub(r'\s+', ' ', name)
        
        # Replace spaces with underscores (optional)
        # name = name.replace(' ', '_')
        
        # Remove leading/trailing spaces
        name = name.strip()
        
        return f"{name}{ext}"
    
    def add_date_prefix(self, filename: str, date: datetime = None, format: str = "%Y-%m-%d") -> str:
        """
        Add date prefix to filename
        
        Args:
            filename: Original filename
            date: Date to use (default: file creation date)
            format: Date format string
            
        Returns:
            Filename with date prefix
        """
        if date is None:
            date = datetime.now()
        
        name = Path(filename).stem
        ext = Path(filename).suffix
        
        date_str = date.strftime(format)
        
        # Check if already has date prefix
        if name.startswith(date_str):
            return filename
        
        return f"{date_str}_{name}{ext}"
    
    def standardize_case(self, filename: str, style: str = "title") -> str:
        """
        Standardize filename case
        
        Args:
            filename: Original filename
            style: "title", "lower", "upper", "camel", "snake"
            
        Returns:
            Filename with standardized case
        """
        name = Path(filename).stem
        ext = Path(filename).suffix.lower()  # Extensions always lowercase
        
        if style == "title":
            # Title Case For Each Word
            name = name.replace('_', ' ').replace('-', ' ')
            name = ' '.join(word.capitalize() for word in name.split())
        
        elif style == "lower":
            # all lowercase
            name = name.lower()
        
        elif style == "upper":
            # ALL UPPERCASE
            name = name.upper()
        
        elif style == "camel":
            # camelCaseExample
            words = re.split(r'[\s_-]+', name)
            name = words[0].lower() + ''.join(word.capitalize() for word in words[1:])
        
        elif style == "snake":
            # snake_case_example
            name = re.sub(r'[\s-]+', '_', name).lower()
        
        return f"{name}{ext}"
    
    def remove_patterns(self, filename: str, patterns: List[str]) -> str:
        """
        Remove specific patterns from filename
        
        Args:
            filename: Original filename
            patterns: List of patterns to remove (e.g., ["IMG_", "Copy of "])
            
        Returns:
            Filename with patterns removed
        """
        name = Path(filename).stem
        ext = Path(filename).suffix
        
        for pattern in patterns:
            name = name.replace(pattern, '')
        
        # Clean up any double spaces
        name = re.sub(r'\s+', ' ', name).strip()
        
        return f"{name}{ext}"
    
    def add_suffix(self, filename: str, suffix: str) -> str:
        """
        Add suffix before extension
        
        Args:
            filename: Original filename
            suffix: Suffix to add (e.g., "_backup", "_v2")
            
        Returns:
            Filename with suffix
        """
        name = Path(filename).stem
        ext = Path(filename).suffix
        
        return f"{name}{suffix}{ext}"
    
    def replace_text(self, filename: str, find: str, replace: str) -> str:
        """
        Replace text in filename
        
        Args:
            filename: Original filename
            find: Text to find
            replace: Text to replace with
            
        Returns:
            Filename with text replaced
        """
        name = Path(filename).stem
        ext = Path(filename).suffix
        
        name = name.replace(find, replace)
        
        return f"{name}{ext}"
    
    def sequential_numbering(self, filenames: List[str], start: int = 1, digits: int = 3) -> List[Tuple[str, str]]:
        """
        Add sequential numbers to multiple files
        
        Args:
            filenames: List of original filenames
            start: Starting number
            digits: Number of digits (e.g., 3 = "001", "002")
            
        Returns:
            List of (original, new) filename tuples
        """
        results = []
        
        for i, filename in enumerate(filenames):
            name = Path(filename).stem
            ext = Path(filename).suffix
            
            number = str(start + i).zfill(digits)
            new_name = f"{name}_{number}{ext}"
            
            results.append((filename, new_name))
        
        return results
    
    def bulk_rename_preview(self, file_paths: List[Path], operations: List[Dict]) -> List[Tuple[Path, str, str]]:
        """
        Preview bulk rename operations
        
        Args:
            file_paths: List of file paths to rename
            operations: List of operation dictionaries
                Example: [
                    {"type": "sanitize"},
                    {"type": "add_date", "format": "%Y-%m-%d"},
                    {"type": "case", "style": "title"}
                ]
        
        Returns:
            List of (path, old_name, new_name) tuples
        """
        preview = []
        
        for file_path in file_paths:
            original_name = file_path.name
            new_name = original_name
            
            # Apply each operation in sequence
            for op in operations:
                op_type = op.get("type")
                
                if op_type == "sanitize":
                    new_name = self.sanitize_filename(new_name)
                
                elif op_type == "add_date":
                    date_format = op.get("format", "%Y-%m-%d")
                    file_date = datetime.fromtimestamp(file_path.stat().st_ctime)
                    new_name = self.add_date_prefix(new_name, file_date, date_format)
                
                elif op_type == "case":
                    style = op.get("style", "title")
                    new_name = self.standardize_case(new_name, style)
                
                elif op_type == "remove":
                    patterns = op.get("patterns", [])
                    new_name = self.remove_patterns(new_name, patterns)
                
                elif op_type == "suffix":
                    suffix = op.get("suffix", "")
                    new_name = self.add_suffix(new_name, suffix)
                
                elif op_type == "replace":
                    find = op.get("find", "")
                    replace = op.get("replace", "")
                    new_name = self.replace_text(new_name, find, replace)
            
            # Only add to preview if name actually changed
            if new_name != original_name:
                preview.append((file_path, original_name, new_name))
        
        self.rename_preview = preview
        return preview
    
    def execute_renames(self, preview: List[Tuple[Path, str, str]] = None, dry_run: bool = True) -> Tuple[int, int, List[str]]:
        """
        Execute the rename operations
        
        Args:
            preview: List from bulk_rename_preview (uses self.rename_preview if None)
            dry_run: If True, don't actually rename
            
        Returns:
            (success_count, error_count, messages)
        """
        if preview is None:
            preview = self.rename_preview
        
        success_count = 0
        error_count = 0
        messages = []
        
        for file_path, old_name, new_name in preview:
            try:
                new_path = file_path.parent / new_name
                
                # Check if destination already exists
                if new_path.exists() and new_path != file_path:
                    messages.append(f"Skip (exists): {old_name} → {new_name}")
                    error_count += 1
                    continue
                
                if not dry_run:
                    file_path.rename(new_path)
                    messages.append(f"Renamed: {old_name} → {new_name}")
                    success_count += 1
                else:
                    messages.append(f"Would rename: {old_name} → {new_name}")
                    success_count += 1
            
            except Exception as e:
                messages.append(f"Error renaming {old_name}: {str(e)}")
                error_count += 1
        
        return success_count, error_count, messages
    
    def suggest_rename(self, filename: str) -> str:
        """
        Automatically suggest best rename based on filename analysis
        
        Args:
            filename: Original filename
            
        Returns:
            Suggested new filename
        """
        # Start with sanitized version
        new_name = self.sanitize_filename(filename)
        
        # Check for common prefixes to remove
        common_prefixes = ["IMG_", "DSC_", "Copy of ", "Copy (", "Untitled"]
        for prefix in common_prefixes:
            if new_name.startswith(prefix):
                new_name = self.remove_patterns(new_name, [prefix])
        
        # Apply title case for readability
        new_name = self.standardize_case(new_name, "title")
        
        return new_name


# Preset rename recipes
RENAME_RECIPES = {
    "photos": [
        {"type": "add_date", "format": "%Y-%m-%d"},
        {"type": "remove", "patterns": ["IMG_", "DSC_", "DCIM_"]},
        {"type": "case", "style": "title"}
    ],
    "documents": [
        {"type": "sanitize"},
        {"type": "remove", "patterns": ["Copy of ", "Copy (", "- Copy"]},
        {"type": "case", "style": "title"}
    ],
    "downloads": [
        {"type": "sanitize"},
        {"type": "remove", "patterns": [" (1)", " (2)", " - Copy"]},
        {"type": "case", "style": "title"}
    ],
    "clean_all": [
        {"type": "sanitize"},
        {"type": "case", "style": "title"}
    ]
}
